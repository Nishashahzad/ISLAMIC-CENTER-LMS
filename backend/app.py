from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import mysql.connector
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from datetime import date
from fastapi.responses import FileResponse
import os
import shutil
from fastapi import UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse
import re  
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import json

app = FastAPI()

# Create uploads directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Mount static files for serving uploaded files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ✅ Allow frontend requests
origins = [
    "http://localhost:5173",   # React dev server
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # use ["*"] to allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Database connection function
def get_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",           # your MySQL password if any
            database="islamiccenter"
        )
        return conn
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

# ✅ Pydantic Schemas
class Year(BaseModel):
    id: Optional[int] = None
    code: str
    name: str
    start_date: date   # FIX: accept date instead of str

class Subject(BaseModel):
    id: Optional[int] = None
    year_id: int
    subject_name: str
    duration_months: float  # CHANGED: from int to float to match your data

# ------------------- Predefined Data -------------------
predefined_years = [
    {"code": "D25", "name": "First Year", "start_date": "2025-01-01"},
    {"code": "D24", "name": "Second Year", "start_date": "2025-01-01"},
    {"code": "D23", "name": "Third Year", "start_date": "2025-01-01"},
    {"code": "D22", "name": "Fourth Year", "start_date": "2025-01-01"},
    {"code": "D21", "name": "Fifth Year", "start_date": "2025-01-01"},
]

predefined_subjects: Dict[int, List[Dict]] = {
    1: [  # Year 1
        {"subject_name": "Ilm-Un-Nahw", "duration_months": 5.0},
        {"subject_name": "Tarjama-Tul-Quran", "duration_months": 3.0},
        {"subject_name": "Arabi Adab", "duration_months": 2.0},
        {"subject_name": "Ilm-Us-Surf", "duration_months": 3.0},
        {"subject_name": "Fiqh (Urdu)", "duration_months": 3.0},
        {"subject_name": "Aqaid", "duration_months": 3.0},
        {"subject_name": "Tajveed", "duration_months": 1.0},
    ],
    2: [  # Year 2
        {"subject_name": "Hidaya-Tun-Nahw", "duration_months": 5.0},
        {"subject_name": "Tarjama-Tul-Quran", "duration_months": 2.5},
        {"subject_name": "Usool-Ul-Fiqh", "duration_months": 2.5},
        {"subject_name": "Fiqh (Qudoori & Kanz)", "duration_months": 8.0},
        {"subject_name": "Mantiq", "duration_months": 2.0},
    ],
    3: [  # Year 3
        {"subject_name": "Hidaya F & Ahkam Sharia", "duration_months": 5.0},
        {"subject_name": "Falsafa", "duration_months": 3.0},
        {"subject_name": "Mantiq", "duration_months": 2.0},
        {"subject_name": "Usool-Ul-Fiqh (1 Ur, 2Ar)", "duration_months": 3.0},
        {"subject_name": "Ilm-Ul-Kalam (Aqaid)", "duration_months": 3.0},
        {"subject_name": "Balagat", "duration_months": 3.0},
    ],
    4: [  # Year 4
        {"subject_name": "Islamic Finance & Trade", "duration_months": 4.0},
        {"subject_name": "Ilm-e-Kalam & Falsafa", "duration_months": 3.0},
        {"subject_name": "Usool-Ul-Hadith", "duration_months": 2.0},
        {"subject_name": "Usool-Ul-Tafseer", "duration_months": 1.0},
        {"subject_name": "Ilhaad & Modernism (1/2)", "duration_months": 2.0},
        {"subject_name": "Complete Tafseer ul Quran (1/2)", "duration_months": 8.0},
    ],
    5: [  # Year 5
        {"subject_name": "Sahih Bukhari", "duration_months": 5.0},
        {"subject_name": "Sahih Muslim", "duration_months": 5.0},
        {"subject_name": "Sunan Tirmizi", "duration_months": 2.0},
        {"subject_name": "Ilhaad & Modernism (2/2)", "duration_months": 2.0},
        {"subject_name": "Complete Tafseer ul Quran (2/2)", "duration_months": 8.0},
    ],
}

# ------------------- API Endpoints -------------------

# Get Predefined Years
@app.get("/predefined_years")
def get_predefined_years():
    return predefined_years

# Get Predefined Subjects
@app.get("/predefined_subjects")
def get_predefined_subjects():
    return predefined_subjects

# Get Predefined Subjects by Year ID
@app.get("/predefined_subjects/{year_id}")
def get_predefined_subjects_by_year(year_id: int):
    if year_id not in predefined_subjects:
        raise HTTPException(status_code=404, detail=f"No predefined subjects found for year {year_id}")
    return predefined_subjects[year_id]

