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
import StudentQuizzes from "./components/StudentQuizzes";
import StudentAssignments from "./components/StudentAssignments";
import StudentLayout from "./components/StudentLayout";
import StudentDashboard from "./components/StudentDashboard";
import StudentCourses from "./components/StudentCourses";
import StudentProfile from "./components/StudentProfile";
import TeacherDashboard from "./components/TeacherDashboard";
import TeacherLayout from "./components/TeacherLayout";
import TeacherCourses from "./components/TeacherCourses";
import TeacherProfile from "./components/TeacherProfile";

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
          <Route path="profile" element={<StudentProfile />} />
          <Route path="notifications" element={<StudentNotifications />} />
          <Route path="materials" element={<StudentMaterials />} />
          <Route path="lectures" element={<StudentLectures />} />
          <Route path="quizzes" element={<StudentQuizzes />} />
          <Route path="assignments" element={<StudentAssignments />} />
        </Route>

        {/* Teacher Routes */}
        <Route path="/teacher-dashboard/:userId" element={<TeacherLayout />}>
          <Route index element={<TeacherDashboard />} />
          <Route path="courses" element={<TeacherCourses />} />
          <Route path="profile" element={<TeacherProfile />} />
          {/* <Route path="assignments" element={<TeacherAssignments />} /> */}
        </Route>
      </Routes>
    </Router>
  );
}

export default App;