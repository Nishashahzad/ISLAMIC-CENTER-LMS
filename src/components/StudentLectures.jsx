import React, { useState, useEffect } from 'react';
import "./StudentCourses.css";
import { useLocation, useNavigate, useParams } from 'react-router-dom';

const StudentLectures = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { userId } = useParams();
  const { subject, teacher, studentData } = location.state || {};

  const [lectures, setLectures] = useState([]);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(null);
  const [viewing, setViewing] = useState(null);
  const [selectedLecture, setSelectedLecture] = useState(null);
  const [showViewer, setShowViewer] = useState(false);
  const [viewerError, setViewerError] = useState(null);

  useEffect(() => {
    if (subject && teacher) {
      fetchLectures();
    }
  }, [subject, teacher]);

  const fetchLectures = async () => {
    try {
      const response = await fetch(`http://localhost:8000/lectures/${teacher.userId}/${subject}`);
      const data = await response.json();

      if (data.success) {
        // For now, let's use basic file type detection without API calls
        const enhancedLectures = data.lectures.map(lecture => {
          const fileInfo = detectFileType(lecture);
          return {
            ...lecture,
            file_info: fileInfo,
            can_view: fileInfo.can_view
          };
        });
        setLectures(enhancedLectures);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error fetching lectures:', error);
      setLoading(false);
    }
  };

  // Simple client-side file type detection
  const detectFileType = (lecture) => {
    const fileName = lecture.file_name || '';
    const fileExtension = fileName.split('.').pop()?.toLowerCase();

    const viewableExtensions = [
      'pdf', 'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm',
      'mp3', 'wav', 'ogg', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'txt'
    ];

    const fileTypes = {
      'pdf': 'document',
      'mp4': 'video', 'avi': 'video', 'mov': 'video', 'wmv': 'video', 'flv': 'video', 'webm': 'video',
      'mp3': 'audio', 'wav': 'audio', 'ogg': 'audio',
      'jpg': 'image', 'jpeg': 'image', 'png': 'image', 'gif': 'image', 'bmp': 'image',
      'txt': 'document'
    };

    const canView = viewableExtensions.includes(fileExtension);
    const fileType = fileTypes[fileExtension] || 'unknown';

    return {
      extension: `.${fileExtension}`,
      type: fileType,
      can_view: canView,
      exists: true // Assume file exists for now
    };
  };

  const handleBack = () => {
    navigate(`/student-dashboard/${userId}/courses`);
  };

  const handleDownload = async (lecture) => {
    try {
      setDownloading(lecture.id);

      // First update the download count
      await fetch(`http://localhost:8000/lectures/${lecture.id}/download`, {
        method: 'POST'
      });

      // Then download the file
      const downloadUrl = `http://localhost:8000/download/lecture/${lecture.id}`;

      // Create a temporary anchor element to trigger download
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.setAttribute('download', lecture.file_name || `lecture_${lecture.id}`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // Refresh lectures to get updated download count
      fetchLectures();

    } catch (error) {
      console.error('Error downloading file:', error);
      alert('Failed to download file. Please try again.');
    } finally {
      setDownloading(null);
    }
  };

  const handleView = async (lecture) => {
    try {
      setViewing(lecture.id);
      setViewerError(null);

      console.log('Testing lecture file...', lecture.id);

      // First, test if the file is accessible
      const testResponse = await fetch(`http://localhost:8000/test/video/${lecture.id}`);
      const testData = await testResponse.json();

      console.log('File test result:', testData);

      if (!testData.success) {
        throw new Error(testData.error || 'Failed to access lecture file');
      }

      if (!testData.file_stats.exists) {
        throw new Error('Lecture file not found on server');
      }

      if (!testData.file_stats.readable) {
        throw new Error('File exists but is not readable');
      }

      if (testData.file_stats.size === 0) {
        throw new Error('File is empty (0 bytes)');
      }

      console.log('File stats:', testData.file_stats);
      console.log('View URL:', testData.view_url);

      if (lecture.can_view) {
        setSelectedLecture(lecture);
        setShowViewer(true);
      } else {
        await handleDownload(lecture);
      }

    } catch (error) {
      console.error('Error viewing lecture:', error);
      setViewerError(error.message);

      // Show detailed error
      alert(`Cannot view lecture: ${error.message}\n\nFile may be corrupted or not accessible.`);

      // Fall back to download
      await handleDownload(lecture);
    } finally {
      setViewing(null);
    }
  };

  const closeViewer = () => {
    setShowViewer(false);
    setSelectedLecture(null);
    setViewerError(null);
    // Refresh to update view count
    fetchLectures();
  };

  // Format file size
  const formatFileSize = (bytes) => {
    if (!bytes) return 'N/A';
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  // Get file type icon
  const getFileIcon = (lecture) => {
    if (!lecture.file_info?.extension) return '📄';

    const extension = lecture.file_info.extension;
    const icons = {
      '.pdf': '📕',
      '.mp4': '🎥',
      '.avi': '🎬',
      '.mov': '🎬',
      '.mp3': '🎵',
      '.wav': '🎵',
      '.jpg': '🖼️',
      '.jpeg': '🖼️',
      '.png': '🖼️',
      '.doc': '📄',
      '.docx': '📄',
      '.ppt': '📊',
      '.pptx': '📊',
      '.xls': '📈',
      '.xlsx': '📈',
      '.txt': '📝'
    };

    return icons[extension] || '📄';
  };

  if (loading) return <div className="loading">Loading lectures...</div>;

  return (
    <div className="student-lectures-container">
      {/* Lecture Viewer Modal */}
      {showViewer && selectedLecture && (
        <div className="lecture-viewer-overlay">
          <div className="lecture-viewer-modal">
            <div className="viewer-header">
              <h3>{selectedLecture.title}</h3>
              <button className="close-viewer" onClick={closeViewer}>✕</button>
            </div>
            <div className="viewer-content">
              {viewerError ? (
                <div className="viewer-error">
                  <h4>❌ Error Loading Lecture</h4>
                  <p>{viewerError}</p>
                  <button
                    onClick={() => handleDownload(selectedLecture)}
                    className="download-in-viewer"
                  >
                    📥 Download Instead
                  </button>
                </div>
              ) : (
                <>
                  {selectedLecture.file_info?.type === 'video' && (
                    <div className="video-container">
                      <video
                        controls
                        autoPlay
                        style={{ width: '100%', maxHeight: '70vh' }}
                        onError={(e) => {
                          console.error('Video error:', e);
                          setViewerError('Failed to load video. The file may be corrupted or in an unsupported format.');
                        }}
                        onLoadStart={() => setViewerError(null)}
                      >
                        <source
                          src={`http://localhost:8000/stream/lecture/${selectedLecture.id}`}
                          type="video/mp4"
                        />
                        Your browser does not support the video tag.
                      </video>

                      {viewerError && (
                        <div className="video-fallback-options">
                          <p>Video playback failed. Try these options:</p>
                          <div className="fallback-buttons">
                            <button
                              onClick={() => window.open(`http://localhost:8000/view/lecture/${selectedLecture.id}`, '_blank')}
                              className="secondary-btn"
                            >
                              Open in Default Player
                            </button>
                            <button
                              onClick={() => handleDownload(selectedLecture)}
                              className="secondary-btn"
                            >
                              Download Instead
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {selectedLecture.file_info?.type === 'audio' && (
                    <audio controls autoPlay style={{ width: '100%' }}>
                      <source
                        src={`http://localhost:8000/view/lecture/${selectedLecture.id}`}
                        type="audio/mpeg"
                      />
                      Your browser does not support the audio tag.
                    </audio>
                  )}

                  {selectedLecture.file_info?.type === 'image' && (
                    <img
                      src={`http://localhost:8000/view/lecture/${selectedLecture.id}`}
                      alt={selectedLecture.title}
                      style={{ maxWidth: '100%', maxHeight: '70vh' }}
                      onError={(e) => {
                        setViewerError('Failed to load image. The file may be corrupted.');
                      }}
                    />
                  )}

                  {(selectedLecture.file_info?.type === 'document' || selectedLecture.file_info?.extension === '.pdf') && (
                    <iframe
                      src={`http://localhost:8000/view/lecture/${selectedLecture.id}`}
                      style={{ width: '100%', height: '70vh', border: 'none' }}
                      title={selectedLecture.title}
                      onError={(e) => {
                        setViewerError('Failed to load document. The file may be corrupted.');
                      }}
                    />
                  )}

                  {selectedLecture.file_info?.type === 'unknown' && (
                    <div className="unsupported-format">
                      <p>📄 This file type is best viewed by downloading.</p>
                      <button
                        onClick={() => handleDownload(selectedLecture)}
                        className="download-in-viewer"
                      >
                        📥 Download File
                      </button>
                    </div>
                  )}
                </>
              )}
            </div>
            <div className="viewer-footer">
              <p><strong>File:</strong> {selectedLecture.file_name}</p>
              <div className="viewer-actions">
                <button
                  onClick={() => handleDownload(selectedLecture)}
                  className="secondary-btn"
                >
                  📥 Download
                </button>
                <button onClick={closeViewer} className="primary-btn">
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Lectures List */}
      <div className="student-lectures-header">
        <button onClick={handleBack} className="student-lectures-back-btn">
          ← Back to Courses
        </button>
        <h1 className="student-lectures-title">📚 Lectures - {subject}</h1>
      </div>

      <div className="student-lectures-content-section">
        <div className="student-lectures-info-card">
          <p><strong>Teacher:</strong> {teacher?.fullName || 'Not assigned'}</p>
          <p><strong>Total Lectures:</strong> {lectures.length}</p>
        </div>

        {lectures.length === 0 ? (
          <div className="no-data">No lectures available for this subject.</div>
        ) : (
          <div className="student-lectures-list">
            {lectures.map((lecture) => (
              <div key={lecture.id} className="student-lecture-card">
                <div className="lecture-icon">
                  {getFileIcon(lecture)}
                </div>

                <div className="student-lecture-info">
                  <h3>{lecture.title}</h3>
                  <p>{lecture.description}</p>
                  <div className="student-lecture-meta">
                    <span>Uploaded: {new Date(lecture.upload_date).toLocaleDateString()}</span>
                    <span>Downloads: {lecture.downloads || 0}</span>
                    {lecture.file_size && (
                      <span>Size: {formatFileSize(lecture.file_size)}</span>
                    )}
                  </div>
                  {lecture.file_name && (
                    <div className="student-lecture-filename">
                      File: {lecture.file_name}
                      {lecture.file_info?.type && (
                        <span className="file-type-badge">
                          {lecture.file_info.type.toUpperCase()}
                        </span>
                      )}
                    </div>
                  )}
                </div>

                <div className="lecture-actions">
                  <button
                    onClick={() => handleView(lecture)}
                    className="student-lecture-view-btn"
                    disabled={viewing === lecture.id}
                    title={lecture.can_view ? "View in browser" : "View not supported - will download instead"}
                  >
                    {viewing === lecture.id ? '⏳ Opening...' : '👁️ View'}
                  </button>

                  <button
                    onClick={() => handleDownload(lecture)}
                    className="student-lecture-download-btn"
                    disabled={downloading === lecture.id}
                  >
                    {downloading === lecture.id ? '⏳ Downloading...' : '📥 Download'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default StudentLectures;