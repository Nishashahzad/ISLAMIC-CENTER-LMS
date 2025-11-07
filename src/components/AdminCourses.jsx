import React, { useState, useEffect } from "react";

const Courses = () => {
  const [years, setYears] = useState([]);
  const [selectedYear, setSelectedYear] = useState(null);
  const [subjects, setSubjects] = useState([]);

  // ✅ Fetch Predefined Years (from predefined data, not database)
  useEffect(() => {
    fetch("http://localhost:8000/predefined_years")
      .then((res) => res.json())
      .then((data) => setYears(data))
      .catch((err) => console.error("Error fetching predefined years:", err));
  }, []);

  // ✅ Fetch Predefined Subjects when year changes
  useEffect(() => {
    if (selectedYear) {
      fetch(`http://localhost:8000/predefined_subjects/${selectedYear}`)
        .then((res) => {
          if (!res.ok) {
            throw new Error('No subjects found for this year');
          }
          return res.json();
        })
        .then((data) => setSubjects(data))
        .catch((err) => {
          console.error("Error fetching predefined subjects:", err);
          setSubjects([]);
        });
    }
  }, [selectedYear]);

  // ✅ Initialize database with predefined data (optional button)
  const initializeDatabase = () => {
    fetch("http://localhost:8000/initialize_data", {
      method: "POST"
    })
      .then((res) => res.json())
      .then((data) => {
        alert(data.message);
      })
      .catch((err) => console.error("Error initializing data:", err));
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>📚 Islamic Center Courses</h1>

      {/* Initialize Database Button */}
      <div style={{ marginBottom: "20px" }}>
        <button 
          onClick={initializeDatabase}
          style={{
            padding: "10px 15px",
            backgroundColor: "#4CAF50",
            color: "white",
            border: "none",
            borderRadius: "5px",
            cursor: "pointer"
          }}
        >
          🗃️ Initialize Database with Predefined Data
        </button>
        <p style={{ fontSize: "12px", color: "#666", marginTop: "5px" }}>
          (One-time setup to populate database with all subjects)
        </p>
      </div>

      {/* Dropdown for Years */}
      <div style={{ marginBottom: "20px" }}>
        <label><strong>Select Academic Year: </strong></label>
        <select
          value={selectedYear || ""}
          onChange={(e) => setSelectedYear(parseInt(e.target.value))}
          style={{
            padding: "8px",
            fontSize: "16px",
            marginLeft: "10px",
            borderRadius: "5px",
            border: "1px solid #ccc"
          }}
        >
          <option value="">-- Choose Year --</option>
          {years.map((year, index) => (
            <option key={index} value={index + 1}>
              {year.name} ({year.code})
            </option>
          ))}
        </select>
      </div>

      {/* Subjects List */}
      {selectedYear && (
        <div style={{ marginTop: "20px" }}>
          <h2>📖 Subjects for Year {selectedYear}</h2>
          {subjects.length > 0 ? (
            <div>
              <p><strong>Total Subjects: {subjects.length}</strong></p>
              <ul style={{ listStyle: "none", padding: 0 }}>
                {subjects.map((subj, index) => (
                  <li 
                    key={index}
                    style={{
                      padding: "10px",
                      margin: "5px 0",
                      backgroundColor: "#f9f9f9",
                      border: "1px solid #ddd",
                      borderRadius: "5px"
                    }}
                  >
                    <strong>{subj.subject_name}</strong> 
                    <span style={{ float: "right", color: "#666" }}>
                      📅 {subj.duration_months} months
                    </span>
                  </li>
                ))}
              </ul>
              
              {/* Total Duration */}
              <div style={{ 
                marginTop: "20px", 
                padding: "15px", 
                backgroundColor: "#e8f5e8",
                border: "1px solid #4CAF50",
                borderRadius: "5px"
              }}>
                <strong>Total Program Duration: </strong>
                {subjects.reduce((total, subj) => total + subj.duration_months, 0)} months
              </div>
            </div>
          ) : (
            <p style={{ color: "#666" }}>No subjects found for Year {selectedYear}.</p>
          )}
        </div>
      )}

      {/* Available Years Overview */}
      <div style={{ marginTop: "40px" }}>
        <h3>🎓 Available Academic Years</h3>
        <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
          {years.map((year, index) => (
            <div 
              key={index}
              style={{
                padding: "15px",
                border: "1px solid #ccc",
                borderRadius: "8px",
                minWidth: "120px",
                textAlign: "center",
                backgroundColor: selectedYear === index + 1 ? "#e3f2fd" : "#fff",
                cursor: "pointer"
              }}
              onClick={() => setSelectedYear(index + 1)}
            >
              <strong>{year.name}</strong>
              <br />
              <small>{year.code}</small>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Courses;