import React, { useState, useEffect } from "react";
import "./Teachers.css";

const TeacherProfile = () => {
  const [teacherData, setTeacherData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch teacher data from database
  useEffect(() => {
    const fetchTeacherData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Get current user from localStorage to get their userid
        const localUser = JSON.parse(localStorage.getItem("user"));
        
        if (!localUser) {
          throw new Error('No user found in localStorage. Please log in again.');
        }

        const useridToFetch = localUser.userid || localUser.userId || localUser.id;
        
        if (useridToFetch) {
          console.log("🌐 Fetching REAL teacher data from API with userid:", useridToFetch);
          
          const apiUrl = `http://localhost/islamiccenter-api/users.php?userid=${useridToFetch}`;
          console.log("📡 API URL:", apiUrl);
          
          const response = await fetch(apiUrl);
          console.log("📨 Response status:", response.status);
          
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          
          const data = await response.json();
          console.log("📊 API Response data:", data);
          
          if (data.error) {
            throw new Error(data.error);
          }
          
          // If we get an array, take the first user
          const realTeacherData = Array.isArray(data) ? data[0] : data;
          
          if (!realTeacherData) {
            throw new Error('No teacher data found in database');
          }
          
          console.log("✅ REAL teacher data set successfully:", realTeacherData);
          setTeacherData(realTeacherData);
        } 
        else {
          throw new Error('No teacher userid available to fetch data');
        }
      } catch (err) {
        console.error('❌ Error fetching REAL teacher data:', err);
        setError(err.message);
      } finally {
        setLoading(false);
        console.log("🏁 Fetch completed, loading set to false");
      }
    };

    fetchTeacherData();
  }, []);

  // Test the API with the actual userid
  const testApi = async () => {
    try {
      const localUser = JSON.parse(localStorage.getItem("user"));
      const useridToTest = localUser?.userid || localUser?.userId || localUser?.id;
      
      console.log("🧪 Testing API with userid:", useridToTest);
      
      const testUrl = `http://localhost/islamiccenter-api/users.php?userid=${useridToTest}`;
      const response = await fetch(testUrl);
      const data = await response.json();
      console.log("🧪 API Test Result:", data);
      alert(`API test successful! Found data for teacher: ${useridToTest}. Check console for details.`);
    } catch (err) {
      console.error("🧪 API Test Failed:", err);
      alert('API test failed: ' + err.message);
    }
  };

  if (loading) {
    return (
      <div className="profile-container">
        <div className="loading-message">
          <h2>Loading Teacher Profile...</h2>
          <p>Please wait while we fetch your real data from database.</p>
          <button 
            className="edit-btn" 
            onClick={testApi}
            style={{marginTop: '10px'}}
          >
            Test API Connection
          </button>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="profile-container">
        <div className="error-message">
          <h2>Error Loading Teacher Data</h2>
          <p>{error}</p>
          <div style={{marginTop: '20px', display: 'flex', gap: '10px', justifyContent: 'center'}}>
            <button 
              className="edit-btn" 
              onClick={() => window.location.reload()}
            >
              Try Again
            </button>
            <button 
              className="change-password-btn" 
              onClick={testApi}
            >
              Test API
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!teacherData) {
    return (
      <div className="profile-container">
        <div className="error-message">
          <h2>Teacher data not found</h2>
          <p>No real teacher data found in database.</p>
          <button 
            className="edit-btn" 
            onClick={testApi}
            style={{marginTop: '10px'}}
          >
            Test API Connection
          </button>
        </div>
      </div>
    );
  }

  console.log("🎯 Rendering with REAL teacherData:", teacherData);

  return (
    <div className="profile-container">
      <div className="profile-header">
        <h1>Teacher Profile</h1>
        <div className="role-badge">{teacherData.role || "teacher"}</div>
      </div>

      {/* Debug panel - shows we're using real data now */}
      <div style={{
        background: '#d4edda', 
        padding: '10px', 
        margin: '10px 0', 
        borderRadius: '5px',
        fontSize: '12px',
        border: '1px solid #c3e6cb',
        color: '#155724'
      }}>
        <strong>✅ Using REAL Database Data</strong> 
        <br />
        Data Source: Database API
        <br />
        Teacher: {teacherData.fullName || teacherData.name}
        <br />
        Email: {teacherData.email}
      </div>

      <div className="profile-content">
        <div className="profile-section">
          <h2>Personal Information</h2>
          <div className="info-grid">
            <div className="info-item">
              <label>Full Name:</label>
              <span>{teacherData.fullName || teacherData.name || "Not provided"}</span>
            </div>
            <div className="info-item">
              <label>User ID:</label>
              <span>{teacherData.userid || teacherData.userId || teacherData.id || "Not provided"}</span>
            </div>
            <div className="info-item">
              <label>Date of Birth:</label>
              <span>{teacherData.dob || "Not provided"}</span>
            </div>
            <div className="info-item">
              <label>Phone:</label>
              <span>{teacherData.phone || "Not provided"}</span>
            </div>
            <div className="info-item">
              <label>Email:</label>
              <span>{teacherData.email || "Not provided"}</span>
            </div>
          </div>
        </div>

        <div className="profile-section">
          <h2>Professional Information</h2>
          <div className="info-grid">
            <div className="info-item">
              <label>Qualification:</label>
              <span>{teacherData.qualification || "Not provided"}</span>
            </div>
            <div className="info-item">
              <label>Subject:</label>
              <span>{teacherData.subject || "Not provided"}</span>
            </div>
            <div className="info-item">
              <label>Education:</label>
              <span>{teacherData.education || "Not provided"}</span>
            </div>
            <div className="info-item">
              <label>Current Year:</label>
              <span>{teacherData.current_year || "Not provided"}</span>
            </div>
          </div>
        </div>

        <div className="profile-section">
          <h2>Contact Information</h2>
          <div className="info-grid">
            <div className="info-item full-width">
              <label>Address:</label>
              <span>{teacherData.address || "Not provided"}</span>
            </div>
          </div>
        </div>

        <div className="profile-section">
          <h2>Account Information</h2>
          <div className="info-grid">
            <div className="info-item">
              <label>Role:</label>
              <span className="role-text">{teacherData.role || "teacher"}</span>
            </div>
            <div className="info-item">
              <label>Account Created:</label>
              <span>{teacherData.created_at ? new Date(teacherData.created_at).toLocaleDateString() : "Not available"}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="profile-actions">
        <button className="edit-btn" onClick={() => window.print()}>
          Print Profile
        </button>
        <button className="change-password-btn" onClick={testApi}>
          Test Data Source
        </button>
      </div>
    </div>
  );
};

export default TeacherProfile;