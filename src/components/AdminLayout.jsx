import React, { useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import logo from "../assets/logo.png";
import {
  FaUsers,
  FaChalkboardTeacher,
  FaBook,
  FaClipboardList,
  FaChartBar,
  FaMoneyBill,
  FaCog,
} from "react-icons/fa";
import "./AdminDashboard.css";

const AdminLayout = () => {
  const [showSettings, setShowSettings] = useState(false);
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("authToken");
    sessionStorage.removeItem("authToken");
    navigate("/");
  };

  return (
    <div>
      {/* Navbar */}
      <header className="admin-navbar">
        <div className="admin-logo-container">
          <img src={logo} alt="LMS Logo" className="admin-logo-img" />
        </div>

        {/* Desktop nav */}
        <nav className="admin-nav">
          <ul className="admin-nav-list">
            <li className="admin-nav-item">
              <NavLink to="students">Students</NavLink>
            </li>
            <li className="admin-nav-item">
              <NavLink to="teachers">Teachers</NavLink>
            </li>
            <li className="admin-nav-item">
              <NavLink to="AdminCourses">Courses</NavLink>
            </li>
            <li className="admin-nav-item">
              <NavLink to="enrollments">Enrollments</NavLink>
            </li>
            <li className="admin-nav-item">
              <NavLink to="reports">Reports</NavLink>
            </li>
            <li className="admin-nav-item">
              <NavLink to="payments">Payments</NavLink>
            </li>

            {/* Settings Dropdown (Desktop only) */}
            <li
              className="admin-nav-item"
              onClick={() => setShowSettings(!showSettings)}
            >
              Settings ▾
              {showSettings && (
                <ul className="admin-dropdown">
                  <li className="admin-dropdown-item">
                    <NavLink to="profile">My Profile</NavLink>
                  </li>
                  <li className="admin-dropdown-item">
                    <button onClick={handleLogout} className="logout-btn">
                      Logout
                    </button>
                  </li>
                </ul>
              )}
            </li>
          </ul>
        </nav>

        {/* Settings Cog (Mobile only) */}
        <div className="mobile-settings">
          <FaCog
            className="settings-icon"
            onClick={() => setShowSettings(!showSettings)}
          />
          {showSettings && (
            <ul className="settings-dropdown">
              <li>
                <NavLink to="profile">My Profile</NavLink>
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
      <main className="admin-content">
        <Outlet />
      </main>

      {/* Bottom Nav (mobile only) */}
      <nav className="admin-bottom-nav">
        <ul>
          <li>
            <NavLink to="students">
              <FaUsers />
            </NavLink>
          </li>
          <li>
            <NavLink to="teachers">
              <FaChalkboardTeacher />
            </NavLink>
          </li>
          <li>
            <NavLink to="courses">
              <FaBook />
            </NavLink>
          </li>
          <li>
            <NavLink to="enrollments">
              <FaClipboardList />
            </NavLink>
          </li>
          <li>
            <NavLink to="reports">
              <FaChartBar />
            </NavLink>
          </li>
          <li>
            <NavLink to="payments">
              <FaMoneyBill />
            </NavLink>
          </li>
        </ul>
      </nav>
    </div>
  );
};

export default AdminLayout;
