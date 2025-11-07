<?php
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With");
header("Content-Type: application/json");

if ($_SERVER['REQUEST_METHOD'] == 'OPTIONS') {
    http_response_code(200);
    exit();
}

// Enable error reporting for debugging
error_reporting(E_ALL);
ini_set('display_errors', 1);

$host = "localhost";
$user = "root";
$pass = "";
$db   = "islamiccenter";

$conn = new mysqli($host, $user, $pass, $db);
if ($conn->connect_error) {
    echo json_encode(["error" => "DB Connection failed: " . $conn->connect_error]);
    exit();
}

$method = $_SERVER["REQUEST_METHOD"];

// ==== READ USERS (GET) ====
if ($method === "GET") {
    error_log("=== GET REQUEST ===");
    error_log("GET Parameters: " . print_r($_GET, true));
    
    if (isset($_GET["id"])) {
        // Get single user by ID
        $id = $_GET["id"];
        $stmt = $conn->prepare("SELECT * FROM users WHERE id = ?");
        $stmt->bind_param("i", $id);
        $stmt->execute();
        $result = $stmt->get_result();
        $user = $result->fetch_assoc();
        
        if ($user) {
            // Ensure consistent field names
            $user['userid'] = $user['userId'] ?? $user['userid'] ?? null;
            echo json_encode($user);
        } else {
            echo json_encode(["error" => "User not found"]);
        }
        $stmt->close();
    } 
    elseif (isset($_GET["userid"])) {
        // Get single user by userid (username)
        $userid = $_GET["userid"];
        $stmt = $conn->prepare("SELECT * FROM users WHERE userId = ? OR userid = ?");
        $stmt->bind_param("ss", $userid, $userid);
        $stmt->execute();
        $result = $stmt->get_result();
        $users = [];
        while ($row = $result->fetch_assoc()) {
            // Ensure consistent field names
            $row['userid'] = $row['userId'] ?? $row['userid'] ?? null;
            $users[] = $row;
        }
        
        if (count($users) > 0) {
            echo json_encode(count($users) === 1 ? $users[0] : $users);
        } else {
            echo json_encode(["error" => "User not found with userid: " . $userid]);
        }
        $stmt->close();
    }
    elseif (isset($_GET["role"])) {
        // Role-based filtering
        $role = $_GET["role"];
        $stmt = $conn->prepare("SELECT * FROM users WHERE role = ?");
        $stmt->bind_param("s", $role);
        $stmt->execute();
        $result = $stmt->get_result();
        $users = [];
        while ($row = $result->fetch_assoc()) {
            // Ensure consistent field names - map userId to userid
            $row['userid'] = $row['userId'] ?? $row['userid'] ?? null;
            $users[] = $row;
        }
        error_log("Returning " . count($users) . " users with role: " . $role);
        echo json_encode($users);
        $stmt->close();
    } else {
        // Get all users
        $stmt = $conn->prepare("SELECT * FROM users");
        $stmt->execute();
        $result = $stmt->get_result();
        $users = [];
        while ($row = $result->fetch_assoc()) {
            // Ensure consistent field names
            $row['userid'] = $row['userId'] ?? $row['userid'] ?? null;
            $users[] = $row;
        }
        echo json_encode($users);
        $stmt->close();
    }
}

