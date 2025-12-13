// components/StudentSubmissionView.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import './StudentAssignmentSubmission.css';

const StudentSubmissionView = () => {
  const { submissionId, userId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const { subject, teacher, studentData, submission: existingSubmission } = location.state || {};
  
  const [submission, setSubmission] = useState(existingSubmission);
  const [loading, setLoading] = useState(!existingSubmission);

  useEffect(() => {
    if (!existingSubmission && submissionId) {
      fetchSubmission();
    }
  }, [submissionId, existingSubmission]);

  const fetchSubmission = async () => {
    try {
      const studentUserId = studentData?.userid || studentData?.userId || studentData?.id;
      const response = await fetch(`http://localhost:8000/student/${studentUserId}/assignment_submissions`);
      const data = await response.json();
      
      if (data.success) {
        const foundSubmission = data.submissions.find(s => s.id === parseInt(submissionId));
        if (foundSubmission) {
          setSubmission(foundSubmission);
        }
      }
      setLoading(false);
    } catch (error) {
      console.error('Error fetching submission:', error);
      setLoading(false);
    }
  };

  const handleBack = () => {
    navigate(`/student-dashboard/${userId}/assignments`, {
      state: { subject, teacher, studentData }
    });
  };

  const downloadSubmissionFile = () => {
    if (submission?.file_path) {
      const studentUserId = studentData?.userid || studentData?.userId || studentData?.id;
      window.open(`http://localhost:8000/assignments/submissions/${submissionId}/download?student_userId=${studentUserId}`, '_blank');
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

  if (loading) {
    return <div className="loading">Loading submission...</div>;
  }

  if (!submission) {
    return (
      <div className="error-message">
        <h2>Submission not found</h2>
        <button onClick={handleBack}>Go Back</button>
      </div>
    );
  }

  return (
    <div className="submission-view-container">
      <div className="submission-view-header">
        <button onClick={handleBack} className="back-button">
          ← Back to Assignments
        </button>
        <h1>📄 Submission Details</h1>
        <p className="subtitle">
          {subject} • {submission.assignment_title}
        </p>
      </div>

      <div className="submission-details-card">
        <div className="submission-meta">
          <div className="meta-section">
            <h3>Submission Information</h3>
            <div className="meta-grid">
              <div className="meta-item">
                <strong>Status:</strong>
                <span className={`status-badge ${submission.status}`}>
                  {submission.status === 'graded' ? '✅ Graded' : 
                   submission.status === 'late' ? '⏰ Late' : '📤 Submitted'}
                </span>
              </div>
              <div className="meta-item">
                <strong>Submitted:</strong> {formatDate(submission.submission_date)}
              </div>
              <div className="meta-item">
                <strong>Due Date:</strong> {formatDate(submission.assignment_due_date)}
              </div>
              {submission.graded_date && (
                <div className="meta-item">
                  <strong>Graded:</strong> {formatDate(submission.graded_date)}
                </div>
              )}
            </div>
          </div>

          {submission.marks_obtained !== null && (
            <div className="grade-section">
              <h3>Grading Result</h3>
              <div className="grade-display">
                <div className="grade-score">
                  <span className="score">{submission.marks_obtained}</span>
                  <span className="total">/{submission.assignment_total_marks}</span>
                </div>
                <div className="grade-percentage">
                  {Math.round((submission.marks_obtained / submission.assignment_total_marks) * 100)}%
                </div>
              </div>
            </div>
          )}
        </div>

        {submission.submission_text && (
          <div className="submission-text-section">
            <h3>Your Answer</h3>
            <div className="text-content">
              {submission.submission_text}
            </div>
          </div>
        )}

        {submission.file_name && (
          <div className="submission-file-section">
            <h3>Attached File</h3>
            <button onClick={downloadSubmissionFile} className="download-btn">
              📎 {submission.file_name}
            </button>
          </div>
        )}

        {submission.feedback && (
          <div className="feedback-section">
            <h3>Teacher Feedback</h3>
            <div className="feedback-content">
              {submission.feedback}
            </div>
            {submission.graded_by_name && (
              <div className="graded-by">
                <small>— {submission.graded_by_name}</small>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default StudentSubmissionView;