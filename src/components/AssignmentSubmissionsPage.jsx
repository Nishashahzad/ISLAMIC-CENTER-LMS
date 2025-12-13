import React, { useState, useEffect } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import "./AssignmentSubmissionsPage.css";

const AssignmentSubmissionsPage = () => {
    const { assignmentId } = useParams();
    const navigate = useNavigate();
    const location = useLocation();

    const [assignment, setAssignment] = useState(null);
    const [submissions, setSubmissions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [gradingForm, setGradingForm] = useState({});
    const [teacherData, setTeacherData] = useState(null);
    const [stats, setStats] = useState({
        total: 0,
        submitted: 0,
        graded: 0,
        pending: 0,
        averageScore: 0
    });

    // Moved handleViewFile outside of useEffect
    const handleViewFile = (submission) => {
        if (!submission.file_path) {
            alert('No file attached to this submission');
            return;
        }
        
        // Navigate to file viewer page
        navigate(`/teacher/file-viewer/${submission.id}`, {
            state: {
                teacherData,
                submission,
                assignment,
                subject: assignment?.subject_name
            }
        });
    };

    // Get teacher data from location state or localStorage
    useEffect(() => {
        const fetchTeacherData = async () => {
            try {
                let teacherInfo = null;

                // Try to get from location state
                if (location.state && location.state.teacherData) {
                    teacherInfo = location.state.teacherData;
                } else {
                    // Try to get from localStorage
                    const storedUser = localStorage.getItem('user');
                    if (storedUser) {
                        const userData = JSON.parse(storedUser);
                        if (userData.role === 'teacher') {
                            teacherInfo = userData;
                        }
                    }
                }

                if (!teacherInfo) {
                    setError("Teacher data not found. Please log in again.");
                    return;
                }

                setTeacherData(teacherInfo);

                // Fetch assignment and submissions
                await fetchAssignmentData(teacherInfo);
                await fetchSubmissions(teacherInfo);

            } catch (err) {
                console.error("Error loading teacher data:", err);
                setError("Failed to load teacher information.");
                setLoading(false);
            }
        };

        const fetchAssignmentData = async (teacherInfo) => {
            try {
                const teacherId = teacherInfo?.userId || teacherInfo?.userid || teacherInfo?.id;

                const response = await fetch(
                    `http://localhost:8000/assignments/${assignmentId}/submissions?teacher_userId=${teacherId}`
                );

                const data = await response.json();

                console.log("Assignment data response:", data); // DEBUG

                if (data.success) {
                    setAssignment(data.assignment);

                    // Calculate statistics
                    if (data.submissions) {
                        const total = data.submissions.length;
                        const graded = data.submissions.filter(s => s.marks_obtained !== null).length;
                        const submitted = data.submissions.filter(s => s.status === 'submitted' || s.status === 'graded').length;
                        const pending = total - submitted;

                        // Calculate average score
                        const gradedSubmissions = data.submissions.filter(s => s.marks_obtained !== null);
                        const totalScore = gradedSubmissions.reduce((sum, s) => sum + (parseFloat(s.marks_obtained) || 0), 0);
                        const averageScore = gradedSubmissions.length > 0 ? totalScore / gradedSubmissions.length : 0;

                        setStats({
                            total,
                            submitted,
                            graded,
                            pending,
                            averageScore: averageScore.toFixed(1)
                        });
                    }
                } else {
                    console.error("Error in assignment data:", data); // DEBUG
                    setError(data.error || data.detail || 'Failed to load assignment data');
                }
            } catch (err) {
                console.error("Error fetching assignment:", err);
                setError("Failed to load assignment data.");
            }
        };

        const fetchSubmissions = async (teacherInfo) => {
            try {
                const teacherId = teacherInfo?.userId || teacherInfo?.userid || teacherInfo?.id;

                console.log("Fetching submissions for teacher:", teacherId);
                console.log("Assignment ID:", assignmentId);

                // OPTION 1: Use the debug endpoint (no auth needed)
                const response = await fetch(
                    `http://localhost:8000/debug/direct-submissions/${assignmentId}`
                );

                const data = await response.json();

                console.log("Submissions response:", data);

                if (data.success) {
                    setSubmissions(data.submissions || []);
                    setAssignment(data.assignment);

                    // Calculate statistics
                    if (data.submissions) {
                        const total = data.submissions.length;
                        const graded = data.submissions.filter(s => s.marks_obtained !== null).length;
                        const submitted = data.submissions.filter(s => s.status === 'submitted' || s.status === 'graded').length;
                        const pending = total - submitted;

                        // Calculate average score
                        const gradedSubmissions = data.submissions.filter(s => s.marks_obtained !== null);
                        const totalScore = gradedSubmissions.reduce((sum, s) => sum + (parseFloat(s.marks_obtained) || 0), 0);
                        const averageScore = gradedSubmissions.length > 0 ? totalScore / gradedSubmissions.length : 0;

                        setStats({
                            total,
                            submitted,
                            graded,
                            pending,
                            averageScore: averageScore.toFixed(1)
                        });
                    }
                } else {
                    console.error("Error in submissions:", data);
                    setError(data.error || data.detail || 'Failed to load submissions');
                }
            } catch (err) {
                console.error("Error fetching submissions:", err);
                setError("Failed to load submissions.");
            } finally {
                setLoading(false);
            }
        };

        fetchTeacherData();
    }, [assignmentId, location.state, navigate]);

    const handleGradeSubmission = async (submissionId, marks, feedback) => {
    if (!marks || marks < 0) {
        alert('Please enter valid marks');
        return;
    }

    try {
        const teacherId = teacherData?.userId || teacherData?.userid || teacherData?.id;
        
        console.log("Grading submission:", submissionId);
        console.log("Teacher ID:", teacherId);
        console.log("Marks:", marks);
        console.log("Feedback:", feedback);

        const response = await fetch(
            `http://localhost:8000/assignments/submissions/${submissionId}/grade?teacher_userId=${teacherId}`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    marks_obtained: parseFloat(marks),
                    feedback: feedback || '',
                    graded_by: teacherId
                })
            }
        );

        const data = await response.json();

        console.log("Grade submission response:", data);

        if (data.success) {
            alert('Grade submitted successfully!');
            
            // Refresh the page to show updated data
            window.location.reload();
            
        } else {
            // Show detailed error
            let errorMessage = 'Error submitting grade';
            if (data.error) {
                errorMessage += ': ' + data.error;
            }
            if (data.detail) {
                errorMessage += ': ' + data.detail;
            }
            if (data.debug) {
                console.error("Debug info:", data.debug);
            }
            alert(errorMessage);
        }
    } catch (error) {
        console.error('Error grading submission:', error);
        alert('Error submitting grade: ' + error.message);
    }
};
    const handleDownloadFile = (submission) => {
        if (!submission.file_path) {
            alert('No file attached to this submission');
            return;
        }

        const teacherId = teacherData?.userId || teacherData?.userid || teacherData?.id;
        window.open(
            `http://localhost:8000/assignments/submissions/${submission.id}/download?teacher_userId=${teacherId}`,
            '_blank'
        );
    };

    const formatDate = (dateString) => {
        if (!dateString) return 'N/A';

        try {
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', {
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

    const handleBack = () => {
        navigate(-1); // Go back to previous page
    };

    const handleUpdateGradingForm = (submissionId, field, value) => {
        setGradingForm(prev => ({
            ...prev,
            [submissionId]: {
                ...prev[submissionId],
                [field]: value
            }
        }));
    };

    const getStatusBadge = (submission) => {
        if (submission.marks_obtained !== null && submission.marks_obtained !== undefined) {
            return { label: 'Graded', className: 'graded' };
        } else if (submission.status === 'late') {
            return { label: 'Late', className: 'late' };
        } else {
            return { label: 'Submitted', className: 'submitted' };
        }
    };

    if (loading) {
        return (
            <div className="submissions-container">
                <div className="loading-overlay">
                    <div className="spinner"></div>
                    <p>Loading submissions...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="submissions-container">
                <div className="error-message">
                    <h2>⚠️ Error</h2>
                    <p>{error}</p>
                    <button onClick={handleBack} className="btn-primary">
                        Go Back
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="submissions-container">
            {/* Header */}
            <div className="submissions-header">
                <button onClick={handleBack} className="back-btn">
                    ← Back
                </button>
                <h1>📝 Assignment Submissions</h1>
                {assignment && (
                    <div className="assignment-info">
                        <h2>{assignment.title}</h2>
                        <div className="assignment-meta">
                            <span><strong>Subject:</strong> {assignment.subject_name}</span>
                            <span><strong>Due Date:</strong> {formatDate(assignment.due_date)}</span>
                            <span><strong>Total Marks:</strong> {assignment.total_marks || 'N/A'}</span>
                        </div>
                        <p className="assignment-description">{assignment.description}</p>
                    </div>
                )}
            </div>

            {/* Statistics */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-value">{stats.total}</div>
                    <div className="stat-label">Total Students</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value">{stats.submitted}</div>
                    <div className="stat-label">Submitted</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value">{stats.graded}</div>
                    <div className="stat-label">Graded</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value">{stats.pending}</div>
                    <div className="stat-label">Pending</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value">{stats.averageScore}%</div>
                    <div className="stat-label">Avg. Score</div>
                </div>
            </div>

            {/* Submissions List */}
            <div className="submissions-list">
                <h3>Student Submissions ({submissions.length})</h3>

                {submissions.length === 0 ? (
                    <div className="no-submissions">
                        <p>No submissions yet.</p>
                    </div>
                ) : (
                    <div className="submissions-table">
                        {submissions.map((submission) => {
                            const status = getStatusBadge(submission);
                            const formState = gradingForm[submission.id] || { marks_obtained: '', feedback: '' };

                            return (
                                <div key={submission.id} className="submission-card">
                                    <div className="submission-header">
                                        <div className="student-info">
                                            <h4>{submission.student_name || 'Unknown Student'}</h4>
                                            <p className="student-email">{submission.student_email || 'No email'}</p>
                                            <div className="submission-meta">
                                                <span>Submitted: {formatDate(submission.submission_date)}</span>
                                                {submission.hours_early !== undefined && (
                                                    <span className={`time-indicator ${submission.hours_early >= 0 ? 'early' : 'late'}`}>
                                                        {submission.hours_early >= 0 ?
                                                            `${submission.hours_early} hours early` :
                                                            `${Math.abs(submission.hours_early)} hours late`}
                                                    </span>
                                                )}
                                            </div>
                                        </div>

                                        <div className="submission-status">
                                            <span className={`status-badge ${status.className}`}>
                                                {status.label}
                                            </span>

                                            {submission.marks_obtained !== null ? (
                                                <div className="grade-display">
                                                    <span className="grade-score">
                                                        {submission.marks_obtained}/{assignment?.total_marks || 'N/A'}
                                                    </span>
                                                    <small>
                                                        Graded by: {submission.graded_by_name || 'Teacher'}
                                                        {submission.graded_date && ` on ${formatDate(submission.graded_date)}`}
                                                    </small>
                                                </div>
                                            ) : (
                                                <div className="grade-form">
                                                    <input
                                                        type="number"
                                                        placeholder="Marks"
                                                        value={formState.marks_obtained}
                                                        onChange={(e) => handleUpdateGradingForm(submission.id, 'marks_obtained', e.target.value)}
                                                        max={assignment?.total_marks || 100}
                                                        min="0"
                                                        step="0.5"
                                                        className="marks-input"
                                                    />
                                                    <textarea
                                                        placeholder="Feedback (optional)"
                                                        value={formState.feedback}
                                                        onChange={(e) => handleUpdateGradingForm(submission.id, 'feedback', e.target.value)}
                                                        className="feedback-input"
                                                        rows="2"
                                                    />
                                                    <button
                                                        onClick={() => handleGradeSubmission(
                                                            submission.id,
                                                            formState.marks_obtained,
                                                            formState.feedback
                                                        )}
                                                        className="grade-btn"
                                                        disabled={!formState.marks_obtained}
                                                    >
                                                        ✅ Grade
                                                    </button>
                                                </div>
                                            )}
                                        </div>
                                    </div>

                                    <div className="submission-content">
                                        {submission.submission_text && (
                                            <div className="submission-text">
                                                <strong>Answer:</strong>
                                                <p>{submission.submission_text}</p>
                                            </div>
                                        )}

                                       {submission.file_name && (
  <div className="submission-file">
    <strong>Attached File:</strong>
    <div className="file-actions">
      <button
        onClick={() => handleViewFile(submission)}
        className="view-file-btn"
        style={{
          background: '#4a6fa5',
          color: 'white',
          border: 'none',
          padding: '5px 10px',
          borderRadius: '4px',
          cursor: 'pointer',
          marginRight: '10px',
          display: 'inline-flex',
          alignItems: 'center',
          gap: '5px'
        }}
      >
        👁️ View File
      </button>
      <button
        onClick={() => handleDownloadFile(submission)}
        className="file-download-btn"
        style={{
          background: '#f8f9fa',
          border: '1px solid #e0e0e0',
          padding: '5px 10px',
          borderRadius: '4px',
          cursor: 'pointer',
          color: '#555',
          display: 'inline-flex',
          alignItems: 'center',
          gap: '5px'
        }}
      >
        📎 {submission.file_name}
      </button>
    </div>
  </div>
)}

                                        {submission.feedback && (
                                            <div className="teacher-feedback">
                                                <strong>Feedback:</strong>
                                                <p>{submission.feedback}</p>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>

            {/* Export Options */}
            <div className="export-section">
                <h3>Export Options</h3>
                <div className="export-buttons">
                    <button className="export-btn">
                        📊 Export Grades (CSV)
                    </button>
                    <button className="export-btn">
                        📋 Export All (PDF)
                    </button>
                    <button className="export-btn">
                        📧 Email All Students
                    </button>
                </div>
            </div>
        </div>
    );
};

export default AssignmentSubmissionsPage;