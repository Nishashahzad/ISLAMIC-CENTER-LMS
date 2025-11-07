import React, { useState, useEffect, useRef } from "react";
import "./AdminDashboard.css";

const Teachers = () => {
  const [teachers, setTeachers] = useState([]);
  const [allSubjects, setAllSubjects] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [loading, setLoading] = useState(true);
  const [selectedSuggestionIndex, setSelectedSuggestionIndex] = useState(-1);
  const [formData, setFormData] = useState({
    fullName: "",
    dob: "",
    qualification: "",
    subject: "",
    address: "",
    phone: "",
    email: "",
  });
  const [editingIndex, setEditingIndex] = useState(null);
  const [menuIndex, setMenuIndex] = useState(null);

  const suggestionsRef = useRef(null);
  const inputRef = useRef(null);

  // Generate unique User ID
  const generateUserId = (name) => {
    const randomNum = Math.floor(1000 + Math.random() * 9000);
    return "teacher_" + name.toLowerCase().replace(/\s+/g, "") + "_" + randomNum;
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

  // Fetch teachers from DB
  const fetchTeachers = async () => {
    try {
      const response = await fetch("http://localhost/islamiccenter-api/users.php?role=teacher");
      if (!response.ok) throw new Error('Network response was not ok');
      const data = await response.json();
      console.log("Fetched teachers:", data);
      setTeachers(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Error fetching teachers:", err);
      setTeachers([]);
    }
  };

  // Fetch all subjects from FastAPI
  const fetchAllSubjects = async () => {
    try {
      const response = await fetch("http://localhost:8000/all_subjects");
      if (!response.ok) throw new Error('Failed to fetch subjects from API');
      const data = await response.json();
      console.log("Fetched all subjects:", data);
      setAllSubjects(data.subjects || []);
    } catch (err) {
      console.error("Error fetching subjects:", err);
      setAllSubjects([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      await Promise.all([fetchTeachers(), fetchAllSubjects()]);
    };
    loadData();
  }, []);

  // Handle subject input with autocomplete - FIXED: Always show matching subjects
  const handleSubjectChange = (e) => {
    const value = e.target.value;
    setFormData({ ...formData, subject: value });
    setSelectedSuggestionIndex(-1);

    // ✅ take only the last part after comma for filtering
    const lastPart = value.split(",").pop().trim();

    if (lastPart.length >= 2) {
      const filtered = allSubjects.filter(subject =>
        subject && subject.toLowerCase().includes(lastPart.toLowerCase())
      );
      setSuggestions(filtered);
      setShowSuggestions(filtered.length > 0);
    } else {
      setShowSuggestions(false);
      setSuggestions([]);
    }
  };

  // Select suggestion - FIXED: Better subject assignment
  const selectSuggestion = (subject) => {
    if (!subject) return;

    console.log("Selecting subject:", subject);

    // ✅ replace only last part after comma
    const parts = formData.subject.split(",");
    parts[parts.length - 1] = " " + subject; 
    const newValue = parts.join(",").trim();

    setFormData({ ...formData, subject: newValue });

    setShowSuggestions(false);
    setSelectedSuggestionIndex(-1);

    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  // Handle keyboard navigation - FIXED
  const handleKeyDown = (e) => {
    if (showSuggestions && suggestions.length > 0) {
      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          setSelectedSuggestionIndex(prev =>
            prev < suggestions.length - 1 ? prev + 1 : 0
          );
          break;

        case 'ArrowUp':
          e.preventDefault();
          setSelectedSuggestionIndex(prev =>
            prev > 0 ? prev - 1 : suggestions.length - 1
          );
          break;

        case 'Enter':
          e.preventDefault();
          if (selectedSuggestionIndex >= 0 && selectedSuggestionIndex < suggestions.length) {
            const selectedSubject = suggestions[selectedSuggestionIndex];
            console.log("Enter pressed, selecting:", selectedSubject);
            if (!isSubjectAssigned(selectedSubject, editingIndex !== null ? teachers[editingIndex]?.id : null)) {
              selectSuggestion(selectedSubject);
            }
          } else if (suggestions.length === 1) {
            // Auto-select if only one suggestion
            const selectedSubject = suggestions[0];
            console.log("Auto-selecting single suggestion:", selectedSubject);
            if (!isSubjectAssigned(selectedSubject, editingIndex !== null ? teachers[editingIndex]?.id : null)) {
              selectSuggestion(selectedSubject);
            }
          }
          break;

        case 'Tab':
          if (selectedSuggestionIndex >= 0 && selectedSuggestionIndex < suggestions.length) {
            e.preventDefault();
            const selectedSubject = suggestions[selectedSuggestionIndex];
            if (!isSubjectAssigned(selectedSubject, editingIndex !== null ? teachers[editingIndex]?.id : null)) {
              selectSuggestion(selectedSubject);
            }
          }
          break;

        case 'Escape':
          setShowSuggestions(false);
          setSelectedSuggestionIndex(-1);
          break;

        default:
          break;
      }
    }
  };

  // Handle click outside to close suggestions
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        suggestionsRef.current &&
        !suggestionsRef.current.contains(event.target) &&
        inputRef.current &&
        !inputRef.current.contains(event.target)
      ) {
        setShowSuggestions(false);
        setSelectedSuggestionIndex(-1);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Check if subject is already assigned to another teacher
  const isSubjectAssigned = (subject, currentTeacherId = null) => {
    if (!subject) return false;

    return teachers.some(teacher => {
      // Skip the current teacher when editing
      if (currentTeacherId && teacher.id === currentTeacherId) return false;
      return teacher.subject && teacher.subject.toLowerCase() === subject.toLowerCase();
    });
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    if (name === "subject") {
      handleSubjectChange(e);
    } else {
      setFormData({ ...formData, [name]: value });
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // Validation
    if (
      !formData.fullName ||
      !formData.dob ||
      !formData.qualification ||
      !formData.subject ||
      !formData.address ||
      !formData.phone ||
      !formData.email
    ) {
      alert("Please fill all fields!");
      return;
    }

    // Check if subject is already assigned (only for new teachers)
    const currentTeacherId = editingIndex !== null ? teachers[editingIndex]?.id : null;
    if (isSubjectAssigned(formData.subject, currentTeacherId)) {
      alert("This subject is already assigned to another teacher! Please choose a different subject.");
      return;
    }

    if (editingIndex !== null) {
      // Update teacher in DB
      const teacherId = teachers[editingIndex]?.id;
      if (!teacherId) {
        alert("Error: Teacher ID not found");
        return;
      }

      const updatedTeacher = {
        id: teacherId,
        fullName: formData.fullName,
        dob: formData.dob,
        qualification: formData.qualification,
        subject: formData.subject,
        address: formData.address,
        phone: formData.phone,
        email: formData.email,
      };

      console.log("Updating teacher:", updatedTeacher);

      fetch("http://localhost/islamiccenter-api/users.php", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updatedTeacher),
      })
        .then((res) => res.json())
        .then((result) => {
          console.log("Update response:", result);
          if (result.success) {
            fetchTeachers();
            setEditingIndex(null);
            resetForm();
            alert("Teacher updated successfully!");
          } else {
            alert("Update failed: " + (result.error || "Unknown error"));
          }
        })
        .catch(err => {
          console.error("Update error:", err);
          alert("Update failed: " + err.message);
        });

    } else {
      // Create new teacher
      const password = generatePassword(); // Store password to show in alert
      const newTeacher = {
        ...formData,
        userid: generateUserId(formData.fullName),
        password: password,
        role: "teacher",
        current_year: "2024",
        education: formData.qualification
      };

      console.log("Creating teacher:", newTeacher);

      fetch("http://localhost/islamiccenter-api/users.php", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newTeacher),
      })
        .then((res) => res.json())
        .then((result) => {
          console.log("Create response:", result);
          if (result.success) {
            fetchTeachers();
            resetForm();
            // Show credentials like in student table
            alert(`Teacher created successfully!\n\nUser ID: ${newTeacher.userid}\nPassword: ${password}`);
          } else {
            alert("Create failed: " + (result.error || "Unknown error"));
          }
        })
        .catch(err => {
          console.error("Create error:", err);
          alert("Create failed: " + err.message);
        });
    }
  };

  const resetForm = () => {
    setFormData({
      fullName: "",
      dob: "",
      qualification: "",
      subject: "",
      address: "",
      phone: "",
      email: "",
    });
    setShowSuggestions(false);
    setSuggestions([]);
    setSelectedSuggestionIndex(-1);
  };

  const handleEdit = (index) => {
    const teacher = teachers[index];
    if (!teacher) return;

    setFormData({
      fullName: teacher.fullName || "",
      dob: teacher.dob || "",
      qualification: teacher.qualification || teacher.education || "",
      subject: teacher.subject || "",
      address: teacher.address || "",
      phone: teacher.phone || "",
      email: teacher.email || "",
    });
    setEditingIndex(index);
    setMenuIndex(null);
    setShowSuggestions(false);
    setSelectedSuggestionIndex(-1);
  };

  const handleDelete = (index) => {
    const teacher = teachers[index];
    if (!teacher || !teacher.id) {
      alert("Error: Cannot delete teacher - ID not found");
      return;
    }

    if (!window.confirm("Are you sure you want to delete this teacher?")) return;

    fetch(`http://localhost/islamiccenter-api/users.php?id=${teacher.id}`, {
      method: "DELETE",
    })
      .then((res) => res.json())
      .then((result) => {
        console.log("Delete response:", result);
        if (result.success) {
          fetchTeachers();
          alert("Teacher deleted successfully!");
        } else {
          alert("Delete failed: " + (result.error || "Unknown error"));
        }
      })
      .catch(err => {
        console.error("Delete error:", err);
        alert("Delete failed: " + err.message);
      });
    setMenuIndex(null);
  };

  // Simple menu toggle
  const toggleMenu = (index) => {
    setMenuIndex(menuIndex === index ? null : index);
  };

  if (loading) {
    return <div className="loading">Loading teachers and subjects...</div>;
  }

  return (
    <div className="students-container">
      <h1>Teachers Management</h1>

      {/* Teacher Form */}
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
            <label>Qualification *</label>
            <input
              type="text"
              name="qualification"
              placeholder="Enter qualification"
              value={formData.qualification}
              onChange={handleChange}
              required
            />
          </div>
          <div className="input-group">
            <label>Assigned Subject *</label>
            <div className="subject-input-container">
              <input
                ref={inputRef}
                type="text"
                name="subject"
                placeholder="Type subject name (min 2 letters)..."
                value={formData.subject}
                onChange={handleChange}
                onKeyDown={handleKeyDown}
                onFocus={() => {
                  if (formData.subject.length >= 2) {
                    const filtered = allSubjects.filter(subject =>
                      subject && subject.toLowerCase().includes(formData.subject.toLowerCase())
                    );
                    setSuggestions(filtered);
                    setShowSuggestions(filtered.length > 0);
                  }
                }}
                required
              />
              {showSuggestions && suggestions.length > 0 && (
                <div className="suggestions-dropdown" ref={suggestionsRef}>
                  {suggestions.map((subject, index) => {
                    const assigned = isSubjectAssigned(subject, editingIndex !== null ? teachers[editingIndex]?.id : null);
                    const isSelected = index === selectedSuggestionIndex;
                    return (
                      <div
                        key={index}
                        className={`suggestion-item ${assigned ? 'assigned' : 'available'} ${isSelected ? 'selected' : ''}`}
                        onClick={() => {
                          console.log("Clicked subject:", subject);
                          if (!assigned) {
                            selectSuggestion(subject);
                          }
                        }}
                        onMouseEnter={() => setSelectedSuggestionIndex(index)}
                      >
                        <span>{subject}</span>
                        {assigned && (
                          <span className="assigned-badge">Already Assigned</span>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="input-group">
          <label>Address *</label>
          <textarea
            name="address"
            placeholder="Enter full address"
            value={formData.address}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-buttons">
          <button type="submit" className="btn-primary">
            {editingIndex !== null ? "Update Teacher" : "Create Teacher"}
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

      {/* Teacher List - Updated to match student table style */}
      <div className="table-section">
        <h2>All Teachers ({teachers.length})</h2>
        {teachers.length === 0 ? (
          <p className="no-data">No teachers found.</p>
        ) : (
          <table className="students-table">
            <thead>
              <tr>
                <th>User ID</th>
                <th>Password</th>
                <th>Full Name</th>
                <th>Subject</th>
                <th>Qualification</th>
                <th>Email</th>
                <th>Phone</th>
                <th>DOB</th>
                <th>Address</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {teachers.map((teacher, index) => (
                <tr key={teacher.id || index}>
                  <td>{teacher.userid || "N/A"}</td>
                  <td>{teacher.password || "N/A"}</td>
                  <td>{teacher.fullName || "N/A"}</td>
                  <td>
                    <span className={`subject-badge ${isSubjectAssigned(teacher.subject) ? 'assigned' : ''}`}>
                      {teacher.subject || "Not assigned"}
                    </span>
                  </td>
                  <td>{teacher.qualification || teacher.education || "N/A"}</td>
                  <td>{teacher.email || "N/A"}</td>
                  <td>{teacher.phone || "N/A"}</td>
                  <td>{teacher.dob || "N/A"}</td>
                  <td>{teacher.address || "N/A"}</td>
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

export default Teachers;