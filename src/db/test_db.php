<?php
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json");

$host = "localhost";
$user = "root";
$pass = "";
$db   = "islamiccenter";

$conn = new mysqli($host, $user, $pass, $db);

if ($conn->connect_error) {
    die(json_encode(["error" => "DB Connection failed: " . $conn->connect_error]));
}

// Test direct database update
$test_sql = "UPDATE users SET phone = 'TEST_PHONE', email = 'test@test.com', current_year = 'TEST_YEAR' WHERE id = 8";

if ($conn->query($test_sql)) {
    echo json_encode(["success" => true, "message" => "Direct update worked", "affected_rows" => $conn->affected_rows]);
} else {
    echo json_encode(["success" => false, "error" => $conn->error]);
}

$conn->close();
?>