// ==== CREATE USER (POST) ====
elseif ($method === "POST") {
    $input = file_get_contents("php://input");
    $data = json_decode($input, true);

    error_log("=== CREATE USER REQUEST ===");
    error_log("Data: " . print_r($data, true));

    // Extract into variables
    $userid = $data["userid"] ?? null;
    $password = $data["password"] ?? null;
    $fullName = $data["fullName"] ?? null;
    $dob = $data["dob"] ?? null;
    $phone = $data["phone"] ?? null;
    $email = $data["email"] ?? null;
    $education = $data["education"] ?? null;
    $address = $data["address"] ?? null;
    $current_year = $data["current_year"] ?? null;
    $role = $data["role"] ?? null;

    // Required fields check
    if (!$userid || !$password || !$fullName || !$dob || !$email || !$current_year || !$role) {
        $missing = [];
        if (!$userid) $missing[] = "userid";
        if (!$password) $missing[] = "password";
        if (!$fullName) $missing[] = "fullName";
        if (!$dob) $missing[] = "dob";
        if (!$email) $missing[] = "email";
        if (!$current_year) $missing[] = "current_year";
        if (!$role) $missing[] = "role";
        
        echo json_encode(["success" => false, "error" => "Missing required fields: " . implode(", ", $missing)]);
        exit();
    }

    $stmt = $conn->prepare("INSERT INTO users 
        (userId, password, fullName, dob, phone, email, education, address, current_year, role) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)");
    
    if (!$stmt) {
        echo json_encode(["success" => false, "error" => "Prepare failed: " . $conn->error]);
        exit();
    }

    // Using variables - note: using userId (database column name)
    $stmt->bind_param(
        "ssssssssss",
        $userid, $password, $fullName, $dob, $phone, $email,
        $education, $address, $current_year, $role
    );

    if ($stmt->execute()) {
        echo json_encode(["success" => true, "insert_id" => $stmt->insert_id]);
    } else {
        echo json_encode(["success" => false, "error" => $stmt->error]);
    }
    $stmt->close();
}

// ==== UPDATE USER (PUT) ====
elseif ($method === "PUT") {
    $input = file_get_contents("php://input");
    $data = json_decode($input, true);

    error_log("=== UPDATE REQUEST ===");
    error_log("Data: " . print_r($data, true));

    $id = $data["id"] ?? null;
    if (!$id) {
        echo json_encode(["success" => false, "error" => "Missing ID"]);
        exit();
    }

    // Extract values into variables first
    $fullName = $data["fullName"] ?? "";
    $dob = $data["dob"] ?? "";
    $phone = $data["phone"] ?? "";
    $email = $data["email"] ?? "";
    $education = $data["education"] ?? "";
    $qualification = $data["qualification"] ?? "";
    $subject = $data["subject"] ?? "";
    $address = $data["address"] ?? "";
    $current_year = $data["current_year"] ?? "";

    $sql = "UPDATE users SET 
            fullName = ?, 
            dob = ?, 
            phone = ?, 
            email = ?, 
            education = ?, 
            qualification = ?,
            subject = ?,
            address = ?, 
            current_year = ? 
            WHERE id = ?";

    $stmt = $conn->prepare($sql);
    if (!$stmt) {
        error_log("Prepare error: " . $conn->error);
        echo json_encode(["success" => false, "error" => "Prepare failed: " . $conn->error]);
        exit();
    }

    $stmt->bind_param(
        "sssssssssi",
        $fullName,      // 1st ? in SQL
        $dob,           // 2nd ? in SQL  
        $phone,         // 3rd ? in SQL
        $email,         // 4th ? in SQL
        $education,     // 5th ? in SQL
        $qualification, // 6th ? in SQL
        $subject,       // 7th ? in SQL
        $address,       // 8th ? in SQL
        $current_year,  // 9th ? in SQL
        $id             // 10th ? in SQL
    );

    if ($stmt->execute()) {
        error_log("✅ UPDATE SUCCESSFUL");
        error_log("Affected rows: " . $stmt->affected_rows);
        
        echo json_encode([
            "success" => true,
            "affected_rows" => $stmt->affected_rows,
            "message" => "Student updated successfully"
        ]);
    } else {
        error_log("❌ UPDATE FAILED: " . $stmt->error);
        echo json_encode([
            "success" => false, 
            "error" => $stmt->error
        ]);
    }

    $stmt->close();
}

// ==== DELETE USER ====
elseif ($method === "DELETE") {
    $id = $_GET["id"] ?? null;
    if (!$id) {
        echo json_encode(["success" => false, "error" => "Missing ID"]);
        exit();
    }

    $stmt = $conn->prepare("DELETE FROM users WHERE id=?");
    $stmt->bind_param("i", $id);
    
    if ($stmt->execute()) {
        echo json_encode(["success" => true, "affected_rows" => $stmt->affected_rows]);
    } else {
        echo json_encode(["success" => false, "error" => $stmt->error]);
    }
    $stmt->close();
} else {
    echo json_encode(["error" => "Method not allowed"]);
}

$conn->close();
?>