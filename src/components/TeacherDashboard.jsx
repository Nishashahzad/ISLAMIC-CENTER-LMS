import React, { useState, useEffect } from "react";
import "./TeacherDashboard.css";

const TeacherDashboard = () => {
  const [user, setUser] = useState(null);
  const [dashboardData, setDashboardData] = useState({
    teacher_info: {},
    stats: {},
    subject_performance: [],
    pending_grading: [],
    recent_quiz_attempts: [],
    upcoming_deadlines: [],
    recent_activities: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [greeting, setGreeting] = useState("");
  const [dailyQuote, setDailyQuote] = useState("");

  // Get user from localStorage
  useEffect(() => {
    const userData = JSON.parse(localStorage.getItem("user"));
    console.log("🔍 Teacher user data:", userData);
    
    if (!userData) {
      console.error("No user found in localStorage");
      setError("Please login to access the dashboard");
      setLoading(false);
      return;
    }
    
    if (userData.role !== "teacher") {
      console.error("User is not a teacher:", userData.role);
      setError("Access denied. Teacher dashboard only.");
      setLoading(false);
      return;
    }
    
    setUser(userData);
  }, []);

  // Greetings based on time
  useEffect(() => {
    const hour = new Date().getHours();
    if (hour < 12) setGreeting("Good Morning");
    else if (hour < 17) setGreeting("Good Afternoon");
    else setGreeting("Good Evening");
  }, []);

  // Islamic quotes for teachers
  const quotes = [
    "The best among you are those who learn the Quran and teach it. - Prophet Muhammad ﷺ",
    "When a man dies, his deeds come to an end except for three things: ongoing charity, beneficial knowledge, or a righteous child who prays for him. - Prophet Muhammad ﷺ",
    "Acquire knowledge and impart it to the people. - Prophet Muhammad ﷺ",
    "Allah makes the way to Paradise easy for him who treads a path in search of knowledge. - Prophet Muhammad ﷺ",
    "The example of guidance and knowledge with which Allah has sent me is like abundant rain falling on the earth. - Prophet Muhammad ﷺ"
  ];

  // Get random quote
  useEffect(() => {
    const randomQuote = quotes[Math.floor(Math.random() * quotes.length)];
    setDailyQuote(randomQuote);
  }, []);

  // Fetch REAL teacher dashboard data
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        if (!user) {
          console.log("Waiting for user data...");
          return;
        }

        const teacherId = user.userId;
        console.log("🔄 Fetching dashboard data for teacher:", teacherId);
        
        // Fetch dashboard stats
        const statsResponse = await fetch(`http://localhost:8000/teacher/${teacherId}/dashboard/stats`);
        
        if (!statsResponse.ok) {
          throw new Error(`Failed to fetch dashboard stats: ${statsResponse.status}`);
        }
        
        const statsData = await statsResponse.json();
        console.log("📊 Teacher dashboard stats:", statsData);
        
        if (!statsData.success) {
          throw new Error(statsData.error || "Failed to load dashboard data");
        }
        
        // Fetch recent activities
        let activitiesData = { activities: [] };
        try {
          const activitiesResponse = await fetch(`http://localhost:8000/teacher/${teacherId}/dashboard/recent-activity?limit=5`);
          if (activitiesResponse.ok) {
            activitiesData = await activitiesResponse.json();
          }
        } catch (e) {
          console.warn("Could not fetch recent activities:", e);
        }
        
        setDashboardData({
          teacher_info: statsData.teacher_info || {},
          stats: statsData.stats || {},
          subject_performance: statsData.subject_performance || [],
          pending_grading: statsData.pending_grading || [],
          recent_quiz_attempts: statsData.recent_quiz_attempts || [],
          upcoming_deadlines: statsData.upcoming_deadlines || [],
          recent_activities: activitiesData.activities || []
        });
        
        console.log("🎉 Teacher dashboard loaded successfully!");
        setError(null);
        
      } catch (error) {
        console.error("❌ Error fetching teacher dashboard:", error);
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      fetchDashboardData();
    }
  }, [user]);

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return "N/A";
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="teacher-dashboard">
        <div className="loading">
          <h2>Loading Teacher Dashboard...</h2>
          <div className="spinner"></div>
          <p>Fetching your teaching analytics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="teacher-dashboard">
        <div className="error-message">
          <h2>⚠️ Unable to Load Dashboard</h2>
          <p>{error}</p>
          {user && (
            <div style={{marginTop: '20px', background: '#e8f4fc', padding: '15px', borderRadius: '8px'}}>
              <p>Logged in as: <strong>{user.fullName}</strong></p>
              <p>User ID: {user.userId}</p>
              <p>Role: {user.role}</p>
            </div>
          )}
          <button 
            className="retry-btn"
            onClick={() => window.location.reload()}
            style={{marginTop: '20px'}}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="teacher-dashboard">
        <div className="error-message">
          <h2>Please Login</h2>
          <p>You need to login to access the teacher dashboard.</p>
        </div>
      </div>
    );
  }

  const teacherInfo = dashboardData.teacher_info;
  const stats = dashboardData.stats;

  return (
    <div className="teacher-dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <div className="welcome-section">
          <h1>{greeting}, {teacherInfo.fullName || user.fullName}! 👩‍🏫</h1>
          <p className="subtitle">Teacher Dashboard - Islamic Studies</p>
          <div className="teacher-info">
            <span className="teacher-id">ID: {teacherInfo.userId || user.userId}</span>
            <span className="teacher-subjects">
              Subjects: {teacherInfo.assigned_subjects?.length || 0} assigned
            </span>
          </div>
        </div>
        <div className="current-date">
          <p>{new Date().toLocaleDateString('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
          })}</p>
          <small>Real-time teaching analytics</small>
        </div>
      </div>

      {/* Daily Quote */}
      <div className="quote-section">
        <div className="quote-icon">📚</div>
        <div className="quote-content">
          <p className="quote-text">"{dailyQuote}"</p>
          <p className="quote-source">Prophet Muhammad ﷺ</p>
        </div>
      </div>

      {/* Quick Stats - NON-CLICKABLE */}
      <div className="quick-stats">
        <div className="stat-card">
          <div className="stat-icon" style={{background: 'linear-gradient(135deg, #3498db, #2980b9)'}}>
            🎥
          </div>
          <div className="stat-details">
            <h3>{stats.lectures?.total || 0}</h3>
            <p>Lectures</p>
            <small>{stats.lectures?.downloads || 0} downloads</small>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon" style={{background: 'linear-gradient(135deg, #2ecc71, #27ae60)'}}>
            📝
          </div>
          <div className="stat-details">
            <h3>{stats.assignments?.total || 0}</h3>
            <p>Assignments</p>
            <small>{stats.assignments?.submissions || 0} submissions</small>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon" style={{background: 'linear-gradient(135deg, #9b59b6, #8e44ad)'}}>
            📊
          </div>
          <div className="stat-details">
            <h3>{stats.quizzes?.total || 0}</h3>
            <p>Quizzes</p>
            <small>{stats.quizzes?.attempts || 0} attempts</small>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon" style={{background: 'linear-gradient(135deg, #e74c3c, #c0392b)'}}>
            ⏳
          </div>
          <div className="stat-details">
            <h3>{dashboardData.pending_grading?.length || 0}</h3>
            <p>Pending Grading</p>
            <small>Need attention</small>
          </div>
        </div>
      </div>

      {/* Engagement Score */}
      <div className="engagement-section">
        <div className="engagement-header">
          <h3>Teaching Engagement</h3>
          <span className="engagement-score">{stats.engagement_score || 0}%</span>
        </div>
        <div className="engagement-stats">
          <div className="engagement-stat">
            <div className="engagement-label">Student Participation</div>
            <div className="engagement-bar">
              <div 
                className="engagement-fill" 
                style={{ width: `${stats.engagement_score || 0}%` }}
              >
                <span>{stats.engagement_score || 0}%</span>
              </div>
            </div>
          </div>
          <div className="engagement-details">
            <div className="detail-item">
              <span className="detail-label">Assignment Submissions:</span>
              <span className="detail-value">{stats.assignments?.submissions || 0}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Quiz Attempts:</span>
              <span className="detail-value">{stats.quizzes?.attempts || 0}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Lecture Views:</span>
              <span className="detail-value">{stats.lectures?.views || 0}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Two Column Layout */}
      <div className="dashboard-columns">
        {/* Left Column */}
        <div className="column-left">
          {/* Subject Performance */}
          {dashboardData.subject_performance && dashboardData.subject_performance.length > 0 && (
            <div className="subject-performance">
              <h3>Subject Performance</h3>
              <div className="subject-list">
                {dashboardData.subject_performance.map((subject, index) => (
                  <div key={index} className="subject-item">
                    <h4>{subject.subject_name}</h4>
                    <div className="subject-stats">
                      <div className="subject-stat">
                        <span className="stat-icon-small">📝</span>
                        <span className="stat-detail">
                          {subject.assignments.total} assignments • {subject.assignments.submissions} submissions
                        </span>
                      </div>
                      <div className="subject-stat">
                        <span className="stat-icon-small">📊</span>
                        <span className="stat-detail">
                          {subject.quizzes.total} quizzes • {subject.quizzes.attempts} attempts
                        </span>
                      </div>
                      <div className="subject-stat">
                        <span className="stat-icon-small">🎥</span>
                        <span className="stat-detail">
                          {subject.lectures.total} lectures • {subject.lectures.downloads} downloads
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Upcoming Deadlines - NON-CLICKABLE */}
          {dashboardData.upcoming_deadlines && dashboardData.upcoming_deadlines.length > 0 && (
            <div className="upcoming-section">
              <h3>Upcoming Deadlines</h3>
              <div className="deadlines-list">
                {dashboardData.upcoming_deadlines.map((deadline, index) => (
                  <div key={index} className="deadline-item">
                    <div className="deadline-icon">
                      📝
                    </div>
                    <div className="deadline-details">
                      <h4>{deadline.title}</h4>
                      <p className="deadline-subject">{deadline.subject_name}</p>
                      <div className="deadline-meta">
                        <span className={`deadline-status ${deadline.days_left < 3 ? 'urgent' : ''}`}>
                          {deadline.deadline_text}
                        </span>
                        <span className="deadline-submissions">
                          {deadline.submissions || 0} submissions
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Column */}
        <div className="column-right">
          {/* Pending Grading - NON-CLICKABLE */}
          {dashboardData.pending_grading && dashboardData.pending_grading.length > 0 && (
            <div className="pending-grading">
              <div className="section-header">
                <h3>Pending Grading</h3>
                <span className="badge">{dashboardData.pending_grading.length}</span>
              </div>
              <div className="grading-list">
                {dashboardData.pending_grading.map((submission, index) => (
                  <div key={index} className="grading-item">
                    <div className="grading-icon">📝</div>
                    <div className="grading-details">
                      <h4>{submission.assignment_title}</h4>
                      <p className="grading-student">{submission.student_name}</p>
                      <div className="grading-meta">
                        <span className="grading-subject">{submission.subject_name}</span>
                        <span className="grading-date">
                          Submitted {formatDate(submission.submission_date)}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recent Quiz Attempts - NON-CLICKABLE */}
          {dashboardData.recent_quiz_attempts && dashboardData.recent_quiz_attempts.length > 0 && (
            <div className="quiz-attempts">
              <h3>Recent Quiz Attempts</h3>
              <div className="attempts-list">
                {dashboardData.recent_quiz_attempts.slice(0, 3).map((attempt, index) => (
                  <div key={index} className="attempt-item">
                    <div className="attempt-icon">📊</div>
                    <div className="attempt-details">
                      <h4>{attempt.quiz_title}</h4>
                      <p className="attempt-student">{attempt.student_name}</p>
                      <div className="attempt-meta">
                        <span className="attempt-score">Score: {attempt.total_score}</span>
                        <span className="attempt-date">{formatDate(attempt.submitted_at)}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recent Activities - NON-CLICKABLE */}
          {dashboardData.recent_activities && dashboardData.recent_activities.length > 0 && (
            <div className="recent-activities">
              <h3>Recent Activity</h3>
              <div className="activities-list">
                {dashboardData.recent_activities.map((activity, index) => (
                  <div key={index} className="activity-item">
                    <div className="activity-icon">{activity.title.includes('Submission') ? '📝' : '📊'}</div>
                    <div className="activity-details">
                      <h4>{activity.title}</h4>
                      <p className="activity-description">{activity.description}</p>
                      <div className="activity-meta">
                        <span className="activity-subject">{activity.subject_name}</span>
                        {activity.student_name && (
                          <span className="activity-student">{activity.student_name}</span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Dashboard Info */}
      <div className="data-source-info">
        <p className="info-text">
          <small>
            📊 Real-time teacher dashboard • 
            Last updated: {new Date().toLocaleTimeString()} • 
            Using FastAPI backend at localhost:8000
          </small>
        </p>
        <p className="info-note">
          <small>
            💡 Note: Manage lectures, assignments, quizzes, and materials directly from your Course Management Page
          </small>
        </p>
      </div>
    </div>
  );
};

export default TeacherDashboard;