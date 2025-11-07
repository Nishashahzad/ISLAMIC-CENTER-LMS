import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./HomePage.css";
import logo from "../assets/logo.png";
import logo2 from "../assets/logo2.jpg"; // ✅ added import

const HomePage = () => {
  const [userId, setUserId] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch("http://localhost/islamiccenter-api/login.php", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ userId, password }),
      });

      const data = await response.json();
      if (data.success) {
        // Save user info in localStorage
        localStorage.setItem("user", JSON.stringify(data));

        if (data.role === "admin") {
          navigate("/admin-dashboard");
        } else if (data.role === "student") {
          navigate(`/student-dashboard/${data.userId}`); // ✅ student goes to their own dashboard
        } else if (data.role === "teacher") {
          navigate(`/teacher-dashboard/${data.userId}`);
        }

      }
      else {
        alert(data.message || "Invalid User ID or Password!");
      }
    } catch (error) {
      console.error("Login error:", error);
      alert("Server error, please try again.");
    }
  };


  return (
    <div className="homepage">
      <header className="navbar">
        <div className="logo-container">
          <img src={logo} alt="LMS Logo" className="logo-img" />
        </div>
      </header>

      <div className="hero-section">
        <div className="login-box">
          <h2>
            <img src={logo2} alt="Login" className="logo2-img" />
          </h2>
          <form onSubmit={handleLogin}>
            <input
              type="text"
              placeholder="User ID"
              className="input-field"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
            />
            <input
              type="password"
              placeholder="Password"
              className="input-field"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <button type="submit" className="login-btn">
              Login
            </button>

            {/* Forgot Password button → goes to Forget Password page */}
            <button
              type="button"
              onClick={() => navigate("/forget-password")}
              className="forgot-password"
            >
              Forgot Password?
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
