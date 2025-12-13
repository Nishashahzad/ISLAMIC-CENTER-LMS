import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import './StudentQuizDashboard.css';

const StudentQuizzes = () => {
  const { userId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  
  const { subject, teacher, studentData } = location.state || {};
  
  const [quizzes, setQuizzes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (userId && subject) {
      fetchAvailableQuizzes();
    }
  }, [userId, subject]);

  const fetchAvailableQuizzes = async () => {
    try {
      // Always pass subject parameter
      let url = `http://localhost:8000/student/quizzes/available/${userId}?subject_name=${encodeURIComponent(subject)}`;
      
      const response = await fetch(url);
      const data = await response.json();
      
      if (data.success) {
        setQuizzes(data.quizzes);
      }
    } catch (error) {
      console.error('Error fetching quizzes:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTakeQuiz = (quiz) => {
    // Check if already attempted
    if (quiz.attempts_count > 0) {
      alert(`You have already attempted this quiz. Your best score: ${quiz.best_score || 0}/${quiz.total_marks}`);
      return;
    }
    
    // Check if quiz is active
    const now = new Date();
    const startDate = new Date(quiz.start_date);
    const endDate = new Date(quiz.end_date);
    
    if (now < startDate) {
      alert(`This quiz will start on ${formatDate(quiz.start_date)}`);
      return;
    }
    
    if (now > endDate) {
      alert(`This quiz ended on ${formatDate(quiz.end_date)}`);
      return;
    }
    
    navigate(`/student-dashboard/${userId}/quizzes/take/${quiz.id}`, {
      state: { quiz, subject, teacher, studentData }
    });
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getQuizStatus = (quiz) => {
    const now = new Date();
    const startDate = new Date(quiz.start_date);
    const endDate = new Date(quiz.end_date);
    
    if (now < startDate) {
      return {
        type: 'upcoming',
        label: 'Upcoming',
        color: '#ff9800',
        bgColor: '#fff3e0'
      };
    } else if (now > endDate) {
      return {
        type: 'ended',
        label: 'Ended',
        color: '#f44336',
        bgColor: '#ffebee'
      };
    } else {
      return {
        type: 'active',
        label: 'Active',
        color: '#4caf50',
        bgColor: '#e8f5e9'
      };
    }
  };

  const getButtonText = (quiz) => {
    const hasAttempted = quiz.attempts_count > 0;
    const now = new Date();
    const startDate = new Date(quiz.start_date);
    const endDate = new Date(quiz.end_date);
    
    if (hasAttempted) {
      return 'View Result';
    } else if (now < startDate) {
      return 'Starting Soon';
    } else if (now > endDate) {
      return 'Quiz Ended';
    } else {
      return 'Take Quiz';
    }
  };

  const isButtonDisabled = (quiz) => {
    const hasAttempted = quiz.attempts_count > 0;
    const now = new Date();
    const startDate = new Date(quiz.start_date);
    const endDate = new Date(quiz.end_date);
    
    return hasAttempted || now < startDate || now > endDate;
  };

  if (loading) {
    return (
      <div className="student-quizzes-container">
        <div className="loading">Loading quizzes...</div>
      </div>
    );
  }

  return (
    <div className="student-quizzes-container">
      {/* Header with Back Button */}
      <div className="quiz-header">
        <button 
          onClick={() => navigate(`/student-dashboard/${userId}/courses`)}
          className="back-btn"
        >
          ← Back to Courses
        </button>
        
        <h1>
          📝 {subject} Quizzes
          {teacher && <span className="teacher-subtitle"> | Teacher: {teacher.fullName}</span>}
        </h1>
      </div>

      {/* Available Quizzes */}
      <div className="available-quizzes">
        {quizzes.length === 0 ? (
          <div className="no-data">
            <p>No quizzes available for {subject}</p>
            <p className="hint">Check back later or contact your teacher</p>
          </div>
        ) : (
          <div className="quiz-list">
            {quizzes.map((quiz) => {
              const hasAttempted = quiz.attempts_count > 0;
              const status = getQuizStatus(quiz);
              const buttonText = getButtonText(quiz);
              const isDisabled = isButtonDisabled(quiz);
              
              return (
                <div key={quiz.id} className="quiz-card">
                  <div className="quiz-card-header">
                    <h3>{quiz.title}</h3>
                    <div className="status-container">
                      <span 
                        className="quiz-status" 
                        style={{ 
                          backgroundColor: status.bgColor,
                          color: status.color,
                          border: `1px solid ${status.color}`
                        }}
                      >
                        {status.label}
                      </span>
                      {hasAttempted && (
                        <span className="attempted-badge">
                          ✓ Attempted
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <div className="quiz-card-content">
                    <div className="quiz-meta-row">
                      <span className="meta-item">
                        <strong>👨‍🏫 Teacher:</strong> {quiz.teacher_name}
                      </span>
                      <span className="meta-item">
                        <strong>⏱️ Duration:</strong> {quiz.duration_minutes} minutes
                      </span>
                    </div>
                    
                    <div className="quiz-meta-row">
                      <span className="meta-item">
                        <strong>📊 Total Marks:</strong> {quiz.total_marks}
                      </span>
                      <span className="meta-item">
                        <strong>❓ Questions:</strong> {quiz.questions_count}
                      </span>
                    </div>
                    
                    <div className="quiz-dates">
                      <div className="date-item">
                        <strong>📅 Start:</strong> {formatDate(quiz.start_date)}
                      </div>
                      <div className="date-item">
                        <strong>📅 End:</strong> {formatDate(quiz.end_date)}
                      </div>
                    </div>
                    
                    {hasAttempted && (
                      <div className="previous-attempt-info">
                        <div className="attempt-item">
                          <strong>🎯 Your Best Score:</strong> {quiz.best_score || 0} / {quiz.total_marks}
                        </div>
                        <div className="attempt-item">
                          <strong>📝 Attempts:</strong> {quiz.attempts_count}
                        </div>
                      </div>
                    )}
                  </div>
                  
                  <div className="quiz-card-actions">
                    <button 
                      onClick={() => handleTakeQuiz(quiz)}
                      className={`take-quiz-btn ${hasAttempted ? 'attempted' : ''} ${isDisabled ? 'disabled' : ''}`}
                      disabled={isDisabled}
                    >
                      {buttonText}
                    </button>
                    
                    {hasAttempted && (
                      <button 
                        onClick={() => navigate(`/student-dashboard/${userId}/quizzes`)}
                        className="view-result-btn"
                      >
                        View Details
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default StudentQuizzes;