import React, { useState, useEffect, useRef } from "react";
import "./AdminDashboard.css";

const Students = () => {
  const [students, setStudents] = useState([]);
  const [allYears, setAllYears] = useState([]);
  const [yearSuggestions, setYearSuggestions] = useState([]);
  const [showYearSuggestions, setShowYearSuggestions] = useState(false);
  const [selectedYearSuggestionIndex, setSelectedYearSuggestionIndex] = useState(-1);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    fullName: "",
    dob: "",
    education: "",
    address: "",
    phone: "",
    email: "",
    current_year: "",
  });
  const [editingIndex, setEditingIndex] = useState(null);
  const [menuIndex, setMenuIndex] = useState(null);

  const yearInputRef = useRef(null);

  // Generate unique User ID
  const generateUserId = (name) => {
    const randomNum = Math.floor(1000 + Math.random() * 9000);
    return "student_" + name.toLowerCase().replace(/\s+/g, "") + "_" + randomNum;
  };

  // Generate random password
  const generatePassword = () => {
    const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    let pass = "";
    for (let i = 0; i < 8; i++) {
      pass += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return pass;
  };

  // Fetch students
  const fetchStudents = () => {
    fetch("http://localhost/islamiccenter-api/users.php?role=student")
      .then((res) => res.json())
      .then((data) => setStudents(data))
      .catch((err) => console.error("Error fetching students:", err));
  };

  // Fetch all years from FastAPI
  const fetchAllYears = async () => {
    try {
      const response = await fetch("http://localhost:8000/years");
      if (!response.ok) throw new Error('Failed to fetch years from API');
      const data = await response.json();
      console.log("Fetched all years:", data);
      setAllYears(data || []);
    } catch (err) {
      console.error("Error fetching years:", err);
      setAllYears([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      await Promise.all([fetchStudents(), fetchAllYears()]);
    };
    loadData();
  }, []);

  // Handle year input with autocomplete
  const handleYearChange = (e) => {
    const value = e.target.value;
    setFormData({ ...formData, current_year: value });
    setSelectedYearSuggestionIndex(-1);

    if (value.length >= 1) {
      const filtered = allYears.filter(year =>
        year.name.toLowerCase().includes(value.toLowerCase()) ||
        year.code.toLowerCase().includes(value.toLowerCase())
      );
      setYearSuggestions(filtered);
      setShowYearSuggestions(true);
    } else {
      setShowYearSuggestions(false);
      setYearSuggestions([]);
    }
  };

  // Select year suggestion
  const selectYearSuggestion = (year) => {
    if (!year) return;
    setFormData({ ...formData, current_year: year.name });
    setShowYearSuggestions(false);
    setYearSuggestions([]);
    setSelectedYearSuggestionIndex(-1);
  };

  // Handle keyboard navigation for years
  const handleYearKeyDown = (e) => {
    if (!showYearSuggestions || yearSuggestions.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedYearSuggestionIndex(prev => 
          prev < yearSuggestions.length - 1 ? prev + 1 : 0
        );
        break;
      
      case 'ArrowUp':
        e.preventDefault();
        setSelectedYearSuggestionIndex(prev => 
          prev > 0 ? prev - 1 : yearSuggestions.length - 1
        );
        break;
      
      case 'Enter':
        e.preventDefault();
        if (selectedYearSuggestionIndex >= 0 && selectedYearSuggestionIndex < yearSuggestions.length) {
          const selectedYear = yearSuggestions[selectedYearSuggestionIndex];
          selectYearSuggestion(selectedYear);
        } else if (yearSuggestions.length === 1) {
          // Auto-select if only one suggestion
          const selectedYear = yearSuggestions[0];
          selectYearSuggestion(selectedYear);
        }
        break;
      
      case 'Tab':
        if (selectedYearSuggestionIndex >= 0 && selectedYearSuggestionIndex < yearSuggestions.length) {
          e.preventDefault();
          const selectedYear = yearSuggestions[selectedYearSuggestionIndex];
          selectYearSuggestion(selectedYear);
        }
        break;
      
      case 'Escape':
        setShowYearSuggestions(false);
        setSelectedYearSuggestionIndex(-1);
        break;
      
      default:
        break;
    }
  };

  // Handle click outside to close suggestions
  useEffect(() => {
    const handleClickOutside = (event) => {
      // Close year suggestions
      if (
        yearInputRef.current &&
        !yearInputRef.current.contains(event.target) &&
        !event.target.closest('.year-suggestions-dropdown')
      ) {
        setShowYearSuggestions(false);
        setSelectedYearSuggestionIndex(-1);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    if (name === "current_year") {
      handleYearChange(e);
    } else {
      setFormData({ ...formData, [name]: value });
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Debug: Check what data we're sending
    console.log("Form data before submit:", formData);

    if (!formData.fullName || !formData.dob || !formData.phone || !formData.email || !formData.current_year) {
      alert("Please fill required fields!");
      return;
    }

    if (editingIndex !== null) {
      // Update student
      const updatedStudent = {
        id: students[editingIndex].id,
        fullName: formData.fullName,
        dob: formData.dob,
        phone: formData.phone,
        email: formData.email,
        education: formData.education || "",
        address: formData.address || "",
        current_year: formData.current_year,
      };

      console.log("Sending UPDATE data:", updatedStudent);

      fetch("http://localhost/islamiccenter-api/users.php", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updatedStudent),
      })
        .then((res) => res.json())
        .then((result) => {
          console.log("Update RESPONSE:", result);
          if (result.success) {
            setStudents((prev) =>
              prev.map((s) =>
                s.id === updatedStudent.id ? { ...s, ...updatedStudent } : s
              )
            );
            setEditingIndex(null);
            resetForm();
          }
        })
        .catch(err => console.error("Update error:", err));

    } else {
      // Create new student
      const newStudent = {
        ...formData,
        userid: generateUserId(formData.fullName),
        password: generatePassword(),
        role: "student",
      };

      console.log("Sending CREATE data:", newStudent);

      fetch("http://localhost/islamiccenter-api/users.php", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newStudent),
      })
        .then((res) => res.json())
        .then((result) => {
          console.log("Create RESPONSE:", result);
          if (result.success) {
            fetchStudents();
            resetForm();
          } else {
            alert("Error creating student: " + (result.error || "Unknown error"));
          }
        })
        .catch(err => console.error("Create error:", err));
    }
  };

  const resetForm = () => {
    setFormData({
      fullName: "",
      dob: "",
      education: "",
      address: "",
      phone: "",
      email: "",
      current_year: "",
    });
    setShowYearSuggestions(false);
    setYearSuggestions([]);
    setSelectedYearSuggestionIndex(-1);
  };

  const handleEdit = (index) => {
    setFormData({
      fullName: students[index].fullName || "",
      dob: students[index].dob || "",
      education: students[index].education || "",
      address: students[index].address || "",
      phone: students[index].phone || "",
      email: students[index].email || "",
      current_year: students[index].current_year || "",
    });
    setEditingIndex(index);
    setMenuIndex(null);
    setShowYearSuggestions(false);
    setSelectedYearSuggestionIndex(-1);
  };

  const handleDelete = (index) => {
    const studentId = students[index].id;
    if (!window.confirm("Are you sure you want to delete this student?")) return;
    
    fetch(`http://localhost/islamiccenter-api/users.php?id=${studentId}`, {
      method: "DELETE",
    })
      .then((res) => res.json())
      .then((result) => {
        console.log("Delete response:", result);
        if (result.success) {
          fetchStudents();
        }
      })
      .catch(err => console.error("Delete error:", err));
    setMenuIndex(null);
  };

  // Simple menu toggle
  const toggleMenu = (index) => {
    setMenuIndex(menuIndex === index ? null : index);
  };

  if (loading) {
    return <div className="loading">Loading students and years...</div>;
  }

  return (
    <div className="students-container">
      <h1>Students Management</h1>

      {/* Student Form */}
      <form className="student-form" onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="input-group">
            <label>Full Name *</label>
            <input
              type="text"
              name="fullName"
              placeholder="Enter full name"
              value={formData.fullName}
              onChange={handleChange}
              required
            />
          </div>
          <div className="input-group">
            <label>Date of Birth *</label>
            <input
              type="date"
              name="dob"
              value={formData.dob}
              onChange={handleChange}
              required
            />
          </div>
        </div>

        <div className="form-row">
          <div className="input-group">
            <label>Phone Number *</label>
            <input
              type="text"
              name="phone"
              placeholder="Enter phone number"
              value={formData.phone}
              onChange={handleChange}
              required
            />
          </div>
          <div className="input-group">
            <label>Email Address *</label>
            <input
              type="email"
              name="email"
              placeholder="Enter email address"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>
        </div>

        <div className="form-row">
          <div className="input-group">
            <label>Previous Education</label>
            <input
              type="text"
              name="education"
              placeholder="Enter previous education"
              value={formData.education}
              onChange={handleChange}
            />
          </div>
          <div className="input-group">
            <label>Current Year *</label>
            <div className="subject-input-container">
              <input
                ref={yearInputRef}
                type="text"
                name="current_year"
                placeholder="Type year name or code..."
                value={formData.current_year}
                onChange={handleChange}
                onKeyDown={handleYearKeyDown}
                onFocus={() => formData.current_year.length >= 1 && setShowYearSuggestions(true)}
                required
              />
              {showYearSuggestions && yearSuggestions.length > 0 && (
                <div className="suggestions-dropdown year-suggestions-dropdown">
                  {yearSuggestions.map((year, index) => {
                    const isSelected = index === selectedYearSuggestionIndex;
                    return (
                      <div
                        key={year.id}
                        className={`suggestion-item ${isSelected ? 'selected' : ''}`}
                        onClick={() => selectYearSuggestion(year)}
                        onMouseEnter={() => setSelectedYearSuggestionIndex(index)}
                      >
                        <div>
                          <strong>{year.name}</strong>
                          <div style={{ fontSize: '11px', color: '#666' }}>
                            Code: {year.code} | Start: {year.start_date}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="input-group">
          <label>Address</label>
          <textarea
            name="address"
            placeholder="Enter full address"
            value={formData.address}
            onChange={handleChange}
          />
        </div>

        <div className="form-buttons">
          <button type="submit" className="btn-primary">
            {editingIndex !== null ? "Update Student" : "Create Student"}
          </button>
          {editingIndex !== null && (
            <button type="button" className="btn-secondary" onClick={() => {
              setEditingIndex(null);
              resetForm();
            }}>
              Cancel Edit
            </button>
          )}
        </div>
      </form>

      {/* Student List */}
      <div className="table-section">
        <h2>All Students ({students.length})</h2>
        {students.length === 0 ? (
          <p className="no-data">No students found.</p>
        ) : (
          <table className="students-table">
            <thead>
              <tr>
                <th>User ID</th>
                <th>Password</th>
                <th>Full Name</th>
                <th>DOB</th>
                <th>Phone</th>
                <th>Email</th>
                <th>Education</th>
                <th>Current Year</th>
                <th>Address</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {students.map((s, index) => (
                <tr key={s.id}>
                  <td>{s.userid}</td>
                  <td>{s.password}</td>
                  <td>{s.fullName}</td>
                  <td>{s.dob}</td>
                  <td>{s.phone || "N/A"}</td>
                  <td>{s.email}</td>
                  <td>{s.education || "N/A"}</td>
                  <td>{s.current_year}</td>
                  <td>{s.address || "N/A"}</td>
                  <td className="actions-cell">
                    <div
                      className="menu-trigger"
                      onClick={() => toggleMenu(index)}
                    >
                      ⋮
                    </div>
                    {menuIndex === index && (
                      <div className="dropdown-menu">
                        <button onClick={() => handleEdit(index)}>Edit</button>
                        <button onClick={() => handleDelete(index)}>Delete</button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default Students;