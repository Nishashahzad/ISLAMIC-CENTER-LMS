import React, { useState, useEffect } from "react";
import { useOutletContext } from "react-router-dom";
import "./StudentCourses.css";

const StudentCourses = () => {
  const studentData = useOutletContext();
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [studentWithYear, setStudentWithYear] = useState(null);

  // Fetch complete student data including year
  useEffect(() => {
    const fetchStudentWithYear = async () => {
      if (!studentData?.userid && !studentData?.id) {
        setError("No student ID available");
        setLoading(false);
        return;
      }

      const studentId = studentData.userid || studentData.id;
      
      try {
        const response = await fetch(`http://localhost/islamiccenter-api/users.php?userid=${studentId}`);
        if (!response.ok) throw new Error('Failed to fetch student data');
        
        const completeStudentData = await response.json();
        setStudentWithYear(completeStudentData);
        
        if (completeStudentData.current_year) {
          await fetchSubjectsForYear(completeStudentData.current_year);
        } else {
          setError("Student does not have a year assigned in the database");
          setLoading(false);
        }
      } catch (err) {
        console.error("Error fetching student data:", err);
        setError("Failed to load student information");
        setLoading(false);
      }
    };

    const fetchSubjectsForYear = async (yearName) => {
      const getYearNumber = (yearName) => {
        if (!yearName) return null;
        
        const yearMap = {
          "first year": 1, "1st year": 1, "year 1": 1, "year1": 1, "first": 1,
          "second year": 2, "2nd year": 2, "year 2": 2, "year2": 2, "second": 2,
          "third year": 3, "3rd year": 3, "year 3": 3, "year3": 3, "third": 3,
          "fourth year": 4, "4th year": 4, "year 4": 4, "year4": 4, "fourth": 4,
          "fifth year": 5, "5th year": 5, "year 5": 5, "year5": 5, "fifth": 5
        };
        
        const normalizedYear = yearName.toString().toLowerCase().trim();
        return yearMap[normalizedYear] || null;
      };

      const yearNumber = getYearNumber(yearName);
      
      if (!yearNumber) {
        setError(`Cannot determine year number from: "${yearName}". Please contact administration.`);
        setLoading(false);
        return;
      }

      try {
        // Use the NEW endpoint that provides exact matching
        const response = await fetch(`http://localhost:8000/student_subjects/${yearNumber}`);
        if (!response.ok) throw new Error('Failed to fetch subjects');
        
        const data = await response.json();
        
        if (data.success) {
          // Fetch stats for each subject
          const subjectsWithStats = await Promise.all(
            data.subjects.map(async (subject) => {
              const statsResponse = await fetch(`http://localhost:8000/subject_stats/${encodeURIComponent(subject.subject_name)}`);
              const statsData = await statsResponse.json();
              
              return {
                ...subject,
                stats: statsData.success ? statsData.stats : { 
                  lectures: 0, 
                  assignments: 0, 
                  quizzes: 0, 
                  notifications: 0,
                  materials: Math.floor(Math.random() * 5) + 1 // Random materials count for demo
                }
              };
            })
          );
          
          setSubjects(subjectsWithStats);
        } else {
          throw new Error('Failed to load subjects data');
        }
        
        setLoading(false);
      } catch (err) {
        console.error("Error fetching subjects:", err);
        setError("Failed to load course subjects");
        setLoading(false);
      }
    };

    fetchStudentWithYear();
  }, [studentData]);

  // Get current year from the fetched student data
  const currentYear = studentWithYear?.current_year || 
                     studentData?.current_year || 
                     "Not assigned";

  // Function to handle actions
  const handleAction = (action, subjectName) => {
    console.log(`${action} for ${subjectName}`);
    // Add your implementation for each action
    switch(action) {
      case 'download':
        // Download files logic
        break;
      case 'assignments':
        // View assignments logic
        break;
      case 'quizzes':
        // View quizzes logic
        break;
      case 'notifications':
        // View notifications logic
        break;
      case 'materials':
        // View materials logic
        break;
      default:
        break;
    }
  };

  if (loading) {
    return (
      <div className="students-container">
        <div className="loading">Loading your courses and student information...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="students-container">
        <div className="error-message">
          <h3>⚠️ Unable to Load Courses</h3>
          <p>{error}</p>
          <div style={{ marginTop: '15px', fontSize: '14px', color: '#666' }}>
            <p><strong>Student ID:</strong> {studentData?.userid || studentData?.id || 'N/A'}</p>
            <p><strong>Student Name:</strong> {studentData?.fullName || studentData?.name || 'N/A'}</p>
            <p><strong>Note:</strong> Please contact administration to assign you to a year.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="students-container">
      <h1>📚 My Courses</h1>
      
      <div className="student-info-card">
        <div className="info-row">
          <strong>Student Name:</strong> 
          <span>{studentWithYear?.fullName || studentData?.fullName || studentData?.name || "N/A"}</span>
        </div>
        <div className="info-row">
          <strong>Current Year:</strong> 
          <span className="year-badge">{currentYear}</span>
        </div>
        <div className="info-row">
          <strong>User ID:</strong> 
          <span>{studentWithYear?.userid || studentData?.userid || studentData?.id || "N/A"}</span>
        </div>
        {studentWithYear?.email && (
          <div className="info-row">
            <strong>Email:</strong> 
            <span>{studentWithYear.email}</span>
          </div>
        )}
      </div>

      <div className="courses-section">
        <h2>📖 Subjects for {currentYear}</h2>
        
        {subjects.length === 0 ? (
          <div className="no-data">
            No subjects found for {currentYear}. Please contact administration.
          </div>
        ) : (
          <div className="subjects-grid">
            {subjects.map((subject, index) => (
              <div key={index} className="subject-card">
                {/* Header Section */}
                <div className="subject-header">
                  <h3>{subject.subject_name}</h3>
                  <span className="lecture-count">
                    {subject.stats?.lectures || 0} Lectures
                  </span>
                </div>

                {/* Teacher Info Section */}
                <div className="teacher-section">
                  <div className="teacher-info">
                    <span className="teacher-label">Teacher:</span>
                    <span className="teacher-name">
                      {subject.teachers && subject.teachers.length > 0 
                        ? subject.teachers[0].fullName 
                        : "Not assigned"}
                    </span>
                  </div>
                </div>

                {/* Icons Section - All icons in one row */}
                <div className="subject-icons">
                  <div className="icon-group">
                    {/* Assignments Icon */}
                    <div 
                      className="icon-item"
                      onClick={() => handleAction('assignments', subject.subject_name)}
                    >
                      <span className="icon">📝</span>
                      <span className="icon-label">Assignments</span>
                      {subject.stats?.assignments > 0 && (
                        <span className="notification-badge">
                          {subject.stats.assignments}
                        </span>
                      )}
                    </div>
                    
                    {/* Quizzes Icon */}
                    <div 
                      className="icon-item"
                      onClick={() => handleAction('quizzes', subject.subject_name)}
                    >
                      <span className="icon">📊</span>
                      <span className="icon-label">Quizzes</span>
                      {subject.stats?.quizzes > 0 && (
                        <span className="notification-badge">
                          {subject.stats.quizzes}
                        </span>
                      )}
                    </div>
                    
                    {/* Notifications Icon */}
                    <div 
                      className="icon-item"
                      onClick={() => handleAction('notifications', subject.subject_name)}
                    >
                      <span className="icon">🔔</span>
                      <span className="icon-label">Alerts</span>
                      {subject.stats?.notifications > 0 && (
                        <span className="notification-badge">
                          {subject.stats.notifications}
                        </span>
                      )}
                    </div>

                    {/* Materials Icon */}
                    <div 
                      className="icon-item"
                      onClick={() => handleAction('materials', subject.subject_name)}
                    >
                      <span className="icon">📚</span>
                      <span className="icon-label">Materials</span>
                      {subject.stats?.materials > 0 && (
                        <span className="notification-badge">
                          {subject.stats.materials}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Summary Section */}
      {subjects.length > 0 && (
        <div className="summary-card">
          <h3>📊 Academic Summary - {currentYear}</h3>
          <div className="summary-grid">
            <div className="summary-item">
              <div className="summary-value">{subjects.length}</div>
              <div className="summary-label">Total Subjects</div>
            </div>
            <div className="summary-item">
              <div className="summary-value">
                {subjects.reduce((total, subject) => total + subject.duration_months, 0)}
              </div>
              <div className="summary-label">Total Duration (Months)</div>
            </div>
            <div className="summary-item">
              <div className="summary-value">
                {subjects.reduce((total, subject) => total + (subject.stats?.lectures || 0), 0)}
              </div>
              <div className="summary-label">Total Lectures</div>
            </div>
            <div className="summary-item">
              <div className="summary-value">
                {subjects.reduce((total, subject) => total + (subject.stats?.assignments || 0), 0)}
              </div>
              <div className="summary-label">Pending Assignments</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StudentCourses;