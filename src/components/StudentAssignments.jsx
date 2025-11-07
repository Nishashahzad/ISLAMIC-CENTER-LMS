import React, { useState, useEffect } from 'react';
import "./StudentCourses.css";
import { useLocation, useNavigate, useParams } from 'react-router-dom';

const StudentAssignments = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { userId } = useParams();
  const { subject, teacher, studentData } = location.state || {};
  
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (subject && teacher) {
      fetchAssignments();
    }
  }, [subject, teacher]);

  const fetchAssignments = async () => {
    try {
      const response = await fetch(`http://localhost:8000/assignments/${teacher.userId}/${subject}`);
      const data = await response.json();
      
      if (data.success) {
        setAssignments(data.assignments);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error fetching assignments:', error);
      setLoading(false);
    }
  };

  const handleBack = () => {
    navigate(`/student-dashboard/${userId}/courses`);
  };

  const handleDownload = async (assignment) => {
    try {
      window.open(`http://localhost:8000${assignment.file_path}`, '_blank');
    } catch (error) {
      console.error('Error downloading file:', error);
    }
  };

  if (loading) return <div className="loading">Loading assignments...</div>;

 return (
  <div className="student-assignments-container">
    <div className="student-assignments-header">
      <button onClick={handleBack} className="student-assignments-back-btn">
        ← Back to Courses
      </button>
      <h1 className="student-assignments-title">📝 Assignments - {subject}</h1>
    </div>

    <div className="student-assignments-content-section">
      <div className="student-assignments-info-card">
        <p><strong>Teacher:</strong> {teacher?.fullName || 'Not assigned'}</p>
        <p><strong>Total Assignments:</strong> {assignments.length}</p>
      </div>

      {assignments.length === 0 ? (
        <div className="no-data">No assignments available for this subject.</div>
      ) : (
        <div className="student-assignments-list">
          {assignments.map((assignment) => (
            <div key={assignment.id} className="student-assignment-card">
              <div className="student-assignment-info">
                <h3>{assignment.title}</h3>
                <p>{assignment.description}</p>
                <div className="student-assignment-meta">
                  <span>Due: {new Date(assignment.due_date).toLocaleDateString()}</span>
                  <span>Start: {new Date(assignment.start_date).toLocaleDateString()}</span>
                </div>
              </div>
              {assignment.file_path && (
                <button 
                  onClick={() => handleDownload(assignment)}
                  className="student-assignment-download-btn"
                >
                  📥 Download
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  </div>
);
};

export default StudentAssignments;