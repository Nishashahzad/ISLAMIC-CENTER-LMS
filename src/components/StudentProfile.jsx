import React, { useState, useEffect } from "react";
import { useOutletContext, useParams } from "react-router-dom";
import "./Teachers.css";

const StudentProfile = () => {
  const [studentData, setStudentData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const contextData = useOutletContext();
  const { id } = useParams();

  console.log("🔍 StudentProfile Debug:", {
    contextData,
    id,
    hasContext: !!contextData,
    hasId: !!id,
    studentData,
    loading,
    error
  });

  // Fetch REAL student data from database using the userid from context
  useEffect(() => {
    const fetchStudentData = async () => {
      try {
        setLoading(true);
        setError(null);
        console.log("🔄 Starting data fetch...");
        
        // Get the actual userid from context to fetch real data
        const useridToFetch = contextData?.id || id;
        
        if (useridToFetch) {
          console.log("🌐 Fetching REAL data from API with userid:", useridToFetch);
          
          // Fetch by userid (not id) - you might need to adjust your API
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
          const realStudentData = Array.isArray(data) ? data[0] : data;
          
          if (!realStudentData) {
            throw new Error('No student data found in database');
          }
          
          console.log("✅ REAL data set successfully:", realStudentData);
          setStudentData(realStudentData);
        } 
        else {
          throw new Error('No student userid available to fetch data');
        }
      } catch (err) {
        console.error('❌ Error fetching REAL student data:', err);
        setError(err.message);
      } finally {
        setLoading(false);
        console.log("🏁 Fetch completed, loading set to false");
      }
    };

    fetchStudentData();
  }, [contextData, id]);

  // Test the API with the actual userid
  const testApi = async () => {
    try {
      const useridToTest = contextData?.id || id;
      console.log("🧪 Testing API with userid:", useridToTest);
      
      const testUrl = `http://localhost/islamiccenter-api/users.php?userid=${useridToTest}`;
      const response = await fetch(testUrl);
      const data = await response.json();
      console.log("🧪 API Test Result:", data);
      alert(`API test successful! Found data for user: ${useridToTest}. Check console for details.`);
    } catch (err) {
      console.error("🧪 API Test Failed:", err);
      alert('API test failed: ' + err.message);
    }
  };

  if (loading) {
    return (
      <div className="profile-container">
        <div className="loading-message">
          <h2>Loading Student Profile...</h2>
          <p>Please wait while we fetch your real data from database.</p>
          <div style={{marginTop: '20px', fontSize: '14px', color: '#666'}}>
            <p>User ID: {contextData?.id || id || 'Not available'}</p>
            <p>Fetching from: {`http://localhost/islamiccenter-api/users.php?userid=${contextData?.id || id}`}</p>
          </div>
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
          <h2>Error Loading Student Data</h2>
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

  if (!studentData) {
    return (
      <div className="profile-container">
        <div className="error-message">
          <h2>Student data not found</h2>
          <p>No real student data found in database.</p>
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

  console.log("🎯 Rendering with REAL studentData:", studentData);

  return (
    <div className="profile-container">
      <div className="profile-header">
        <h1>Student Profile</h1>
        <div className="role-badge">{studentData.role || "student"}</div>
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
        User: {studentData.fullName || studentData.name}
        <br />
        Email: {studentData.email}
      </div>

      <div className="profile-content">
        <div className="profile-section">
          <h2>Personal Information</h2>
          <div className="info-grid">
            <div className="info-item">
              <label>Full Name:</label>
              <span>{studentData.fullName || studentData.name || "Not provided"}</span>
            </div>
            <div className="info-item">
              <label>User ID:</label>
              <span>{studentData.userid || studentData.userId || studentData.id || "Not provided"}</span>
            </div>
            <div className="info-item">
              <label>Date of Birth:</label>
              <span>{studentData.dob || "Not provided"}</span>
            </div>
            <div className="info-item">
              <label>Phone:</label>
              <span>{studentData.phone || "Not provided"}</span>
            </div>
            <div className="info-item">
              <label>Email:</label>
              <span>{studentData.email || "Not provided"}</span>
            </div>
          </div>
        </div>

        <div className="profile-section">
          <h2>Academic Information</h2>
          <div className="info-grid">
            <div className="info-item">
              <label>Education:</label>
              <span>{studentData.education || "Not provided"}</span>
            </div>
            <div className="info-item">
              <label>Qualification:</label>
              <span>{studentData.qualification || "Not provided"}</span>
            </div>
            <div className="info-item">
              <label>Subject:</label>
              <span>{studentData.subject || "Not provided"}</span>
            </div>
            <div className="info-item">
              <label>Current Year:</label>
              <span>{studentData.current_year || "Not provided"}</span>
            </div>
          </div>
        </div>

        <div className="profile-section">
          <h2>Contact Information</h2>
          <div className="info-grid">
            <div className="info-item full-width">
              <label>Address:</label>
              <span>{studentData.address || "Not provided"}</span>
            </div>
          </div>
        </div>

        <div className="profile-section">
          <h2>Account Information</h2>
          <div className="info-grid">
            <div className="info-item">
              <label>Role:</label>
              <span className="role-text">{studentData.role || "student"}</span>
            </div>
            <div className="info-item">
              <label>Account Created:</label>
              <span>{studentData.created_at ? new Date(studentData.created_at).toLocaleDateString() : "Not available"}</span>
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

export default StudentProfile;