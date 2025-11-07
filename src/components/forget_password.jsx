import React from "react";
import { useNavigate } from "react-router-dom";
import "./HomePage.css"; 
import logo from "../assets/logo.png";

const ForgetPassword = () => {
    const navigate = useNavigate();

    return (
        <div className="homepage">
            <header className="navbar">
                <div className="logo-container">
                    <img src={logo} alt="LMS Logo" className="logo-img" />
                </div>
            </header>

            <div className="hero-section">
                <div className="forget-password-box">
                    <h2>Reset Password</h2>
                    <p>Please contact the <b>Administrator</b> to reset your password.</p>
                    <button
                        className="login-btn"
                        onClick={() => navigate("/")}
                    >
                        Back to Login
                    </button>
                </div>
            </div>

        </div>
    );
};

export default ForgetPassword;
