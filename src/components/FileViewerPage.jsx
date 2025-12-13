import React, { useState, useEffect } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import "./FileViewerPage.css";

const FileViewerPage = () => {
  const { submissionId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  
  const [submission, setSubmission] = useState(null);
  const [fileUrl, setFileUrl] = useState("");
  const [fileType, setFileType] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [teacherData, setTeacherData] = useState(null);
  const [fileContent, setFileContent] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Get teacher data
        let teacherInfo = null;
        
        if (location.state && location.state.teacherData) {
          teacherInfo = location.state.teacherData;
        } else {
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
          setLoading(false);
          return;
        }
        
        setTeacherData(teacherInfo);
        
        // Fetch submission details
        await fetchSubmissionDetails(teacherInfo);
        
      } catch (err) {
        console.error("Error loading data:", err);
        setError("Failed to load file information.");
        setLoading(false);
      }
    };

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

    const fetchSubmissionDetails = async (teacherInfo) => {
  try {
    const teacherId = teacherInfo?.userId || teacherInfo?.userid || teacherInfo?.id;
    
    // Use the new endpoint
    const response = await fetch(
      `http://localhost:8000/submission/${submissionId}?teacher_userId=${teacherId}`
    );
    
    const data = await response.json();
    
    if (data.success) {
      setSubmission(data.submission);
      
      // Determine file type and set URLs
      const fileName = data.submission.file_name || "";
      const filePath = data.submission.file_path || "";
      const extension = fileName.split('.').pop().toLowerCase();
      
      // Set file type
      if (['pdf'].includes(extension)) {
        setFileType('pdf');
      } else if (['jpg', 'jpeg', 'png', 'gif', 'bmp'].includes(extension)) {
        setFileType('image');
      } else if (['txt', 'text'].includes(extension)) {
        setFileType('text');
        await fetchTextFile(data.submission, teacherId);
      } else if (['doc', 'docx'].includes(extension)) {
        setFileType('document');
      } else if (['mp4', 'avi', 'mov', 'wmv'].includes(extension)) {
        setFileType('video');
      } else {
        setFileType('other');
      }
      
      // Set download URL
      if (filePath) {
        const downloadUrl = `http://localhost:8000/assignments/submissions/${submissionId}/download?teacher_userId=${teacherId}`;
        setFileUrl(downloadUrl);
      }
    } else {
      setError(data.error || "Failed to load submission details");
    }
  } catch (err) {
    console.error("Error fetching submission:", err);
    setError("Failed to load submission details.");
  } finally {
    setLoading(false);
  }
};

    const fetchTextFile = async (submission, teacherId) => {
      try {
        const response = await fetch(
          `http://localhost:8000/assignments/submissions/${submissionId}/download?teacher_userId=${teacherId}`
        );
        
        if (response.ok) {
          const text = await response.text();
          setFileContent(text);
        }
      } catch (err) {
        console.error("Error fetching text file:", err);
        // Continue without text content
      }
    };

    fetchData();
  }, [submissionId, location.state]);

  const handleBack = () => {
    navigate(-1); // Go back to previous page
  };

  const handleDownload = () => {
    if (fileUrl) {
      window.open(fileUrl, '_blank');
    }
  };

  const getFileIcon = () => {
    const fileName = submission?.file_name || "";
    const extension = fileName.split('.').pop().toLowerCase();
    
    const iconMap = {
      'pdf': '📕',
      'jpg': '🖼️',
      'jpeg': '🖼️',
      'png': '🖼️',
      'gif': '🖼️',
      'txt': '📄',
      'text': '📄',
      'doc': '📝',
      'docx': '📝',
      'mp4': '🎬',
      'avi': '🎬',
      'mov': '🎬',
      'wmv': '🎬',
      'default': '📎'
    };
    
    return iconMap[extension] || iconMap.default;
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

  const renderFileContent = () => {
    if (!submission || !submission.file_path) {
      return <div className="no-file">No file attached to this submission</div>;
    }
    
    switch (fileType) {
      case 'pdf':
        return (
          <div className="pdf-viewer">
            <iframe
              src={fileUrl}
              title={submission.file_name}
              className="pdf-frame"
            />
            <div className="pdf-controls">
              <button onClick={handleDownload} className="download-btn">
                ⬇️ Download PDF
              </button>
              <a href={fileUrl} target="_blank" rel="noopener noreferrer" className="open-new-btn">
                ↗️ Open in New Tab
              </a>
            </div>
          </div>
        );
        
      case 'image':
        return (
          <div className="image-viewer">
            <img
              src={fileUrl}
              alt={submission.file_name}
              className="image-preview"
              onError={(e) => {
                e.target.onerror = null;
                e.target.src = "https://via.placeholder.com/800x600?text=Image+Not+Available";
              }}
            />
            <div className="image-controls">
              <button onClick={handleDownload} className="download-btn">
                ⬇️ Download Image
              </button>
            </div>
          </div>
        );
        
      case 'text':
        return (
          <div className="text-viewer">
            <div className="text-header">
              <h4>Text Content:</h4>
              <button onClick={handleDownload} className="download-btn">
                ⬇️ Download Text File
              </button>
            </div>
            <pre className="text-content">
              {fileContent || "Loading text content..."}
            </pre>
          </div>
        );
        
      case 'video':
        return (
          <div className="video-viewer">
            <video
              controls
              className="video-player"
              src={fileUrl}
              title={submission.file_name}
            >
              Your browser does not support the video tag.
            </video>
            <div className="video-controls">
              <button onClick={handleDownload} className="download-btn">
                ⬇️ Download Video
              </button>
            </div>
          </div>
        );
        
      default:
        return (
          <div className="generic-file-viewer">
            <div className="file-icon-large">
              {getFileIcon()}
              <span className="file-name">{submission.file_name}</span>
            </div>
            <p className="file-info">
              This file type cannot be previewed directly.
            </p>
            <button onClick={handleDownload} className="download-btn-large">
              ⬇️ Download File
            </button>
            <p className="file-hint">
              You can download the file and open it with appropriate software.
            </p>
          </div>
        );
    }
  };

  if (loading) {
    return (
      <div className="file-viewer-container">
        <div className="loading-overlay">
          <div className="spinner"></div>
          <p>Loading file...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="file-viewer-container">
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
    <div className="file-viewer-container">
      {/* Header */}
      <div className="file-viewer-header">
        <button onClick={handleBack} className="back-btn">
          ← Back to Submissions
        </button>
        <h1>
          {getFileIcon()} File Viewer
        </h1>
      </div>

      {/* Submission Info */}
      {submission && (
        <div className="submission-info-card">
          <div className="submission-header">
            <h3>Submission Details</h3>
            <div className="submission-meta">
              <span><strong>Student:</strong> {submission.student_name || 'Unknown'}</span>
              <span><strong>Submitted:</strong> {formatDate(submission.submission_date)}</span>
              <span><strong>Status:</strong> 
                <span className={`status-badge ${submission.status || 'submitted'}`}>
                  {submission.status || 'submitted'}
                </span>
              </span>
            </div>
          </div>
          
          <div className="file-details">
            <div className="file-icon">
              {getFileIcon()}
            </div>
            <div className="file-info">
              <h4>{submission.file_name || 'Unnamed File'}</h4>
              <p className="file-path">{submission.file_path || 'No file path'}</p>
              <div className="file-actions">
                <button onClick={handleDownload} className="action-btn">
                  ⬇️ Download
                </button>
                <a 
                  href={fileUrl} 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="action-btn"
                >
                  ↗️ Open in New Tab
                </a>
              </div>
            </div>
          </div>
          
          {submission.submission_text && (
            <div className="submission-text">
              <h4>Student's Comments:</h4>
              <p>{submission.submission_text}</p>
            </div>
          )}
        </div>
      )}

      {/* File Content */}
      <div className="file-content-section">
        <h3>File Preview</h3>
        <div className="file-preview-container">
          {renderFileContent()}
        </div>
      </div>

      {/* File Information */}
      <div className="file-info-section">
        <h3>File Information</h3>
        <div className="info-grid">
          <div className="info-item">
            <strong>File Name:</strong>
            <span>{submission?.file_name || 'N/A'}</span>
          </div>
          <div className="info-item">
            <strong>File Type:</strong>
            <span>{fileType.toUpperCase() || 'Unknown'}</span>
          </div>
          <div className="info-item">
            <strong>Submitted:</strong>
            <span>{formatDate(submission?.submission_date)}</span>
          </div>
          <div className="info-item">
            <strong>Student:</strong>
            <span>{submission?.student_name || 'Unknown'}</span>
          </div>
          <div className="info-item">
            <strong>Student Email:</strong>
            <span>{submission?.student_email || 'N/A'}</span>
          </div>
          <div className="info-item">
            <strong>Status:</strong>
            <span className={`status-badge ${submission?.status || 'submitted'}`}>
              {submission?.status || 'submitted'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FileViewerPage;