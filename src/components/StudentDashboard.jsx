import React, { useState, useEffect } from "react";
import { useOutletContext } from "react-router-dom";
import "./StudentDashboard.css";

const StudentDashboard = () => {
  const contextData = useOutletContext();
  
  console.log("🔍 StudentDashboard Debug - Context Data:", contextData);
  
  const [dashboardData, setDashboardData] = useState({
    student_info: {},
    stats: {},
    subject_performance: [],
    recent_activities: [],
    upcoming_deadlines: []
  });
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [greeting, setGreeting] = useState("");
  const [dailyQuote, setDailyQuote] = useState("");

  // Greetings based on time
  useEffect(() => {
    const hour = new Date().getHours();
    if (hour < 12) setGreeting("Good Morning");
    else if (hour < 17) setGreeting("Good Afternoon");
    else setGreeting("Good Evening");
  }, []);

  // Islamic quotes
  const quotes = [
    "Seeking knowledge is an obligation upon every Muslim. - Prophet Muhammad ﷺ",
    "The best among you are those who learn the Quran and teach it. - Prophet Muhammad ﷺ",
    "Acquire knowledge, it enables its possessor to distinguish right from wrong. - Prophet Muhammad ﷺ",
    "Whoever treads a path in search of knowledge, Allah will make easy for him the path to Paradise. - Prophet Muhammad ﷺ",
    "The ink of the scholar is more sacred than the blood of the martyr. - Prophet Muhammad ﷺ"
  ];

  // Get random quote
  useEffect(() => {
    const randomQuote = quotes[Math.floor(Math.random() * quotes.length)];
    setDailyQuote(randomQuote);
  }, []);

  // Get student ID from context
  const getStudentId = () => {
    console.log("📋 Getting student ID from context:", contextData);
    
    // Try different possible properties
    if (contextData?.userId) {
      console.log("✅ Found userId in context:", contextData.userId);
      return contextData.userId;
    }
    if (contextData?.userid) {
      console.log("✅ Found userid in context:", contextData.userid);
      return contextData.userid;
    }
    if (contextData?.id) {
      console.log("✅ Found id in context (will fetch from API):", contextData.id);
      return contextData.id;
    }
    if (typeof contextData === 'string') {
      console.log("✅ Context is string (userid):", contextData);
      return contextData;
    }
    
    console.log("❌ No student ID found in context");
    return null;
  };

  // Fetch student info first, then dashboard data
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const studentId = getStudentId();
        
        if (!studentId) {
          console.log("No student ID available in context");
          setError("No student ID found. Please login again.");
          setLoading(false);
          return;
        }

        console.log("🔄 Starting dashboard fetch for student:", studentId);
        
        // FIRST: Get student info from your FastAPI
        console.log("📡 Fetching student info from FastAPI...");
        const userResponse = await fetch(`http://localhost:8000/users?userId=${studentId}`);
        
        if (!userResponse.ok) {
          console.error("Failed to fetch user info:", userResponse.status);
          throw new Error(`Failed to fetch user info: ${userResponse.status}`);
        }
        
        const userData = await userResponse.json();
        console.log("📊 User info response:", userData);
        
        if (!userData.success || !userData.users || userData.users.length === 0) {
          throw new Error("Student not found in database");
        }
        
        const studentInfo = userData.users[0];
        console.log("✅ Student info found:", studentInfo);
        
        // Check if this is actually a student
        if (studentInfo.role !== 'student') {
          throw new Error("User is not a student");
        }
        
        // SECOND: Now fetch dashboard stats using the userId
        const statsResponse = await fetch(`http://localhost:8000/student/${studentId}/dashboard/stats`);
        
        if (!statsResponse.ok) {
          console.error("Failed to fetch dashboard stats:", statsResponse.status);
          throw new Error(`Failed to fetch dashboard stats: ${statsResponse.status}`);
        }
        
        const statsData = await statsResponse.json();
        console.log("📊 Dashboard stats received:", statsData);
        
        if (!statsData.success) {
          throw new Error(statsData.error || "Failed to load dashboard data");
        }
        
        // THIRD: Fetch upcoming deadlines
        let upcomingData = { upcoming: [] };
        try {
          const upcomingResponse = await fetch(`http://localhost:8000/student/${studentId}/dashboard/upcoming?days=7`);
          if (upcomingResponse.ok) {
            upcomingData = await upcomingResponse.json();
          }
        } catch (e) {
          console.warn("Could not fetch upcoming deadlines:", e);
        }
        
        // FOURTH: Fetch recent activities
        let activitiesData = { activities: [] };
        try {
          const activitiesResponse = await fetch(`http://localhost:8000/student/${studentId}/dashboard/activities?limit=5`);
          if (activitiesResponse.ok) {
            activitiesData = await activitiesResponse.json();
          }
        } catch (e) {
          console.warn("Could not fetch activities:", e);
        }
        
        // Combine all data
        setDashboardData({
          student_info: {
            ...studentInfo,
            // Ensure we have all required fields
            userId: studentInfo.userId || studentId,
            fullName: studentInfo.fullName,
            current_year: studentInfo.current_year || "First Year"
          },
          stats: statsData.stats || {},
          subject_performance: statsData.subject_performance || [],
          recent_activities: activitiesData.activities || [],
          upcoming_deadlines: upcomingData.upcoming || []
        });
        
        console.log("🎉 Dashboard data loaded successfully!");
        setError(null);
        
      } catch (error) {
        console.error("❌ Error fetching dashboard data:", error);
        setError(error.message);
        
        // Fallback: try to show at least student info
        const studentId = getStudentId();
        if (studentId) {
          try {
            const fallbackResponse = await fetch(`http://localhost:8000/users?userId=${studentId}`);
            if (fallbackResponse.ok) {
              const fallbackData = await fallbackResponse.json();
              if (fallbackData.success && fallbackData.users && fallbackData.users.length > 0) {
                const student = fallbackData.users[0];
                setDashboardData(prev => ({
                  ...prev,
                  student_info: {
                    userId: student.userId || studentId,
                    fullName: student.fullName,
                    current_year: student.current_year || "First Year"
                  },
                  stats: {
                    pending_assignments: 0,
                    submitted_assignments: 0,
                    upcoming_quizzes: 0,
                    completed_quizzes: 0,
                    overall_progress: 0
                  }
                }));
                setError("Dashboard stats unavailable, but student info loaded");
              }
            }
          } catch (e) {
            console.error("Fallback also failed:", e);
          }
        }
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [contextData]);

  // Function to format date
  const formatDate = (dateString) => {
    if (!dateString) return "N/A";
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: 'numeric'
    });
  };

  // Function to format time
  const formatTime = (dateString) => {
    if (!dateString) return "";
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  if (loading) {
    return (
      <div className="simple-dashboard">
        <div className="loading">
          <h2>Loading Dashboard...</h2>
          <div className="spinner"></div>
          <p>Fetching your real-time academic data...</p>
          <div style={{marginTop: '20px', fontSize: '14px', color: '#666'}}>
            <p>Student ID from context: {getStudentId() || 'Not available'}</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    const studentId = getStudentId();
    return (
      <div className="simple-dashboard">
        <div className="error-message">
          <h2>⚠️ Unable to Load Dashboard</h2>
          <p>{error}</p>
          <p style={{fontSize: '14px', marginTop: '10px', color: '#666'}}>
            Student ID: {studentId || 'Not found'}
          </p>
          <button 
            className="retry-btn"
            onClick={() => window.location.reload()}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const studentName = dashboardData.student_info.fullName || "Student";
  const studentYear = dashboardData.student_info.current_year || "First Year";
  const stats = dashboardData.stats;

  return (
    <div className="simple-dashboard">
      {/* Header with Greeting and Name */}
      <div className="dashboard-header">
        <div className="welcome-message">
          <h1>{greeting}, {studentName.split(' ')[0]}! 👋</h1>
          <p className="subtitle">Welcome to your Islamic Studies Dashboard</p>
          <p className="student-year">
            Currently in <strong>{studentYear}</strong> • 
            <span className="student-id"> ID: {dashboardData.student_info.userId}</span>
          </p>
        </div>
        <div className="current-date">
          <p>{new Date().toLocaleDateString('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
          })}</p>
          <small>Real-time academic dashboard</small>
        </div>
      </div>

      {/* Daily Quote */}
      <div className="quote-section">
        <div className="quote-icon">🕌</div>
        <div className="quote-content">
          <p className="quote-text">"{dailyQuote}"</p>
          <p className="quote-source">Prophet Muhammad ﷺ</p>
        </div>
      </div>

      {/* Quick Stats - NON-CLICKABLE */}
      <div className="quick-stats">
        <div className="stat-card">
          <div className="stat-icon">📝</div>
          <div className="stat-details">
            <h3>{stats.pending_assignments || 0}</h3>
            <p>Pending Assignments</p>
            <small>Need your attention</small>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-details">
            <h3>{stats.upcoming_quizzes || 0}</h3>
            <p>Upcoming Quizzes</p>
            <small>Prepare Now</small>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">✅</div>
          <div className="stat-details">
            <h3>{stats.submitted_assignments || 0}</h3>
            <p>Submitted Assignments</p>
            <small>{stats.graded_assignments || 0} graded</small>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">🏆</div>
          <div className="stat-details">
            <h3>{stats.completed_quizzes || 0}</h3>
            <p>Quizzes Completed</p>
            <small>Avg: {stats.avg_quiz_score || 0}%</small>
          </div>
        </div>
      </div>

      {/* Progress Bar with Real Data */}
      <div className="progress-section">
        <div className="progress-header">
          <h3>Your Learning Progress</h3>
          <span className="progress-percentage">{stats.overall_progress || 0}%</span>
        </div>
        <div className="progress-container">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${stats.overall_progress || 0}%` }}
            >
              <span className="progress-text">{stats.overall_progress || 0}%</span>
            </div>
          </div>
          <div className="progress-details">
            <div className="progress-item">
              <span className="progress-label">Assignments</span>
              <span className="progress-value">
                {stats.submitted_assignments || 0} submitted • Avg: {stats.avg_assignment_score || 0}%
              </span>
            </div>
            <div className="progress-item">
              <span className="progress-label">Quizzes</span>
              <span className="progress-value">
                {stats.completed_quizzes || 0} completed • Avg: {stats.avg_quiz_score || 0}%
              </span>
            </div>
            <div className="progress-item">
              <span className="progress-label">Overall</span>
              <span className="progress-value highlight">
                {stats.overall_progress || 0}% Complete • {dashboardData.subject_performance?.length || 0} subjects
              </span>
            </div>
          </div>
        </div>
        <p className="progress-message">
          {stats.overall_progress >= 80 
            ? "Excellent work! You're making great progress in your studies. 🎉"
            : stats.overall_progress >= 50
            ? "Good progress! Keep up the consistent effort. 📚"
            : "Keep learning! Every step brings you closer to knowledge. ✨"}
        </p>
      </div>

      {/* Subject Performance */}
      {dashboardData.subject_performance && dashboardData.subject_performance.length > 0 && (
        <div className="subject-performance">
          <h3>Subject Performance</h3>
          <div className="subject-grid">
            {dashboardData.subject_performance.slice(0, 4).map((subject, index) => (
              <div key={index} className="subject-card">
                <h4>{subject.subject_name}</h4>
                <div className="subject-stats">
                  <div className="subject-stat">
                    <span className="stat-label">Assignments:</span>
                    <span className="stat-value">{subject.assignments_submitted} submitted</span>
                  </div>
                  <div className="subject-stat">
                    <span className="stat-label">Quizzes:</span>
                    <span className="stat-value">{subject.quizzes_attempted} attempted</span>
                  </div>
                  <div className="subject-stat">
                    <span className="stat-label">Average:</span>
                    <span className="stat-value highlight">{subject.average_score}%</span>
                  </div>
                </div>
                <div className="subject-progress">
                  <div 
                    className="subject-progress-bar"
                    style={{ width: `${subject.performance_percentage}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Activities */}
      {dashboardData.recent_activities && dashboardData.recent_activities.length > 0 && (
        <div className="recent-activities">
          <h3>Recent Activities</h3>
          <div className="activities-list">
            {dashboardData.recent_activities.map((activity, index) => (
              <div key={index} className="activity-item">
                <div className="activity-icon">
                  {activity.activity_type === 'assignment_submission' ? '📝' : '📊'}
                </div>
                <div className="activity-details">
                  <h4>{activity.title}</h4>
                  <p className="activity-description">{activity.description}</p>
                  <div className="activity-meta">
                    <span className="activity-subject">{activity.subject_name}</span>
                    <span className="activity-date">
                      {formatDate(activity.timestamp)} • {formatTime(activity.timestamp)}
                    </span>
                  </div>
                  {activity.score !== null && (
                    <div className="activity-score">
                      Score: <strong>{activity.score}</strong> / {activity.max_score}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Upcoming Deadlines - NON-CLICKABLE */}
      {dashboardData.upcoming_deadlines && dashboardData.upcoming_deadlines.length > 0 && (
        <div className="upcoming-deadlines">
          <h3>Upcoming Deadlines</h3>
          <div className="deadlines-list">
            {dashboardData.upcoming_deadlines.slice(0, 5).map((deadline, index) => (
              <div key={index} className="deadline-item">
                <div className="deadline-icon">
                  {deadline.type === 'assignment' ? '📝' : '📊'}
                </div>
                <div className="deadline-details">
                  <h4>{deadline.title}</h4>
                  <p className="deadline-subject">{deadline.subject_name}</p>
                  <div className="deadline-meta">
                    <span className="deadline-days">{deadline.deadline_text}</span>
                    <span className="deadline-teacher">By: {deadline.teacher_name}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Dashboard Info */}
      <div className="data-source-info">
        <p className="info-text">
          <small>
            📊 Real-time dashboard • 
            Student ID: {dashboardData.student_info.userId} • 
            Last updated: {new Date().toLocaleTimeString()} • 
            Using FastAPI backend at localhost:8000
          </small>
        </p>
        <p className="info-note">
          <small>
            💡 Note: Access assignments, quizzes, and materials directly from your Course Page
          </small>
        </p>
      </div>
      
    </div>
  );
};

export default StudentDashboard;