import React, { useEffect, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import "./StudentCourses.css";

const StudentAssignments = () => {
  const { userId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();

  const { subject, teacher, studentData } = location.state || {};

  const [assignments, setAssignments] = useState([]);
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  /* =========================
     FETCH DATA
  ==========================*/
  useEffect(() => {
    if (!subject || !teacher || !studentData) {
      setError("Missing required data");
      setLoading(false);
      return;
    }

    fetchAssignments();
    fetchStudentSubmissions();
  }, []);

  const fetchAssignments = async () => {
    try {
      const res = await fetch(
        `http://localhost:8000/assignments/${teacher.userId}/${subject}`
      );
      const data = await res.json();

      if (data.success) {
        setAssignments(data.assignments || []);
      } else {
        setError("Failed to load assignments");
      }
    } catch (err) {
      setError("Server error while loading assignments");
    }
  };

  const fetchStudentSubmissions = async () => {
    try {
      const studentUserId =
        studentData.userId || studentData.userid || studentData.id;

      const res = await fetch(
        `http://localhost:8000/student/${studentUserId}/assignment_submissions?subject_name=${encodeURIComponent(
          subject
        )}`
      );

      const data = await res.json();

      if (data.success) {
        setSubmissions(data.submissions || []);
      } else {
        setSubmissions([]);
      }
    } catch (err) {
      setSubmissions([]);
    } finally {
      setLoading(false);
    }
  };

  /* =========================
     TRIGGER AUTO-GRADING FOR OVERDUE ASSIGNMENTS
  ==========================*/
  useEffect(() => {
    const triggerAutoGrading = async () => {
      if (!assignments.length || !studentData || loading) return;

      const studentUserId = studentData.userId || studentData.userid || studentData.id;
      const now = new Date();
      
      // Check each assignment
      for (const assignment of assignments) {
        const submission = getSubmission(assignment.id);
        const dueDate = new Date(assignment.due_date);
        
        // If overdue and not submitted
        if (dueDate < now && !submission) {
          try {
            // Call backend endpoint to auto-grade
            const response = await fetch('http://localhost:8000/auto-grade/check-and-grade', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                student_userId: studentUserId,
                assignment_id: assignment.id,
                teacher_userId: teacher.userId,
                subject_name: subject
              })
            });

            const result = await response.json();
            
            if (result.success && result.auto_graded) {
              console.log(`Assignment "${assignment.title}" auto-graded`);
              
              // Refresh submissions after auto-grading
              setTimeout(() => {
                fetchStudentSubmissions();
              }, 1000);
            }
          } catch (error) {
            console.error('Error triggering auto-grading:', error);
          }
        }
      }
    };

    if (!loading && assignments.length > 0) {
      triggerAutoGrading();
    }
  }, [assignments, loading, studentData, teacher, subject]);

  /* =========================
     CHECK IF ASSIGNMENT IS OVERDUE
  ==========================*/
  const checkAssignmentStatus = (assignment) => {
    const submission = getSubmission(assignment.id);
    const dueDate = new Date(assignment.due_date);
    const now = new Date();
    const isOverdue = dueDate < now;
    const isSubmitted = !!submission;
    
    // Check if auto-graded - handle both old and new field names
    const isAutoGraded = submission ? 
      (submission.auto_graded === true || 
       submission.auto_graded === 1 || 
       submission.status === 'auto_graded') : false;
    
    return {
      isOverdue,
      isSubmitted,
      isAutoGraded,
      dueDate,
      canSubmit: !isOverdue && !submission // Only if NOT overdue AND NOT submitted
    };
  };

  /* =========================
     HELPERS
  ==========================*/
  const getSubmission = (assignmentId) =>
    submissions.find((s) => s.assignment_id === assignmentId);

  const formatDate = (date) =>
    date
      ? new Date(date).toLocaleString("en-US", {
          year: "numeric",
          month: "short",
          day: "numeric",
          hour: "2-digit",
          minute: "2-digit",
        })
      : "Not set";

  const calculatePercentage = (marks, total = 100) =>
    marks != null ? Math.round((marks / total) * 100) : 0;

  const getStatusBadge = (assignment) => {
    const status = checkAssignmentStatus(assignment);
    const submission = getSubmission(assignment.id);

    if (status.isAutoGraded) {
      return <span className="status-badge auto-graded">Auto-Graded (0 marks)</span>;
    }

    if (!submission) {
      if (status.isOverdue) {
        return <span className="status-badge overdue">Overdue</span>;
      }
      return <span className="status-badge pending">Pending</span>;
    }

    if (submission.marks_obtained == null) {
      return <span className="status-badge submitted">Submitted</span>;
    }

    return <span className="status-badge graded">Graded</span>;
  };

  const getGradeDisplay = (submission, totalMarks) => {
    if (!submission || submission.marks_obtained == null) return null;

    const percentage = calculatePercentage(submission.marks_obtained, totalMarks);
    const isAutoGraded = submission.auto_graded === true || submission.auto_graded === 1;
    
    return (
      <div className="grade-display-box">
        <span className="grade-label">Grade:</span>
        <span className={`grade-value ${submission.marks_obtained === 0 ? 'zero-grade' : ''}`}>
          {submission.marks_obtained}/{totalMarks}
        </span>
        <span className="grade-percentage">({percentage}%)</span>
        {isAutoGraded && (
          <span className="auto-grade-badge">Auto</span>
        )}
      </div>
    );
  };

  const canSubmitAssignment = (assignment) => {
    const status = checkAssignmentStatus(assignment);
    return status.canSubmit;
  };

  /* =========================
     UI STATES
  ==========================*/
  if (loading) {
    return <div className="loading">Loading assignments...</div>;
  }

  if (error) {
    return (
      <div className="error-message">
        <p>{error}</p>
        <button onClick={() => navigate(-1)}>Go Back</button>
      </div>
    );
  }

  // Calculate stats
  const stats = {
    total: assignments.length,
    submitted: assignments.filter(assignment => {
      const submission = getSubmission(assignment.id);
      return submission != null;
    }).length,
    graded: assignments.filter(assignment => {
      const submission = getSubmission(assignment.id);
      return submission && submission.marks_obtained != null;
    }).length,
    pending: assignments.filter(assignment => {
      const submission = getSubmission(assignment.id);
      return !submission;
    }).length,
    autoGraded: assignments.filter(assignment => {
      const submission = getSubmission(assignment.id);
      return submission && (submission.auto_graded === true || submission.auto_graded === 1);
    }).length
  };

  /* =========================
     RENDER
  ==========================*/
  return (
    <div className="student-assignments-container">
      {/* Header */}
      <div className="student-assignments-header">
        <button 
          onClick={() => navigate(-1)} 
          className="student-assignments-back-btn"
        >
          ← Back to Courses
        </button>
        <h1 className="student-assignments-title">{subject} – Assignments</h1>
        <p className="student-assignments-subtitle">
          Teacher: {teacher.fullName} • Student: {studentData.fullName}
        </p>
        <p className="assignment-policy-note important-note">
          ⚠️ Important: Late submissions are NOT allowed. Assignments not submitted before the deadline will be automatically graded with 0 marks.
        </p>
      </div>

      {/* Stats Card */}
      <div className="assignments-stats-card">
        <div className="stats-grid">
          <div className="stat-item">
            <div className="stat-value">{stats.total}</div>
            <div className="stat-label">Total Assignments</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">{stats.submitted}</div>
            <div className="stat-label">Submitted</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">{stats.graded}</div>
            <div className="stat-label">Graded</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">{stats.autoGraded}</div>
            <div className="stat-label">Auto-Graded (0 marks)</div>
          </div>
        </div>
      </div>

      {/* Assignments List */}
      <div className="student-assignments-list">
        {assignments.length === 0 ? (
          <div className="no-data">
            <p>No assignments found for this subject</p>
            <p className="hint">Check back later or contact your teacher</p>
          </div>
        ) : (
          assignments.map((assignment, index) => {
            const submission = getSubmission(assignment.id);
            const totalMarks = assignment.total_marks || 100;
            const status = checkAssignmentStatus(assignment);
            const canSubmit = canSubmitAssignment(assignment);
            const isAutoGraded = submission && (submission.auto_graded === true || submission.auto_graded === 1);

            return (
              <div key={assignment.id} className="student-assignment-card">
                {/* Card Header */}
                <div className="assignment-card-header">
                  <div>
                    <h3>
                      Assignment {index + 1}: {assignment.title}
                      {isAutoGraded && (
                        <span className="auto-grade-indicator"> (Auto-Graded with 0 marks)</span>
                      )}
                    </h3>
                    <div className="assignment-meta-row">
                      <span className="meta-item">
                        <strong>Due:</strong> {formatDate(assignment.due_date)}
                        {status.isOverdue && !status.isSubmitted && (
                          <span className="overdue-text"> • Deadline Passed</span>
                        )}
                        {isAutoGraded && (
                          <span className="auto-grade-text"> • Auto-graded: No submission received</span>
                        )}
                      </span>
                      <span className="meta-item">
                        <strong>Total Marks:</strong> {totalMarks}
                      </span>
                    </div>
                  </div>
                  <div className="status-container">
                    {getStatusBadge(assignment)}
                    {getGradeDisplay(submission, totalMarks)}
                  </div>
                </div>

                {/* Assignment Description */}
                <div className="assignment-card-content">
                  <div className="assignment-description">
                    {assignment.description}
                  </div>

                  {/* Submission Information */}
                  {submission && (
                    <div className={`submission-info-section ${isAutoGraded ? 'auto-graded-section' : ''}`}>
                      <div className="submission-header">
                        <h4>
                          {isAutoGraded ? 'Auto-Graded Result' : 'Your Submission'}
                        </h4>
                        <span className="submission-date">
                          {isAutoGraded ? 'Auto-graded' : 'Submitted'}: {formatDate(submission.submission_date)}
                        </span>
                      </div>
                      
                      {submission.submission_text && (
                        <div className="submission-text-preview">
                          <strong>{isAutoGraded ? 'System Message:' : 'Text Submission:'}</strong>
                          <p>{submission.submission_text}</p>
                        </div>
                      )}

                      {submission.submission_file && (
                        <div className="submission-file-info">
                          <strong>File:</strong> {submission.submission_file}
                          <button className="download-assignment-btn">
                            📥 Download File
                          </button>
                        </div>
                      )}

                      {/* Teacher/System Feedback */}
                      {submission.feedback && (
                        <div className={`feedback-container ${isAutoGraded ? 'auto-feedback' : 'teacher-feedback-preview'}`}>
                          <strong>{isAutoGraded ? 'System Feedback:' : 'Teacher Feedback:'}</strong>
                          <p>{submission.feedback}</p>
                        </div>
                      )}

                      {/* Auto-Grade Notice */}
                      {isAutoGraded && (
                        <div className="auto-grade-notice">
                          <p>
                            ⚠️ This assignment was automatically graded with 0 marks because 
                            no submission was received before the deadline. Late submissions are not accepted.
                          </p>
                        </div>
                      )}

                      {/* Pending Grading */}
                      {submission && submission.marks_obtained == null && !isAutoGraded && (
                        <div className="pending-grading">
                          <p className="pending-text">
                            Your submission is pending review by the teacher
                          </p>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Overdue Warning */}
                  {status.isOverdue && !submission && !isAutoGraded && (
                    <div className="overdue-warning">
                      <p className="overdue-alert">
                        ⚠️ This assignment is overdue. It will be automatically graded with 0 marks.
                        <strong> Late submissions are not accepted.</strong>
                      </p>
                    </div>
                  )}
                </div>

                {/* Card Actions */}
                <div className="assignment-card-actions">
                  <button
                    className={`submit-btn ${!canSubmit ? 'disabled' : ''}`}
                    onClick={() => {
                      if (canSubmit) {
                        navigate(
                          `/student-dashboard/${userId}/assignments/submit/${assignment.id}`,
                          {
                            state: {
                              assignment,
                              subject,
                              teacher,
                              studentData,
                              isResubmit: false
                            },
                          }
                        );
                      }
                    }}
                    disabled={!canSubmit}
                  >
                    {!canSubmit ? (
                      isAutoGraded ? '✓ Auto-graded with 0 marks' : 
                      status.isOverdue ? '⏰ Submission Closed - Deadline Passed' : 
                      submission ? '✓ Already Submitted' : 'Submission Not Available'
                    ) : '📤 Submit Assignment'}
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default StudentAssignments;