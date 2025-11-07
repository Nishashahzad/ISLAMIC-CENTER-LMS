// src/components/TeacherLayout.js
import React, { useState } from "react";
import { NavLink, Outlet, useNavigate, useParams } from "react-router-dom";
import { FaCog } from "react-icons/fa"; // settings icon
import logo from "../assets/logo.png";
import "./Teachers.css";

const TeacherLayout = () => {
  const navigate = useNavigate();
  const { userId } = useParams(); // ✅ get userId from route
  const [showSettings, setShowSettings] = useState(false);

  const handleLogout = () => {
    localStorage.removeItem("user");
    navigate("/");
  };

  return (
    <div>
      {/* Top Navbar */}
      <header className="teacher-navbar">
        {/* Logo */}
        <div className="teacher-logo-container">
          <img src={logo} alt="Logo" />
        </div>

        {/* Desktop Nav */}
        <nav className="teacher-nav">
          <ul className="teacher-nav-list">
            <li className="teacher-nav-item">
              <NavLink to={`/teacher-dashboard/${userId}`}>Dashboard</NavLink>
            </li>
            <li className="teacher-nav-item">
              <NavLink to={`/teacher-dashboard/${userId}/courses`}>
                My Courses
              </NavLink>
            </li>
            {/* <li className="teacher-nav-item">
              <NavLink to={`/teacher-dashboard/${userId}/assignments`}>
                Assignments
              </NavLink>
            </li> */}
            <li className="teacher-nav-item">
              <NavLink to={`/teacher-dashboard/${userId}/profile`}>
                Profile
              </NavLink>
            </li>
            <li className="teacher-nav-item">
              <button onClick={handleLogout} className="logout-btn">
                Logout
              </button>
            </li>
          </ul>
        </nav>

        {/* Mobile Settings (cog) */}
        <div className="mobile-settings">
          <FaCog
            className="settings-icon"
            onClick={() => setShowSettings(!showSettings)}
          />
          {showSettings && (
            <ul className="settings-dropdown">
              <li>
                <NavLink to={`/teacher-dashboard/${userId}/profile`}>
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

      {/* Mobile Bottom Nav */}
      <div className="teacher-bottom-nav">
        <ul>
          <li>
            <NavLink to={`/teacher-dashboard/${userId}`}>🏠</NavLink>
          </li>
          <li>
            <NavLink to={`/teacher-dashboard/${userId}/courses`}>📚</NavLink>
          </li>
          {/*<li>
            <NavLink to={`/teacher-dashboard/${userId}/assignments`}>📝</NavLink>
          </li>*/}
          <li>
            <NavLink to={`/teacher-dashboard/${userId}/profile`}>👤</NavLink>
          </li>
        </ul>
      </div>

      {/* Page Content */}
      <main className="teacher-content">
        <Outlet />
      </main>
    </div>
  );
};

export default TeacherLayout;
