import React, { useState, useEffect } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import "./StudentCourses.css";

const StudentNotifications = () => {
  const { userId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();

  const { subject, teacher, studentData } = location.state || {};

  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterPriority, setFilterPriority] = useState("all");
  const [showAllSubjects, setShowAllSubjects] = useState(false);

  /* =========================
     FETCH NOTIFICATIONS
  ==========================*/
  useEffect(() => {
    if (!studentData) {
      setError("Student data not found");
      setLoading(false);
      return;
    }

    fetchNotifications();
  }, [subject, showAllSubjects]);

  const fetchNotifications = async () => {
    try {
      setLoading(true);
      const studentUserId = studentData.userId || studentData.userid || studentData.id;

      let apiUrl;
      if (showAllSubjects || !subject) {
        // Get all notifications for all subjects
        apiUrl = `http://localhost:8000/student/${studentUserId}/notifications`;
      } else {
        // Get notifications for specific subject
        apiUrl = `http://localhost:8000/student/${studentUserId}/notifications?subject_name=${encodeURIComponent(subject)}`;
      }

      const response = await fetch(apiUrl);
      const data = await response.json();

      if (data.success) {
        setNotifications(data.notifications || []);
      } else {
        setError(data.error || "Failed to load notifications");
      }
    } catch (err) {
      setError("Server error while loading notifications");
      console.error("Error fetching notifications:", err);
    } finally {
      setLoading(false);
    }
  };

  /* =========================
     HELPERS
  ==========================*/
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    });
  };

  const getPriorityBadge = (priority) => {
    const priorityConfig = {
      high: { label: "High", class: "priority-high", icon: "🔴" },
      medium: { label: "Medium", class: "priority-medium", icon: "🟡" },
      low: { label: "Low", class: "priority-low", icon: "🟢" }
    };
    
    const config = priorityConfig[priority] || { label: priority, class: "priority-medium", icon: "🔔" };
    
    return (
      <span className={`priority-badge ${config.class}`}>
        {config.icon} {config.label}
      </span>
    );
  };

  const getFilteredNotifications = () => {
    if (filterPriority === "all") {
      return notifications;
    }
    return notifications.filter(notification => notification.priority === filterPriority);
  };

  const getUnreadCount = () => {
    // You can implement read/unread tracking if you add a 'read' column to notifications table
    return notifications.length; // For now, show total count
  };

  const filteredNotifications = getFilteredNotifications();

  /* =========================
     UI STATES
  ==========================*/
  if (loading) {
    return (
      <div className="student-assignments-container">
        <div className="loading">Loading notifications...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="student-assignments-container">
        <div className="error-message">
          <p>{error}</p>
          <button onClick={() => navigate(-1)}>Go Back</button>
        </div>
      </div>
    );
  }

  return (
    <div className="student-assignments-container">
      {/* Header */}
      <div className="student-assignments-header">
        <button 
          onClick={() => navigate(-1)} 
          className="student-assignments-back-btn"
        >
          ← Back to Courses
        </button>
        <h1 className="student-assignments-title">
          {showAllSubjects || !subject ? "All Notifications" : `${subject} – Notifications`}
        </h1>
        <p className="student-assignments-subtitle">
          Student: {studentData.fullName}
          {subject && !showAllSubjects && ` • Subject: ${subject}`}
          {teacher && ` • Teacher: ${teacher.fullName}`}
        </p>
      </div>

      {/* Stats Card */}
      <div className="assignments-stats-card">
        <div className="stats-grid">
          <div className="stat-item">
            <div className="stat-value">{notifications.length}</div>
            <div className="stat-label">Total Notifications</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">{getUnreadCount()}</div>
            <div className="stat-label">New</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">
              {notifications.filter(n => n.priority === "high").length}
            </div>
            <div className="stat-label">High Priority</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">
              {[...new Set(notifications.map(n => n.subject_name))].length}
            </div>
            <div className="stat-label">Subjects</div>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="notification-controls">
        <div className="filter-controls">
          <label>Filter by Priority:</label>
          <select 
            value={filterPriority} 
            onChange={(e) => setFilterPriority(e.target.value)}
            className="priority-filter"
          >
            <option value="all">All Priorities</option>
            <option value="high">High Priority</option>
            <option value="medium">Medium Priority</option>
            <option value="low">Low Priority</option>
          </select>
        </div>

        <div className="view-controls">
          {subject && (
            <button 
              onClick={() => setShowAllSubjects(!showAllSubjects)}
              className="toggle-view-btn"
            >
              {showAllSubjects ? `Show ${subject} Only` : "Show All Subjects"}
            </button>
          )}
          
          <button 
            onClick={fetchNotifications}
            className="refresh-btn"
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* Notifications List */}
      <div className="student-assignments-list">
        {filteredNotifications.length === 0 ? (
          <div className="no-data">
            <p>No notifications found</p>
            <p className="hint">
              {filterPriority !== "all" 
                ? `Try changing the priority filter or check back later`
                : showAllSubjects 
                  ? "No notifications for any of your subjects"
                  : "No notifications for this subject yet"}
            </p>
          </div>
        ) : (
          filteredNotifications.map((notification, index) => (
            <div key={notification.id} className="student-assignment-card notification-card">
              <div className="assignment-card-header">
                <div>
                  <h3>
                    {notification.title}
                    <span className="subject-badge">
                      {notification.subject_name}
                    </span>
                  </h3>
                  <div className="assignment-meta-row">
                    <span className="meta-item">
                      <strong>From:</strong> {notification.teacher_name}
                    </span>
                    <span className="meta-item">
                      <strong>Date:</strong> {formatDate(notification.created_date)}
                    </span>
                  </div>
                </div>
                <div className="status-container">
                  {getPriorityBadge(notification.priority)}
                </div>
              </div>

              <div className="assignment-card-content">
                <div className="notification-message">
                  <p>{notification.message}</p>
                </div>

                <div className="notification-footer">
                  <small>
                    Notification ID: {notification.id} • 
                    Sent via: Teacher Portal •
                    {notification.teacher_userId && ` Teacher ID: ${notification.teacher_userId}`}
                  </small>
                </div>
              </div>

              <div className="assignment-card-actions">
                <div className="notification-actions">
                  <button className="view-notification-btn">
                    📋 View Details
                  </button>
                  <button className="mark-read-btn">
                    ✓ Mark as Read
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Instructions */}
      <div className="instructions-card">
        <h4>📋 About Notifications</h4>
        <ul>
          <li>• <strong>High Priority (🔴)</strong>: Urgent announcements, deadline changes, or important updates</li>
          <li>• <strong>Medium Priority (🟡)</strong>: Regular class announcements, assignment reminders</li>
          <li>• <strong>Low Priority (🟢)</strong>: General information, resources updates</li>
          <li>• Check notifications regularly to stay updated with class information</li>
          <li>• Notifications are sent by your subject teachers</li>
        </ul>
      </div>
    </div>
  );
};

export default StudentNotifications;