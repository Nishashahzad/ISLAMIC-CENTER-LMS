import React from "react";

const TeacherDashboard = () => {
  const user = JSON.parse(localStorage.getItem("user"));

  return (
    <div>
      <h1>Welcome, {user.fullName} 👩‍🏫</h1>
      <p>Your Role: {user.role}</p>
      <p>User ID: {user.userId}</p>
    </div>
  );
};

export default TeacherDashboard;
