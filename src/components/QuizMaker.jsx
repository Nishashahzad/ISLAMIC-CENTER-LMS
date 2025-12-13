// components/QuizMaker.jsx
import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import './QuizMaker.css';

const QuizMaker = () => {
  const [searchParams] = useSearchParams();
  
  // Get teacher ID and subject from URL parameters
  const teacherIdFromURL = searchParams.get('teacherId');
  const subjectFromURL = searchParams.get('subject');
  
  const [quizData, setQuizData] = useState({
    title: '',
    description: '',
    subject_name: subjectFromURL || '', // Pre-fill from URL
    start_date: '',
    end_date: '',
    duration_minutes: 30,
    total_marks: 100,
    is_published: false,
    questions: []
  });

  const [activeLanguage, setActiveLanguage] = useState('english');
  const [questionLanguage, setQuestionLanguage] = useState('english');
  const [currentQuestion, setCurrentQuestion] = useState({
    question_text: '',
    question_type: 'mcq',
    marks: 1,
    correct_answer: '',
    options: [
      { option_text: '', is_correct: false },
      { option_text: '', is_correct: false },
      { option_text: '', is_correct: false },
      { option_text: '', is_correct: false }
    ]
  });

  const [isRecording, setIsRecording] = useState(false);
  const [teacherAssignedSubjects, setTeacherAssignedSubjects] = useState([]);
  const [teacherId, setTeacherId] = useState(teacherIdFromURL || '');
  const [teacherName, setTeacherName] = useState('');
  const [showLanguageSelector, setShowLanguageSelector] = useState(true);
  const [loading, setLoading] = useState(true);
  const [subjectValidated, setSubjectValidated] = useState(false);
  const [validationError, setValidationError] = useState('');

  const recognitionRef = useRef(null);

  useEffect(() => {
    // Get teacher data from localStorage as backup
    const storedTeacher = JSON.parse(localStorage.getItem('user') || '{}');
    const quizTeacherData = JSON.parse(localStorage.getItem('quizTeacherData') || '{}');
    
    let finalTeacherId = teacherId;
    let finalTeacherName = '';
    let finalSubject = subjectFromURL;
    
    // Priority: URL params > quizTeacherData > localStorage
    if (!finalTeacherId && quizTeacherData.userId) {
      finalTeacherId = quizTeacherData.userId;
    } else if (!finalTeacherId && storedTeacher.userId) {
      finalTeacherId = storedTeacher.userId;
    } else if (!finalTeacherId && storedTeacher.userid) {
      finalTeacherId = storedTeacher.userid;
    } else if (!finalTeacherId && storedTeacher.id) {
      finalTeacherId = storedTeacher.id;
    }
    
    if (quizTeacherData.fullName) {
      finalTeacherName = quizTeacherData.fullName;
    } else if (storedTeacher.fullName) {
      finalTeacherName = storedTeacher.fullName;
    }
    
    if (!finalSubject && quizTeacherData.selectedSubject) {
      finalSubject = quizTeacherData.selectedSubject;
    } else if (!finalSubject && quizTeacherData.prefillSubject) {
      finalSubject = quizTeacherData.prefillSubject;
    }
    
    // Update state
    if (finalTeacherId) {
      setTeacherId(finalTeacherId);
    }
    
    if (finalTeacherName) {
      setTeacherName(finalTeacherName);
    }
    
    if (finalSubject && !quizData.subject_name) {
      setQuizData(prev => ({
        ...prev,
        subject_name: finalSubject
      }));
    }
    
    // Validate teacher and subject
    validateTeacherAndSubject(finalTeacherId, finalSubject);
  }, []);

  const validateTeacherAndSubject = async (teacherId, subject) => {
    try {
      setLoading(true);
      
      if (!teacherId) {
        setValidationError('Teacher ID not found. Please log in as a teacher.');
        setLoading(false);
        return;
      }
      
      if (!subject) {
        setValidationError('No subject specified. Please select a subject in your courses first.');
        setLoading(false);
        return;
      }
      
      // Fetch teacher's assigned subjects to validate
      const response = await fetch(`http://localhost:8000/teacher/${teacherId}/assigned_subjects`);
      const data = await response.json();
      
      if (data.success) {
        const assignedSubjects = data.assigned_subjects || [];
        setTeacherAssignedSubjects(assignedSubjects);
        
        // Check if the subject is in teacher's assigned subjects
        const subjectMatch = assignedSubjects.some(assignedSubject => 
          assignedSubject.toLowerCase() === subject.toLowerCase()
        );
        
        if (!subjectMatch && assignedSubjects.length > 0) {
          setValidationError(`You are not assigned to teach "${subject}". Your assigned subjects: ${assignedSubjects.join(', ')}`);
        } else if (subjectMatch) {
          setSubjectValidated(true);
          console.log(`✅ Subject validated: ${subject} for teacher ${teacherId}`);
        }
      } else {
        setValidationError('Error validating your teaching subjects. Please try again.');
      }
    } catch (error) {
      console.error('Error validating teacher:', error);
      setValidationError('Error connecting to server. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Language Selection Screen
  const LanguageSelector = () => (
    <div className="language-selector-screen">
      <div className="language-selector-container">
        <h2>🌐 Choose Quiz Language</h2>
        <p className="language-selector-description">
          Creating quiz for: <strong>{quizData.subject_name}</strong>
        </p>
        
        <div className="language-options">
          <div 
            className={`language-option ${activeLanguage === 'english' ? 'selected' : ''}`}
            onClick={() => {
              setActiveLanguage('english');
              setQuestionLanguage('english');
              setShowLanguageSelector(false);
            }}
          >
            <div className="language-icon">🇺🇸</div>
            <div className="language-info">
              <h3>English</h3>
              <p>Create questions in English</p>
            </div>
            <div className="language-select-arrow">→</div>
          </div>
          
          <div 
            className={`language-option ${activeLanguage === 'urdu' ? 'selected' : ''}`}
            onClick={() => {
              setActiveLanguage('urdu');
              setQuestionLanguage('urdu');
              setShowLanguageSelector(false);
            }}
          >
            <div className="language-icon">🇵🇰</div>
            <div className="language-info">
              <h3>اردو</h3>
              <p>Create questions in Urdu</p>
            </div>
            <div className="language-select-arrow">→</div>
          </div>
          
          <div 
            className={`language-option ${activeLanguage === 'arabic' ? 'selected' : ''}`}
            onClick={() => {
              setActiveLanguage('arabic');
              setQuestionLanguage('arabic');
              setShowLanguageSelector(false);
            }}
          >
            <div className="language-icon">🇸🇦</div>
            <div className="language-info">
              <h3>العربية</h3>
              <p>Create questions in Arabic</p>
            </div>
            <div className="language-select-arrow">→</div>
          </div>
        </div>
        
        <div className="subject-info-card">
          <h4>Quiz Details</h4>
          <p><strong>Subject:</strong> {quizData.subject_name}</p>
          {teacherName && <p><strong>Teacher:</strong> {teacherName}</p>}
        </div>
        
        <div className="language-tip">
          <p>💡 You can change the language for each question using the language switcher.</p>
        </div>
      </div>
    </div>
  );

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setQuizData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleQuestionChange = (e) => {
    const { name, value } = e.target;
    setCurrentQuestion(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleOptionChange = (index, value) => {
    const updatedOptions = [...currentQuestion.options];
    updatedOptions[index] = {
      ...updatedOptions[index],
      option_text: value
    };
    setCurrentQuestion(prev => ({
      ...prev,
      options: updatedOptions
    }));
  };

  const handleCorrectOption = (index) => {
    const updatedOptions = currentQuestion.options.map((opt, i) => ({
      ...opt,
      is_correct: i === index
    }));
    setCurrentQuestion(prev => ({
      ...prev,
      options: updatedOptions,
      correct_answer: currentQuestion.options[index].option_text
    }));
  };

  const addQuestion = () => {
    if (!currentQuestion.question_text.trim()) {
      alert('Please enter question text');
      return;
    }

    // Create question with all language fields (even if empty)
    const questionToAdd = {
      question_text: questionLanguage === 'english' ? currentQuestion.question_text : '',
      question_text_urdu: questionLanguage === 'urdu' ? currentQuestion.question_text : '',
      question_text_arabic: questionLanguage === 'arabic' ? currentQuestion.question_text : '',
      question_type: currentQuestion.question_type,
      marks: currentQuestion.marks,
      correct_answer: currentQuestion.correct_answer,
      options: currentQuestion.options.map(opt => ({
        option_text: questionLanguage === 'english' ? opt.option_text : '',
        option_text_urdu: questionLanguage === 'urdu' ? opt.option_text : '',
        option_text_arabic: questionLanguage === 'arabic' ? opt.option_text : '',
        is_correct: opt.is_correct
      }))
    };

    setQuizData(prev => ({
      ...prev,
      questions: [...prev.questions, questionToAdd]
    }));

    // Reset current question
    setCurrentQuestion({
      question_text: '',
      question_type: 'mcq',
      marks: 1,
      correct_answer: '',
      options: [
        { option_text: '', is_correct: false },
        { option_text: '', is_correct: false },
        { option_text: '', is_correct: false },
        { option_text: '', is_correct: false }
      ]
    });
  };

  const removeQuestion = (index) => {
    setQuizData(prev => ({
      ...prev,
      questions: prev.questions.filter((_, i) => i !== index)
    }));
  };

  const startVoiceRecording = () => {
    setIsRecording(true);
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.lang = questionLanguage === 'urdu' ? 'ur-PK' : 
                        questionLanguage === 'arabic' ? 'ar-SA' : 'en-US';
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;

      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[event.results.length - 1][0].transcript;
        setCurrentQuestion(prev => ({ ...prev, question_text: transcript }));
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsRecording(false);
      };

      recognitionRef.current.start();
    } else {
      alert('Speech recognition not supported in this browser');
      setIsRecording(false);
    }
  };

  const stopVoiceRecording = () => {
    setIsRecording(false);
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
  };

const submitQuiz = async () => {
  if (!teacherId) {
    alert('Teacher ID not found. Please log in as a teacher.');
    return;
  }

  if (!quizData.subject_name) {
    alert('Subject not found. Please go back and select a subject first.');
    return;
  }

  if (!quizData.title || quizData.questions.length === 0) {
    alert('Please fill quiz title and add at least one question');
    return;
  }

  // Make sure dates are properly formatted
  const quizPayload = {
    teacher_id: teacherId,
    subject_name: quizData.subject_name,
    title: quizData.title,
    description: quizData.description || "",
    start_date: quizData.start_date,
    end_date: quizData.end_date,
    total_marks: parseInt(quizData.total_marks) || 100,
    duration_minutes: parseInt(quizData.duration_minutes) || 30,
    is_published: quizData.is_published,
    questions: quizData.questions
  };

  console.log('Submitting quiz:', quizPayload);

  try {
    const response = await fetch('http://localhost:8000/create_quiz_with_questions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(quizPayload)
    });

    const data = await response.json();
    
    if (!response.ok) {
      // Handle HTTP errors
      throw new Error(data.detail || `HTTP error! status: ${response.status}`);
    }
    
    if (data.success) {
      alert('Quiz created successfully!');
      // Reset form
      setQuizData({
        title: '',
        description: '',
        subject_name: quizData.subject_name, // Keep same subject
        start_date: '',
        end_date: '',
        duration_minutes: 30,
        total_marks: 100,
        is_published: false,
        questions: []
      });
      setShowLanguageSelector(true);
    } else {
      alert('Error creating quiz: ' + (data.detail || 'Unknown error'));
    }
  } catch (error) {
    console.error('Error submitting quiz:', error);
    alert('Error creating quiz: ' + error.message);
  }
};

  // Get language label
  const getLanguageLabel = (lang) => {
    const labels = {
      'english': 'English',
      'urdu': 'اردو',
      'arabic': 'العربية'
    };
    return labels[lang] || lang;
  };

  // Loading screen
  if (loading) {
    return (
      <div className="quiz-maker-container">
        <div className="loading-screen">
          <h2>Loading quiz maker...</h2>
          <p>Validating your teaching permissions for: <strong>{quizData.subject_name}</strong></p>
          <div className="loading-spinner"></div>
        </div>
      </div>
    );
  }

  // Validation error
  if (validationError) {
    return (
      <div className="quiz-maker-container">
        <div className="validation-error">
          <h2>⚠️ Access Denied</h2>
          <p>{validationError}</p>
          <button 
            onClick={() => window.close()}
            className="back-button"
          >
            ← Close and Go Back
          </button>
        </div>
      </div>
    );
  }

  // Language selector
  if (showLanguageSelector) {
    return <LanguageSelector />;
  }

  return (
    <div className="quiz-maker-container">
      {/* Header with Language Switcher */}
      <div className="quiz-maker-header">
        <div className="header-left">
          <h1>🎯 Create MCQ Quiz</h1>
          <div className="subject-display">
            <div className="subject-badge">
              📚 Subject: <strong>{quizData.subject_name}</strong>
            </div>
            <div className="teacher-info">
              {teacherName && <span className="teacher-name">Teacher: {teacherName}</span>}
            </div>
          </div>
        </div>
        <div className="header-right">
          <div className="language-switcher">
            <span className="current-language">
              Language: <strong>{getLanguageLabel(questionLanguage)}</strong>
            </span>
            <button 
              className="change-language-btn"
              onClick={() => setShowLanguageSelector(true)}
            >
              🔄 Change Language
            </button>
          </div>
        </div>
      </div>
      
      {/* Quiz Information Section */}
      <div className="quiz-info-section">
        <h2>Quiz Information</h2>
        <div className="form-group">
          <label>Quiz Title *</label>
          <input
            type="text"
            name="title"
            value={quizData.title}
            onChange={handleInputChange}
            placeholder="Enter quiz title"
            required
          />
        </div>

        {/* Hidden subject field - automatically filled */}
        <input type="hidden" name="subject_name" value={quizData.subject_name} />
        
        {/* Subject Display (Read-only) */}
        <div className="form-group">
          <label>Subject</label>
          <div className="subject-display-box">
            <input
              type="text"
              value={quizData.subject_name}
              readOnly
              className="readonly-subject-input"
            />
            <span className="subject-lock-icon">🔒</span>
          </div>
          <small className="subject-hint">
            This quiz will be created for your assigned subject: <strong>{quizData.subject_name}</strong>
          </small>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Start Date *</label>
            <input
              type="date"
              name="start_date"
              value={quizData.start_date}
              onChange={handleInputChange}
              required
            />
          </div>
          
          <div className="form-group">
            <label>End Date *</label>
            <input
              type="date"
              name="end_date"
              value={quizData.end_date}
              onChange={handleInputChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Duration (minutes)</label>
            <input
              type="number"
              name="duration_minutes"
              value={quizData.duration_minutes}
              onChange={handleInputChange}
              min="1"
            />
          </div>

          <div className="form-group">
            <label>Total Marks</label>
            <input
              type="number"
              name="total_marks"
              value={quizData.total_marks}
              onChange={handleInputChange}
              min="1"
            />
          </div>
        </div>

        <div className="form-group">
          <label>Description</label>
          <textarea
            name="description"
            value={quizData.description}
            onChange={handleInputChange}
            placeholder="Enter quiz description"
            rows="3"
          />
        </div>
      </div>

      {/* Question Creation Section */}
      <div className="question-section">
        <div className="section-header">
          <h2>Add Questions ({quizData.questions.length} added)</h2>
          <div className="language-badge">
            <span className="badge-icon">
              {questionLanguage === 'english' ? '🇺🇸' : 
               questionLanguage === 'urdu' ? '🇵🇰' : '🇸🇦'}
            </span>
            <span className="badge-text">{getLanguageLabel(questionLanguage)} Mode</span>
          </div>
        </div>

        {/* Voice Input Button */}
        <div className="voice-input-section">
          <button
            className={`voice-btn ${isRecording ? 'recording' : ''}`}
            onClick={isRecording ? stopVoiceRecording : startVoiceRecording}
            type="button"
          >
            {isRecording ? '🛑 Stop Recording' : '🎤 Start Voice Input'}
          </button>
          <small>Click and speak to input text in {getLanguageLabel(questionLanguage)}</small>
        </div>

        {/* Question Input */}
        <div className="form-group">
          <label>Question Text ({getLanguageLabel(questionLanguage)}) *</label>
          <textarea
            name="question_text"
            value={currentQuestion.question_text}
            onChange={handleQuestionChange}
            placeholder={`Enter question in ${getLanguageLabel(questionLanguage)}`}
            rows="3"
            className={`question-input ${questionLanguage === 'urdu' || questionLanguage === 'arabic' ? 'rtl' : ''}`}
            dir={questionLanguage === 'urdu' || questionLanguage === 'arabic' ? 'rtl' : 'ltr'}
            required
          />
        </div>

        <div className="form-group">
          <label>Question Type</label>
          <select
            name="question_type"
            value={currentQuestion.question_type}
            onChange={handleQuestionChange}
          >
            <option value="mcq">Multiple Choice (MCQ)</option>
            <option value="true_false">True/False</option>
            <option value="short_answer">Short Answer</option>
          </select>
        </div>

        <div className="form-group">
          <label>Marks</label>
          <input
            type="number"
            name="marks"
            value={currentQuestion.marks}
            onChange={handleQuestionChange}
            min="1"
          />
        </div>

        {/* Options for MCQ */}
        {currentQuestion.question_type === 'mcq' && (
          <div className="options-section">
            <h3>Options - Select correct answer with radio button</h3>
            {currentQuestion.options.map((option, index) => (
              <div key={index} className="option-row">
                <input
                  type="radio"
                  name="correct_option"
                  checked={option.is_correct}
                  onChange={() => handleCorrectOption(index)}
                  className="correct-radio"
                />
                
                <input
                  type="text"
                  placeholder={`Option ${index + 1} in ${getLanguageLabel(questionLanguage)}`}
                  value={option.option_text}
                  onChange={(e) => handleOptionChange(index, e.target.value)}
                  className={`option-input ${questionLanguage === 'urdu' || questionLanguage === 'arabic' ? 'rtl' : ''}`}
                  dir={questionLanguage === 'urdu' || questionLanguage === 'arabic' ? 'rtl' : 'ltr'}
                />
              </div>
            ))}
          </div>
        )}

        {/* Correct Answer for Short Answer */}
        {currentQuestion.question_type === 'short_answer' && (
          <div className="form-group">
            <label>Correct Answer</label>
            <input
              type="text"
              name="correct_answer"
              value={currentQuestion.correct_answer}
              onChange={handleQuestionChange}
              placeholder={`Enter correct answer in ${getLanguageLabel(questionLanguage)}`}
              className={questionLanguage === 'urdu' || questionLanguage === 'arabic' ? 'rtl' : ''}
              dir={questionLanguage === 'urdu' || questionLanguage === 'arabic' ? 'rtl' : 'ltr'}
            />
          </div>
        )}

        <div className="question-actions">
          <button className="add-question-btn" onClick={addQuestion} type="button">
            ➕ Add This Question
          </button>
          <button 
            className="new-language-btn"
            onClick={() => {
              // Save current question if exists
              if (currentQuestion.question_text.trim()) {
                if (window.confirm('Switch language? Current question will be saved.')) {
                  addQuestion();
                }
              }
              setShowLanguageSelector(true);
            }}
            type="button"
          >
            🌐 Add Question in Another Language
          </button>
        </div>
      </div>

      {/* Added Questions List */}
      {quizData.questions.length > 0 && (
        <div className="added-questions">
          <h3>Added Questions ({quizData.questions.length})</h3>
          {quizData.questions.map((q, index) => (
            <div key={index} className="question-card">
              <div className="question-header">
                <span>Q{index + 1}: 
                  {q.question_text || q.question_text_urdu || q.question_text_arabic || 'No text'}
                </span>
                <button onClick={() => removeQuestion(index)} className="remove-btn" type="button">
                  ❌ Remove
                </button>
              </div>
              <div className="question-meta">
                <span>Type: {q.question_type}</span>
                <span>Marks: {q.marks}</span>
                <span>
                  Language: 
                  {q.question_text ? ' English' : 
                   q.question_text_urdu ? ' Urdu' : 
                   q.question_text_arabic ? ' Arabic' : ' Unknown'}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Submit Button */}
      <div className="submit-section">
        <label className="publish-toggle">
          <input
            type="checkbox"
            checked={quizData.is_published}
            onChange={(e) => setQuizData(prev => ({ ...prev, is_published: e.target.checked }))}
          />
          Publish immediately
        </label>
        
        <div className="submit-actions">
          <button 
            className="back-to-language-btn"
            onClick={() => setShowLanguageSelector(true)}
            type="button"
          >
            ↩️ Back to Language Selector
          </button>
          <button className="submit-quiz-btn" onClick={submitQuiz} type="button">
            📝 Create Quiz for {quizData.subject_name}
          </button>
        </div>
      </div>
    </div>
  );
};

export default QuizMaker;