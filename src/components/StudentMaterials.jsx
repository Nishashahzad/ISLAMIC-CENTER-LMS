import React, { useState, useEffect } from 'react';
import "./StudentCourses.css";
import { useLocation, useNavigate, useParams } from 'react-router-dom';

const StudentMaterials = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { userId } = useParams();
  const { subject, teacher, studentData } = location.state || {};
  
  const [materials, setMaterials] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (subject) {
      fetchMaterials();
    }
  }, [subject]);

  const fetchMaterials = async () => {
    try {
      const response = await fetch(`http://localhost:8000/student_materials/${subject}`);
      const data = await response.json();
      
      if (data.success) {
        setMaterials(data.materials);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error fetching materials:', error);
      setLoading(false);
    }
  };

  const handleBack = () => {
    navigate(`/student-dashboard/${userId}/courses`);
  };

  const handleDownload = async (material) => {
    try {
      await fetch(`http://localhost:8000/materials/${material.id}/download`, {
        method: 'POST'
      });
      
      window.open(`http://localhost:8000${material.file_path}`, '_blank');
    } catch (error) {
      console.error('Error downloading file:', error);
    }
  };

  if (loading) return <div className="loading">Loading materials...</div>;

  return (
  <div className="student-materials-container">
    <div className="student-materials-header">
      <button onClick={handleBack} className="student-materials-back-btn">
        ← Back to Courses
      </button>
      <h1 className="student-materials-title">📚 Materials - {subject}</h1>
    </div>

    <div className="student-materials-content-section">
      <div className="student-materials-info-card">
        <p><strong>Subject:</strong> {subject}</p>
        <p><strong>Total Materials:</strong> {materials.length}</p>
      </div>

      {materials.length === 0 ? (
        <div className="no-data">No materials available for this subject.</div>
      ) : (
        <div className="student-materials-list">
          {materials.map((material) => (
            <div key={material.id} className="student-material-card">
              <div className="student-material-info">
                <h3>{material.title}</h3>
                <p>{material.description}</p>
                <div className="student-material-meta">
                  <span>Type: {material.material_type}</span>
                  <span>Teacher: {material.teacher_name}</span>
                  <span>Uploaded: {new Date(material.upload_date).toLocaleDateString()}</span>
                  <span>Downloads: {material.downloads}</span>
                </div>
              </div>
              {material.file_path && (
                <button 
                  onClick={() => handleDownload(material)}
                  className="student-material-download-btn"
                >
                  📥 Download
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  </div>
);
};

export default StudentMaterials;