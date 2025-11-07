import React, { useState, useEffect } from 'react';
import "./StudentCourses.css";
import { useLocation, useNavigate, useParams } from 'react-router-dom';

const StudentNotifications = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { userId } = useParams();
  const { subject, teacher, studentData } = location.state || {};
  
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (subject && teacher) {
      fetchNotifications();
    }
  }, [subject, teacher]);

  const fetchNotifications = async () => {
    try {
      const response = await fetch(`http://localhost:8000/notifications/${teacher.userId}/${subject}`);
      const data = await response.json();
      
      if (data.success) {
        setNotifications(data.notifications);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error fetching notifications:', error);
      setLoading(false);
    }
  };

  const handleBack = () => {
    navigate(`/student-dashboard/${userId}/courses`);
  };

  if (loading) return <div className="loading">Loading notifications...</div>;

  return (
  <div className="student-notifications-container">
    <div className="student-notifications-header">
      <button onClick={handleBack} className="student-notifications-back-btn">
        ← Back to Courses
      </button>
      <h1 className="student-notifications-title">🔔 Notifications - {subject}</h1>
    </div>

    <div className="student-notifications-content-section">
      <div className="student-notifications-info-card">
        <p><strong>Teacher:</strong> {teacher?.fullName || 'Not assigned'}</p>
        <p><strong>Total Notifications:</strong> {notifications.length}</p>
      </div>

      {notifications.length === 0 ? (
        <div className="no-data">No notifications available for this subject.</div>
      ) : (
        <div className="student-notifications-list">
          {notifications.map((notification) => (
            <div key={notification.id} className={`student-notification-card ${notification.priority}`}>
              <div className="student-notification-header">
                <h3>{notification.title}</h3>
                <span className={`student-priority-badge ${notification.priority}`}>
                  {notification.priority}
                </span>
              </div>
              <p>{notification.message}</p>
              <div className="student-notification-meta">
                <span>Posted: {new Date(notification.created_date).toLocaleDateString()}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  </div>
);
};

export default StudentNotifications;