// components/StudentAssignmentSubmission.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import './StudentAssignmentSubmission.css';

const StudentAssignmentSubmission = () => {
  const { assignmentId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const { studentData, subject, teacher } = location.state || {};
  
  const [assignment, setAssignment] = useState(null);
  const [submission, setSubmission] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    submission_text: '',
    file: null,
    fileName: ''
  });

  useEffect(() => {
    if (assignmentId && studentData) {
      fetchAssignmentDetails();
      checkExistingSubmission();
    }
  }, [assignmentId, studentData]);

  const fetchAssignmentDetails = async () => {
    try {
      // First, get assignment details from assignments endpoint
      const teacherId = teacher?.userId || teacher?.userid;
      const response = await fetch(`http://localhost:8000/assignments/${teacherId}/${subject}`);
      const data = await response.json();
      
      if (data.success) {
        const foundAssignment = data.assignments.find(a => a.id === parseInt(assignmentId));
        if (foundAssignment) {
          setAssignment(foundAssignment);
        } else {
          alert('Assignment not found');
          navigate(-1);
        }
      }
    } catch (error) {
      console.error('Error fetching assignment:', error);
      alert('Error loading assignment details');
    } finally {
      setLoading(false);
    }
  };

  const checkExistingSubmission = async () => {
    try {
      const studentUserId = studentData?.userid || studentData?.userId || studentData?.id;
      const response = await fetch(`http://localhost:8000/student/${studentUserId}/assignment_submissions?subject_name=${encodeURIComponent(subject)}`);
      const data = await response.json();
      
      if (data.success) {
        const existing = data.submissions.find(s => s.assignment_id === parseInt(assignmentId));
        if (existing) {
          setSubmission(existing);
        }
      }
    } catch (error) {
      console.error('Error checking existing submission:', error);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setFormData({
        ...formData,
        file: file,
        fileName: file.name
      });
    }
  };

  const handleTextChange = (e) => {
    setFormData({
      ...formData,
      submission_text: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.submission_text.trim() && !formData.file) {
      alert('Please provide either text submission or upload a file');
      return;
    }
    
    if (!studentData) {
      alert('Student data not found');
      return;
    }
    
    const studentUserId = studentData?.userid || studentData?.userId || studentData?.id;
    
    const formDataToSend = new FormData();
    formDataToSend.append('student_userId', studentUserId);
    formDataToSend.append('submission_text', formData.submission_text);
    if (formData.file) {
      formDataToSend.append('file', formData.file);
    }
    
    setSubmitting(true);
    
    try {
      const response = await fetch(`http://localhost:8000/assignments/${assignmentId}/submit`, {
        method: 'POST',
        body: formDataToSend,
      });
      
      const data = await response.json();
      
      if (data.success) {
        alert('Assignment submitted successfully!');
        // Refresh submission data
        checkExistingSubmission();
        setFormData({
          submission_text: '',
          file: null,
          fileName: ''
        });
      } else {
        alert('Error submitting assignment: ' + data.detail);
      }
    } catch (error) {
      console.error('Error submitting assignment:', error);
      alert('Error submitting assignment. Please try again.');
    } finally {
      setSubmitting(false);
    }
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

  const downloadAssignmentFile = () => {
    if (assignment?.file_path) {
      window.open(`http://localhost:8000${assignment.file_path}`, '_blank');
    }
  };

  const downloadSubmissionFile = async () => {
    try {
      const studentUserId = studentData?.userid || studentData?.userId || studentData?.id;
      window.open(`http://localhost:8000/assignments/submissions/${submission.id}/download?student_userId=${studentUserId}`, '_blank');
    } catch (error) {
      console.error('Error downloading submission:', error);
    }
  };

  if (loading) {
    return (
      <div className="assignment-submission-container">
        <div className="loading">Loading assignment...</div>
      </div>
    );
  }

  if (!assignment) {
    return (
      <div className="assignment-submission-container">
        <div className="error-message">
          <h2>Assignment not found</h2>
          <button onClick={() => navigate(-1)}>Go Back</button>
        </div>
      </div>
    );
  }

  // Check if deadline has passed
  const currentDate = new Date();
  const dueDate = new Date(assignment.due_date);
  const isDeadlinePassed = currentDate > dueDate;

  return (
    <div className="assignment-submission-container">
      {/* Header */}
      <div className="assignment-header">
        <button onClick={() => navigate(-1)} className="back-button">
          ← Back to Assignments
        </button>
        <h1>📝 Assignment Submission</h1>
        <div className="assignment-meta">
          <span className="subject-badge">{subject}</span>
          {teacher && <span className="teacher-info">Teacher: {teacher.fullName}</span>}
        </div>
      </div>

      {/* Assignment Details */}
      <div className="assignment-details-card">
        <div className="assignment-header-info">
          <h2>{assignment.title}</h2>
          <div className="assignment-status">
            {isDeadlinePassed ? (
              <span className="status-badge late">⏰ Deadline Passed</span>
            ) : (
              <span className="status-badge active">📅 Active</span>
            )}
            {submission && (
              <span className={`status-badge ${submission.status === 'graded' ? 'graded' : 'submitted'}`}>
                {submission.status === 'graded' ? '✅ Graded' : '📤 Submitted'}
              </span>
            )}
          </div>
        </div>
        
        <p className="assignment-description">{assignment.description}</p>
        
        <div className="assignment-meta-info">
          <div className="meta-row">
            <div className="meta-item">
              <strong>📅 Due Date:</strong> {formatDate(assignment.due_date)}
            </div>
            <div className="meta-item">
              <strong>📊 Total Marks:</strong> {assignment.total_marks || 'Not specified'}
            </div>
          </div>
          <div className="meta-row">
            <div className="meta-item">
              <strong>👥 Submissions:</strong> {assignment.submissions || 0}
            </div>
            <div className="meta-item">
              <strong>👨‍🏫 Teacher:</strong> {assignment.teacher_name || teacher?.fullName}
            </div>
          </div>
        </div>
        
        {assignment.file_name && (
          <div className="assignment-file-section">
            <h4>📎 Assignment File:</h4>
            <button onClick={downloadAssignmentFile} className="download-btn">
              📥 Download {assignment.file_name}
            </button>
          </div>
        )}
      </div>

      {/* Submission Status */}
      {submission && (
        <div className="submission-status-card">
          <h3>📤 Your Submission</h3>
          <div className="submission-details">
            <div className="submission-meta">
              <span><strong>Submitted:</strong> {formatDate(submission.submission_date)}</span>
              <span className={`status ${submission.status}`}>
                {submission.status === 'graded' ? 'Graded' : 
                 submission.status === 'late' ? 'Late Submission' : 'Submitted'}
              </span>
            </div>
            
            {submission.submission_text && (
              <div className="submission-text">
                <strong>Your Answer:</strong>
                <p>{submission.submission_text}</p>
              </div>
            )}
            
            {submission.file_name && (
              <div className="submission-file">
                <strong>Attached File:</strong>
                <button onClick={downloadSubmissionFile} className="file-download-btn">
                  📎 {submission.file_name}
                </button>
              </div>
            )}
            
            {/* Grade Display */}
            {submission.marks_obtained !== null && (
              <div className="grade-display">
                <div className="grade-header">
                  <h4>📊 Grading Result</h4>
                  <span className="grade-badge">
                    {submission.marks_obtained}/{submission.assignment_total_marks}
                  </span>
                </div>
                <div className="grade-details">
                  <div className="grade-item">
                    <strong>Marks Obtained:</strong> {submission.marks_obtained}
                  </div>
                  <div className="grade-item">
                    <strong>Total Marks:</strong> {submission.assignment_total_marks}
                  </div>
                  <div className="grade-item">
                    <strong>Percentage:</strong> 
                    {Math.round((submission.marks_obtained / submission.assignment_total_marks) * 100)}%
                  </div>
                  {submission.feedback && (
                    <div className="feedback-section">
                      <strong>Teacher Feedback:</strong>
                      <p className="feedback-text">{submission.feedback}</p>
                    </div>
                  )}
                  {submission.graded_by_name && (
                    <div className="graded-by">
                      <small>Graded by: {submission.graded_by_name}</small>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Submission Form (only if not submitted or deadline hasn't passed) */}
      {(!submission || !isDeadlinePassed) && !(submission?.status === 'graded') && (
        <div className="submission-form-card">
          <h3>{submission ? 'Resubmit Assignment' : 'Submit Assignment'}</h3>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Text Submission (Optional)</label>
              <textarea
                value={formData.submission_text}
                onChange={handleTextChange}
                placeholder="Type your answer here..."
                rows={6}
                className="submission-textarea"
              />
            </div>
            
            <div className="form-group">
              <label>File Upload (Optional - PDF, DOC, DOCX, TXT)</label>
              <div className="file-upload-area">
                <input
                  type="file"
                  id="assignmentFile"
                  onChange={handleFileChange}
                  accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png"
                  className="file-input"
                />
                <label htmlFor="assignmentFile" className="file-upload-label">
                  {formData.fileName ? `📎 ${formData.fileName}` : '📁 Choose File'}
                </label>
                {formData.fileName && (
                  <button 
                    type="button" 
                    onClick={() => setFormData({...formData, file: null, fileName: ''})}
                    className="remove-file-btn"
                  >
                    ❌
                  </button>
                )}
              </div>
            </div>
            
            <div className="form-note">
              <p>💡 You can submit text, a file, or both. Make sure to submit before the deadline.</p>
              {isDeadlinePassed && (
                <p className="warning-note">⚠️ Late submissions will be marked as "Late"</p>
              )}
            </div>
            
            <div className="form-actions">
              <button
                type="button"
                onClick={() => navigate(-1)}
                className="cancel-btn"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting || (!formData.submission_text.trim() && !formData.file)}
                className="submit-btn"
              >
                {submitting ? 'Submitting...' : submission ? 'Resubmit' : 'Submit Assignment'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Instructions */}
      <div className="instructions-card">
        <h4>📋 Submission Guidelines</h4>
        <ul>
          <li>Submit your assignment before the deadline</li>
          <li>You can submit multiple times - the latest submission will be graded</li>
          <li>Accepted file types: PDF, Word, Text, Images</li>
          <li>Maximum file size: 10MB</li>
          <li>Your teacher will grade the assignment and provide feedback</li>
          <li>Check back later to see your grade and feedback</li>
        </ul>
      </div>
    </div>
  );
};

export default StudentAssignmentSubmission;