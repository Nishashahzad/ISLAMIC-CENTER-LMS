<?php
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: POST, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With");
header("Content-Type: application/json");

if ($_SERVER['REQUEST_METHOD'] == 'OPTIONS') {
    http_response_code(200);
    exit();
}

$host = "localhost";
$user = "root";
$pass = "";
$db   = "IslamicCenter";

$conn = new mysqli($host, $user, $pass, $db);
if ($conn->connect_error) {
    echo json_encode(["error" => "DB Connection failed"]);
    exit();
}

$data = json_decode(file_get_contents("php://input"), true);
$userId   = $data["userId"];
$password = $data["password"];

// ✅ Check user from DB
$stmt = $conn->prepare("SELECT * FROM users WHERE userId=? AND password=?");
$stmt->bind_param("ss", $userId, $password);
$stmt->execute();
$result = $stmt->get_result();

if ($row = $result->fetch_assoc()) {
    echo json_encode([
        "success" => true,
        "role" => $row["role"],
        "fullName" => $row["fullName"],
        "userId" => $row["userId"]
    ]);
} else {
    echo json_encode(["success" => false, "message" => "Invalid credentials"]);
}

$stmt->close();
$conn->close();
?>