# Add this to your FastAPI app (main.py)
@app.get("/all_subjects")
def get_all_subjects():
    try:
        # Use the existing predefined_subjects data
        all_subjects_set = set()
        for year_subjects in predefined_subjects.values():
            for subject in year_subjects:
                all_subjects_set.add(subject["subject_name"])
        
        # Convert to list and sort alphabetically
        all_subjects_list = sorted(list(all_subjects_set))
        return {"subjects": all_subjects_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching subjects: {str(e)}")
# Initialize Database with Predefined Data
@app.post("/initialize_data")
def initialize_data():
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Insert years
        year_ids = {}
        for year_data in predefined_years:
            cursor.execute(
                "INSERT INTO years (code, name, start_date) VALUES (%s, %s, %s)",
                (year_data["code"], year_data["name"], year_data["start_date"])
            )
            year_ids[year_data["code"]] = cursor.lastrowid
        
        db.commit()
        
        # Insert subjects
        for year_num, subjects in predefined_subjects.items():
            year_code = f"Y{year_num}"
            if year_code in year_ids:
                for subject in subjects:
                    cursor.execute(
                        "INSERT INTO subjects (year_id, subject_name, duration_months) VALUES (%s, %s, %s)",
                        (year_ids[year_code], subject["subject_name"], subject["duration_months"])
                    )
        
        db.commit()
        cursor.close()
        db.close()
        
        return {"message": "Database initialized with predefined data successfully!"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing data: {str(e)}")

# ----------- Years Endpoints -----------

@app.get("/years", response_model=List[Year])
def get_years():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id, code, name, start_date FROM years")
        result = cursor.fetchall()
        cursor.close()
        db.close()
        # FIX: serialize MySQL date → JSON
        return jsonable_encoder(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching years: {str(e)}")

@app.post("/years")
def add_year(year: Year):
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO years (code, name, start_date) VALUES (%s, %s, %s)",
                       (year.code, year.name, year.start_date))
        db.commit()
        cursor.close()
        db.close()
        return {"message": "Year added successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding year: {str(e)}")

# ----------- Subjects Endpoints -----------

@app.get("/subjects/{year_id}", response_model=List[Subject])
def get_subjects(year_id: int):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # First check if the year exists
        cursor.execute("SELECT id FROM years WHERE id = %s", (year_id,))
        year_exists = cursor.fetchone()
        if not year_exists:
            raise HTTPException(status_code=404, detail="Year not found")
        
        cursor.execute("SELECT id, year_id, subject_name, duration_months FROM subjects WHERE year_id = %s", (year_id,))
        result = cursor.fetchall()
        cursor.close()
        db.close()
        return jsonable_encoder(result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching subjects: {str(e)}")

@app.post("/subjects")
def add_subject(subject: Subject):
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Verify year exists
        cursor.execute("SELECT id FROM years WHERE id = %s", (subject.year_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Year not found")
        
        cursor.execute("INSERT INTO subjects (year_id, subject_name, duration_months) VALUES (%s, %s, %s)",
                       (subject.year_id, subject.subject_name, subject.duration_months))
        db.commit()
        cursor.close()
        db.close()
        return {"message": "Subject added successfully!"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding subject: {str(e)}")


def is_subject_match(teacher_subject, available_subject):
    """Strict subject matching (ignores punctuation & case, but not just words)"""
    if not teacher_subject or not available_subject:
        return False
        
    # Convert to lowercase and remove extra spaces/punctuation
    teacher_subj = teacher_subject.lower().strip().replace('-', ' ').replace('&', 'and')
    available_subj = available_subject.lower().strip().replace('-', ' ').replace('&', 'and')
    
    # Remove common punctuation
    import string
    teacher_subj = teacher_subj.translate(str.maketrans('', '', string.punctuation))
    available_subj = available_subj.translate(str.maketrans('', '', string.punctuation))
    
    # Exact match
    if teacher_subj == available_subj:
        return True
    
    # Partial matches (optional: if you don’t want "aqaid" inside "ilm-ul-kalam (aqaid)", remove this)
    if teacher_subj in available_subj or available_subj in teacher_subj:
        return True
    
    # Common spelling variations mapping
    variations = {
        "ilin": "ilm",
        "agaid": "aqaid", 
        "kalam": "kalām",
        "fiqh": "fiqh",
        "quran": "qur'an",
        "ul": "ul",
        "un": "un",
        "us": "us",
        "surf": "sarf",
        "koraz": "kanz",
        "hidaya": "hidāyah",
        "ahkam": "aḥkām",
        "sharia": "sharīʿah",
        "ilm ul": "ilm-ul",
        "ilm un": "ilm-un",
        "ilm us": "ilm-us"
    }
    
    # Replace common variations
    normalized_teacher = teacher_subj
    normalized_available = available_subj
    
    for wrong, correct in variations.items():
        normalized_teacher = normalized_teacher.replace(wrong, correct)
        normalized_available = normalized_available.replace(wrong, correct)
    
    # ✅ Strict match only (no "common words" fuzzy rule)
    return normalized_teacher == normalized_available


@app.get("/teacher_subjects/{user_id}")
def get_teacher_subjects(user_id: str):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        print(f"Looking for teacher with userID: {user_id}")  # Debug log
        
        # Search by userId instead of id
        cursor.execute("SELECT * FROM users WHERE userId = %s AND role = 'teacher'", (user_id,))
        teacher = cursor.fetchone()
        
        print(f"Query result: {teacher}")  # Debug log
        
        if not teacher:
            cursor.close()
            db.close()
            raise HTTPException(status_code=404, detail=f"Teacher not found with userID: {user_id}")
        
        teacher_subject = teacher.get("subject")
        print(f"Found teacher: {teacher['fullName']}, Subject: {teacher_subject}")  # Debug
        
        # Get all available subjects
        all_subjects_set = set()
        for year_subjects in predefined_subjects.values():
            for subject in year_subjects:
                all_subjects_set.add(subject["subject_name"])
        
        all_subjects_list = sorted(list(all_subjects_set))
        
        # Find matching subjects with flexible matching
        matched_subjects = []
        if teacher_subject:
            for subject in all_subjects_list:
                if is_subject_match(teacher_subject, subject):
                    matched_subjects.append(subject)
        
        cursor.close()
        db.close()
        
        return {
            "teacher_data": {
                "id": teacher["id"],
                "userId": teacher["userId"],
                "fullName": teacher["fullName"],
                "subject": teacher["subject"],
                "email": teacher["email"],
                "phone": teacher["phone"]
            },
            "teacher_subject": teacher_subject,
            "matched_subjects": matched_subjects,
            "all_subjects": all_subjects_list,
            "success": True
        }
        
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching teacher subjects: {str(e)}")

# Also update the other teacher endpoint
@app.get("/teacher/{user_id}")
def get_teacher_data(user_id: str):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Search by userId instead of id
        cursor.execute("SELECT * FROM users WHERE userId = %s AND role = 'teacher'", (user_id,))
        teacher = cursor.fetchone()
        
        if not teacher:
            raise HTTPException(status_code=404, detail=f"Teacher not found with userID: {user_id}")
        
        cursor.close()
        db.close()
        
        return {
            "teacher_data": teacher,
            "success": True
        }
        
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching teacher data: {str(e)}")

@app.get("/teachers")
def get_all_teachers():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Get all teachers from users table - CORRECTED COLUMN NAMES
        cursor.execute("SELECT id, userId, fullName, subject, email, phone FROM users WHERE role = 'teacher'")
        teachers = cursor.fetchall()
        
        cursor.close()
        db.close()
        
        return {
            "teachers": teachers,
            "success": True
        }
        
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching teachers: {str(e)}")

# Debug endpoint to check database structure
@app.get("/debug/database-structure")
def debug_database_structure():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Check users table structure
        cursor.execute("DESCRIBE users")
        users_structure = cursor.fetchall()
        
        # Check if any teachers exist
        cursor.execute("SELECT id, userId, fullName, subject, role FROM users WHERE role = 'teacher'")
        teachers = cursor.fetchall()
        
        cursor.close()
        db.close()
        
        return {
            "users_table_structure": users_structure,
            "existing_teachers": teachers,
            "total_teachers": len(teachers),
            "success": True
        }
        
    except Exception as e:
        return {"error": str(e), "success": False}

# Create sample teachers if needed (with correct column names)
@app.post("/create-sample-teachers")
def create_sample_teachers():
    """Create sample teachers for testing with correct column names"""

    try:
        db = get_db()
        cursor = db.cursor()
        
        sample_teachers = [
            ('T001', 'password123', 'Ahmed Khan', '1990-01-01', '1234567890', 'ahmed@example.com', 'Masters', 'Islamic Studies', 'Fiqh', 'Address 1', '2024', 'teacher'),
            ('T002', 'password123', 'Fatima Ali', '1985-05-15', '1234567891', 'fatima@example.com', 'PhD', 'Quranic Studies', 'Quran', 'Address 2', '2024', 'teacher'),
            ('T003', 'password123', 'Mohammed Hassan', '1988-08-20', '1234567892', 'mohammed@example.com', 'Masters', 'Theology', 'Aqaid', 'Address 3', '2024', 'teacher'),
        ]
        
        for teacher in sample_teachers:
            cursor.execute(
                """INSERT INTO users 
                (userId, password, fullName, dob, phone, email, education, qualification, subject, address, current_year, role) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                teacher
            )
        
        db.commit()
        cursor.close()
        db.close()
        
        return {"message": "Sample teachers created successfully", "success": True}
        
    except Exception as e:
        return {"error": str(e), "success": False}


#teacher courses and materials endpoints will go here

# ------------------- LECTURES ENDPOINTS -------------------

@app.post("/lectures")
async def create_lecture(
    teacher_id: str = Form(...),
    subject_name: str = Form(...),
    title: str = Form(...),
    description: str = Form(""),
    file: UploadFile = File(None)
):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # First, get the numeric ID from the users table using userId
        cursor.execute("SELECT id, userId, fullName FROM users WHERE userId = %s AND role = 'teacher'", (teacher_id,))
        teacher = cursor.fetchone()
        
        if not teacher:
            raise HTTPException(status_code=404, detail=f"Teacher not found with user ID: {teacher_id}")
        
        # Use the numeric ID for the foreign key
        numeric_teacher_id = teacher['id']
        
        file_path = None
        file_name = None
        file_size = 0
        
        if file and file.filename:
            # Create teacher directory using userId (for file organization)
            teacher_dir = os.path.join(UPLOAD_DIR, "lectures", teacher_id)
            os.makedirs(teacher_dir, exist_ok=True)
            
            # Save file
            file_extension = os.path.splitext(file.filename)[1]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"{timestamp}_{title.replace(' ', '_')}{file_extension}"
            file_path = os.path.join("uploads", "lectures", teacher_id, file_name)
            full_file_path = os.path.join(UPLOAD_DIR, "lectures", teacher_id, file_name)
            
            with open(full_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            file_size = os.path.getsize(full_file_path)
        
        # Insert using numeric teacher_id for foreign key
        cursor.execute(
            """INSERT INTO lectures 
            (teacher_id, subject_name, title, description, file_path, file_name, file_size) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (numeric_teacher_id, subject_name, title, description, file_path, file_name, file_size)
        )
        
        db.commit()
        cursor.close()
        db.close()
        
        return {
            "message": "Lecture created successfully", 
            "success": True,
            "teacher_name": teacher['fullName']
        }
        
    except mysql.connector.Error as e:
        if e.errno == 1452:
            raise HTTPException(status_code=400, detail=f"Database constraint error. Please contact administrator.")
        else:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating lecture: {str(e)}")

@app.get("/lectures/{teacher_userId}/{subject_name}")
def get_lectures(teacher_userId: str, subject_name: str):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute(
            """SELECT l.*, u.userId as teacher_userId, u.fullName as teacher_name
               FROM lectures l 
               JOIN users u ON l.teacher_id = u.id 
               WHERE u.userId = %s AND l.subject_name = %s 
               ORDER BY l.upload_date DESC""",
            (teacher_userId, subject_name)
        )
        
        lectures = cursor.fetchall()
        cursor.close()
        db.close()
        
        return {"lectures": lectures, "success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching lectures: {str(e)}")

@app.delete("/lectures/{lecture_id}")
def delete_lecture(lecture_id: int):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Get file path before deleting
        cursor.execute("SELECT file_path FROM lectures WHERE id = %s", (lecture_id,))
        lecture = cursor.fetchone()
        
        # Delete file from filesystem
        if lecture and lecture['file_path']:
            full_file_path = os.path.join(os.getcwd(), lecture['file_path'])
            if os.path.exists(full_file_path):
                os.remove(full_file_path)
        
        # Delete from database
        cursor.execute("DELETE FROM lectures WHERE id = %s", (lecture_id,))
        db.commit()
        cursor.close()
        db.close()
        
        return {"message": "Lecture deleted successfully", "success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting lecture: {str(e)}")

@app.post("/lectures/{lecture_id}/download")
def increment_download_count(lecture_id: int):
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute(
            "UPDATE lectures SET downloads = downloads + 1 WHERE id = %s",
            (lecture_id,)
        )
        
        db.commit()
        cursor.close()
        db.close()
        
        return {"message": "Download count updated", "success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating download count: {str(e)}")

# ------------------- ASSIGNMENTS ENDPOINTS -------------------

@app.post("/assignments")
async def create_assignment(
    teacher_id: str = Form(...),
    subject_name: str = Form(...),
    title: str = Form(...),
    description: str = Form(""),
    start_date: str = Form(...),
    due_date: str = Form(...),
    file: UploadFile = File(None)
):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Get numeric ID from users table
        cursor.execute("SELECT id, userId, fullName FROM users WHERE userId = %s AND role = 'teacher'", (teacher_id,))
        teacher = cursor.fetchone()
        
        if not teacher:
            raise HTTPException(status_code=404, detail=f"Teacher not found with user ID: {teacher_id}")
        
        numeric_teacher_id = teacher['id']
        
        file_path = None
        file_name = None
        
        if file and file.filename:
            teacher_dir = os.path.join(UPLOAD_DIR, "assignments", teacher_id)
            os.makedirs(teacher_dir, exist_ok=True)
            
            file_extension = os.path.splitext(file.filename)[1]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"{timestamp}_{title.replace(' ', '_')}{file_extension}"
            file_path = os.path.join("uploads", "assignments", teacher_id, file_name)
            full_file_path = os.path.join(UPLOAD_DIR, "assignments", teacher_id, file_name)
            
            with open(full_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        
        cursor.execute(
            """INSERT INTO assignments 
            (teacher_id, subject_name, title, description, file_path, file_name, start_date, due_date) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (numeric_teacher_id, subject_name, title, description, file_path, file_name, start_date, due_date)
        )
        
        db.commit()
        cursor.close()
        db.close()
        
        return {
            "message": "Assignment created successfully", 
            "success": True,
            "teacher_name": teacher['fullName']
        }
        
    except mysql.connector.Error as e:
        if e.errno == 1452:
            raise HTTPException(status_code=400, detail=f"Database constraint error. Please contact administrator.")
        else:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating assignment: {str(e)}")

@app.get("/assignments/{teacher_userId}/{subject_name}")
def get_assignments(teacher_userId: str, subject_name: str):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute(
            """SELECT a.*, u.userId as teacher_userId, u.fullName as teacher_name
               FROM assignments a 
               JOIN users u ON a.teacher_id = u.id 
               WHERE u.userId = %s AND a.subject_name = %s 
               ORDER BY a.created_date DESC""",
            (teacher_userId, subject_name)
        )
        
        assignments = cursor.fetchall()
        cursor.close()
        db.close()
        
        return {"assignments": assignments, "success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching assignments: {str(e)}")

@app.delete("/assignments/{assignment_id}")
def delete_assignment(assignment_id: int):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Get file path before deleting
        cursor.execute("SELECT file_path FROM assignments WHERE id = %s", (assignment_id,))
        assignment = cursor.fetchone()
        
        # Delete file from filesystem
        if assignment and assignment['file_path']:
            full_file_path = os.path.join(os.getcwd(), assignment['file_path'])
            if os.path.exists(full_file_path):
                os.remove(full_file_path)
        
        # Delete from database
        cursor.execute("DELETE FROM assignments WHERE id = %s", (assignment_id,))
        db.commit()
        cursor.close()
        db.close()
        
        return {"message": "Assignment deleted successfully", "success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting assignment: {str(e)}")

# ------------------- NOTIFICATIONS ENDPOINTS -------------------

@app.post("/notifications")
async def create_notification(
    teacher_id: str = Form(...),
    subject_name: str = Form(...),
    title: str = Form(...),
    message: str = Form(...),
    priority: str = Form("medium")
):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Get numeric ID from users table
        cursor.execute("SELECT id, userId, fullName FROM users WHERE userId = %s AND role = 'teacher'", (teacher_id,))
        teacher = cursor.fetchone()
        
        if not teacher:
            raise HTTPException(status_code=404, detail=f"Teacher not found with user ID: {teacher_id}")
        
        numeric_teacher_id = teacher['id']
        
        cursor.execute(
            """INSERT INTO notifications 
            (teacher_id, subject_name, title, message, priority) 
            VALUES (%s, %s, %s, %s, %s)""",
            (numeric_teacher_id, subject_name, title, message, priority)
        )
        
        db.commit()
        cursor.close()
        db.close()
        
        return {
            "message": "Notification created successfully", 
            "success": True,
            "teacher_name": teacher['fullName']
        }
        
    except mysql.connector.Error as e:
        if e.errno == 1452:
            raise HTTPException(status_code=400, detail=f"Database constraint error. Please contact administrator.")
        else:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating notification: {str(e)}")

@app.get("/notifications/{teacher_userId}/{subject_name}")
def get_notifications(teacher_userId: str, subject_name: str):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute(
            """SELECT n.*, u.userId as teacher_userId, u.fullName as teacher_name
               FROM notifications n 
               JOIN users u ON n.teacher_id = u.id 
               WHERE u.userId = %s AND n.subject_name = %s 
               ORDER BY n.created_date DESC""",
            (teacher_userId, subject_name)
        )
        
        notifications = cursor.fetchall()
        cursor.close()
        db.close()
        
        return {"notifications": notifications, "success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching notifications: {str(e)}")

@app.delete("/notifications/{notification_id}")
def delete_notification(notification_id: int):
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("DELETE FROM notifications WHERE id = %s", (notification_id,))
        db.commit()
        cursor.close()
        db.close()
        
        return {"message": "Notification deleted successfully", "success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting notification: {str(e)}")

# ------------------- QUIZZES ENDPOINTS -------------------

@app.post("/quizzes")
async def create_quiz(
    teacher_id: str = Form(...),
    subject_name: str = Form(...),
    title: str = Form(...),
    description: str = Form(""),
    start_date: str = Form(...),
    end_date: str = Form(...),
    total_marks: int = Form(100),
    questions_count: int = Form(10),
    duration_minutes: int = Form(30)
):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Get numeric ID from users table
        cursor.execute("SELECT id, userId, fullName FROM users WHERE userId = %s AND role = 'teacher'", (teacher_id,))
        teacher = cursor.fetchone()
        
        if not teacher:
            raise HTTPException(status_code=404, detail=f"Teacher not found with user ID: {teacher_id}")
        
        numeric_teacher_id = teacher['id']
        
        cursor.execute(
            """INSERT INTO quizzes 
            (teacher_id, subject_name, title, description, start_date, end_date, total_marks, questions_count, duration_minutes) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (numeric_teacher_id, subject_name, title, description, start_date, end_date, total_marks, questions_count, duration_minutes)
        )
        
        db.commit()
        cursor.close()
        db.close()
        
        return {
            "message": "Quiz created successfully", 
            "success": True,
            "teacher_name": teacher['fullName']
        }
        
    except mysql.connector.Error as e:
        if e.errno == 1452:
            raise HTTPException(status_code=400, detail=f"Database constraint error. Please contact administrator.")
        else:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating quiz: {str(e)}")

@app.get("/quizzes/{teacher_userId}/{subject_name}")
def get_quizzes(teacher_userId: str, subject_name: str):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute(
            """SELECT q.*, u.userId as teacher_userId, u.fullName as teacher_name
               FROM quizzes q 
               JOIN users u ON q.teacher_id = u.id 
               WHERE u.userId = %s AND q.subject_name = %s 
               ORDER BY q.created_date DESC""",
            (teacher_userId, subject_name)
        )
        
        quizzes = cursor.fetchall()
        cursor.close()
        db.close()
        
        return {"quizzes": quizzes, "success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching quizzes: {str(e)}")

@app.get("/quiz/{quiz_id}")
def get_quiz(quiz_id: int):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute(
            """SELECT * FROM quizzes WHERE id = %s""",
            (quiz_id,)
        )
        
        quiz = cursor.fetchone()
        cursor.close()
        db.close()
        
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        return {"quiz": quiz, "success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching quiz: {str(e)}")

@app.delete("/quizzes/{quiz_id}")
def delete_quiz(quiz_id: int):
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("DELETE FROM quizzes WHERE id = %s", (quiz_id,))
        db.commit()
        cursor.close()
        db.close()
        
        return {"message": "Quiz deleted successfully", "success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting quiz: {str(e)}")

# ------------------- FILE DOWNLOAD ENDPOINT -------------------

@app.get("/download/{file_type}/{teacher_id}/{filename}")
async def download_file(file_type: str, teacher_id: str, filename: str):
    """
    Download files securely
    file_type: lectures, assignments
    """
    try:
        # Security check - prevent directory traversal
        if ".." in filename or "/" in filename or "\\" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        file_path = os.path.join(UPLOAD_DIR, file_type, teacher_id, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Return file for download
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/octet-stream'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")

# ------------------- STATISTICS ENDPOINTS -------------------

@app.get("/teacher/{teacher_id}/stats")
def get_teacher_stats(teacher_id: str):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Get counts for different content types
        cursor.execute("SELECT COUNT(*) as lecture_count FROM lectures WHERE teacher_id = %s", (teacher_id,))
        lecture_count = cursor.fetchone()['lecture_count']
        
        cursor.execute("SELECT COUNT(*) as assignment_count FROM assignments WHERE teacher_id = %s", (teacher_id,))
        assignment_count = cursor.fetchone()['assignment_count']
        
        cursor.execute("SELECT COUNT(*) as quiz_count FROM quizzes WHERE teacher_id = %s", (teacher_id,))
        quiz_count = cursor.fetchone()['quiz_count']
        
        cursor.execute("SELECT COUNT(*) as notification_count FROM notifications WHERE teacher_id = %s", (teacher_id,))
        notification_count = cursor.fetchone()['notification_count']
        
        # Get total downloads
        cursor.execute("SELECT SUM(downloads) as total_downloads FROM lectures WHERE teacher_id = %s", (teacher_id,))
        total_downloads = cursor.fetchone()['total_downloads'] or 0
        
        cursor.close()
        db.close()
        
        return {
            "stats": {
                "lecture_count": lecture_count,
                "assignment_count": assignment_count,
                "quiz_count": quiz_count,
                "notification_count": notification_count,
                "total_downloads": total_downloads
            },
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching teacher stats: {str(e)}")

# ------------------- GENERAL GET ENDPOINTS -------------------

@app.get("/lectures")
def get_all_lectures():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute(
            """SELECT l.*, u.userId as teacher_userId, u.fullName as teacher_name
               FROM lectures l 
               JOIN users u ON l.teacher_id = u.id 
               ORDER BY l.upload_date DESC"""
        )
        
        lectures = cursor.fetchall()
        cursor.close()
        db.close()
        
        return {"lectures": lectures, "success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching lectures: {str(e)}")

@app.get("/assignments")
def get_all_assignments():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute(
            """SELECT a.*, u.userId as teacher_userId, u.fullName as teacher_name
               FROM assignments a 
               JOIN users u ON a.teacher_id = u.id 
               ORDER BY a.created_date DESC"""
        )
        
        assignments = cursor.fetchall()
        cursor.close()
        db.close()
        
        return {"assignments": assignments, "success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching assignments: {str(e)}")

@app.get("/notifications")
def get_all_notifications():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute(
            """SELECT n.*, u.userId as teacher_userId, u.fullName as teacher_name
               FROM notifications n 
               JOIN users u ON n.teacher_id = u.id 
               ORDER BY n.created_date DESC"""
        )
        
        notifications = cursor.fetchall()
        cursor.close()
        db.close()
        
        return {"notifications": notifications, "success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching notifications: {str(e)}")

@app.get("/quizzes")
def get_all_quizzes():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute(
            """SELECT q.*, u.userId as teacher_userId, u.fullName as teacher_name
               FROM quizzes q 
               JOIN users u ON q.teacher_id = u.id 
               ORDER BY q.created_date DESC"""
        )
        
        quizzes = cursor.fetchall()
        cursor.close()
        db.close()
        
        return {"quizzes": quizzes, "success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching quizzes: {str(e)}")

# NEW ENDPOINT - Exact subject matching for student courses
@app.get("/student_subjects/{year_id}")
def get_student_subjects_with_teachers(year_id: int):
    """Get subjects for students with exact teacher matching"""
    try:
        # Get predefined subjects for the year
        if year_id not in predefined_subjects:
            raise HTTPException(status_code=404, detail=f"No predefined subjects found for year {year_id}")
        
        subjects_data = predefined_subjects[year_id]
        
        # Get all teachers
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT userId, fullName, subject FROM users WHERE role = 'teacher'")
        all_teachers = cursor.fetchall()
        cursor.close()
        db.close()
        
        # Function for exact matching
        def exact_subject_match(teacher_subject, target_subject):
            if not teacher_subject or not target_subject:
                return False
            
            # Normalize both subjects
            teacher_norm = teacher_subject.lower().strip()
            target_norm = target_subject.lower().strip()
            
            # Remove punctuation and extra spaces
            import string
            teacher_norm = teacher_norm.translate(str.maketrans('', '', string.punctuation))
            target_norm = target_norm.translate(str.maketrans('', '', string.punctuation))
            
            teacher_norm = ' '.join(teacher_norm.split())
            target_norm = ' '.join(target_norm.split())
            
            # EXACT MATCH ONLY
            return teacher_norm == target_norm
        
        # Prepare result with teachers for each subject
        result_subjects = []
        for subject in subjects_data:
            subject_name = subject["subject_name"]
            matched_teachers = []
            
            # Find teachers that exactly match this subject
            for teacher in all_teachers:
                teacher_subject = teacher.get("subject", "")
                if teacher_subject:
                    # Handle multiple subjects (comma-separated)
                    teacher_subjects = [s.strip() for s in teacher_subject.split(',')]
                    for ts in teacher_subjects:
                        if exact_subject_match(ts, subject_name):
                            matched_teachers.append({
                                "userId": teacher["userId"],
                                "fullName": teacher["fullName"],
                                "subject": teacher["subject"]
                            })
                            break  # No need to check other subjects for this teacher
            
            result_subjects.append({
                "subject_name": subject_name,
                "duration_months": subject["duration_months"],
                "teachers": matched_teachers,
                "teacher_count": len(matched_teachers)
            })
        
        return {
            "subjects": result_subjects,
            "year_id": year_id,
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching student subjects: {str(e)}")

# NEW ENDPOINT - Get subject statistics for student view
@app.get("/subject_stats/{subject_name}")
def get_subject_stats(subject_name: str):
    """Get statistics for a specific subject"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Get lectures count
        cursor.execute("SELECT COUNT(*) as count FROM lectures WHERE subject_name = %s", (subject_name,))
        lecture_count = cursor.fetchone()['count']
        
        # Get assignments count
        cursor.execute("SELECT COUNT(*) as count FROM assignments WHERE subject_name = %s", (subject_name,))
        assignment_count = cursor.fetchone()['count']
        
        # Get quizzes count
        cursor.execute("SELECT COUNT(*) as count FROM quizzes WHERE subject_name = %s", (subject_name,))
        quiz_count = cursor.fetchone()['count']
        
        # Get notifications count
        cursor.execute("SELECT COUNT(*) as count FROM notifications WHERE subject_name = %s", (subject_name,))
        notification_count = cursor.fetchone()['count']
        
        cursor.close()
        db.close()
        
        return {
            "subject_name": subject_name,
            "stats": {
                "lectures": lecture_count,
                "assignments": assignment_count,
                "quizzes": quiz_count,
                "notifications": notification_count
            },
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching subject stats: {str(e)}")


# ------------------- MATERIALS ENDPOINTS -------------------

@app.post("/materials")
async def create_material(
    teacher_id: str = Form(...),
    subject_name: str = Form(...),
    title: str = Form(...),
    description: str = Form(""),
    material_type: str = Form("other"),
    file: UploadFile = File(None)
):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # First, get the numeric ID from the users table using userId
        cursor.execute("SELECT id, userId, fullName FROM users WHERE userId = %s AND role = 'teacher'", (teacher_id,))
        teacher = cursor.fetchone()
        
        if not teacher:
            raise HTTPException(status_code=404, detail=f"Teacher not found with user ID: {teacher_id}")
        
        # Use the numeric ID for the foreign key
        numeric_teacher_id = teacher['id']
        
        file_path = None
        file_name = None
        file_size = 0
        
        if file and file.filename:
            # Create teacher directory using userId (for file organization)
            teacher_dir = os.path.join(UPLOAD_DIR, "materials", teacher_id)
            os.makedirs(teacher_dir, exist_ok=True)
            
            # Save file
            file_extension = os.path.splitext(file.filename)[1]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"{timestamp}_{title.replace(' ', '_')}{file_extension}"
            file_path = os.path.join("uploads", "materials", teacher_id, file_name)
            full_file_path = os.path.join(UPLOAD_DIR, "materials", teacher_id, file_name)
            
            with open(full_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            file_size = os.path.getsize(full_file_path)
        
        # Insert using numeric teacher_id for foreign key
        cursor.execute(
            """INSERT INTO materials 
            (teacher_id, subject_name, title, description, file_path, file_name, file_size, material_type) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (numeric_teacher_id, subject_name, title, description, file_path, file_name, file_size, material_type)
        )
        
        db.commit()
        cursor.close()
        db.close()
        
        return {
            "message": "Material uploaded successfully", 
            "success": True,
            "teacher_name": teacher['fullName']
        }
        
    except mysql.connector.Error as e:
        if e.errno == 1452:
            raise HTTPException(status_code=400, detail=f"Database constraint error. Please contact administrator.")
        else:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading material: {str(e)}")

@app.get("/materials/{teacher_userId}/{subject_name}")
def get_materials(teacher_userId: str, subject_name: str):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute(
            """SELECT m.*, u.userId as teacher_userId, u.fullName as teacher_name
               FROM materials m 
               JOIN users u ON m.teacher_id = u.id 
               WHERE u.userId = %s AND m.subject_name = %s 
               ORDER BY m.upload_date DESC""",
            (teacher_userId, subject_name)
        )
        
        materials = cursor.fetchall()
        cursor.close()
        db.close()
        
        return {"materials": materials, "success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching materials: {str(e)}")

@app.get("/materials")
def get_all_materials():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute(
            """SELECT m.*, u.userId as teacher_userId, u.fullName as teacher_name
               FROM materials m 
               JOIN users u ON m.teacher_id = u.id 
               ORDER BY m.upload_date DESC"""
        )
        
        materials = cursor.fetchall()
        cursor.close()
        db.close()
        
        return {"materials": materials, "success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching materials: {str(e)}")

@app.delete("/materials/{material_id}")
def delete_material(material_id: int):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Get file path before deleting
        cursor.execute("SELECT file_path FROM materials WHERE id = %s", (material_id,))
        material = cursor.fetchone()
        
        # Delete file from filesystem
        if material and material['file_path']:
            full_file_path = os.path.join(os.getcwd(), material['file_path'])
            if os.path.exists(full_file_path):
                os.remove(full_file_path)
        
        # Delete from database
        cursor.execute("DELETE FROM materials WHERE id = %s", (material_id,))
        db.commit()
        cursor.close()
        db.close()
        
        return {"message": "Material deleted successfully", "success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting material: {str(e)}")

@app.post("/materials/{material_id}/download")
def increment_material_download_count(material_id: int):
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute(
            "UPDATE materials SET downloads = downloads + 1 WHERE id = %s",
            (material_id,)
        )
        
        db.commit()
        cursor.close()
        db.close()
        
        return {"message": "Download count updated", "success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating download count: {str(e)}")

# ------------------- ALL MATERIALS ENDPOINT (for teachers to download everything) -------------------

@app.get("/all_materials/{teacher_userId}/{subject_name}")
def get_all_course_materials(teacher_userId: str, subject_name: str):
    """Get all materials (lectures, assignments, materials) for a subject"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Get teacher's numeric ID
        cursor.execute("SELECT id FROM users WHERE userId = %s", (teacher_userId,))
        teacher = cursor.fetchone()
        
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher not found")
        
        numeric_teacher_id = teacher['id']
        
        # Get lectures
        cursor.execute(
            """SELECT 
                id, 
                'lecture' as type, 
                title, 
                description, 
                file_path, 
                file_name, 
                upload_date,
                downloads,
                NULL as due_date,
                NULL as material_type
               FROM lectures 
               WHERE teacher_id = %s AND subject_name = %s""",
            (numeric_teacher_id, subject_name)
        )
        lectures = cursor.fetchall()
        
        # Get assignments
        cursor.execute(
            """SELECT 
                id, 
                'assignment' as type, 
                title, 
                description, 
                file_path, 
                file_name, 
                created_date as upload_date,
                0 as downloads,
                due_date,
                NULL as material_type
               FROM assignments 
               WHERE teacher_id = %s AND subject_name = %s""",
            (numeric_teacher_id, subject_name)
        )
        assignments = cursor.fetchall()
        
        # Get materials
        cursor.execute(
            """SELECT 
                id, 
                'material' as type, 
                title, 
                description, 
                file_path, 
                file_name, 
                upload_date,
                downloads,
                NULL as due_date,
                material_type
               FROM materials 
               WHERE teacher_id = %s AND subject_name = %s""",
            (numeric_teacher_id, subject_name)
        )
        materials = cursor.fetchall()
        
        cursor.close()
        db.close()
        
        # Combine all materials
        all_materials = lectures + assignments + materials
        
        # Sort by upload date (most recent first)
        all_materials.sort(key=lambda x: x['upload_date'], reverse=True)
        
        return {
            "materials": all_materials,
            "total_count": len(all_materials),
            "lecture_count": len(lectures),
            "assignment_count": len(assignments),
            "material_count": len(materials),
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching all materials: {str(e)}")


# ------------------- MATERIALS ENDPOINTS -------------------

@app.post("/materials")
async def create_material(
    teacher_id: str = Form(...),
    subject_name: str = Form(...),
    title: str = Form(...),
    description: str = Form(""),
    material_type: str = Form("other"),
    file: UploadFile = File(None)
):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # First, get the numeric ID from the users table using userId
        cursor.execute("SELECT id, userId, fullName FROM users WHERE userId = %s AND role = 'teacher'", (teacher_id,))
        teacher = cursor.fetchone()
        
        if not teacher:
            raise HTTPException(status_code=404, detail=f"Teacher not found with user ID: {teacher_id}")
        
        # Use the numeric ID for the foreign key
        numeric_teacher_id = teacher['id']
        
        file_path = None
        file_name = None
        file_size = 0
        
        if file and file.filename:
            # Create teacher directory using userId (for file organization)
            teacher_dir = os.path.join(UPLOAD_DIR, "materials", teacher_id)
            os.makedirs(teacher_dir, exist_ok=True)
            
            # Save file
            file_extension = os.path.splitext(file.filename)[1]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"{timestamp}_{title.replace(' ', '_')}{file_extension}"
            file_path = os.path.join("uploads", "materials", teacher_id, file_name)
            full_file_path = os.path.join(UPLOAD_DIR, "materials", teacher_id, file_name)
            
            with open(full_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            file_size = os.path.getsize(full_file_path)
        
        # Insert using numeric teacher_id for foreign key
        cursor.execute(
            """INSERT INTO materials 
            (teacher_id, subject_name, title, description, file_path, file_name, file_size, material_type) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (numeric_teacher_id, subject_name, title, description, file_path, file_name, file_size, material_type)
        )
        
        db.commit()
        cursor.close()
        db.close()
        
        return {
            "message": "Material uploaded successfully", 
            "success": True,
            "teacher_name": teacher['fullName']
        }
        
    except mysql.connector.Error as e:
        if e.errno == 1452:
            raise HTTPException(status_code=400, detail=f"Database constraint error. Please contact administrator.")
        else:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading material: {str(e)}")

@app.get("/materials/{teacher_userId}/{subject_name}")
def get_materials(teacher_userId: str, subject_name: str):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute(
            """SELECT m.*, u.userId as teacher_userId, u.fullName as teacher_name
               FROM materials m 
               JOIN users u ON m.teacher_id = u.id 
               WHERE u.userId = %s AND m.subject_name = %s 
               ORDER BY m.upload_date DESC""",
            (teacher_userId, subject_name)
        )
        
        materials = cursor.fetchall()
        cursor.close()
        db.close()
        
        return {"materials": materials, "success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching materials: {str(e)}")

# NEW ENDPOINT: Get materials for students by subject
@app.get("/student_materials/{subject_name}")
def get_student_materials(subject_name: str):
    """Get all materials for a subject (for students)"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute(
            """SELECT m.*, u.userId as teacher_userId, u.fullName as teacher_name
               FROM materials m 
               JOIN users u ON m.teacher_id = u.id 
               WHERE m.subject_name = %s 
               ORDER BY m.upload_date DESC""",
            (subject_name,)
        )
        
        materials = cursor.fetchall()
        cursor.close()
        db.close()
        
        return {"materials": materials, "success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching materials: {str(e)}")

@app.get("/materials")
def get_all_materials():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute(
            """SELECT m.*, u.userId as teacher_userId, u.fullName as teacher_name
               FROM materials m 
               JOIN users u ON m.teacher_id = u.id 
               ORDER BY m.upload_date DESC"""
        )
        
        materials = cursor.fetchall()
        cursor.close()
        db.close()
        
        return {"materials": materials, "success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching materials: {str(e)}")

@app.delete("/materials/{material_id}")
def delete_material(material_id: int):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Get file path before deleting
        cursor.execute("SELECT file_path FROM materials WHERE id = %s", (material_id,))
        material = cursor.fetchone()
        
        # Delete file from filesystem
        if material and material['file_path']:
            full_file_path = os.path.join(os.getcwd(), material['file_path'])
            if os.path.exists(full_file_path):
                os.remove(full_file_path)
        
        # Delete from database
        cursor.execute("DELETE FROM materials WHERE id = %s", (material_id,))
        db.commit()
        cursor.close()
        db.close()
        
        return {"message": "Material deleted successfully", "success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting material: {str(e)}")

@app.post("/materials/{material_id}/download")
def increment_material_download_count(material_id: int):
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute(
            "UPDATE materials SET downloads = downloads + 1 WHERE id = %s",
            (material_id,)
        )
        
        db.commit()
        cursor.close()
        db.close()
        
        return {"message": "Download count updated", "success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating download count: {str(e)}")



# ------------------- FILE PATH RESOLUTION FUNCTIONS FOR LECTURES -------------------


def fix_file_path(file_path, teacher_id):
    """Fix common file path issues with enhanced logic"""
    if not file_path or file_path == 'NULL':
        return None
    
    path = file_path
    
    # Apply common fixes
    fixes = [
        ('uploadselectures', 'uploads/lectures'),
        ('uploadsassignments', 'uploads/assignments'),
        ('uploadsmaterials', 'uploads/materials'),
        ('@', '/'),
        ('teacher_harma', 'teacher_hamna'),
        ('teacher_harma_5674', 'teacher_hamna_5674'),
        ('//', '/'),
        ('\\', '/'),  # Convert backslashes to forward slashes
    ]
    
    for wrong, correct in fixes:
        path = path.replace(wrong, correct)
    
    # Ensure it's a proper path
    if not path.startswith('uploads/'):
        # Try to reconstruct the path
        if 'lectures' in path:
            path = f"uploads/lectures/{path}"
        elif 'assignments' in path:
            path = f"uploads/assignments/{path}"
        elif 'materials' in path:
            path = f"uploads/materials/{path}"
        else:
            path = f"uploads/lectures/{path}"
    
    # Clean up the path
    path = os.path.normpath(path).replace('\\', '/')
    
    return path

def search_file_by_name(filename, teacher_id):
    """Enhanced file search with multiple strategies"""
    if not filename:
        return None
    
    search_dirs = [
        f"uploads/lectures/teacher_{teacher_id}",
        f"uploads/lectures/teacher_{teacher_id}_5674",
        f"uploads/lectures/{teacher_id}",
        "uploads/lectures",
        f"uploads/lectures/teacher_{teacher_id.lower()}",
        f"uploads/lectures/teacher_{teacher_id.upper()}",
    ]
    
    # Strategy 1: Exact match
    for search_dir in search_dirs:
        if not os.path.exists(search_dir):
            continue
        
        exact_path = os.path.join(search_dir, filename)
        if os.path.exists(exact_path):
            return exact_path
    
    # Strategy 2: Case-insensitive match
    for search_dir in search_dirs:
        if not os.path.exists(search_dir):
            continue
        
        try:
            for file in os.listdir(search_dir):
                if file.lower() == filename.lower():
                    return os.path.join(search_dir, file)
        except OSError:
            continue
    
    # Strategy 3: Partial filename match
    filename_without_ext = os.path.splitext(filename)[0]
    for search_dir in search_dirs:
        if not os.path.exists(search_dir):
            continue
        
        try:
            for file in os.listdir(search_dir):
                if filename_without_ext.lower() in file.lower():
                    return os.path.join(search_dir, file)
        except OSError:
            continue
    
    return None

def search_file_by_name(filename, teacher_id):
    """Search for file by name in teacher directories"""
    search_dirs = [
        f"uploads/lectures/teacher_{teacher_id}",
        f"uploads/lectures/teacher_{teacher_id}_5674",
        "uploads/lectures",
    ]
    
    for search_dir in search_dirs:
        if not os.path.exists(search_dir):
            continue
        
        # Exact match
        exact_path = os.path.join(search_dir, filename)
        if os.path.exists(exact_path):
            return exact_path
        
        # Case-insensitive match
        try:
            for file in os.listdir(search_dir):
                if file.lower() == filename.lower():
                    return os.path.join(search_dir, file)
        except OSError:
            continue
    
    return None

def find_any_teacher_file(teacher_id):
    """Find any file in teacher's directory as fallback"""
    teacher_dirs = [
        f"uploads/lectures/teacher_{teacher_id}",
        f"uploads/lectures/teacher_{teacher_id}_5674",
    ]
    
    for teacher_dir in teacher_dirs:
        if os.path.exists(teacher_dir):
            try:
                files = os.listdir(teacher_dir)
                if files:
                    first_file = files[0]
                    return {
                        'path': os.path.join(teacher_dir, first_file),
                        'name': first_file
                    }
            except OSError:
                continue
    
    return None

def search_with_different_extensions(filename, teacher_id):
    """Search for file with different extensions"""
    name_without_ext = os.path.splitext(filename)[0]
    extensions = ['.mp4', '.MP4', '.pdf', '.PDF', '.doc', '.DOC', '.docx', '.DOCX']
    
    search_dirs = [
        f"uploads/lectures/teacher_{teacher_id}",
        f"uploads/lectures/teacher_{teacher_id}_5674",
    ]
    
    for search_dir in search_dirs:
        if not os.path.exists(search_dir):
            continue
        
        for ext in extensions:
            test_filename = f"{name_without_ext}{ext}"
            test_path = os.path.join(search_dir, test_filename)
            if os.path.exists(test_path):
                return test_path
    
    return None

def find_actual_lecture_file(lecture, teacher_id):
    """Find the actual file location with multiple fallback strategies"""
    
    # Strategy 1: Check the path from database
    db_path = lecture.get('file_path')
    db_filename = lecture.get('file_name')
    
    if db_path and db_path != 'NULL':
        # Fix common path issues
        fixed_path = fix_file_path(db_path, teacher_id)
        if fixed_path and os.path.exists(fixed_path):
            return {
                'exists': True,
                'actual_path': fixed_path,
                'url': f"http://localhost:8000/{fixed_path}",
                'status': 'found'
            }
    
    # Strategy 2: Search by filename in teacher directories
    if db_filename and db_filename != 'NULL':
        found_path = search_file_by_name(db_filename, teacher_id)
        if found_path:
            return {
                'exists': True,
                'actual_path': found_path,
                'url': f"http://localhost:8000/{found_path}",
                'status': 'found_by_search'
            }
    
    # Strategy 3: Search any file in teacher directories (fallback)
    any_file = find_any_teacher_file(teacher_id)
    if any_file:
        return {
            'exists': True,
            'actual_path': any_file['path'],
            'url': f"http://localhost:8000/{any_file['path']}",
            'status': 'found_any_file'
        }
    
    # Strategy 4: Check if file exists with different extensions
    if db_filename:
        found_with_extension = search_with_different_extensions(db_filename, teacher_id)
        if found_with_extension:
            return {
                'exists': True,
                'actual_path': found_with_extension,
                'url': f"http://localhost:8000/{found_with_extension}",
                'status': 'found_different_extension'
            }
    
    return {
        'exists': False,
        'actual_path': None,
        'url': None,
        'status': 'not_found'
    }

# ------------------- ENHANCED LECTURE ENDPOINTS -------------------

# Replace your existing get_lectures endpoint with this enhanced version
@app.get("/lectures/{teacher_userId}/{subject_name}")
def get_lectures(teacher_userId: str, subject_name: str):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute(
            """SELECT l.*, u.userId as teacher_userId, u.fullName as teacher_name
               FROM lectures l 
               JOIN users u ON l.teacher_id = u.id 
               WHERE u.userId = %s AND l.subject_name = %s 
               ORDER BY l.upload_date DESC""",
            (teacher_userId, subject_name)
        )
        
        lectures = cursor.fetchall()
        
        # Process lectures to add file existence info
        processed_lectures = []
        for lecture in lectures:
            lecture_dict = dict(lecture)
            file_info = find_actual_lecture_file(lecture_dict, teacher_userId)
            lecture_dict['file_exists'] = file_info['exists']
            lecture_dict['file_status'] = file_info['status']
            lecture_dict['resolved_file_url'] = file_info['url']
            processed_lectures.append(lecture_dict)
        
        cursor.close()
        db.close()
        
        return {
            "lectures": processed_lectures, 
            "success": True,
            "file_check_summary": {
                "total": len(processed_lectures),
                "exists": sum(1 for l in processed_lectures if l['file_exists']),
                "missing": sum(1 for l in processed_lectures if not l['file_exists'])
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching lectures: {str(e)}")

# NEW ENDPOINT: Enhanced lecture streaming with file resolution
@app.get("/lectures/{lecture_id}/stream")
def stream_lecture_file(lecture_id: int):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Get lecture from database
        cursor.execute("SELECT * FROM lectures WHERE id = %s", (lecture_id,))
        lecture = cursor.fetchone()
        
        if not lecture:
            raise HTTPException(status_code=404, detail="Lecture not found")
        
        # Get teacher_id for file resolution
        cursor.execute("SELECT userId FROM users WHERE id = %s", (lecture['teacher_id'],))
        teacher = cursor.fetchone()
        teacher_id = teacher['userId'] if teacher else None
        
        file_info = find_actual_lecture_file(lecture, teacher_id)
        
        if not file_info['exists']:
            raise HTTPException(
                status_code=404, 
                detail=f"Lecture file not found. Status: {file_info['status']}"
            )
        
        cursor.close()
        db.close()
        
        return FileResponse(
            file_info['actual_path'],
            media_type='application/octet-stream',
            filename=lecture.get('file_name') or f"lecture_{lecture_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error streaming lecture: {str(e)}")

# NEW ENDPOINT: Enhanced lecture download with file resolution
@app.get("/lectures/{lecture_id}/download")
def download_lecture_file(lecture_id: int):
    """Enhanced download endpoint with file existence check"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Get lecture from database
        cursor.execute("SELECT * FROM lectures WHERE id = %s", (lecture_id,))
        lecture = cursor.fetchone()
        
        if not lecture:
            raise HTTPException(status_code=404, detail="Lecture not found")
        
        # Get teacher_id for file resolution
        cursor.execute("SELECT userId FROM users WHERE id = %s", (lecture['teacher_id'],))
        teacher = cursor.fetchone()
        teacher_id = teacher['userId'] if teacher else None
        
        file_info = find_actual_lecture_file(lecture, teacher_id)
        
        if not file_info['exists']:
            raise HTTPException(
                status_code=404, 
                detail=f"Lecture file not found. Status: {file_info['status']}"
            )
        
        # Update download count
        cursor.execute(
            "UPDATE lectures SET downloads = downloads + 1 WHERE id = %s",
            (lecture_id,)
        )
        db.commit()
        
        cursor.close()
        db.close()
        
        return FileResponse(
            file_info['actual_path'],
            media_type='application/octet-stream',
            filename=lecture.get('file_name') or f"lecture_{lecture_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading lecture: {str(e)}")

# NEW ENDPOINT: Diagnostic endpoint to check uploads structure
@app.get("/admin/check-uploads")
def check_uploads_directory():
    """Check what files actually exist in uploads directory"""
    base_path = "uploads/lectures"
    
    if not os.path.exists(base_path):
        return {
            "success": False,
            "message": "Base uploads directory doesn't exist",
            "suggested_fix": "Create the directory structure: mkdir -p uploads/lectures"
        }
    
    # Walk through all directories and files
    all_files = {}
    for root, dirs, files in os.walk(base_path):
        relative_path = root.replace(base_path, "").lstrip('/')
        all_files[relative_path or '/'] = files
    
    return {
        "success": True,
        "base_path": base_path,
        "exists": os.path.exists(base_path),
        "files_structure": all_files
    }

# NEW ENDPOINT: Check files for specific teacher
@app.get("/admin/check-teacher-files/{teacher_id}")
def check_teacher_files(teacher_id: str):
    """Check files for a specific teacher"""
    possible_dirs = [
        f"uploads/lectures/teacher_{teacher_id}",
        f"uploads/lectures/teacher_{teacher_id}_5674",
        f"uploads/lectures/{teacher_id}",
    ]
    
    results = {}
    for directory in possible_dirs:
        exists = os.path.exists(directory)
        files = []
        if exists:
            try:
                files = os.listdir(directory)
            except Exception as e:
                files = [f"Error: {str(e)}"]
        
        results[directory] = {
            "exists": exists,
            "files": files
        }
    
    return {
        "success": True,
        "teacher_id": teacher_id,
        "directories_checked": results
    }
# Health check endpoint
@app.get("/")
def read_root():
    return {"message": "Islamic Center API is running!"}

# ------------------- ENHANCED DOWNLOAD ENDPOINTS -------------------

@app.get("/download/lecture/{lecture_id}")
def download_lecture(lecture_id: int):
    """Enhanced lecture download with proper file resolution"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Get lecture from database
        cursor.execute(
            """SELECT l.*, u.userId as teacher_userId 
               FROM lectures l 
               JOIN users u ON l.teacher_id = u.id 
               WHERE l.id = %s""", 
            (lecture_id,)
        )
        lecture = cursor.fetchone()
        
        if not lecture:
            raise HTTPException(status_code=404, detail="Lecture not found")
        
        teacher_id = lecture['teacher_userId']
        file_path = lecture.get('file_path')
        file_name = lecture.get('file_name') or f"lecture_{lecture_id}"
        
        if not file_path or file_path == 'NULL':
            raise HTTPException(status_code=404, detail="No file attached to this lecture")
        
        # Fix common file path issues
        fixed_path = fix_file_path(file_path, teacher_id)
        
        if not fixed_path or not os.path.exists(fixed_path):
            # Try to find the file using alternative methods
            found_path = search_file_by_name(file_name, teacher_id)
            if found_path:
                fixed_path = found_path
            else:
                raise HTTPException(status_code=404, detail="Lecture file not found on server")
        
        # Update download count
        cursor.execute(
            "UPDATE lectures SET downloads = downloads + 1 WHERE id = %s",
            (lecture_id,)
        )
        db.commit()
        cursor.close()
        db.close()
        
        # Return file for download
        return FileResponse(
            fixed_path,
            media_type='application/octet-stream',
            filename=file_name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading lecture: {str(e)}")

# Similar endpoint for materials
@app.get("/download/material/{material_id}")
def download_material(material_id: int):
    """Download material file"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Get material from database
        cursor.execute(
            """SELECT m.*, u.userId as teacher_userId 
               FROM materials m 
               JOIN users u ON m.teacher_id = u.id 
               WHERE m.id = %s""", 
            (material_id,)
        )
        material = cursor.fetchone()
        
        if not material:
            raise HTTPException(status_code=404, detail="Material not found")
        
        teacher_id = material['teacher_userId']
        file_path = material.get('file_path')
        file_name = material.get('file_name') or f"material_{material_id}"
        
        if not file_path or file_path == 'NULL':
            raise HTTPException(status_code=404, detail="No file attached to this material")
        
        # Fix file path if needed
        fixed_path = file_path
        if not os.path.exists(fixed_path):
            # Try alternative path resolution for materials
            material_dir = os.path.join(UPLOAD_DIR, "materials", teacher_id)
            alt_path = os.path.join(material_dir, file_name)
            if os.path.exists(alt_path):
                fixed_path = alt_path
            else:
                raise HTTPException(status_code=404, detail="Material file not found on server")
        
        # Update download count
        cursor.execute(
            "UPDATE materials SET downloads = downloads + 1 WHERE id = %s",
            (material_id,)
        )
        db.commit()
        cursor.close()
        db.close()
        
        # Return file for download
        return FileResponse(
            fixed_path,
            media_type='application/octet-stream',
            filename=file_name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading material: {str(e)}")
    
    
# ------------------- DIAGNOSTIC & TESTING ENDPOINTS -------------------

@app.get("/test/lecture/{lecture_id}/info")
def test_lecture_info(lecture_id: int):
    """Test endpoint to check lecture file information"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute(
            """SELECT l.*, u.userId as teacher_userId, u.fullName as teacher_name
               FROM lectures l 
               JOIN users u ON l.teacher_id = u.id 
               WHERE l.id = %s""", 
            (lecture_id,)
        )
        lecture = cursor.fetchone()
        
        if not lecture:
            return {"success": False, "error": "Lecture not found"}
        
        teacher_id = lecture['teacher_userId']
        file_path = lecture.get('file_path')
        file_name = lecture.get('file_name')
        
        # Check file existence using multiple methods
        file_checks = {}
        
        # 1. Check original file path
        if file_path and file_path != 'NULL':
            file_checks['original_path'] = {
                'path': file_path,
                'exists': os.path.exists(file_path),
                'absolute_path': os.path.abspath(file_path) if file_path else None
            }
        
        # 2. Check fixed file path
        fixed_path = fix_file_path(file_path, teacher_id)
        file_checks['fixed_path'] = {
            'path': fixed_path,
            'exists': os.path.exists(fixed_path) if fixed_path else False,
            'absolute_path': os.path.abspath(fixed_path) if fixed_path else None
        }
        
        # 3. Search by filename
        if file_name:
            found_path = search_file_by_name(file_name, teacher_id)
            file_checks['filename_search'] = {
                'filename': file_name,
                'found_path': found_path,
                'exists': os.path.exists(found_path) if found_path else False
            }
        
        # 4. Check teacher directories
        teacher_dirs = {}
        possible_dirs = [
            f"uploads/lectures/teacher_{teacher_id}",
            f"uploads/lectures/teacher_{teacher_id}_5674",
            f"uploads/lectures/{teacher_id}",
            "uploads/lectures"
        ]
        
        for directory in possible_dirs:
            exists = os.path.exists(directory)
            files = []
            if exists:
                try:
                    files = os.listdir(directory)
                except Exception as e:
                    files = [f"Error: {str(e)}"]
            
            teacher_dirs[directory] = {
                "exists": exists,
                "files": files
            }
        
        cursor.close()
        db.close()
        
        return {
            "success": True,
            "lecture_info": {
                "id": lecture['id'],
                "title": lecture['title'],
                "teacher_id": teacher_id,
                "teacher_name": lecture['teacher_name'],
                "file_path": file_path,
                "file_name": file_name,
                "file_size": lecture.get('file_size'),
                "upload_date": lecture.get('upload_date')
            },
            "file_checks": file_checks,
            "teacher_directories": teacher_dirs,
            "file_exists": any(check.get('exists') for check in file_checks.values() if 'exists' in check)
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/test/uploads-structure")
def test_uploads_structure():
    """Check the complete uploads directory structure"""
    base_path = "uploads"
    
    if not os.path.exists(base_path):
        return {
            "success": False,
            "message": "Uploads directory doesn't exist",
            "suggested_fix": "Create directory: mkdir -p uploads/lectures uploads/assignments uploads/materials"
        }
    
    structure = {}
    for root, dirs, files in os.walk(base_path):
        relative_path = root.replace(base_path, "").lstrip('/')
        structure[relative_path or '/'] = {
            "directories": dirs,
            "files": files,
            "file_count": len(files)
        }
    
    return {
        "success": True,
        "base_path": os.path.abspath(base_path),
        "structure": structure
    }

@app.get("/test/teacher-files/{teacher_id}")
def test_teacher_files(teacher_id: str):
    """Check all files for a specific teacher"""
    results = {}
    
    # Check all possible file types
    file_types = ["lectures", "assignments", "materials"]
    
    for file_type in file_types:
        possible_dirs = [
            f"uploads/{file_type}/teacher_{teacher_id}",
            f"uploads/{file_type}/teacher_{teacher_id}_5674",
            f"uploads/{file_type}/{teacher_id}",
            f"uploads/{file_type}"
        ]
        
        type_results = {}
        for directory in possible_dirs:
            exists = os.path.exists(directory)
            files = []
            if exists:
                try:
                    files = os.listdir(directory)
                    # Get file details
                    file_details = []
                    for file in files:
                        file_path = os.path.join(directory, file)
                        file_details.append({
                            "name": file,
                            "size": os.path.getsize(file_path) if os.path.isfile(file_path) else 0,
                            "modified": os.path.getmtime(file_path) if os.path.isfile(file_path) else 0
                        })
                    files = file_details
                except Exception as e:
                    files = [f"Error: {str(e)}"]
            
            type_results[directory] = {
                "exists": exists,
                "files": files,
                "file_count": len(files) if isinstance(files, list) else 0
            }
        
        results[file_type] = type_results
    
    return {
        "success": True,
        "teacher_id": teacher_id,
        "file_structure": results
    }

@app.get("/test/download/{lecture_id}")
def test_download_lecture(lecture_id: int):
    """Simple test endpoint for download functionality"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute(
            """SELECT l.*, u.userId as teacher_userId 
               FROM lectures l 
               JOIN users u ON l.teacher_id = u.id 
               WHERE l.id = %s""", 
            (lecture_id,)
        )
        lecture = cursor.fetchone()
        
        if not lecture:
            return {"success": False, "error": "Lecture not found"}
        
        teacher_id = lecture['teacher_userId']
        file_path = lecture.get('file_path')
        file_name = lecture.get('file_name')
        
        # Test file resolution
        fixed_path = fix_file_path(file_path, teacher_id)
        file_exists = fixed_path and os.path.exists(fixed_path)
        
        if not file_exists and file_name:
            found_path = search_file_by_name(file_name, teacher_id)
            if found_path:
                fixed_path = found_path
                file_exists = True
        
        cursor.close()
        db.close()
        
        return {
            "success": True,
            "lecture_id": lecture_id,
            "title": lecture['title'],
            "teacher_id": teacher_id,
            "original_file_path": file_path,
            "file_name": file_name,
            "resolved_file_path": fixed_path,
            "file_exists": file_exists,
            "download_url": f"http://localhost:8000/download/lecture/{lecture_id}" if file_exists else None,
            "test_info_url": f"http://localhost:8000/test/lecture/{lecture_id}/info"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}
    
# ------------------- ENHANCED DIAGNOSTIC ENDPOINTS -------------------

# ------------------- VIEW LECTURE ENDPOINT -------------------

@app.get("/view/lecture/{lecture_id}")
def view_lecture(lecture_id: int):
    """View lecture file in browser (for supported file types)"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Get lecture from database
        cursor.execute(
            """SELECT l.*, u.userId as teacher_userId 
               FROM lectures l 
               JOIN users u ON l.teacher_id = u.id 
               WHERE l.id = %s""", 
            (lecture_id,)
        )
        lecture = cursor.fetchone()
        
        if not lecture:
            raise HTTPException(status_code=404, detail="Lecture not found")
        
        teacher_id = lecture['teacher_userId']
        file_path = lecture.get('file_path')
        file_name = lecture.get('file_name')
        
        if not file_path or file_path == 'NULL':
            raise HTTPException(status_code=404, detail="No file attached to this lecture")
        
        # Fix common file path issues
        fixed_path = fix_file_path(file_path, teacher_id)
        
        if not fixed_path or not os.path.exists(fixed_path):
            # Try to find the file using alternative methods
            found_path = search_file_by_name(file_name, teacher_id)
            if found_path:
                fixed_path = found_path
            else:
                raise HTTPException(status_code=404, detail="Lecture file not found on server")
        
        # Determine content type based on file extension
        def get_content_type(file_path):
            """Determine content type based on file extension"""
            extension = os.path.splitext(file_path)[1].lower()
            
            content_types = {
                '.pdf': 'application/pdf',
                '.mp4': 'video/mp4',
                '.avi': 'video/x-msvideo',
                '.mov': 'video/quicktime',
                '.wmv': 'video/x-ms-wmv',
                '.flv': 'video/x-flv',
                '.webm': 'video/webm',
                '.mp3': 'audio/mpeg',
                '.wav': 'audio/wav',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.txt': 'text/plain',
                '.doc': 'application/msword',
                '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                '.ppt': 'application/vnd.ms-powerpoint',
                '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            }
            
            return content_types.get(extension, 'application/octet-stream')
        
        content_type = get_content_type(fixed_path)
        
        # Update view count
        try:
            cursor.execute(
                "UPDATE lectures SET views = COALESCE(views, 0) + 1 WHERE id = %s",
                (lecture_id,)
            )
            db.commit()
        except:
            # If views column doesn't exist, continue without error
            pass
        
        cursor.close()
        db.close()
        
        # Return file for viewing
        return FileResponse(
            fixed_path,
            media_type=content_type,
            filename=file_name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error viewing lecture: {str(e)}")

@app.get("/test/video/{lecture_id}")
def test_video_file(lecture_id: int):
    """Simple test to check if video file is accessible"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute(
            """SELECT l.*, u.userId as teacher_userId 
               FROM lectures l 
               JOIN users u ON l.teacher_id = u.id 
               WHERE l.id = %s""", 
            (lecture_id,)
        )
        lecture = cursor.fetchone()
        
        if not lecture:
            return {"success": False, "error": "Lecture not found"}
        
        teacher_id = lecture['teacher_userId']
        file_path = lecture.get('file_path')
        file_name = lecture.get('file_name')
        
        # Find actual file
        fixed_path = fix_file_path(file_path, teacher_id)
        actual_file_path = None
        
        if fixed_path and os.path.exists(fixed_path):
            actual_file_path = fixed_path
        else:
            found_path = search_file_by_name(file_name, teacher_id)
            if found_path:
                actual_file_path = found_path
        
        if not actual_file_path:
            return {
                "success": False, 
                "error": "File not found",
                "searched_paths": [fixed_path, f"uploads/lectures/teacher_{teacher_id}/{file_name}"]
            }
        
        # Check file properties
        file_stats = {
            "exists": os.path.exists(actual_file_path),
            "is_file": os.path.isfile(actual_file_path),
            "size": os.path.getsize(actual_file_path) if os.path.exists(actual_file_path) else 0,
            "readable": os.access(actual_file_path, os.R_OK) if os.path.exists(actual_file_path) else False,
            "path": actual_file_path
        }
        
        cursor.close()
        db.close()
        
        return {
            "success": True,
            "lecture": {
                "id": lecture['id'],
                "title": lecture['title'],
                "file_name": file_name
            },
            "file_stats": file_stats,
            "direct_url": f"http://localhost:8000{actual_file_path}" if actual_file_path.startswith('/') else f"http://localhost:8000/{actual_file_path}",
            "stream_url": f"http://localhost:8000/stream/lecture/{lecture_id}",
            "view_url": f"http://localhost:8000/view/lecture/{lecture_id}"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/stream/lecture/{lecture_id}")
async def stream_lecture_file(lecture_id: int, request: Request):
    """Stream lecture file with proper video headers for HTML5 video player"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Get lecture from database
        cursor.execute(
            """SELECT l.*, u.userId as teacher_userId 
               FROM lectures l 
               JOIN users u ON l.teacher_id = u.id 
               WHERE l.id = %s""", 
            (lecture_id,)
        )
        lecture = cursor.fetchone()
        
        if not lecture:
            raise HTTPException(status_code=404, detail="Lecture not found")
        
        teacher_id = lecture['teacher_userId']
        file_path = lecture.get('file_path')
        file_name = lecture.get('file_name')
        
        # Find the actual file
        fixed_path = fix_file_path(file_path, teacher_id)
        actual_file_path = None
        
        if fixed_path and os.path.exists(fixed_path) and os.path.isfile(fixed_path):
            actual_file_path = fixed_path
        else:
            found_path = search_file_by_name(file_name, teacher_id)
            if found_path and os.path.exists(found_path) and os.path.isfile(found_path):
                actual_file_path = found_path
        
        if not actual_file_path:
            raise HTTPException(status_code=404, detail="Lecture file not found")
        
        # Get file size for range requests (video streaming)
        file_size = os.path.getsize(actual_file_path)
        
        # Determine content type
        def get_content_type(file_path):
            extension = os.path.splitext(file_path)[1].lower()
            content_types = {
                '.mp4': 'video/mp4',
                '.avi': 'video/x-msvideo',
                '.mov': 'video/quicktime',
                '.wmv': 'video/x-ms-wmv',
                '.flv': 'video/x-flv',
                '.webm': 'video/webm',
                '.mkv': 'video/x-matroska',
            }
            return content_types.get(extension, 'video/mp4')
        
        content_type = get_content_type(actual_file_path)
        
        # Check if range header is present (for video seeking)
        range_header = request.headers.get('Range')
        
        if range_header:
            # Handle range requests for video streaming
            range_match = re.match(r'bytes=(\d+)-(\d+)?', range_header)
            if range_match:
                start = int(range_match.group(1))
                end = int(range_match.group(2)) if range_match.group(2) else file_size - 1
                
                if start >= file_size:
                    raise HTTPException(status_code=416, detail="Range not satisfiable")
                
                end = min(end, file_size - 1)
                length = end - start + 1
                
                # Read the specific byte range
                with open(actual_file_path, 'rb') as video_file:
                    video_file.seek(start)
                    data = video_file.read(length)
                
                # Return partial content response
                response = Response(
                    content=data,
                    status_code=206,
                    media_type=content_type,
                    headers={
                        'Content-Range': f'bytes {start}-{end}/{file_size}',
                        'Accept-Ranges': 'bytes',
                        'Content-Length': str(length),
                        'Content-Disposition': f'inline; filename="{file_name}"'
                    }
                )
                cursor.close()
                db.close()
                return response
        
        # If no range header, return the entire file
        cursor.close()
        db.close()
        
        return FileResponse(
            actual_file_path,
            media_type=content_type,
            filename=file_name,
            headers={
                'Accept-Ranges': 'bytes',
                'Content-Length': str(file_size),
                'Content-Disposition': f'inline; filename="{file_name}"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error streaming lecture: {str(e)}")

@app.get("/debug/lecture/{lecture_id}")
def debug_lecture_file(lecture_id: int):
    """Debug endpoint to check lecture file issues"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute(
            """SELECT l.*, u.userId as teacher_userId 
               FROM lectures l 
               JOIN users u ON l.teacher_id = u.id 
               WHERE l.id = %s""", 
            (lecture_id,)
        )
        lecture = cursor.fetchone()
        
        if not lecture:
            return {"success": False, "error": "Lecture not found"}
        
        teacher_id = lecture['teacher_userId']
        file_path = lecture.get('file_path')
        file_name = lecture.get('file_name')
        
        # Comprehensive file checking
        file_checks = {}
        
        # 1. Original path
        file_checks['original_path'] = {
            'path': file_path,
            'exists': os.path.exists(file_path) if file_path and file_path != 'NULL' else False,
            'is_file': os.path.isfile(file_path) if file_path and file_path != 'NULL' and os.path.exists(file_path) else False
        }
        
        # 2. Fixed path
        fixed_path = fix_file_path(file_path, teacher_id)
        file_checks['fixed_path'] = {
            'path': fixed_path,
            'exists': os.path.exists(fixed_path) if fixed_path else False,
            'is_file': os.path.isfile(fixed_path) if fixed_path and os.path.exists(fixed_path) else False
        }
        
        # 3. Direct file access test
        actual_file_path = None
        if fixed_path and os.path.exists(fixed_path) and os.path.isfile(fixed_path):
            actual_file_path = fixed_path
        else:
            # Search for the file
            found_path = search_file_by_name(file_name, teacher_id)
            if found_path and os.path.exists(found_path) and os.path.isfile(found_path):
                actual_file_path = found_path
        
        # 4. File details if found
        file_details = {}
        if actual_file_path:
            file_details = {
                'actual_path': actual_file_path,
                'size': os.path.getsize(actual_file_path),
                'modified': os.path.getmtime(actual_file_path),
                'is_readable': os.access(actual_file_path, os.R_OK)
            }
        
        cursor.close()
        db.close()
        
        return {
            "success": True,
            "lecture": {
                "id": lecture['id'],
                "title": lecture['title'],
                "teacher_id": teacher_id,
                "file_path": file_path,
                "file_name": file_name
            },
            "file_checks": file_checks,
            "file_details": file_details,
            "actual_file_path": actual_file_path,
            "direct_view_url": f"http://localhost:8000/view/lecture/{lecture_id}",
            "direct_download_url": f"http://localhost:8000/download/lecture/{lecture_id}"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


    """Stream lecture file with proper video headers"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute(
            """SELECT l.*, u.userId as teacher_userId 
               FROM lectures l 
               JOIN users u ON l.teacher_id = u.id 
               WHERE l.id = %s""", 
            (lecture_id,)
        )
        lecture = cursor.fetchone()
        
        if not lecture:
            raise HTTPException(status_code=404, detail="Lecture not found")
        
        teacher_id = lecture['teacher_userId']
        file_path = lecture.get('file_path')
        file_name = lecture.get('file_name')
        
        # Find the actual file
        fixed_path = fix_file_path(file_path, teacher_id)
        actual_file_path = None
        
        if fixed_path and os.path.exists(fixed_path) and os.path.isfile(fixed_path):
            actual_file_path = fixed_path
        else:
            found_path = search_file_by_name(file_name, teacher_id)
            if found_path and os.path.exists(found_path) and os.path.isfile(found_path):
                actual_file_path = found_path
        
        if not actual_file_path:
            raise HTTPException(status_code=404, detail="Lecture file not found")
        
        # Get file size for range requests (video streaming)
        file_size = os.path.getsize(actual_file_path)
        
        # Check if range header is present (for video seeking)
        range_header = request.headers.get('Range')
        
        if range_header:
            # Handle range requests for video streaming
            range_match = re.match(r'bytes=(\d+)-(\d+)?', range_header)
            if range_match:
                start = int(range_match.group(1))
                end = int(range_match.group(2)) if range_match.group(2) else file_size - 1
                
                if start >= file_size:
                    raise HTTPException(status_code=416, detail="Range not satisfiable")
                
                end = min(end, file_size - 1)
                length = end - start + 1
                
                with open(actual_file_path, 'rb') as video_file:
                    video_file.seek(start)
                    data = video_file.read(length)
                
                response = Response(
                    content=data,
                    status_code=206,
                    media_type='video/mp4',
                    headers={
                        'Content-Range': f'bytes {start}-{end}/{file_size}',
                        'Accept-Ranges': 'bytes',
                        'Content-Length': str(length),
                        'Content-Disposition': f'inline; filename="{file_name}"'
                    }
                )
                return response
        
        # Regular file response
        cursor.close()
        db.close()
        
        return FileResponse(
            actual_file_path,
            media_type='video/mp4',
            filename=file_name,
            headers={
                'Accept-Ranges': 'bytes',
                'Content-Length': str(file_size),
                'Content-Disposition': f'inline; filename="{file_name}"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error streaming lecture: {str(e)}")
    
#make comprehensice mcqs system

# Pydantic models for quizzes
class QuestionBase(BaseModel):
    question_text: str
    question_text_urdu: Optional[str] = None
    question_text_arabic: Optional[str] = None
    question_type: str = "mcq"
    marks: int = 1
    correct_answer: Optional[str] = None

class OptionBase(BaseModel):
    option_text: str
    option_text_urdu: Optional[str] = None
    option_text_arabic: Optional[str] = None
    is_correct: bool = False

class QuestionCreate(BaseModel):
    question: QuestionBase
    options: List[OptionBase]

class QuizCreate(BaseModel):
    teacher_id: str
    subject_name: str
    title: str
    description: Optional[str] = None
    start_date: str
    end_date: str
    total_marks: int = 100
    duration_minutes: int = 30
    is_published: bool = False
    questions: List[QuestionCreate]

# ------------------- QUIZ MANAGEMENT ENDPOINTS -------------------

@app.post("/create_quiz_with_questions")
async def create_quiz_with_questions(quiz_data: QuizCreate):
    """Create a quiz with all questions and options in one go"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Get teacher's numeric ID
        cursor.execute("SELECT id FROM users WHERE userId = %s AND role = 'teacher'", (quiz_data.teacher_id,))
        teacher = cursor.fetchone()
        
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher not found")
        
        numeric_teacher_id = teacher['id']
        
        # Create quiz
        cursor.execute(
            """INSERT INTO quizzes 
            (teacher_id, subject_name, title, description, start_date, end_date, 
             total_marks, duration_minutes, is_published, questions_count) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (numeric_teacher_id, quiz_data.subject_name, quiz_data.title, 
             quiz_data.description, quiz_data.start_date, quiz_data.end_date,
             quiz_data.total_marks, quiz_data.duration_minutes, 
             quiz_data.is_published, len(quiz_data.questions))
        )
        
        quiz_id = cursor.lastrowid
        
        # Add questions and options
        for q in quiz_data.questions:
            cursor.execute(
                """INSERT INTO questions 
                (quiz_id, question_text, question_text_urdu, question_text_arabic, 
                 question_type, marks, correct_answer) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (quiz_id, q.question.question_text, q.question.question_text_urdu,
                 q.question.question_text_arabic, q.question.question_type,
                 q.question.marks, q.question.correct_answer)
            )
            
            question_id = cursor.lastrowid
            
            # Add options for this question
            for opt in q.options:
                cursor.execute(
                    """INSERT INTO options 
                    (question_id, option_text, option_text_urdu, option_text_arabic, is_correct) 
                    VALUES (%s, %s, %s, %s, %s)""",
                    (question_id, opt.option_text, opt.option_text_urdu,
                     opt.option_text_arabic, opt.is_correct)
                )
        
        db.commit()
        cursor.close()
        db.close()
        
        return {
            "message": "Quiz created successfully",
            "quiz_id": quiz_id,
            "questions_added": len(quiz_data.questions),
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating quiz: {str(e)}")

@app.get("/quiz/{quiz_id}/full")
def get_quiz_with_questions(quiz_id: int):
    """Get complete quiz with all questions and options"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Get quiz details
        cursor.execute(
            """SELECT q.*, u.userId as teacher_userId, u.fullName as teacher_name 
               FROM quizzes q 
               JOIN users u ON q.teacher_id = u.id 
               WHERE q.id = %s""",
            (quiz_id,)
        )
        quiz = cursor.fetchone()
        
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        # Get questions with options
        cursor.execute(
            """SELECT * FROM questions WHERE quiz_id = %s ORDER BY id""",
            (quiz_id,)
        )
        questions = cursor.fetchall()
        
        questions_with_options = []
        for question in questions:
            cursor.execute(
                """SELECT * FROM options WHERE question_id = %s ORDER BY id""",
                (question['id'],)
            )
            options = cursor.fetchall()
            
            questions_with_options.append({
                **question,
                'options': options
            })
        
        cursor.close()
        db.close()
        
        return {
            "quiz": quiz,
            "questions": questions_with_options,
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching quiz: {str(e)}")

@app.get("/student_quizzes/{subject_name}")
def get_student_quizzes(subject_name: str):
    """Get all published quizzes for a subject (student view)"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute(
            """SELECT q.*, u.fullName as teacher_name 
               FROM quizzes q 
               JOIN users u ON q.teacher_id = u.id 
               WHERE q.subject_name = %s AND q.is_published = TRUE 
               ORDER BY q.created_date DESC""",
            (subject_name,)
        )
        
        quizzes = cursor.fetchall()
        
        cursor.close()
        db.close()
        
        return {"quizzes": quizzes, "success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching quizzes: {str(e)}")

# ------------------- STUDENT QUIZ ATTEMPT ENDPOINTS -------------------

@app.post("/quiz/{quiz_id}/start_attempt")
def start_quiz_attempt(quiz_id: int, student_userId: str):
    """Start a new quiz attempt for student"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Get student numeric ID
        cursor.execute("SELECT id FROM users WHERE userId = %s", (student_userId,))
        student = cursor.fetchone()
        
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        numeric_student_id = student['id']
        
        # Check if quiz exists and is published
        cursor.execute(
            """SELECT * FROM quizzes 
               WHERE id = %s AND is_published = TRUE 
               AND CURDATE() BETWEEN start_date AND end_date""",
            (quiz_id,)
        )
        quiz = cursor.fetchone()
        
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not available")
        
        # Start new attempt
        cursor.execute(
            """INSERT INTO student_attempts (student_id, quiz_id, total_score) 
               VALUES (%s, %s, 0)""",
            (numeric_student_id, quiz_id)
        )
        
        attempt_id = cursor.lastrowid
        
        db.commit()
        cursor.close()
        db.close()
        
        return {
            "attempt_id": attempt_id,
            "quiz": quiz,
            "success": True,
            "message": "Quiz attempt started"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting quiz: {str(e)}")

@app.post("/quiz/{quiz_id}/submit_answer")
def submit_answer(
    attempt_id: int,
    question_id: int,
    selected_option_id: Optional[int] = None,
    answer_text: Optional[str] = None
):
    """Submit answer for a question"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Get correct answer
        cursor.execute(
            """SELECT o.*, q.marks 
               FROM questions q 
               LEFT JOIN options o ON o.question_id = q.id 
               WHERE q.id = %s AND (o.is_correct = TRUE OR %s IS NULL)""",
            (question_id, selected_option_id)
        )
        
        result = cursor.fetchone()
        
        is_correct = False
        marks_obtained = 0
        
        if selected_option_id:
            # MCQ or True/False
            is_correct = result['is_correct'] if result else False
            marks_obtained = result['marks'] if is_correct else 0
        elif answer_text:
            # Short answer - simple comparison (you can make this more sophisticated)
            cursor.execute(
                "SELECT correct_answer, marks FROM questions WHERE id = %s",
                (question_id,)
            )
            question = cursor.fetchone()
            is_correct = answer_text.strip().lower() == question['correct_answer'].strip().lower()
            marks_obtained = question['marks'] if is_correct else 0
        
        # Save answer
        cursor.execute(
            """INSERT INTO student_answers 
               (attempt_id, question_id, selected_option_id, answer_text, is_correct, marks_obtained) 
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (attempt_id, question_id, selected_option_id, answer_text, is_correct, marks_obtained)
        )
        
        db.commit()
        cursor.close()
        db.close()
        
        return {
            "is_correct": is_correct,
            "marks_obtained": marks_obtained,
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting answer: {str(e)}")

@app.post("/quiz/attempt/{attempt_id}/finish")
def finish_quiz_attempt(attempt_id: int, time_taken_minutes: int):
    """Finish quiz attempt and calculate total score"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Calculate total score
        cursor.execute(
            """SELECT SUM(marks_obtained) as total_score 
               FROM student_answers 
               WHERE attempt_id = %s""",
            (attempt_id,)
        )
        
        total_score = cursor.fetchone()['total_score'] or 0
        
        # Update attempt record
        cursor.execute(
            """UPDATE student_attempts 
               SET total_score = %s, time_taken_minutes = %s 
               WHERE id = %s""",
            (total_score, time_taken_minutes, attempt_id)
        )
        
        db.commit()
        
        # Get attempt details
        cursor.execute(
            """SELECT a.*, q.title as quiz_title, u.fullName as student_name 
               FROM student_attempts a 
               JOIN quizzes q ON a.quiz_id = q.id 
               JOIN users u ON a.student_id = u.id 
               WHERE a.id = %s""",
            (attempt_id,)
        )
        
        attempt_details = cursor.fetchone()
        
        cursor.close()
        db.close()
        
        return {
            "attempt_id": attempt_id,
            "total_score": total_score,
            "time_taken": time_taken_minutes,
            "attempt_details": attempt_details,
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finishing quiz: {str(e)}")

@app.get("/student/{userId}/quiz_results")
def get_student_quiz_results(userId: str):
    """Get all quiz results for a student"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Get student numeric ID
        cursor.execute("SELECT id FROM users WHERE userId = %s", (userId,))
        student = cursor.fetchone()
        
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        numeric_student_id = student['id']
        
        cursor.execute(
            """SELECT a.*, q.title as quiz_title, q.subject_name, q.total_marks,
                      u.fullName as teacher_name,
                      ROUND((a.total_score / q.total_marks) * 100, 2) as percentage
               FROM student_attempts a 
               JOIN quizzes q ON a.quiz_id = q.id 
               JOIN users u ON q.teacher_id = u.id 
               WHERE a.student_id = %s 
               ORDER BY a.submitted_at DESC""",
            (numeric_student_id,)
        )
        
        results = cursor.fetchall()
        
        cursor.close()
        db.close()
        
        return {"results": results, "success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching results: {str(e)}")

@app.get("/teacher/{teacher_userId}/quiz_results/{quiz_id}")
def get_quiz_results_for_teacher(teacher_userId: str, quiz_id: int):
    """Get all student results for a specific quiz"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Verify teacher owns this quiz
        cursor.execute(
            """SELECT q.id FROM quizzes q 
               JOIN users u ON q.teacher_id = u.id 
               WHERE u.userId = %s AND q.id = %s""",
            (teacher_userId, quiz_id)
        )
        
        quiz = cursor.fetchone()
        if not quiz:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        cursor.execute(
            """SELECT a.*, u.fullName as student_name, u.userId as student_userId,
                      ROUND((a.total_score / q.total_marks) * 100, 2) as percentage
               FROM student_attempts a 
               JOIN users u ON a.student_id = u.id 
               JOIN quizzes q ON a.quiz_id = q.id 
               WHERE a.quiz_id = %s 
               ORDER BY a.total_score DESC""",
            (quiz_id,)
        )
        
        results = cursor.fetchall()
        
        cursor.close()
        db.close()
        
        return {"results": results, "quiz_id": quiz_id, "success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching results: {str(e)}")

# ------------------- QUIZ EDITING ENDPOINTS -------------------

@app.put("/quiz/{quiz_id}/publish")
def publish_quiz(quiz_id: int, teacher_userId: str):
    """Publish/unpublish a quiz"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Verify teacher owns this quiz
        cursor.execute(
            """SELECT q.id FROM quizzes q 
               JOIN users u ON q.teacher_id = u.id 
               WHERE u.userId = %s AND q.id = %s""",
            (teacher_userId, quiz_id)
        )
        
        quiz = cursor.fetchone()
        if not quiz:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Toggle publish status
        cursor.execute(
            "UPDATE quizzes SET is_published = NOT is_published WHERE id = %s",
            (quiz_id,)
        )
        
        cursor.execute("SELECT is_published FROM quizzes WHERE id = %s", (quiz_id,))
        new_status = cursor.fetchone()['is_published']
        
        db.commit()
        cursor.close()
        db.close()
        
        status_text = "published" if new_status else "unpublished"
        return {
            "message": f"Quiz {status_text} successfully",
            "is_published": new_status,
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error publishing quiz: {str(e)}")

@app.delete("/quiz/{quiz_id}")
def delete_quiz(quiz_id: int, teacher_userId: str):
    """Delete a quiz and all related data"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Verify teacher owns this quiz
        cursor.execute(
            """SELECT q.id FROM quizzes q 
               JOIN users u ON q.teacher_id = u.id 
               WHERE u.userId = %s AND q.id = %s""",
            (teacher_userId, quiz_id)
        )
        
        quiz = cursor.fetchone()
        if not quiz:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Delete quiz (cascade will delete questions, options, attempts, answers)
        cursor.execute("DELETE FROM quizzes WHERE id = %s", (quiz_id,))
        
        db.commit()
        cursor.close()
        db.close()
        
        return {"message": "Quiz deleted successfully", "success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting quiz: {str(e)}")

# ------------------- VOICE INPUT ENDPOINT -------------------

@app.post("/speech-to-text")
async def speech_to_text(audio: UploadFile = File(...)):
    """Convert speech to text (placeholder - integrate with actual speech API)"""
    try:
        # For now, return mock response
        # In production, integrate with:
        # 1. Google Speech-to-Text API
        # 2. Azure Cognitive Services
        # 3. Or any speech recognition library
        
        # This is a placeholder response
        return {
            "text": "This is a placeholder for speech-to-text conversion.",
            "language": "en",
            "success": True,
            "note": "Integrate with actual speech recognition API for production"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing speech: {str(e)}")