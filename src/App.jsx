import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomePage from "./components/HomePage";
import ForgetPassword from "./components/forget_password";
import AdminLayout from "./components/AdminLayout";
import AdminCourses from "./components/AdminCourses";
import Dashboard from "./components/Dashboard";
import AdminStudents from "./components/AdminStudents";
import AdminTeachers from "./components/AdminTeachers";
import Enrollments from "./components/Enrollments";
import Reports from "./components/Reports";
import Payments from "./components/Payments";
import Settings from "./components/Settings";
import StudentNotifications from "./components/StudentNotifications";
import StudentMaterials from "./components/StudentMaterials";
import StudentLectures from "./components/StudentLectures";
import StudentAssignments from "./components/StudentAssignments";
import StudentLayout from "./components/StudentLayout";
import StudentDashboard from "./components/StudentDashboard";
import StudentCourses from "./components/StudentCourses";
import StudentProfile from "./components/StudentProfile";
import TeacherDashboard from "./components/TeacherDashboard";
import TeacherLayout from "./components/TeacherLayout";
import TeacherCourses from "./components/TeacherCourses";
import TeacherProfile from "./components/TeacherProfile";
import QuizMaker from './components/QuizMaker';

// Import new quiz components
import StudentQuizzes from "./components/StudentQuizDashboard";
import StudentTakeQuiz from "./components/TakeQuiz";
import StudentQuizResult from "./components/QuizResult";

// Import assignment submission components
import StudentAssignmentSubmission from "./components/StudentAssignmentSubmission";
import StudentSubmissionView from "./components/StudentSubmissionView";

// Import the new Assignment Submissions page
import AssignmentSubmissionsPage from "./components/AssignmentSubmissionsPage";
// Import File Viewer Page
import FileViewerPage from "./components/FileViewerPage";

function App() {
  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<HomePage />} />
        <Route path="/forget-password" element={<ForgetPassword />} />

        {/* Admin Routes */}
        <Route path="/admin-dashboard" element={<AdminLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="students" element={<AdminStudents />} />
          <Route path="teachers" element={<AdminTeachers />} />
          <Route path="AdminCourses" element={<AdminCourses />} />
          <Route path="enrollments" element={<Enrollments />} />
          <Route path="reports" element={<Reports />} />
          <Route path="payments" element={<Payments />} />
          <Route path="settings" element={<Settings />} />
        </Route>

        {/* Student Routes */}
        <Route path="/student-dashboard/:userId" element={<StudentLayout />}>
          <Route index element={<StudentDashboard />} />
          <Route path="courses" element={<StudentCourses />} />
          
          {/* Quiz routes */}
          <Route path="quizzes" element={<StudentQuizzes />} />
          <Route path="quizzes/take/:quizId" element={<StudentTakeQuiz />} />
          <Route path="quizzes/result/:attemptId" element={<StudentQuizResult />} />
          
          {/* Assignment routes */}
          <Route path="assignments" element={<StudentAssignments />} />
          <Route path="assignments/submit/:assignmentId" element={<StudentAssignmentSubmission />} />
          <Route path="assignments/submission/:submissionId" element={<StudentSubmissionView />} />
          
          {/* Other routes */}
          <Route path="lectures" element={<StudentLectures />} />
          <Route path="materials" element={<StudentMaterials />} />
          <Route path="notifications" element={<StudentNotifications />} />
          <Route path="profile" element={<StudentProfile />} />
        </Route>

        {/* Teacher Routes */}
        <Route path="/teacher-dashboard/:userId" element={<TeacherLayout />}>
          <Route index element={<TeacherDashboard />} />
          <Route path="courses" element={<TeacherCourses />} />
          <Route path="profile" element={<TeacherProfile />} />
          
          {/* NEW: Teacher assignment submissions route */}
          <Route path="assignments/:assignmentId/submissions" element={<AssignmentSubmissionsPage />} />
        </Route>

        {/* ✅ QuizMaker Route */}
        <Route path="/quiz-maker" element={<QuizMaker />} />
        
        {/* ✅ Direct route for assignment submissions (standalone) */}
        <Route path="/teacher/assignment-submissions/:assignmentId" element={<AssignmentSubmissionsPage />} />
        
        {/* ✅ File Viewer Route for teachers to view submission files */}
        <Route path="/teacher/file-viewer/:submissionId" element={<FileViewerPage />} />
      </Routes>
    </Router>
  );
}

export default App;