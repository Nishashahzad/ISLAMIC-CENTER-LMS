import React, { useState, useEffect } from "react";
import { useOutletContext, useNavigate } from "react-router-dom";
import "./TeacherCourses.css";

const TeacherCourses = () => {
  const outletContext = useOutletContext();
  const navigate = useNavigate();
  const [teacherData, setTeacherData] = useState(null);
  const [subjects, setSubjects] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState(null);
  const [activeTab, setActiveTab] = useState("lectures");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Real data states
  const [lectures, setLectures] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [quizzes, setQuizzes] = useState([]);
  const [materials, setMaterials] = useState([]);

  // Form states
  const [lectureForm, setLectureForm] = useState({ title: "", description: "", file: null });
  const [assignmentForm, setAssignmentForm] = useState({
    title: "",
    description: "",
    startDate: "",
    dueDate: "",
    file: null
  });
  const [notificationForm, setNotificationForm] = useState({ title: "", message: "", priority: "medium" });
  const [quizForm, setQuizForm] = useState({
    title: "",
    description: "",
    startDate: "",
    endDate: "",
    totalMarks: 100,
    questionsCount: 10,
    durationMinutes: 30
  });
  const [materialForm, setMaterialForm] = useState({ 
    title: "", 
    description: "", 
    materialType: "other", 
    file: null 
  });

  // Get teacher data
  useEffect(() => {
    const fetchTeacherData = async () => {
      try {
        setLoading(true);

        let teacherInfo = null;

        if (outletContext) {
          teacherInfo = outletContext;
        }

        if (!teacherInfo) {
          const storedUser = localStorage.getItem('user');
          if (storedUser) {
            teacherInfo = JSON.parse(storedUser);
          }
        }

        if (!teacherInfo) {
          setError("No teacher data found. Please log in.");
          setLoading(false);
          return;
        }

        if (teacherInfo.role !== 'teacher') {
          setError("Access denied. Teachers only.");
          setLoading(false);
          return;
        }

        setTeacherData(teacherInfo);
        await fetchTeacherSubjects(teacherInfo);

      } catch (err) {
        console.error("Error loading teacher data:", err);
        setError("Failed to load teacher information.");
        setLoading(false);
      }
    };

    const fetchTeacherSubjects = async (teacherInfo) => {
      try {
        const teacherId = teacherInfo?.userId || teacherInfo?.userid || teacherInfo?.id;

        if (!teacherId) {
          setError("Teacher ID not found.");
          setLoading(false);
          return;
        }

        const response = await fetch(`http://localhost:8000/teacher_subjects/${teacherId}`);

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (!data.success) {
          throw new Error(data.detail || "API request failed");
        }

        const matchedSubjects = data.matched_subjects || [];
        setSubjects(matchedSubjects);

        if (matchedSubjects.length === 0) {
          setError("No subjects assigned to your profile.");
        }

      } catch (err) {
        console.error("Error fetching teacher subjects:", err);
        setError(`Failed to load courses: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };

    fetchTeacherData();
  }, [outletContext]);

  // Fetch real data when subject changes
  useEffect(() => {
    if (selectedSubject && teacherData) {
      fetchSubjectData();
    }
  }, [selectedSubject, activeTab]);

  const fetchSubjectData = async () => {
    if (!teacherData || !selectedSubject) {
      console.log("No teacher data or selected subject");
      return;
    }

    const teacherId = teacherData?.userId || teacherData?.userid || teacherData?.id;

    try {
      switch (activeTab) {
        case 'lectures':
          const lecturesResponse = await fetch(`http://localhost:8000/lectures/${teacherId}/${selectedSubject}`);
          if (!lecturesResponse.ok) throw new Error('Failed to fetch lectures');
          const lecturesData = await lecturesResponse.json();
          if (lecturesData.success) setLectures(lecturesData.lectures || []);
          break;

        case 'assignments':
          const assignmentsResponse = await fetch(`http://localhost:8000/assignments/${teacherId}/${selectedSubject}`);
          if (!assignmentsResponse.ok) throw new Error('Failed to fetch assignments');
          const assignmentsData = await assignmentsResponse.json();
          if (assignmentsData.success) setAssignments(assignmentsData.assignments || []);
          break;

        case 'notifications':
          const notificationsResponse = await fetch(`http://localhost:8000/notifications/${teacherId}/${selectedSubject}`);
          if (!notificationsResponse.ok) throw new Error('Failed to fetch notifications');
          const notificationsData = await notificationsResponse.json();
          if (notificationsData.success) setNotifications(notificationsData.notifications || []);
          break;

        case 'quizzes':
          const quizzesResponse = await fetch(`http://localhost:8000/quizzes/${teacherId}/${selectedSubject}`);
          if (!quizzesResponse.ok) throw new Error('Failed to fetch quizzes');
          const quizzesData = await quizzesResponse.json();
          if (quizzesData.success) setQuizzes(quizzesData.quizzes || []);
          break;

        case 'materials':
          const materialsResponse = await fetch(`http://localhost:8000/materials/${teacherId}/${selectedSubject}`);
          if (!materialsResponse.ok) throw new Error('Failed to fetch materials');
          const materialsData = await materialsResponse.json();
          if (materialsData.success) setMaterials(materialsData.materials || []);
          break;
      }
    } catch (err) {
      console.error(`Error fetching ${activeTab}:`, err);
      // Set empty arrays on error
      switch (activeTab) {
        case 'lectures': setLectures([]); break;
        case 'assignments': setAssignments([]); break;
        case 'notifications': setNotifications([]); break;
        case 'quizzes': setQuizzes([]); break;
        case 'materials': setMaterials([]); break;
      }
    }
  };

  // Handle file uploads
  const handleFileUpload = (e, formType) => {
    const file = e.target.files[0];
    if (file) {
      if (formType === 'lecture') {
        setLectureForm({ ...lectureForm, file });
      } else if (formType === 'assignment') {
        setAssignmentForm({ ...assignmentForm, file });
      } else if (formType === 'material') {
        setMaterialForm({ ...materialForm, file });
      }
    }
  };

  // Create lecture with real API
  const handleLectureSubmit = async (e) => {
    e.preventDefault();
    if (!teacherData || !selectedSubject) return;

    const teacherId = teacherData?.userId || teacherData?.userid || teacherData?.id;
    const formData = new FormData();

    formData.append('teacher_id', teacherId);
    formData.append('subject_name', selectedSubject);
    formData.append('title', lectureForm.title);
    formData.append('description', lectureForm.description);
    if (lectureForm.file) {
      formData.append('file', lectureForm.file);
    }

    try {
      const response = await fetch('http://localhost:8000/lectures', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (result.success) {
        alert("Lecture uploaded successfully!");
        setLectureForm({ title: "", description: "", file: null });
        fetchSubjectData();
      } else {
        alert("Error uploading lecture: " + result.detail);
      }
    } catch (err) {
      alert("Error uploading lecture: " + err.message);
    }
  };

  // Create assignment with real API
  const handleAssignmentSubmit = async (e) => {
    e.preventDefault();
    if (!teacherData || !selectedSubject) return;

    const teacherId = teacherData?.userId || teacherData?.userid || teacherData?.id;
    const formData = new FormData();

    formData.append('teacher_id', teacherId);
    formData.append('subject_name', selectedSubject);
    formData.append('title', assignmentForm.title);
    formData.append('description', assignmentForm.description);
    formData.append('start_date', assignmentForm.startDate);
    formData.append('due_date', assignmentForm.dueDate);
    if (assignmentForm.file) {
      formData.append('file', assignmentForm.file);
    }

    try {
      const response = await fetch('http://localhost:8000/assignments', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (result.success) {
        alert("Assignment created successfully!");
        setAssignmentForm({ title: "", description: "", startDate: "", dueDate: "", file: null });
        fetchSubjectData();
      } else {
        alert("Error creating assignment: " + result.detail);
      }
    } catch (err) {
      alert("Error creating assignment: " + err.message);
    }
  };

  // Create notification with real API
  const handleNotificationSubmit = async (e) => {
    e.preventDefault();
    if (!teacherData || !selectedSubject) return;

    const teacherId = teacherData?.userId;
    const formData = new FormData();
    formData.append('teacher_id', teacherId);
    formData.append('subject_name', selectedSubject);
    formData.append('title', notificationForm.title);
    formData.append('message', notificationForm.message);
    formData.append('priority', notificationForm.priority);

    try {
      const response = await fetch('http://localhost:8000/notifications', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (result.success) {
        alert("Notification sent successfully!");
        setNotificationForm({ title: "", message: "", priority: "medium" });
        fetchSubjectData();
      } else {
        alert("Error sending notification: " + result.detail);
      }
    } catch (err) {
      alert("Error sending notification: " + err.message);
    }
  };

  // Create quiz with real API
  const handleQuizSubmit = async (e) => {
    e.preventDefault();
    if (!teacherData || !selectedSubject) return;

    const teacherId = teacherData?.userId;
    const formData = new FormData();
    formData.append('teacher_id', teacherId);
    formData.append('subject_name', selectedSubject);
    formData.append('title', quizForm.title);
    formData.append('description', quizForm.description);
    formData.append('start_date', quizForm.startDate);
    formData.append('end_date', quizForm.endDate);
    formData.append('total_marks', quizForm.totalMarks.toString());
    formData.append('questions_count', quizForm.questionsCount.toString());
    formData.append('duration_minutes', quizForm.durationMinutes.toString());

    try {
      const response = await fetch('http://localhost:8000/quizzes', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (result.success) {
        alert("Quiz created successfully!");
        setQuizForm({
          title: "",
          description: "",
          startDate: "",
          endDate: "",
          totalMarks: 100,
          questionsCount: 10,
          durationMinutes: 30
        });
        fetchSubjectData();
      } else {
        alert("Error creating quiz: " + result.detail);
      }
    } catch (err) {
      alert("Error creating quiz: " + err.message);
    }
  };

  // Create material with real API
  const handleMaterialSubmit = async (e) => {
    e.preventDefault();
    if (!teacherData || !selectedSubject) return;

    const teacherId = teacherData?.userId || teacherData?.userid || teacherData?.id;
    const formData = new FormData();

    formData.append('teacher_id', teacherId);
    formData.append('subject_name', selectedSubject);
    formData.append('title', materialForm.title);
    formData.append('description', materialForm.description);
    formData.append('material_type', materialForm.materialType);
    if (materialForm.file) {
      formData.append('file', materialForm.file);
    }

    try {
      const response = await fetch('http://localhost:8000/materials', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (result.success) {
        alert("Material uploaded successfully!");
        setMaterialForm({ title: "", description: "", materialType: "other", file: null });
        fetchSubjectData();
      } else {
        alert("Error uploading material: " + result.detail);
      }
    } catch (err) {
      alert("Error uploading material: " + err.message);
    }
  };

  // Delete lecture
  const deleteLecture = async (lectureId) => {
    if (window.confirm("Are you sure you want to delete this lecture?")) {
      try {
        const response = await fetch(`http://localhost:8000/lectures/${lectureId}`, {
          method: 'DELETE',
        });

        const result = await response.json();

        if (result.success) {
          alert("Lecture deleted successfully!");
          fetchSubjectData();
        } else {
          alert("Error deleting lecture: " + result.detail);
        }
      } catch (err) {
        alert("Error deleting lecture: " + err.message);
      }
    }
  };

  // Delete material
  const deleteMaterial = async (materialId) => {
    if (window.confirm("Are you sure you want to delete this material?")) {
      try {
        const response = await fetch(`http://localhost:8000/materials/${materialId}`, {
          method: 'DELETE',
        });

        const result = await response.json();

        if (result.success) {
          alert("Material deleted successfully!");
          fetchSubjectData();
        } else {
          alert("Error deleting material: " + result.detail);
        }
      } catch (err) {
        alert("Error deleting material: " + err.message);
      }
    }
  };

  // Format date
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const handleRetry = () => {
    setLoading(true);
    setError(null);
    window.location.reload();
  };

  if (loading) {
    return (
      <div className="teacher-courses-container">
        <div className="loading-spinner">Loading your courses...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="teacher-courses-container">
        <div className="error-message">
          <h2>⚠️ Unable to Load Courses</h2>
          <p>{error}</p>
          <button onClick={handleRetry} className="btn-primary">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="teacher-courses-container">
      <div className="teacher-header">
        <h1>👨‍🏫 Teacher Dashboard</h1>
        {teacherData && (
          <div className="teacher-info">
            <div className="info-card">
              <strong>Name:</strong> {teacherData.fullName || "Teacher"}
            </div>
            <div className="info-card">
              <strong>Subject:</strong>
              {subjects.length > 0
                ? subjects.join(', ')
                : "Not assigned"
              }
            </div>
            <div className="info-card">
              <strong>User ID:</strong> {teacherData.userId || teacherData.userid || "N/A"}
            </div>
          </div>
        )}
      </div>

      {/* Subject Selection */}
      <div className="subject-selection">
        <h2>Select Subject to Manage</h2>
        {subjects.length === 0 ? (
          <div className="no-subjects">
            <p>No subjects available for your profile.</p>
            <p>Please contact administration to assign subjects to your account.</p>
          </div>
        ) : (
          <div className="subjects-grid">
            {subjects.map((subject, index) => (
              <div
                key={index}
                className={`subject-card ${selectedSubject === subject ? 'selected' : ''}`}
                onClick={() => setSelectedSubject(subject)}
              >
                <h3>{subject}</h3>
                <p>Click to manage content</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {selectedSubject && (
        <div className="course-management">
          <h2>Managing: {selectedSubject}</h2>

          {/* Tabs */}
          <div className="tabs">
            <button className={`tab ${activeTab === 'lectures' ? 'active' : ''}`} onClick={() => setActiveTab('lectures')}>
              📚 Lectures
            </button>
            <button className={`tab ${activeTab === 'assignments' ? 'active' : ''}`} onClick={() => setActiveTab('assignments')}>
              📝 Assignments
            </button>
            <button className={`tab ${activeTab === 'notifications' ? 'active' : ''}`} onClick={() => setActiveTab('notifications')}>
              🔔 Notifications
            </button>
            <button className={`tab ${activeTab === 'quizzes' ? 'active' : ''}`} onClick={() => setActiveTab('quizzes')}>
              🧩 Quizzes
            </button>
            <button className={`tab ${activeTab === 'materials' ? 'active' : ''}`} onClick={() => setActiveTab('materials')}>
              📦 Materials
            </button>
          </div>

          {/* Tab Content */}
          <div className="tab-content">

            {/* Lectures Tab */}
            {activeTab === 'lectures' && (
              <div className="tab-panel">
                <div className="form-section">
                  <h3>Upload New Lecture</h3>
                  <form onSubmit={handleLectureSubmit} className="upload-form">
                    <input type="text" placeholder="Lecture Title" value={lectureForm.title} onChange={(e) => setLectureForm({ ...lectureForm, title: e.target.value })} required />
                    <textarea placeholder="Lecture Description" value={lectureForm.description} onChange={(e) => setLectureForm({ ...lectureForm, description: e.target.value })} />
                    <input type="file" onChange={(e) => handleFileUpload(e, 'lecture')} accept=".pdf,.doc,.docx,.ppt,.pptx" />
                    <button type="submit" className="btn-primary">Upload Lecture</button>
                  </form>
                </div>

                <div className="content-list">
                  <h3>Uploaded Lectures</h3>
                  {lectures.length === 0 ? (
                    <p className="no-content">No lectures uploaded yet.</p>
                  ) : (
                    lectures.map(lecture => (
                      <div key={lecture.id} className="content-item">
                        <div className="content-info">
                          <h4>{lecture.title}</h4>
                          <p>{lecture.description}</p>
                          <small>Uploaded: {formatDate(lecture.upload_date)} • Downloads: {lecture.downloads}</small>
                          {lecture.file_name && <small>File: {lecture.file_name}</small>}
                        </div>
                        <div className="content-actions">
                          <button className="btn-delete" onClick={() => deleteLecture(lecture.id)}>
                            🗑️ Delete
                          </button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}

            {/* Assignments Tab */}
            {activeTab === 'assignments' && (
              <div className="tab-panel">
                <div className="form-section">
                  <h3>Create New Assignment</h3>
                  <form onSubmit={handleAssignmentSubmit} className="upload-form">
                    <input type="text" placeholder="Assignment Title" value={assignmentForm.title} onChange={(e) => setAssignmentForm({ ...assignmentForm, title: e.target.value })} required />
                    <textarea placeholder="Assignment Description" value={assignmentForm.description} onChange={(e) => setAssignmentForm({ ...assignmentForm, description: e.target.value })} />
                    <div className="form-row">
                      <input type="date" placeholder="Start Date" value={assignmentForm.startDate} onChange={(e) => setAssignmentForm({ ...assignmentForm, startDate: e.target.value })} required />
                      <input type="date" placeholder="Due Date" value={assignmentForm.dueDate} onChange={(e) => setAssignmentForm({ ...assignmentForm, dueDate: e.target.value })} required />
                    </div>
                    <input type="file" onChange={(e) => handleFileUpload(e, 'assignment')} accept=".pdf,.doc,.docx" />
                    <button type="submit" className="btn-primary">Create Assignment</button>
                  </form>
                </div>

                <div className="content-list">
                  <h3>Active Assignments</h3>
                  {assignments.length === 0 ? (
                    <p className="no-content">No assignments created yet.</p>
                  ) : (
                    assignments.map(assignment => (
                      <div key={assignment.id} className="content-item">
                        <div className="content-info">
                          <h4>{assignment.title}</h4>
                          <p>{assignment.description}</p>
                          <small>Start: {formatDate(assignment.start_date)} • Due: {formatDate(assignment.due_date)}</small>
                          <small>Submissions: {assignment.submissions}/{assignment.total_students}</small>
                          {assignment.file_name && <small>File: {assignment.file_name}</small>}
                        </div>
                        <div className="content-actions">
                          <button className="btn-view">👁️ View Submissions</button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}

            {/* Notifications Tab */}
            {activeTab === 'notifications' && (
              <div className="tab-panel">
                <div className="form-section">
                  <h3>Send Notification</h3>
                  <form onSubmit={handleNotificationSubmit} className="upload-form">
                    <input type="text" placeholder="Notification Title" value={notificationForm.title} onChange={(e) => setNotificationForm({ ...notificationForm, title: e.target.value })} required />
                    <textarea placeholder="Notification Message" value={notificationForm.message} onChange={(e) => setNotificationForm({ ...notificationForm, message: e.target.value })} required />
                    <select value={notificationForm.priority} onChange={(e) => setNotificationForm({ ...notificationForm, priority: e.target.value })}>
                      <option value="low">Low Priority</option>
                      <option value="medium">Medium Priority</option>
                      <option value="high">High Priority</option>
                    </select>
                    <button type="submit" className="btn-primary">Send Notification</button>
                  </form>
                </div>

                <div className="content-list">
                  <h3>Sent Notifications</h3>
                  {notifications.map(notification => (
                    <div key={notification.id} className={`notification-item ${notification.priority}`}>
                      <div className="content-info">
                        <h4>{notification.title}</h4>
                        <p>{notification.message}</p>
                        <small>Sent: {formatDate(notification.created_date)} • Priority: {notification.priority}</small>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Quizzes Tab */}
            {activeTab === 'quizzes' && (
              <div className="tab-panel">
                <div className="form-section">
                  <h3>Create New Quiz</h3>
                  <form onSubmit={handleQuizSubmit} className="upload-form">
                    <input type="text" placeholder="Quiz Title" value={quizForm.title} onChange={(e) => setQuizForm({ ...quizForm, title: e.target.value })} required />
                    <textarea placeholder="Quiz Description" value={quizForm.description} onChange={(e) => setQuizForm({ ...quizForm, description: e.target.value })} />
                    <div className="form-row">
                      <input type="date" placeholder="Start Date" value={quizForm.startDate} onChange={(e) => setQuizForm({ ...quizForm, startDate: e.target.value })} required />
                      <input type="date" placeholder="End Date" value={quizForm.endDate} onChange={(e) => setQuizForm({ ...quizForm, endDate: e.target.value })} required />
                    </div>
                    <button type="submit" className="btn-primary">Create Quiz</button>
                  </form>
                </div>

                <div className="content-list">
                  <h3>Active Quizzes</h3>
                  {quizzes.map(quiz => (
                    <div key={quiz.id} className="content-item quiz-item">
                      <div className="content-info">
                        <h4>{quiz.title}</h4>
                        <p>{quiz.description}</p>
                        <small>Start: {formatDate(quiz.start_date)} • End: {formatDate(quiz.end_date)}</small>
                        <small>Total Marks: {quiz.total_marks} • Questions: {quiz.questions_count} • Duration: {quiz.duration_minutes}min</small>
                        <small>Attempts: {quiz.attempts} • Average Score: {quiz.average_score}%</small>
                      </div>
                      <div className="content-actions">
                        <button className="btn-take-quiz">
                          🎯 Take Quiz
                        </button>
                        <button className="btn-view">📊 View Results</button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Materials Tab */}
            {activeTab === 'materials' && (
              <div className="tab-panel">
                <div className="form-section">
                  <h3>Upload New Material</h3>
                  <form onSubmit={handleMaterialSubmit} className="upload-form">
                    <input 
                      type="text" 
                      placeholder="Material Title" 
                      value={materialForm.title} 
                      onChange={(e) => setMaterialForm({ ...materialForm, title: e.target.value })} 
                      required 
                    />
                    <textarea 
                      placeholder="Material Description" 
                      value={materialForm.description} 
                      onChange={(e) => setMaterialForm({ ...materialForm, description: e.target.value })} 
                    />
                    <select 
                      value={materialForm.materialType} 
                      onChange={(e) => setMaterialForm({ ...materialForm, materialType: e.target.value })}
                    >
                      <option value="lecture_note">Lecture Note</option>
                      <option value="reference">Reference Material</option>
                      <option value="supplementary">Supplementary Material</option>
                      <option value="other">Other</option>
                    </select>
                    <input 
                      type="file" 
                      onChange={(e) => handleFileUpload(e, 'material')} 
                      accept=".pdf,.doc,.docx,.ppt,.pptx,.txt,.zip,.jpg,.jpeg,.png" 
                    />
                    <button type="submit" className="btn-primary">Upload Material</button>
                  </form>
                </div>

                <div className="content-list">
                  <h3>Uploaded Materials</h3>
                  {materials.length === 0 ? (
                    <p className="no-content">No materials uploaded yet.</p>
                  ) : (
                    materials.map(material => (
                      <div key={material.id} className="content-item">
                        <div className="content-info">
                          <h4>{material.title}</h4>
                          <p>{material.description}</p>
                          <small>
                            Type: {material.material_type} • 
                            Uploaded: {formatDate(material.upload_date)} • 
                            Downloads: {material.downloads}
                          </small>
                          {material.file_name && <small>File: {material.file_name}</small>}
                        </div>
                        <div className="content-actions">
                          <button className="btn-delete" onClick={() => deleteMaterial(material.id)}>
                            🗑️ Delete
                          </button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default TeacherCourses;