import React, { useState, useEffect } from 'react';
import "./StudentCourses.css";
import { useLocation, useNavigate, useParams } from 'react-router-dom';

const StudentQuizzes = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { userId } = useParams();
  const { subject, teacher, studentData } = location.state || {};
  
  const [quizzes, setQuizzes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (subject && teacher) {
      fetchQuizzes();
    }
  }, [subject, teacher]);

  const fetchQuizzes = async () => {
    try {
      const response = await fetch(`http://localhost:8000/quizzes/${teacher.userId}/${subject}`);
      const data = await response.json();
      
      if (data.success) {
        setQuizzes(data.quizzes);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error fetching quizzes:', error);
      setLoading(false);
    }
  };

  const handleBack = () => {
    navigate(`/student-dashboard/${userId}/courses`);
  };

  const handleTakeQuiz = (quiz) => {
    // Navigate to quiz taking page or show quiz details
    alert(`Taking quiz: ${quiz.title}`);
  };

  if (loading) return <div className="loading">Loading quizzes...</div>;

  return (
  <div className="student-quizzes-container">
    <div className="student-quizzes-header">
      <button onClick={handleBack} className="student-quizzes-back-btn">
        ← Back to Courses
      </button>
      <h1 className="student-quizzes-title">📊 Quizzes - {subject}</h1>
    </div>

    <div className="student-quizzes-content-section">
      <div className="student-quizzes-info-card">
        <p><strong>Teacher:</strong> {teacher?.fullName || 'Not assigned'}</p>
        <p><strong>Total Quizzes:</strong> {quizzes.length}</p>
      </div>

      {quizzes.length === 0 ? (
        <div className="no-data">No quizzes available for this subject.</div>
      ) : (
        <div className="student-quizzes-list">
          {quizzes.map((quiz) => (
            <div key={quiz.id} className="student-quiz-card">
              <div className="student-quiz-info">
                <h3>{quiz.title}</h3>
                <p>{quiz.description}</p>
                <div className="student-quiz-meta">
                  <span>Duration: {quiz.duration_minutes} mins</span>
                  <span>Marks: {quiz.total_marks}</span>
                  <span>Questions: {quiz.questions_count}</span>
                </div>
                <div className="student-quiz-dates">
                  <span>Start: {new Date(quiz.start_date).toLocaleDateString()}</span>
                  <span>End: {new Date(quiz.end_date).toLocaleDateString()}</span>
                </div>
              </div>
              <button 
                onClick={() => handleTakeQuiz(quiz)}
                className="student-quiz-take-btn"
              >
                Take Quiz
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  </div>
);
};

export default StudentQuizzes;