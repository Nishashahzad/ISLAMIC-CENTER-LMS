// components/QuizMaker.jsx
import React, { useState, useEffect } from 'react';
import './QuizMaker.css';

const QuizMaker = () => {
  const [quizData, setQuizData] = useState({
    title: '',
    description: '',
    subject_name: '',
    start_date: '',
    end_date: '',
    duration_minutes: 30,
    total_marks: 100,
    is_published: false,
    questions: []
  });

  const [currentQuestion, setCurrentQuestion] = useState({
    question_text: '',
    question_text_urdu: '',
    question_text_arabic: '',
    question_type: 'mcq',
    marks: 1,
    correct_answer: '',
    options: [
      { option_text: '', option_text_urdu: '', option_text_arabic: '', is_correct: false },
      { option_text: '', option_text_urdu: '', option_text_arabic: '', is_correct: false },
      { option_text: '', option_text_urdu: '', option_text_arabic: '', is_correct: false },
      { option_text: '', option_text_urdu: '', option_text_arabic: '', is_correct: false }
    ]
  });

  const [activeTab, setActiveTab] = useState('english');
  const [isRecording, setIsRecording] = useState(false);
  const [subjects, setSubjects] = useState([]);
  const [teacherId, setTeacherId] = useState('');

  useEffect(() => {
    // Get teacher ID from localStorage or context
    const storedTeacher = JSON.parse(localStorage.getItem('user') || '{}');
    console.log('Stored user:', storedTeacher);
    
    if (storedTeacher.userId) {
      setTeacherId(storedTeacher.userId);
    } else if (storedTeacher.userid) {
      setTeacherId(storedTeacher.userid);
    } else if (storedTeacher.id) {
      setTeacherId(storedTeacher.id);
    }

    // Fetch available subjects
    fetchSubjects();
  }, []);

  const fetchSubjects = async () => {
    try {
      const response = await fetch('http://localhost:8000/all_subjects');
      const data = await response.json();
      if (data.subjects) {
        setSubjects(data.subjects);
      }
    } catch (error) {
      console.error('Error fetching subjects:', error);
    }
  };

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

  const handleOptionChange = (index, field, value) => {
    const updatedOptions = [...currentQuestion.options];
    updatedOptions[index] = {
      ...updatedOptions[index],
      [field]: value
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

    setQuizData(prev => ({
      ...prev,
      questions: [...prev.questions, { ...currentQuestion }]
    }));

    // Reset current question
    setCurrentQuestion({
      question_text: '',
      question_text_urdu: '',
      question_text_arabic: '',
      question_type: 'mcq',
      marks: 1,
      correct_answer: '',
      options: [
        { option_text: '', option_text_urdu: '', option_text_arabic: '', is_correct: false },
        { option_text: '', option_text_urdu: '', option_text_arabic: '', is_correct: false },
        { option_text: '', option_text_urdu: '', option_text_arabic: '', is_correct: false },
        { option_text: '', option_text_urdu: '', option_text_arabic: '', is_correct: false }
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
    // In production, integrate with Web Speech API
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.lang = activeTab === 'urdu' ? 'ur-PK' : 
                        activeTab === 'arabic' ? 'ar-SA' : 'en-US';
      recognition.continuous = true;
      recognition.interimResults = true;

      recognition.onresult = (event) => {
        const transcript = event.results[event.results.length - 1][0].transcript;
        
        if (activeTab === 'english') {
          setCurrentQuestion(prev => ({ ...prev, question_text: transcript }));
        } else if (activeTab === 'urdu') {
          setCurrentQuestion(prev => ({ ...prev, question_text_urdu: transcript }));
        } else if (activeTab === 'arabic') {
          setCurrentQuestion(prev => ({ ...prev, question_text_arabic: transcript }));
        }
      };

      recognition.start();
    } else {
      alert('Speech recognition not supported in this browser');
      setIsRecording(false);
    }
  };

  const stopVoiceRecording = () => {
    setIsRecording(false);
    // Stop speech recognition
  };

  const submitQuiz = async () => {
    if (!teacherId) {
      alert('Teacher ID not found. Please log in as a teacher.');
      return;
    }

    if (!quizData.title || !quizData.subject_name || quizData.questions.length === 0) {
      alert('Please fill all required fields and add at least one question');
      return;
    }

    const quizPayload = {
      teacher_id: teacherId,
      subject_name: quizData.subject_name,
      title: quizData.title,
      description: quizData.description,
      start_date: quizData.start_date,
      end_date: quizData.end_date,
      total_marks: quizData.total_marks,
      duration_minutes: quizData.duration_minutes,
      is_published: quizData.is_published,
      questions: quizData.questions.map(q => ({
        question: {
          question_text: q.question_text,
          question_text_urdu: q.question_text_urdu || '',
          question_text_arabic: q.question_text_arabic || '',
          question_type: q.question_type,
          marks: q.marks,
          correct_answer: q.correct_answer
        },
        options: q.options.map(opt => ({
          option_text: opt.option_text,
          option_text_urdu: opt.option_text_urdu || '',
          option_text_arabic: opt.option_text_arabic || '',
          is_correct: opt.is_correct
        }))
      }))
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
      console.log('Response:', data);
      
      if (data.success) {
        alert('Quiz created successfully!');
        // Reset form
        setQuizData({
          title: '',
          description: '',
          subject_name: '',
          start_date: '',
          end_date: '',
          duration_minutes: 30,
          total_marks: 100,
          is_published: false,
          questions: []
        });
      } else {
        alert('Error creating quiz: ' + (data.detail || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error submitting quiz:', error);
      alert('Error creating quiz. Please try again.');
    }
  };

  return (
    <div className="quiz-maker-container">
      <div className="quiz-maker-header">
        <h1>🎯 Create MCQ Quiz</h1>
        <div className="teacher-info-badge">
          {teacherId ? `Teacher: ${teacherId}` : 'Please log in as teacher'}
        </div>
      </div>
      
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

        <div className="form-group">
          <label>Subject *</label>
          <select
            name="subject_name"
            value={quizData.subject_name}
            onChange={handleInputChange}
            required
          >
            <option value="">Select Subject</option>
            {subjects.map((subject, index) => (
              <option key={index} value={subject}>{subject}</option>
            ))}
          </select>
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

      <div className="question-section">
        <h2>Add Questions ({quizData.questions.length} added)</h2>
        
        {/* Language Tabs */}
        <div className="language-tabs">
          <button 
            className={activeTab === 'english' ? 'active' : ''}
            onClick={() => setActiveTab('english')}
          >
            English
          </button>
          <button 
            className={activeTab === 'urdu' ? 'active' : ''}
            onClick={() => setActiveTab('urdu')}
          >
            Urdu
          </button>
          <button 
            className={activeTab === 'arabic' ? 'active' : ''}
            onClick={() => setActiveTab('arabic')}
          >
            Arabic
          </button>
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
          <small>Click and speak to input text in {activeTab} language</small>
        </div>

        {/* Question Input based on active language */}
        <div className="form-group">
          <label>Question Text ({activeTab.toUpperCase()}) *</label>
          <textarea
            name={activeTab === 'english' ? 'question_text' : 
                  activeTab === 'urdu' ? 'question_text_urdu' : 'question_text_arabic'}
            value={activeTab === 'english' ? currentQuestion.question_text :
                   activeTab === 'urdu' ? currentQuestion.question_text_urdu :
                   currentQuestion.question_text_arabic}
            onChange={handleQuestionChange}
            placeholder={`Enter question in ${activeTab}`}
            rows="3"
            className={`question-input ${activeTab === 'urdu' || activeTab === 'arabic' ? 'rtl' : ''}`}
            dir={activeTab === 'urdu' || activeTab === 'arabic' ? 'rtl' : 'ltr'}
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
            <h3>Options (Select correct answer with radio button)</h3>
            {currentQuestion.options.map((option, index) => (
              <div key={index} className="option-row">
                <input
                  type="radio"
                  name="correct_option"
                  checked={option.is_correct}
                  onChange={() => handleCorrectOption(index)}
                  className="correct-radio"
                />
                
                <div className="option-inputs">
                  <input
                    type="text"
                    placeholder={`Option ${index + 1} (English)`}
                    value={option.option_text}
                    onChange={(e) => handleOptionChange(index, 'option_text', e.target.value)}
                  />
                  <input
                    type="text"
                    placeholder={`Option ${index + 1} (Urdu)`}
                    value={option.option_text_urdu}
                    onChange={(e) => handleOptionChange(index, 'option_text_urdu', e.target.value)}
                    className="rtl"
                    dir="rtl"
                  />
                  <input
                    type="text"
                    placeholder={`Option ${index + 1} (Arabic)`}
                    value={option.option_text_arabic}
                    onChange={(e) => handleOptionChange(index, 'option_text_arabic', e.target.value)}
                    className="rtl"
                    dir="rtl"
                  />
                </div>
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
              placeholder="Enter correct answer"
            />
          </div>
        )}

        <button className="add-question-btn" onClick={addQuestion} type="button">
          ➕ Add This Question
        </button>
      </div>

      {/* Added Questions List */}
      {quizData.questions.length > 0 && (
        <div className="added-questions">
          <h3>Added Questions ({quizData.questions.length})</h3>
          {quizData.questions.map((q, index) => (
            <div key={index} className="question-card">
              <div className="question-header">
                <span>Q{index + 1}: {q.question_text.substring(0, 50)}...</span>
                <button onClick={() => removeQuestion(index)} className="remove-btn" type="button">
                  ❌ Remove
                </button>
              </div>
              <div className="question-meta">
                <span>Type: {q.question_type}</span>
                <span>Marks: {q.marks}</span>
                <span>Language: {q.question_text_urdu ? 'Urdu' : q.question_text_arabic ? 'Arabic' : 'English'}</span>
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
        
        <button className="submit-quiz-btn" onClick={submitQuiz} type="button">
          📝 Create Quiz
        </button>
      </div>
    </div>
  );
};

export default QuizMaker;