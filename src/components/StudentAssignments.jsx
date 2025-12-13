import React, { useState, useEffect } from 'react';
import "./StudentCourses.css";
import { useLocation, useNavigate, useParams } from 'react-router-dom';

const StudentAssignments = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { userId } = useParams();
  const { subject, teacher, studentData } = location.state || {};
  
  const [assignments, setAssignments] = useState([]);
  const [mySubmissions, setMySubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (subject && teacher && studentData) {
      fetchAssignments();
      fetchMySubmissions();
    } else {
      setLoading(false);
      setError("Missing required data. Please go back and try again.");
    }
  }, [subject, teacher, studentData]);

  const fetchAssignments = async () => {
    try {
      console.log("Fetching assignments for:", teacher.userId, subject);
      const response = await fetch(`http://localhost:8000/assignments/${teacher.userId}/${subject}`);
      const data = await response.json();
      
      console.log("Assignments data:", data); // DEBUG
      
      if (data.success) {
        setAssignments(data.assignments || []);
      } else {
        setError(data.detail || "Failed to load assignments");
      }
    } catch (error) {
      console.error('Error fetching assignments:', error);
      setError("Error connecting to server");
    }
  };
const fetchMySubmissions = async () => {
  try {
    const studentUserId = studentData?.userid || studentData?.userId || studentData?.id;
    if (!studentUserId) {
      console.error("No student user ID found");
      return;
    }
    
    console.log("Fetching submissions for student:", studentUserId);
    
    // First, test if the student exists
    const testResponse = await fetch(`http://localhost:8000/test/student/${studentUserId}`);
    const testData = await testResponse.json();
    
    console.log("Test response:", testData);
    
    if (!testData.success) {
      console.error("Student not found in database");
      setMySubmissions([]);
      return;
    }
    
    // Now fetch submissions
    const response = await fetch(
      `http://localhost:8000/student/${studentUserId}/assignment_submissions?subject_name=${encodeURIComponent(subject)}`
    );
    
    console.log("Full URL:", `http://localhost:8000/student/${studentUserId}/assignment_submissions?subject_name=${encodeURIComponent(subject)}`);
    
    const data = await response.json();
    
    console.log("Submissions response:", data);
    
    if (data.success) {
      setMySubmissions(data.submissions || []);
    } else {
      console.warn("No submissions found or error:", data.error || data.detail);
      setMySubmissions([]);
    }
  } catch (error) {
    console.error('Error fetching submissions:', error);
    console.error('Error details:', error.message);
    setMySubmissions([]);
  } finally {
    setLoading(false);
  }
};

  const handleBack = () => {
    navigate(`/student-dashboard/${userId}/courses`);
  };

  const handleDownload = (assignment) => {
    if (assignment?.file_path) {
      // Ensure the path is correct
      const filePath = assignment.file_path.startsWith('http') 
        ? assignment.file_path 
        : `http://localhost:8000/${assignment.file_path}`;
      window.open(filePath, '_blank');
    } else {
      alert('No file available for this assignment');
    }
  };

  const handleSubmitAssignment = (assignment) => {
    navigate(`/student-dashboard/${userId}/assignments/submit/${assignment.id}`, {
      state: { 
        subject, 
        teacher, 
        studentData, 
        assignment 
      }
    });
  };

  const handleViewSubmission = (submission) => {
    navigate(`/student-dashboard/${userId}/assignments/submission/${submission.id}`, {
      state: { 
        subject, 
        teacher, 
        studentData,
        submission 
      }
    });
  };

  const formatDate = (dateString) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (e) {
      return 'Invalid date';
    }
  };

  const getAssignmentStatus = (assignment) => {
    if (!assignment || !assignment.id) {
      return {
        type: 'error',
        label: 'Error',
        color: '#f44336',
        bgColor: '#ffebee',
        submission: null
      };
    }

    const submission = Array.isArray(mySubmissions) 
      ? mySubmissions.find(s => s && s.assignment_id === assignment.id)
      : null;

    const currentDate = new Date();
    const dueDate = assignment.due_date ? new Date(assignment.due_date) : null;
    
    if (submission) {
      // Check if graded (marks_obtained is not null)
      if (submission.marks_obtained !== null && submission.marks_obtained !== undefined) {
        return {
          type: 'graded',
          label: 'Graded',
          color: '#4caf50',
          bgColor: '#e8f5e9',
          submission: submission,
          hasMarks: true,
          marks: submission.marks_obtained
        };
      } 
      // Check if submitted but not graded
      else if (submission.status === 'submitted' || submission.status === 'late' || submission.status === 'graded') {
        // If status is 'graded' but marks_obtained is null, it's still pending
        return {
          type: 'submitted',
          label: submission.status === 'late' ? 'Late' : 'Submitted',
          color: submission.status === 'late' ? '#f44336' : '#2196f3',
          bgColor: submission.status === 'late' ? '#ffebee' : '#e3f2fd',
          submission: submission,
          hasMarks: false
        };
      }
    } else if (dueDate && currentDate > dueDate) {
      return {
        type: 'overdue',
        label: 'Overdue',
        color: '#f44336',
        bgColor: '#ffebee',
        submission: null
      };
    } else {
      return {
        type: 'pending',
        label: 'Pending',
        color: '#ff9800',
        bgColor: '#fff3e0',
        submission: null
      };
    }
  };

  const getGradingStats = () => {
    const submitted = mySubmissions.length;
    const graded = mySubmissions.filter(s => s && s.marks_obtained !== null && s.marks_obtained !== undefined).length;
    const totalMarks = mySubmissions.reduce((total, s) => {
      if (s && s.marks_obtained !== null && s.marks_obtained !== undefined) {
        return total + parseFloat(s.marks_obtained);
      }
      return total;
    }, 0);
    const avgGrade = graded > 0 ? (totalMarks / graded).toFixed(1) : 0;
    
    return { submitted, graded, avgGrade };
  };

  const calculatePercentage = (marks, totalMarks = 100) => {
    if (!marks || !totalMarks) return 0;
    return Math.round((parseFloat(marks) / parseFloat(totalMarks)) * 100);
  };

  if (loading) {
    return (
      <div className="student-assignments-container">
        <div className="loading">
          <div className="loading-spinner"></div>
          <p>Loading assignments...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="student-assignments-container">
        <div className="error-message">
          <h2>⚠️ Error Loading Assignments</h2>
          <p>{error}</p>
          <button onClick={handleBack} className="back-btn">
            ← Go Back
          </button>
        </div>
      </div>
    );
  }

  const gradingStats = getGradingStats();

  return (
    <div className="student-assignments-container">
      <div className="student-assignments-header">
        <button onClick={handleBack} className="student-assignments-back-btn">
          ← Back to Courses
        </button>
        <h1 className="student-assignments-title">📝 {subject} - Assignments</h1>
        <p className="student-assignments-subtitle">Teacher: {teacher?.fullName || 'Not assigned'}</p>
      </div>

      {/* Statistics Card */}
      {assignments.length > 0 && (
        <div className="assignments-stats-card">
          <div className="stats-grid">
            <div className="stat-item">
              <div className="stat-value">{assignments.length}</div>
              <div className="stat-label">Total Assignments</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{gradingStats.submitted}</div>
              <div className="stat-label">Submitted</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{gradingStats.graded}</div>
              <div className="stat-label">Graded</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{gradingStats.avgGrade}%</div>
              <div className="stat-label">Avg. Grade</div>
            </div>
          </div>
        </div>
      )}

      {assignments.length === 0 ? (
        <div className="no-data">
          <p>No assignments available for this subject.</p>
          <p className="hint">Check back later or contact your teacher</p>
        </div>
      ) : (
        <div className="student-assignments-list">
          {assignments.map((assignment) => {
            const status = getAssignmentStatus(assignment);
            const currentDate = new Date();
            const dueDate = assignment.due_date ? new Date(assignment.due_date) : null;
            const isOverdue = dueDate ? currentDate > dueDate : false;
            const canSubmit = !status.submission || !isOverdue;
            const totalMarks = assignment.total_marks || 100; // Default to 100 if column doesn't exist
            
            return (
              <div key={assignment.id} className="student-assignment-card">
                <div className="assignment-card-header">
                  <h3>{assignment.title || 'Untitled Assignment'}</h3>
                  <div className="status-container">
                    <span 
                      className="status-badge" 
                      style={{ 
                        backgroundColor: status.bgColor,
                        color: status.color,
                        border: `1px solid ${status.color}`
                      }}
                    >
                      {status.label}
                    </span>
                    
                    {/* Grade display - show if graded */}
                    {status.type === 'graded' && status.submission && (
                      <div className="grade-display-box">
                        <span className="grade-label">Grade:</span>
                        <span className="grade-value">
                          {status.marks}/{totalMarks}
                        </span>
                        <span className="grade-percentage">
                          ({calculatePercentage(status.marks, totalMarks)}%)
                        </span>
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="assignment-card-content">
                  <p className="assignment-description">
                    {assignment.description || 'No description provided'}
                  </p>
                  
                  <div className="assignment-meta-row">
                    <div className="meta-item">
                      <strong>📅 Due Date:</strong> 
                      <span className={isOverdue ? 'overdue-text' : ''}>
                        {assignment.due_date ? formatDate(assignment.due_date) : 'Not set'}
                        {isOverdue && ' (Overdue)'}
                      </span>
                    </div>
                    <div className="meta-item">
                      <strong>📊 Total Marks:</strong> {totalMarks}
                    </div>
                  </div>
                  
                  <div className="assignment-meta-row">
                    <div className="meta-item">
                      <strong>📅 Start Date:</strong> {assignment.start_date ? formatDate(assignment.start_date) : 'Not set'}
                    </div>
                    <div className="meta-item">
                      <strong>👥 Submissions:</strong> {assignment.submissions || 0}
                    </div>
                  </div>
                  
                  {assignment.file_path && (
                    <div className="assignment-file-section">
                      <strong>📎 Assignment File:</strong>
                      <button 
                        onClick={() => handleDownload(assignment)}
                        className="download-assignment-btn"
                      >
                        📥 Download {assignment.file_name || 'File'}
                      </button>
                    </div>
                  )}
                  
                  {/* Submission Info */}
                  {status.submission && (
                    <div className="submission-info-section">
                      <div className="submission-header">
                        <strong>📤 Your Submission</strong>
                        <span className="submission-date">
                          Submitted: {status.submission.submission_date ? formatDate(status.submission.submission_date) : 'Unknown date'}
                        </span>
                      </div>
                      
                      {status.submission.submission_text && (
                        <div className="submission-text-preview">
                          <p><strong>Your Answer:</strong> {status.submission.submission_text.substring(0, 100)}...</p>
                        </div>
                      )}
                      
                      {status.submission.file_name && (
                        <div className="submission-file-info">
                          <strong>Attached File:</strong> {status.submission.file_name}
                          <button 
                            onClick={() => handleDownload({file_path: status.submission.file_path})}
                            className="view-file-btn-small"
                          >
                            👁️ View
                          </button>
                        </div>
                      )}
                      
                      {/* Teacher Feedback and Grade */}
                      {status.type === 'graded' && (
                        <div className="grading-details">
                          <div className="grade-details">
                            <strong>🎯 Grade:</strong> 
                            <span className="grade-score">
                              {status.marks}/{totalMarks}
                            </span>
                            <span className="grade-percentage-small">
                              ({calculatePercentage(status.marks, totalMarks)}%)
                            </span>
                          </div>
                          
                          {status.submission.feedback && status.submission.feedback.trim() !== '' && (
                            <div className="teacher-feedback-preview">
                              <strong>💬 Teacher Feedback:</strong> 
                              <p className="feedback-text">{status.submission.feedback}</p>
                            </div>
                          )}
                          
                          {status.submission.graded_date && (
                            <div className="graded-date">
                              <small>Graded on: {formatDate(status.submission.graded_date)}</small>
                            </div>
                          )}
                          
                          {status.submission.graded_by_name && (
                            <div className="graded-by">
                              <small>Graded by: {status.submission.graded_by_name}</small>
                            </div>
                          )}
                        </div>
                      )}
                      
                      {/* Show pending grading message if submitted but not graded */}
                      {status.type === 'submitted' && (
                        <div className="pending-grading">
                          <p className="pending-text">
                            ⏳ Your submission is pending grading by the teacher.
                            Check back later for your grade and feedback.
                          </p>
                        </div>
                      )}
                      
                      <button 
                        onClick={() => handleViewSubmission(status.submission)}
                        className="view-submission-btn"
                      >
                        👁️ View Full Submission Details
                      </button>
                    </div>
                  )}
                </div>
                
                <div className="assignment-card-actions">
                  {canSubmit ? (
                    <button
                      onClick={() => handleSubmitAssignment(assignment)}
                      className={`submit-btn ${status.type === 'submitted' || status.type === 'graded' ? 'resubmit' : ''}`}
                    >
                      {status.type === 'graded' ? '📝 Resubmit' : 
                       status.type === 'submitted' ? '📝 Resubmit' : 
                       '📤 Submit Assignment'}
                    </button>
                  ) : (
                    <button className="submit-btn disabled" disabled>
                      ❌ Deadline Passed
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default StudentAssignments;