import React, { useState, useEffect } from 'react';
import "./StudentCourses.css";
import { useLocation, useNavigate, useParams } from 'react-router-dom';

const StudentLectures = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { userId } = useParams(); // Get userId from URL
  const { subject, teacher, studentData } = location.state || {};
  
  const [lectures, setLectures] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (subject && teacher) {
      fetchLectures();
    }
  }, [subject, teacher]);

  const fetchLectures = async () => {
    try {
      const response = await fetch(`http://localhost:8000/lectures/${teacher.userId}/${subject}`);
      const data = await response.json();
      
      if (data.success) {
        setLectures(data.lectures);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error fetching lectures:', error);
      setLoading(false);
    }
  };

  const handleBack = () => {
    navigate(`/student-dashboard/${userId}/courses`);
  };

  const handleDownload = async (lecture) => {
    try {
      await fetch(`http://localhost:8000/lectures/${lecture.id}/download`, {
        method: 'POST'
      });
      
      window.open(`http://localhost:8000${lecture.file_path}`, '_blank');
    } catch (error) {
      console.error('Error downloading file:', error);
    }
  };

  if (loading) return <div className="loading">Loading lectures...</div>;

  // In the return statement, update the class names:
return (
  <div className="student-lectures-container">
    <div className="student-lectures-header">
      <button onClick={handleBack} className="student-lectures-back-btn">
        ← Back to Courses
      </button>
      <h1 className="student-lectures-title">📚 Lectures - {subject}</h1>
    </div>

    <div className="student-lectures-content-section">
      <div className="student-lectures-info-card">
        <p><strong>Teacher:</strong> {teacher?.fullName || 'Not assigned'}</p>
        <p><strong>Total Lectures:</strong> {lectures.length}</p>
      </div>

      {lectures.length === 0 ? (
        <div className="no-data">No lectures available for this subject.</div>
      ) : (
        <div className="student-lectures-list">
          {lectures.map((lecture) => (
            <div key={lecture.id} className="student-lecture-card">
              <div className="student-lecture-info">
                <h3>{lecture.title}</h3>
                <p>{lecture.description}</p>
                <div className="student-lecture-meta">
                  <span>Uploaded: {new Date(lecture.upload_date).toLocaleDateString()}</span>
                  <span>Downloads: {lecture.downloads}</span>
                </div>
              </div>
              {lecture.file_path && (
                <button 
                  onClick={() => handleDownload(lecture)}
                  className="student-lecture-download-btn"
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

export default StudentLectures;