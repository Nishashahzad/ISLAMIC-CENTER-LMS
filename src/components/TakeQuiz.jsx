import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import './TakeQuiz.css';

const StudentTakeQuiz = () => {
  const { userId, quizId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  
  const [quiz, setQuiz] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [timeLeft, setTimeLeft] = useState(null);
  const [quizStarted, setQuizStarted] = useState(false);
  const timerRef = useRef(null);

  useEffect(() => {
    fetchQuizQuestions();
    
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [quizId, userId]);

  useEffect(() => {
    if (quizStarted && timeLeft > 0 && quiz) {
      timerRef.current = setInterval(() => {
        setTimeLeft(prev => {
          if (prev <= 1) {
            handleAutoSubmit();
            return 0;
          }
          return prev - 1;
        });
      }, 60000);
      
      return () => clearInterval(timerRef.current);
    }
  }, [quizStarted, timeLeft]);

  const fetchQuizQuestions = async () => {
    try {
      const response = await fetch(`http://localhost:8000/student/quiz/${quizId}/questions?student_userId=${userId}`);
      const data = await response.json();
      
      if (data.success) {
        setQuiz(data.quiz);
        setQuestions(data.questions);
        setTimeLeft(data.quiz.duration_minutes);
        setQuizStarted(true);
        
        const initialAnswers = {};
        data.questions.forEach(q => {
          initialAnswers[q.id] = {
            question_id: q.id,
            question_type: q.question_type,
            selected_option_id: null,
            answer_text: ''
          };
        });
        setAnswers(initialAnswers);
      } else {
        alert(data.detail || 'Failed to load quiz');
        navigate(-1); // Go back
      }
    } catch (error) {
      console.error('Error fetching quiz questions:', error);
      alert('Error loading quiz. Please try again.');
      navigate(-1); // Go back
    } finally {
      setLoading(false);
    }
  };

  const handleOptionSelect = (questionId, optionId) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: {
        ...prev[questionId],
        selected_option_id: optionId,
        answer_text: ''
      }
    }));
  };

  const handleTextAnswer = (questionId, text) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: {
        ...prev[questionId],
        answer_text: text,
        selected_option_id: null
      }
    }));
  };

  const handleAutoSubmit = async () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }
    
    await submitQuiz();
    alert('Time is up! Your quiz has been automatically submitted.');
  };

  const submitQuiz = async () => {
    const answerArray = Object.values(answers);
    
    try {
      setSubmitting(true);
      
      const response = await fetch(`http://localhost:8000/student/quiz/${quizId}/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          student_userId: userId,
          answers: answerArray
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        // Navigate to result page with attempt_id
        navigate(`/student-dashboard/${userId}/quizzes/result/${data.attempt_id}`, {
          state: { 
            subject: location.state?.subject,
            teacher: location.state?.teacher 
          }
        });
      } else {
        alert('Error submitting quiz: ' + (data.detail || data.message || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error submitting quiz:', error);
      alert('Error submitting quiz. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const formatTime = (minutes) => {
    if (minutes < 60) {
      return `${minutes} minutes`;
    } else {
      const hours = Math.floor(minutes / 60);
      const mins = minutes % 60;
      return `${hours}h ${mins}m`;
    }
  };

  if (loading) {
    return <div className="student-take-quiz-loading">Loading quiz...</div>;
  }

  if (!quiz) {
    return <div className="student-take-quiz-error">Quiz not found</div>;
  }

  return (
    <div className="student-take-quiz-container">
      {/* Header with Back Button */}
      <div className="quiz-header-bar">
        <div className="quiz-header-left">
          <button 
            onClick={() => navigate(-1)}
            className="back-button"
          >
            ← Back
          </button>
          <div className="quiz-info-left">
            <h1>{quiz.title}</h1>
            <p className="quiz-subject-info">Subject: {quiz.subject_name}</p>
            <p className="quiz-teacher-info">Teacher: {quiz.teacher_name}</p>
          </div>
        </div>
        
        <div className="quiz-info-right">
          <div className="timer-container">
            <span className="timer-label">Time Left:</span>
            <span className={`timer-countdown ${timeLeft < 10 ? 'time-warning' : ''}`}>
              {formatTime(timeLeft)}
            </span>
          </div>
          <div className="quiz-statistics">
            <p>Questions: {questions.length}</p>
            <p>Total Marks: {quiz.total_marks}</p>
          </div>
        </div>
      </div>

      <div className="quiz-instructions-box">
        <h3>Instructions:</h3>
        <ul>
          <li>You can attempt this quiz only once</li>
          <li>Answer all questions before submitting</li>
          <li>Quiz will auto-submit when time expires</li>
          <li>Each question shows its marks</li>
        </ul>
      </div>

      <div className="questions-list">
        {questions.map((question, index) => (
          <div key={question.id} className="question-item">
            <div className="question-title-bar">
              <h3>Question {index + 1} <span className="question-score">({question.marks} mark{question.marks !== 1 ? 's' : ''})</span></h3>
              <span className="question-type-tag">{question.question_type.toUpperCase()}</span>
            </div>
            
            <div className="question-text-content">
              {question.question_text || question.question_text_urdu || question.question_text_arabic}
            </div>
            
            {question.question_type === 'mcq' && question.options && (
              <div className="multiple-choice-options">
                {question.options.map((option) => (
                  <div key={option.id} className="choice-option">
                    <input
                      type="radio"
                      id={`q${question.id}_o${option.id}`}
                      name={`question_${question.id}`}
                      checked={answers[question.id]?.selected_option_id === option.id}
                      onChange={() => handleOptionSelect(question.id, option.id)}
                      className="choice-radio"
                    />
                    <label htmlFor={`q${question.id}_o${option.id}`} className="choice-label">
                      {option.option_text || option.option_text_urdu || option.option_text_arabic}
                    </label>
                  </div>
                ))}
              </div>
            )}
            
            {question.question_type === 'true_false' && (
              <div className="true-false-options">
                {[
                  { id: 'true', text: 'True' },
                  { id: 'false', text: 'False' }
                ].map((option) => (
                  <div key={option.id} className="choice-option">
                    <input
                      type="radio"
                      id={`q${question.id}_${option.id}`}
                      name={`question_${question.id}`}
                      checked={answers[question.id]?.selected_option_id === option.id}
                      onChange={() => handleOptionSelect(question.id, option.id)}
                      className="choice-radio"
                    />
                    <label htmlFor={`q${question.id}_${option.id}`} className="choice-label">
                      {option.text}
                    </label>
                  </div>
                ))}
              </div>
            )}
            
            {question.question_type === 'short_answer' && (
              <div className="short-answer-box">
                <textarea
                  value={answers[question.id]?.answer_text || ''}
                  onChange={(e) => handleTextAnswer(question.id, e.target.value)}
                  placeholder="Type your answer here..."
                  rows="4"
                  className="answer-input"
                />
              </div>
            )}
            
            <div className="answer-status-indicator">
              {answers[question.id]?.selected_option_id || answers[question.id]?.answer_text ? (
                <span className="answered-indicator">✓ Answered</span>
              ) : (
                <span className="unanswered-indicator">✗ Not answered</span>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="quiz-controls">
        <button 
          onClick={() => navigate(-1)}
          className="cancel-quiz-button"
        >
          Cancel Quiz
        </button>
        
        <div className="progress-tracker">
          Answered: {
            Object.values(answers).filter(a => a.selected_option_id || a.answer_text).length
          } / {questions.length}
        </div>
        
        <button 
          onClick={submitQuiz}
          disabled={submitting}
          className="submit-quiz-button"
        >
          {submitting ? 'Submitting...' : 'Submit Quiz'}
        </button>
      </div>
    </div>
  );
};

export default StudentTakeQuiz;