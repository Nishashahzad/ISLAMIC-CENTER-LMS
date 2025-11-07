import React, { useState } from "react";
import { NavLink, Outlet, useNavigate, useParams } from "react-router-dom";
import { FaCog } from "react-icons/fa";
import logo from "../assets/logo.png";
import "./Students.css";

const StudentLayout = () => {
  const navigate = useNavigate();
  const { userId } = useParams();
  const [showSettings, setShowSettings] = useState(false);

  // 🔹 Example hardcoded studentData (replace with API call or state)
  const studentData = {
    id: userId,
    name: "John Doe",
    email: "john.doe@example.com",
    courses: ["Math", "Science", "History"],
  };

  const handleLogout = () => {
    localStorage.removeItem("user");
    navigate("/");
  };

  return (
    <div>
      {/* Top Navbar */}
      <header className="student-navbar">
        <div className="student-logo-container">
          <img src={logo} alt="Logo" />
        </div>

        <nav className="student-nav">
          <ul className="student-nav-list">
            <li>
              <NavLink to={`/student-dashboard/${userId}`}>Dashboard</NavLink>
            </li>
            <li>
              <NavLink to={`/student-dashboard/${userId}/courses`}>
                My Courses
              </NavLink>
            </li>
            <li>
              <NavLink to={`/student-dashboard/${userId}/profile`}>
                Profile
              </NavLink>
            </li>
            <li>
              <button onClick={handleLogout} className="logout-btn">
                Logout
              </button>
            </li>
          </ul>
        </nav>

        {/* Mobile Settings */}
        <div className="mobile-settings">
          <FaCog
            className="settings-icon"
            onClick={() => setShowSettings(!showSettings)}
          />
          {showSettings && (
            <ul className="settings-dropdown">
              <li>
                <NavLink to={`/student-dashboard/${userId}/profile`}>
                  Profile
                </NavLink>
              </li>
              <li>
                <button onClick={handleLogout} className="logout-btn">
                  Logout
                </button>
              </li>
            </ul>
          )}
        </div>
      </header>

      {/* Page Content */}
      <main className="student-content">
        {/* 🔹 Provide context here */}
        <Outlet context={studentData} />
      </main>
    </div>
  );
};

export default StudentLayout;
