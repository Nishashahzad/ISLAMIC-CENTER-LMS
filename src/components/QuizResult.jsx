import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import './QuizResult.css';

const StudentQuizResult = () => {
  const { userId, attemptId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  
  const [result, setResult] = useState(null);
  const [quiz, setQuiz] = useState(null);
  const [detailedAnswers, setDetailedAnswers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeLanguage, setActiveLanguage] = useState('english');

  const { subject, teacher } = location.state || {};

  useEffect(() => {
    fetchResultDetails();
  }, [attemptId, userId]);

  const fetchResultDetails = async () => {
  try {
    const response = await fetch(
      `http://localhost:8000/student/quiz/result/${attemptId}?student_userId=${userId}`
    );
    const data = await response.json();
    
    console.log("📊 FULL API RESPONSE:", data); // Debug
    
    if (data.success) {
      setQuiz(data.quiz);
      setResult(data.attempt);
      setDetailedAnswers(data.detailed_answers);
      
      // DEEP DEBUG: Let's see the raw values
      if (data.detailed_answers && data.detailed_answers.length > 0) {
        const firstAnswer = data.detailed_answers[0];
        console.log("🔍 FULL FIRST ANSWER DATA:", JSON.stringify(firstAnswer, null, 2));
        
        // Check specific fields
        console.log("🔍 RAW FIELD VALUES:");
        console.log("question_text:", firstAnswer.question_text, 
                    "Type:", typeof firstAnswer.question_text,
                    "Length:", firstAnswer.question_text?.length);
        console.log("question_text_arabic:", firstAnswer.question_text_arabic,
                    "Type:", typeof firstAnswer.question_text_arabic);
        console.log("question_text_urdu:", firstAnswer.question_text_urdu,
                    "Type:", typeof firstAnswer.question_text_urdu);
        
        console.log("selected_option_text:", firstAnswer.selected_option_text,
                    "Type:", typeof firstAnswer.selected_option_text);
        console.log("correct_option_text:", firstAnswer.correct_option_text,
                    "Type:", typeof firstAnswer.correct_option_text);
        console.log("correct_answer:", firstAnswer.correct_answer,
                    "Type:", typeof firstAnswer.correct_answer);
        
        // Check if it's actually an empty string vs null vs undefined
        console.log("🔍 EMPTY CHECKS:");
        console.log("Is question_text empty string?", firstAnswer.question_text === "");
        console.log("Is question_text null?", firstAnswer.question_text === null);
        console.log("Is question_text undefined?", firstAnswer.question_text === undefined);
      }
    } else {
      alert(data.detail || 'Failed to load result');
      navigate(-1);
    }
  } catch (error) {
    console.error('Error fetching result details:', error);
    alert('Error loading quiz result');
    navigate(-1);
  } finally {
    setLoading(false);
  }
};

  // SIMPLIFIED AND IMPROVED getText function
  const getText = (item, field) => {
  console.log(`🔍 SIMPLE GETTEXT for ${field}:`, {
    itemExists: !!item,
    fieldValue: item?.[field],
    fieldValueType: typeof item?.[field],
    arabicValue: item?.[`${field}_arabic`],
    urduValue: item?.[`${field}_urdu`]
  });
  
  // Just return whatever is in the field, even if empty
  return item?.[field] || 'EMPTY';
};
  // Special function for answers
  const getAnswerText = (answer) => {
    if (!answer) return 'No answer';
    
    console.log("🔍 Getting answer text for:", {
      hasSelectedOption: !!answer.selected_option_text,
      selectedEnglish: answer.selected_option_text,
      selectedArabic: answer.selected_option_text_arabic,
      selectedUrdu: answer.selected_option_text_urdu,
      hasAnswerText: !!answer.answer_text,
      answerText: answer.answer_text
    });
    
    // If it's a selected option (MCQ)
    if (answer.selected_option_id) {
      return getText(answer, 'selected_option_text') || 'No option selected';
    }
    
    // If it's a text answer
    if (answer.answer_text) {
      return answer.answer_text;
    }
    
    return 'No answer provided';
  };

  const getCorrectAnswerText = (answer) => {
    if (!answer) return 'No correct answer';
    
    console.log("🔍 Getting correct answer for:", {
      hasCorrectOption: !!answer.correct_option_text,
      correctEnglish: answer.correct_option_text,
      correctArabic: answer.correct_option_text_arabic,
      correctUrdu: answer.correct_option_text_urdu,
      hasCorrectAnswer: !!answer.correct_answer,
      correctAnswer: answer.correct_answer
    });
    
    // For MCQ questions with options
    if (answer.correct_option_text) {
      return getText(answer, 'correct_option_text') || answer.correct_answer || 'No correct answer';
    }
    
    // For short answer questions
    return answer.correct_answer || 'No correct answer available';
  };

  const getGradeClass = (percentage) => {
    if (percentage >= 90) return 'grade-excellent';
    if (percentage >= 80) return 'grade-good';
    if (percentage >= 70) return 'grade-average';
    if (percentage >= 60) return 'grade-pass';
    return 'grade-fail';
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return <div className="student-quiz-result-loading">Loading result...</div>;
  }

  if (!result || !quiz) {
    return <div className="student-quiz-result-error">Result not found</div>;
  }

  const percentage = Math.round((result.total_score / quiz.total_marks) * 100);
  const gradeClass = getGradeClass(percentage);

  return (
    <div className="student-quiz-result-container">
      <div className="result-navigation">
        <button 
          onClick={() => navigate(-1)}
          className="back-to-quizzes-button"
        >
          ← Back
        </button>
        <h1>Quiz Result</h1>
        
        {/* Language Selector */}
        <div className="language-selector">
          <span className="language-label">View in:</span>
          <button 
            className={`language-btn ${activeLanguage === 'english' ? 'active' : ''}`}
            onClick={() => setActiveLanguage('english')}
          >
            English
          </button>
          <button 
            className={`language-btn ${activeLanguage === 'urdu' ? 'active' : ''}`}
            onClick={() => setActiveLanguage('urdu')}
          >
            اردو
          </button>
          <button 
            className={`language-btn ${activeLanguage === 'arabic' ? 'active' : ''}`}
            onClick={() => setActiveLanguage('arabic')}
          >
            العربية
          </button>
        </div>
      </div>

      <div className="result-overview">
        <div className="quiz-info-card">
          <h2>{quiz.title}</h2>
          <p className="quiz-detail">Subject: {quiz.subject_name}</p>
          <p className="quiz-detail">Teacher: {quiz.teacher_name}</p>
          <p className="quiz-detail">Submitted: {formatDate(result.submitted_at)}</p>
        </div>

        <div className="score-display-card">
          <div className={`score-circle ${gradeClass}`}>
            <span className="score-percentage">{percentage}%</span>
            <span className="score-label">Score</span>
          </div>
          <div className="score-details">
            <p><strong>Marks Obtained:</strong> {result.total_score} / {quiz.total_marks}</p>
            <p><strong>Correct Answers:</strong> {
              detailedAnswers.filter(a => a.is_correct).length
            } / {detailedAnswers.length}</p>
            <p><strong>Grade:</strong> {
              percentage >= 90 ? 'A+' :
              percentage >= 80 ? 'A' :
              percentage >= 70 ? 'B' :
              percentage >= 60 ? 'C' :
              percentage >= 50 ? 'D' : 'F'
            }</p>
          </div>
        </div>
      </div>

      <div className="detailed-analysis">
        <h2>Question-wise Analysis</h2>
        
        {detailedAnswers.map((answer, index) => {
          const questionText = getText(answer, 'question_text');
          const selectedAnswer = getAnswerText(answer);
          const correctAnswer = getCorrectAnswerText(answer);

          console.log(`📝 Answer ${index + 1}:`, {
            questionText,
            selectedAnswer,
            correctAnswer,
            isCorrect: answer.is_correct
          });

          return (
            <div key={answer.id || index} className={`answer-analysis ${answer.is_correct ? 'answer-correct' : 'answer-incorrect'}`}>
              <div className="analysis-header">
                <h3>
                  Question {index + 1} 
                  <span className="question-weight">({answer.marks} mark{answer.marks !== 1 ? 's' : ''})</span>
                </h3>
                <span className={`answer-status ${answer.is_correct ? 'status-correct' : 'status-incorrect'}`}>
                  {answer.is_correct ? '✓ Correct' : '✗ Incorrect'}
                </span>
              </div>
              
              <div className="analysis-question">
                <p><strong>Question:</strong></p>
                <div className={`question-text ${activeLanguage === 'arabic' || activeLanguage === 'urdu' ? 'rtl-text' : ''}`}>
                  {questionText}
                </div>
              </div>
              
              <div className="analysis-answer">
                <p><strong>Your Answer:</strong></p>
                <div className={`answer-text ${activeLanguage === 'arabic' || activeLanguage === 'urdu' ? 'rtl-text' : ''}`}>
                  {selectedAnswer}
                </div>
                
                {!answer.is_correct && correctAnswer && (
                  <div className="correct-answer-reveal">
                    <p><strong>Correct Answer:</strong></p>
                    <div className={`correct-answer-text ${activeLanguage === 'arabic' || activeLanguage === 'urdu' ? 'rtl-text' : ''}`}>
                      {correctAnswer}
                    </div>
                  </div>
                )}
              </div>
              
              <div className="analysis-score">
                <span>Marks Obtained: {answer.marks_obtained} / {answer.marks}</span>
              </div>
            </div>
          );
        })}
      </div>

      <div className="result-actions-panel">
        <button 
          onClick={() => navigate(`/student-dashboard/${userId}/quizzes`)}
          className="back-to-quizzes-button"
        >
          ← Back to Quizzes
        </button>
        
        <button 
          onClick={() => navigate(`/student-dashboard/${userId}/courses`)}
          className="back-to-dashboard-button"
        >
          Back to Dashboard
        </button>
        
        <button 
          onClick={() => window.print()}
          className="print-result-button"
        >
          Print Result
        </button>
      </div>
    </div>
  );
};

export default StudentQuizResult;