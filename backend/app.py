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

# Add this endpoint for students to get notifications
@app.get("/student/{student_userId}/notifications")
def get_student_notifications(student_userId: str, subject_name: str = None):
    """Get notifications for a student, optionally filtered by subject"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        print(f"DEBUG: Getting notifications for student {student_userId}, subject: {subject_name}")
        
        # Get student's current year
        cursor.execute("""
            SELECT id, current_year 
            FROM users 
            WHERE userId = %s AND role = 'student'
        """, (student_userId,))
        
        student = cursor.fetchone()
        
        if not student:
            cursor.close()
            db.close()
            return {
                "success": False,
                "error": "Student not found"
            }
        
        student_id = student['id']
        current_year = student['current_year']
        
        # Build query based on whether subject_name is provided
        if subject_name:
            # Get notifications for specific subject
            query = """
                SELECT n.*, u.fullName as teacher_name, u.userId as teacher_userId
                FROM notifications n
                JOIN users u ON n.teacher_id = u.id
                WHERE n.subject_name = %s
                ORDER BY n.created_date DESC
            """
            cursor.execute(query, (subject_name,))
        else:
            # Get notifications for all subjects in student's year
            # First, get all subjects for student's year
            cursor.execute("""
                SELECT subject_name 
                FROM subjects 
                WHERE year_id IN (
                    SELECT id FROM years WHERE name LIKE %s
                )
            """, (f"%{current_year}%",))
            
            subjects = cursor.fetchall()
            
            if not subjects:
                cursor.close()
                db.close()
                return {
                    "success": True,
                    "notifications": [],
                    "message": "No subjects found for your year"
                }
            
            subject_names = [subject['subject_name'] for subject in subjects]
            
            # Get notifications for all these subjects
            placeholders = ', '.join(['%s'] * len(subject_names))
            query = f"""
                SELECT n.*, u.fullName as teacher_name, u.userId as teacher_userId
                FROM notifications n
                JOIN users u ON n.teacher_id = u.id
                WHERE n.subject_name IN ({placeholders})
                ORDER BY n.created_date DESC
            """
            cursor.execute(query, subject_names)
        
        notifications = cursor.fetchall()
        
        cursor.close()
        db.close()
        
        return {
            "success": True,
            "notifications": notifications,
            "total_notifications": len(notifications),
            "student_year": current_year
        }
        
    except Exception as e:
        print(f"Error in get_student_notifications: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": f"Error fetching notifications: {str(e)}"
        }

# Also add endpoint to get notifications count for stats
@app.get("/student/{student_userId}/notifications/count")
def get_student_notifications_count(student_userId: str):
    """Get count of notifications for a student"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Get student's current year
        cursor.execute("""
            SELECT id, current_year 
            FROM users 
            WHERE userId = %s AND role = 'student'
        """, (student_userId,))
        
        student = cursor.fetchone()
        
        if not student:
            cursor.close()
            db.close()
            return {
                "success": False,
                "error": "Student not found"
            }
        
        current_year = student['current_year']
        
        # Get all subjects for student's year
        cursor.execute("""
            SELECT subject_name 
            FROM subjects 
            WHERE year_id IN (
                SELECT id FROM years WHERE name LIKE %s
            )
        """, (f"%{current_year}%",))
        
        subjects = cursor.fetchall()
        
        if not subjects:
            cursor.close()
            db.close()
            return {
                "success": True,
                "total_notifications": 0,
                "subject_counts": {}
            }
        
        subject_names = [subject['subject_name'] for subject in subjects]
        
        # Get count of notifications for each subject
        notifications_by_subject = {}
        total_count = 0
        
        for subject in subject_names:
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM notifications 
                WHERE subject_name = %s
            """, (subject,))
            
            count_result = cursor.fetchone()
            notifications_by_subject[subject] = count_result['count']
            total_count += count_result['count']
        
        cursor.close()
        db.close()
        
        return {
            "success": True,
            "total_notifications": total_count,
            "subject_counts": notifications_by_subject
        }
        
    except Exception as e:
        print(f"Error in get_student_notifications_count: {str(e)}")
        return {
            "success": False,
            "error": f"Error counting notifications: {str(e)}"
        }

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
# ------------------- QUIZ MODELS (UPDATED) -------------------

# Updated models to match frontend structure
class OptionBase(BaseModel):
    option_text: str
    option_text_urdu: Optional[str] = None
    option_text_arabic: Optional[str] = None
    is_correct: bool = False

class QuestionBase(BaseModel):
    question_text: str
    question_text_urdu: Optional[str] = None
    question_text_arabic: Optional[str] = None
    question_type: str = "mcq"
    marks: int = 1
    correct_answer: Optional[str] = None
    options: List[OptionBase] = []  # Add options directly here

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
    questions: List[QuestionBase]  # Remove QuestionCreate wrapper


class QuestionCreate(BaseModel):
    question: QuestionBase
    options: List[OptionBase]

# ------------------- QUIZ MANAGEMENT ENDPOINTS -------------------
# ------------------- QUIZ CREATION ENDPOINT (WITH PROPER ERROR HANDLING) -------------------

# ------------------- QUIZ CREATION ENDPOINT (SIMPLIFIED) -------------------


@app.post("/create_quiz_with_questions")
async def create_quiz_with_questions(quiz_data: QuizCreate):
    """Create a quiz with all questions and options - WITH SUBJECT VALIDATION - COMPLETE VERSION"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        print(f"=== STARTING QUIZ CREATION ===")
        print(f"Teacher ID: {quiz_data.teacher_id}")
        print(f"Quiz title: {quiz_data.title}")
        print(f"Subject: {quiz_data.subject_name}")
        print(f"Questions received: {len(quiz_data.questions)}")
        
        # Log the full structure to debug
        print(f"Full quiz data: {quiz_data.dict()}")
        
        # Get teacher's numeric ID and assigned subject
        cursor.execute(
            "SELECT id, userId, fullName, subject FROM users WHERE userId = %s AND role = 'teacher'", 
            (quiz_data.teacher_id,)
        )
        teacher = cursor.fetchone()
        
        if not teacher:
            print(f"ERROR: Teacher not found with userId: {quiz_data.teacher_id}")
            cursor.close()
            db.close()
            raise HTTPException(
                status_code=404, 
                detail=f"Teacher not found with ID: {quiz_data.teacher_id}"
            )
        
        numeric_teacher_id = teacher['id']
        teacher_subject = teacher.get('subject', '')
        print(f"✓ Found teacher: {teacher['fullName']} (ID: {numeric_teacher_id})")
        print(f"✓ Teacher's assigned subject: {teacher_subject}")
        
        # ⚠️ SUBJECT VALIDATION: Check if teacher can create quiz for this subject
        if teacher_subject:
            # Split multiple subjects (comma-separated)
            assigned_subjects = [s.strip() for s in teacher_subject.split(',') if s.strip()]
            subject_allowed = False
            
            # Check if quiz subject matches any of teacher's assigned subjects
            for assigned_subj in assigned_subjects:
                if is_subject_match(assigned_subj, quiz_data.subject_name):
                    subject_allowed = True
                    break
            
            if not subject_allowed:
                cursor.close()
                db.close()
                raise HTTPException(
                    status_code=403,
                    detail=f"Not authorized. You can only create quizzes for your assigned subjects: {teacher_subject}"
                )
        else:
            print(f"⚠️ Teacher has no assigned subjects")
        
        # ✅ CREATE QUIZ - ADD THIS PART BACK!
        print(f"Creating quiz: {quiz_data.title}")
        cursor.execute(
            """INSERT INTO quizzes 
            (teacher_id, subject_name, title, description, start_date, end_date, 
             total_marks, duration_minutes, is_published, questions_count) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (numeric_teacher_id, 
             quiz_data.subject_name, 
             quiz_data.title, 
             quiz_data.description or "", 
             quiz_data.start_date, 
             quiz_data.end_date,
             quiz_data.total_marks, 
             quiz_data.duration_minutes, 
             quiz_data.is_published, 
             len(quiz_data.questions))
        )
        
        quiz_id = cursor.lastrowid
        print(f"✓ Quiz created with ID: {quiz_id}")
        
        # Add questions and options
        questions_added = 0
        options_added = 0
        
        for q_index, question in enumerate(quiz_data.questions):
            print(f"\nProcessing question {q_index + 1}/{len(quiz_data.questions)}")
            print(f"  Question text: {question.question_text[:50]}...")
            print(f"  Question type: {question.question_type}")
            print(f"  Marks: {question.marks}")
            print(f"  Options: {len(question.options)}")
            
            # Get correct answer
            correct_answer = question.correct_answer
            if not correct_answer and question.options:
                # Find correct option
                for opt in question.options:
                    if opt.is_correct:
                        correct_answer = opt.option_text
                        print(f"  Found correct answer from options: {correct_answer[:50]}...")
                        break
            
            # Insert question
            cursor.execute(
                """INSERT INTO questions 
                (quiz_id, question_text, question_text_urdu, question_text_arabic, 
                 question_type, marks, correct_answer) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (quiz_id, 
                 question.question_text or "",
                 question.question_text_urdu or "",
                 question.question_text_arabic or "",
                 question.question_type,
                 question.marks,
                 correct_answer or "")
            )
            
            question_id = cursor.lastrowid
            questions_added += 1
            print(f"  ✓ Question added with ID: {question_id}")
            
            # Add options for this question
            for opt_index, option in enumerate(question.options):
                cursor.execute(
                    """INSERT INTO options 
                    (question_id, option_text, option_text_urdu, option_text_arabic, is_correct) 
                    VALUES (%s, %s, %s, %s, %s)""",
                    (question_id, 
                     option.option_text or "",
                     option.option_text_urdu or "",
                     option.option_text_arabic or "",
                     option.is_correct)
                )
                options_added += 1
                if option.is_correct:
                    print(f"    ✓ Option {opt_index + 1}: {option.option_text[:30]}... (CORRECT)")
                else:
                    print(f"    ✓ Option {opt_index + 1}: {option.option_text[:30]}...")
        
        db.commit()
        print(f"\n=== QUIZ CREATION COMPLETE ===")
        print(f"Total questions added: {questions_added}")
        print(f"Total options added: {options_added}")
        
        cursor.close()
        db.close()
        
        return {
            "message": "Quiz created successfully!",
            "quiz_id": quiz_id,
            "quiz_title": quiz_data.title,
            "questions_added": questions_added,
            "options_added": options_added,
            "success": True
        }
        
    except HTTPException as e:
        raise e  # Re-raise HTTP exceptions
    except Exception as e:
        error_msg = f"Error creating quiz: {str(e)}"
        print(f"✗ ERROR: {error_msg}")
        import traceback
        traceback.print_exc()
        
        # Close connections if they exist
        try:
            cursor.close()
            db.close()
        except:
            pass
            
        raise HTTPException(status_code=500, detail=error_msg)

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

#student take quiz

# ------------------- STUDENT QUIZ ENDPOINTS -------------------

@app.get("/student/quizzes/available/{student_userId}")
def get_available_quizzes_for_student(student_userId: str, subject_name: str = None):
    """Get available quizzes for a student - UPDATED"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Get student info including their subjects
        cursor.execute(
            """SELECT id, current_year FROM users WHERE userId = %s""",
            (student_userId,)
        )
        student = cursor.fetchone()
        
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        numeric_student_id = student['id']
        
        # Base query
        query = """
            SELECT DISTINCT q.*, u.fullName as teacher_name,
                   (SELECT COUNT(*) FROM student_attempts 
                    WHERE quiz_id = q.id AND student_id = %s) as attempts_count,
                   (SELECT MAX(total_score) FROM student_attempts 
                    WHERE quiz_id = q.id AND student_id = %s) as best_score
            FROM quizzes q 
            JOIN users u ON q.teacher_id = u.id 
            WHERE q.is_published = TRUE 
            AND q.is_active = TRUE
            AND CURDATE() BETWEEN q.start_date AND q.end_date
        """
        
        params = [numeric_student_id, numeric_student_id]
        
        # Add subject filter if provided
        if subject_name:
            query += " AND q.subject_name = %s"
            params.append(subject_name)
        
        query += " ORDER BY q.end_date ASC"
        
        cursor.execute(query, params)
        quizzes = cursor.fetchall()
        
        cursor.close()
        db.close()
        
        return {"quizzes": quizzes, "success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching quizzes: {str(e)}")


@app.get("/student/quiz/{quiz_id}/questions")
def get_quiz_questions_for_student(quiz_id: int, student_userId: str):
    """Get quiz questions for student (without answers) - UPDATED"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Verify student exists
        cursor.execute("SELECT id FROM users WHERE userId = %s", (student_userId,))
        student = cursor.fetchone()
        
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Get quiz details
        cursor.execute(
            """SELECT q.*, u.fullName as teacher_name 
               FROM quizzes q 
               JOIN users u ON q.teacher_id = u.id 
               WHERE q.id = %s AND q.is_published = TRUE""",
            (quiz_id,)
        )
        quiz = cursor.fetchone()
        
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found or not available")
        
        # Get questions with all language versions
        cursor.execute(
            """SELECT 
                   id, 
                   question_text,
                   question_text_urdu,
                   question_text_arabic,
                   question_type, 
                   marks
               FROM questions WHERE quiz_id = %s ORDER BY id""",
            (quiz_id,)
        )
        questions = cursor.fetchall()
        
        # Get options with all language versions
        for question in questions:
            cursor.execute(
                """SELECT 
                       id, 
                       option_text,
                       option_text_urdu,
                       option_text_arabic
                   FROM options WHERE question_id = %s ORDER BY id""",
                (question['id'],)
            )
            question['options'] = cursor.fetchall()
        
        cursor.close()
        db.close()
        
        return {
            "quiz": quiz,
            "questions": questions,
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching quiz questions: {str(e)}")

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
import traceback

@app.post("/student/quiz/{quiz_id}/submit")
async def submit_student_quiz(quiz_id: int, request_data: dict):
    """Submit a quiz attempt - COMPLETELY FIXED VERSION"""
    try:
        print(f"\n{'='*60}")
        print("📝 QUIZ SUBMISSION REQUEST RECEIVED")
        print(f"{'='*60}")
        
        # Extract data from request
        student_userId = request_data.get('student_userId')
        answers = request_data.get('answers', [])
        
        print(f"Quiz ID: {quiz_id}")
        print(f"Student UserId: {student_userId}")
        print(f"Number of answers: {len(answers)}")
        print(f"Answers data: {answers}")
        
        # Validate input
        if not student_userId:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "detail": "Student ID is required",
                    "error_type": "VALIDATION_ERROR"
                }
            )
        
        if not answers or not isinstance(answers, list):
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "detail": "Answers must be provided as a list",
                    "error_type": "VALIDATION_ERROR"
                }
            )
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # 1. Get student
        cursor.execute("SELECT id, fullName FROM users WHERE userId = %s", (student_userId,))
        student = cursor.fetchone()
        
        if not student:
            cursor.close()
            db.close()
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "detail": f"Student not found: {student_userId}",
                    "error_type": "STUDENT_NOT_FOUND"
                }
            )
        
        numeric_student_id = student['id']
        print(f"✓ Student found: {student['fullName']} (ID: {numeric_student_id})")
        
        # 2. Get quiz
        cursor.execute("""
            SELECT q.*, u.fullName as teacher_name 
            FROM quizzes q 
            LEFT JOIN users u ON q.teacher_id = u.id 
            WHERE q.id = %s
        """, (quiz_id,))
        quiz = cursor.fetchone()
        
        if not quiz:
            cursor.close()
            db.close()
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "detail": f"Quiz {quiz_id} not found",
                    "error_type": "QUIZ_NOT_FOUND"
                }
            )
        
        print(f"✓ Quiz found: {quiz['title']}")
        print(f"  Subject: {quiz['subject_name']}")
        print(f"  Published: {quiz['is_published']}")
        
        # Check if quiz is published
        if not quiz.get('is_published'):
            cursor.close()
            db.close()
            return JSONResponse(
                status_code=403,
                content={
                    "success": False,
                    "detail": "This quiz is not published",
                    "error_type": "QUIZ_NOT_PUBLISHED"
                }
            )
        
        # Check dates
        current_date = datetime.now().date()
        start_date = quiz.get('start_date')
        end_date = quiz.get('end_date')
        
        if start_date and current_date < start_date:
            cursor.close()
            db.close()
            return JSONResponse(
                status_code=403,
                content={
                    "success": False,
                    "detail": "Quiz has not started yet",
                    "error_type": "QUIZ_NOT_STARTED"
                }
            )
        
        if end_date and current_date > end_date:
            cursor.close()
            db.close()
            return JSONResponse(
                status_code=403,
                content={
                    "success": False,
                    "detail": "Quiz has ended",
                    "error_type": "QUIZ_ENDED"
                }
            )
        
        # 3. Get quiz questions for validation
        cursor.execute("""
            SELECT id, marks, correct_answer, question_type 
            FROM questions 
            WHERE quiz_id = %s
        """, (quiz_id,))
        quiz_questions = cursor.fetchall()
        question_ids = [q['id'] for q in quiz_questions]
        
        print(f"✓ Found {len(quiz_questions)} questions for quiz")
        
        # 4. Create quiz attempt
        try:
            cursor.execute("""
                INSERT INTO student_attempts 
                (student_id, quiz_id, total_score, submitted_at) 
                VALUES (%s, %s, %s, NOW())
            """, (numeric_student_id, quiz_id, 0.00))
            
            attempt_id = cursor.lastrowid
            print(f"✓ Created attempt: ID {attempt_id}")
            
        except Exception as e:
            cursor.close()
            db.close()
            print(f"✗ Error creating attempt: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "detail": f"Failed to create quiz attempt: {str(e)}",
                    "error_type": "ATTEMPT_CREATION_FAILED"
                }
            )
        
        # 5. Process each answer
        total_marks = 0.00
        processed_count = 0
        
        for i, answer in enumerate(answers):
            question_id = answer.get('question_id')
            selected_option_id = answer.get('selected_option_id')
            answer_text = answer.get('answer_text', '').strip() if answer.get('answer_text') else None
            
            print(f"\n  Processing answer {i + 1}:")
            print(f"    Question ID: {question_id}")
            print(f"    Option ID: {selected_option_id}")
            print(f"    Answer Text: {answer_text}")
            
            # Validate question exists in this quiz
            if question_id not in question_ids:
                print(f"    ⚠️  Question {question_id} not in this quiz. Skipping.")
                continue
            
            # Get question details
            question = next((q for q in quiz_questions if q['id'] == question_id), None)
            if not question:
                print(f"    ⚠️  Question details not found. Skipping.")
                continue
            
            is_correct = False
            marks_obtained = 0.00
            
            # Handle MCQ/True False
            if selected_option_id:
                print(f"    📋 Checking option {selected_option_id}...")
                cursor.execute("""
                    SELECT is_correct FROM options 
                    WHERE id = %s AND question_id = %s
                """, (selected_option_id, question_id))
                
                option = cursor.fetchone()
                if option:
                    is_correct = bool(option['is_correct'])
                    marks_obtained = float(question['marks']) if is_correct else 0.00
                    print(f"    {'✅' if is_correct else '❌'} Option result: correct={is_correct}, marks={marks_obtained}")
                else:
                    print(f"    ⚠️  Option not found, treating as incorrect")
            
            # Handle short answer
            elif answer_text:
                print(f"    📝 Checking short answer...")
                correct_answer = question.get('correct_answer', '').strip().lower() if question.get('correct_answer') else ''
                if correct_answer:
                    is_correct = answer_text.lower() == correct_answer
                    marks_obtained = float(question['marks']) if is_correct else 0.00
                    print(f"    {'✅' if is_correct else '❌'} Short answer: correct={is_correct}, marks={marks_obtained}")
                else:
                    print(f"    ⚠️  No correct answer defined for this question")
            
            # Insert answer
            try:
                cursor.execute("""
                    INSERT INTO student_answers 
                    (attempt_id, question_id, selected_option_id, answer_text, is_correct, marks_obtained) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    attempt_id,
                    question_id,
                    selected_option_id if selected_option_id else None,
                    answer_text,
                    is_correct,
                    marks_obtained
                ))
                
                total_marks += marks_obtained
                processed_count += 1
                print(f"    ✓ Answer saved successfully")
                
            except Exception as insert_error:
                print(f"    ✗ Failed to save answer: {str(insert_error)}")
                continue
        
        # 6. Update attempt with total score
        cursor.execute("""
            UPDATE student_attempts 
            SET total_score = %s 
            WHERE id = %s
        """, (float(total_marks), attempt_id))
        
        # 7. Update quiz attempts count
        cursor.execute("""
            UPDATE quizzes 
            SET attempts = attempts + 1 
            WHERE id = %s
        """, (quiz_id,))
        
        db.commit()
        
        # 8. Calculate percentage
        percentage = 0.00
        total_quiz_marks = quiz.get('total_marks', 100)
        if total_quiz_marks and total_quiz_marks > 0:
            percentage = round((total_marks / float(total_quiz_marks)) * 100, 2)
        
        print(f"\n{'='*60}")
        print("🎉 QUIZ SUBMISSION COMPLETE")
        print(f"{'='*60}")
        print(f"Attempt ID: {attempt_id}")
        print(f"Processed answers: {processed_count}/{len(answers)}")
        print(f"Total marks: {total_marks}/{total_quiz_marks}")
        print(f"Percentage: {percentage}%")
        
        response_data = {
            "success": True,
            "attempt_id": attempt_id,
            "total_score": total_marks,
            "percentage": percentage,
            "quiz_title": quiz['title'],
            "subject_name": quiz['subject_name'],
            "teacher_name": quiz.get('teacher_name', 'Unknown'),
            "total_marks": total_quiz_marks,
            "processed_answers": processed_count,
            "message": "Quiz submitted successfully!"
        }
        
        cursor.close()
        db.close()
        
        return JSONResponse(status_code=200, content=response_data)
        
    except Exception as e:
        print(f"\n{'✗'*60}")
        print("💥 CRITICAL ERROR IN QUIZ SUBMISSION")
        print(f"{'✗'*60}")
        print(f"Error: {str(e)}")
        traceback.print_exc()
        
        # Cleanup
        try:
            if 'cursor' in locals():
                cursor.close()
            if 'db' in locals():
                db.close()
        except:
            pass
        
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "detail": f"Internal server error: {str(e)}",
                "error_type": "INTERNAL_SERVER_ERROR",
                "traceback": traceback.format_exc()[:500]  # First 500 chars of traceback
            }
        )

@app.get("/student/{userId}/quiz/results")
def get_student_quiz_results_all(userId: str):
    """Get all quiz results for a student"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute(
            """SELECT a.*, q.title as quiz_title, q.subject_name, q.total_marks,
                      u.fullName as teacher_name,
                      ROUND((a.total_score / q.total_marks) * 100, 2) as percentage
               FROM student_attempts a 
               JOIN quizzes q ON a.quiz_id = q.id 
               JOIN users u ON q.teacher_id = u.id 
               WHERE a.student_id = (SELECT id FROM users WHERE userId = %s)
               ORDER BY a.submitted_at DESC""",
            (userId,)
        )
        
        results = cursor.fetchall()
        
        cursor.close()
        db.close()
        
        return {"results": results, "success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching results: {str(e)}")


@app.get("/student/quiz/result/{attempt_id}")
def get_quiz_result_details(attempt_id: int, student_userId: str):
    """Get detailed quiz result for a specific attempt - FIXED FOR EMPTY FIELDS"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Verify the attempt belongs to the student
        cursor.execute(
            """SELECT a.* FROM student_attempts a 
               JOIN users u ON a.student_id = u.id 
               WHERE a.id = %s AND u.userId = %s""",
            (attempt_id, student_userId)
        )
        
        attempt = cursor.fetchone()
        
        if not attempt:
            raise HTTPException(status_code=404, detail="Attempt not found or access denied")
        
        # Get quiz details
        cursor.execute(
            """SELECT q.*, u.fullName as teacher_name 
               FROM quizzes q 
               JOIN users u ON q.teacher_id = u.id 
               WHERE q.id = %s""",
            (attempt['quiz_id'],)
        )
        
        quiz = cursor.fetchone()
        
        # Get detailed answers with COALESCE to handle empty fields
        cursor.execute(
            """SELECT 
                   sa.*, 
                   # Handle question text with fallbacks
                   COALESCE(NULLIF(q.question_text, ''), 
                           NULLIF(q.question_text_arabic, ''), 
                           NULLIF(q.question_text_urdu, ''), 
                           'Question text not available') as question_text,
                   q.question_text_arabic,
                   q.question_text_urdu,
                   q.question_type, 
                   q.marks, 
                   q.correct_answer,
                   # Handle selected option with fallbacks
                   COALESCE(NULLIF(o.option_text, ''), 
                           NULLIF(o.option_text_arabic, ''), 
                           NULLIF(o.option_text_urdu, ''), 
                           '') as selected_option_text,
                   o.option_text_arabic as selected_option_text_arabic,
                   o.option_text_urdu as selected_option_text_urdu,
                   # Handle correct option with fallbacks
                   COALESCE(NULLIF(co.option_text, ''), 
                           NULLIF(co.option_text_arabic, ''), 
                           NULLIF(co.option_text_urdu, ''), 
                           '') as correct_option_text,
                   co.option_text_arabic as correct_option_text_arabic,
                   co.option_text_urdu as correct_option_text_urdu
               FROM student_answers sa 
               JOIN questions q ON sa.question_id = q.id 
               LEFT JOIN options o ON sa.selected_option_id = o.id 
               LEFT JOIN options co ON co.question_id = q.id AND co.is_correct = TRUE
               WHERE sa.attempt_id = %s 
               ORDER BY sa.id""",
            (attempt_id,)
        )
        
        detailed_answers = cursor.fetchall()
        
        cursor.close()
        db.close()
        
        return {
            "quiz": quiz,
            "attempt": attempt,
            "detailed_answers": detailed_answers,
            "percentage": round((attempt['total_score'] / quiz['total_marks']) * 100, 2) if quiz['total_marks'] else 0,
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching result details: {str(e)}")

@app.post("/quiz/{quiz_id}/start_attempt")
def start_quiz_attempt(quiz_id: int, student_userId: str):
    """Start a new quiz attempt for student - CORRECTED"""
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
               WHERE id = %s AND is_published = TRUE""",
            (quiz_id,)
        )
        quiz = cursor.fetchone()
        
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not available")
        
        # Check current date against quiz dates
        from datetime import datetime
        current_date = datetime.now().date()
        start_date = quiz['start_date']
        end_date = quiz['end_date']
        
        if current_date < start_date:
            raise HTTPException(status_code=403, detail="Quiz has not started yet")
        if current_date > end_date:
            raise HTTPException(status_code=403, detail="Quiz has ended")
        
        # Start new attempt - CORRECTED FOR YOUR DATABASE
        cursor.execute(
            """INSERT INTO student_attempts 
               (student_id, quiz_id, total_score) 
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
    
# Add this endpoint to your FastAPI backend
@app.get("/teacher/{teacher_id}/assigned_subjects")
def get_teacher_assigned_subjects(teacher_id: str):
    """Get only the subjects assigned to a specific teacher"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Get teacher's assigned subject
        cursor.execute(
            "SELECT subject FROM users WHERE userId = %s AND role = 'teacher'", 
            (teacher_id,)
        )
        teacher = cursor.fetchone()
        
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher not found")
        
        teacher_subject = teacher.get("subject", "")
        
        if not teacher_subject:
            cursor.close()
            db.close()
            return {
                "assigned_subjects": [],
                "teacher_subject": "",
                "success": True,
                "message": "No subjects assigned to this teacher"
            }
        
        # Split multiple subjects (comma-separated)
        assigned_subjects = [s.strip() for s in teacher_subject.split(',') if s.strip()]
        
        # Get all available subjects for matching
        all_subjects_set = set()
        for year_subjects in predefined_subjects.values():
            for subject in year_subjects:
                all_subjects_set.add(subject["subject_name"])
        
        # Find exact matches for teacher's subjects
        matched_subjects = []
        for teacher_subj in assigned_subjects:
            for available_subj in all_subjects_set:
                if is_subject_match(teacher_subj, available_subj):
                    matched_subjects.append(available_subj)
        
        cursor.close()
        db.close()
        
        return {
            "assigned_subjects": matched_subjects,
            "teacher_subject": teacher_subject,
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching teacher subjects: {str(e)}")
  # ------------------- ASSIGNMENT SUBMISSION SYSTEM -------------------

# Pydantic models for assignment submissions
class AssignmentSubmissionCreate(BaseModel):
    student_userId: str
    assignment_id: int
    submission_text: Optional[str] = None
    file_name: Optional[str] = None
    file_path: Optional[str] = None

class AssignmentGradeUpdate(BaseModel):
    marks_obtained: float
    feedback: Optional[str] = None
    graded_by: str  # teacher ID

# Endpoint for teachers to get all submissions for an assignment
@app.get("/assignments/{assignment_id}/submissions")
def get_assignment_submissions(assignment_id: int, teacher_userId: str):
    """Get all submissions for an assignment (teacher view) - DEBUG VERSION"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        print(f"🔍 DEBUG: Starting get_assignment_submissions for assignment {assignment_id}")
        print(f"🔍 DEBUG: Teacher userId: {teacher_userId}")
        
        # Verify teacher owns this assignment
        cursor.execute(
            """SELECT a.id, a.teacher_id, a.title, u.userId as teacher_userId 
               FROM assignments a 
               JOIN users u ON a.teacher_id = u.id 
               WHERE u.userId = %s AND a.id = %s""",
            (teacher_userId, assignment_id)
        )
        
        assignment_auth = cursor.fetchone()
        print(f"🔍 DEBUG: Teacher authorization check: {assignment_auth}")
        
        if not assignment_auth:
            cursor.close()
            db.close()
            return {
                "error": "Not authorized to view these submissions or assignment not found",
                "success": False,
                "debug": {
                    "assignment_id": assignment_id,
                    "teacher_userId": teacher_userId,
                    "message": "Teacher doesn't own this assignment or assignment doesn't exist"
                }
            }
        
        # Debug: Check what's in assignment_submissions table
        cursor.execute("SELECT COUNT(*) as count FROM assignment_submissions WHERE assignment_id = %s", (assignment_id,))
        count_result = cursor.fetchone()
        print(f"🔍 DEBUG: Total submissions in assignment_submissions table: {count_result['count']}")
        
        # Debug: Show all submissions for this assignment
        cursor.execute("SELECT * FROM assignment_submissions WHERE assignment_id = %s", (assignment_id,))
        raw_submissions = cursor.fetchall()
        print(f"🔍 DEBUG: Raw submissions from assignment_submissions table:")
        for sub in raw_submissions:
            print(f"  - ID: {sub.get('id')}, Student ID: {sub.get('student_id')}, Status: {sub.get('status')}")
        
        # Debug: Check the users table for student info
        if raw_submissions:
            student_ids = [str(sub['student_id']) for sub in raw_submissions if sub.get('student_id')]
            print(f"🔍 DEBUG: Student IDs in submissions: {student_ids}")
            
            cursor.execute(f"SELECT id, userId, fullName FROM users WHERE id IN ({','.join(student_ids)})")
            students = cursor.fetchall()
            print(f"🔍 DEBUG: Students found in users table: {students}")
        
        # Get all submissions with student info using LEFT JOIN to ensure we get all submissions
        # even if student info is missing
        query = """
            SELECT 
                s.*,
                u.userId as student_userId,
                u.fullName as student_name,
                u.email as student_email,
                u.phone as student_phone,
                a.title as assignment_title,
                a.total_marks as assignment_total_marks,
                TIMESTAMPDIFF(HOUR, s.submission_date, a.due_date) as hours_early
            FROM assignment_submissions s
            LEFT JOIN assignments a ON s.assignment_id = a.id
            LEFT JOIN users u ON s.student_id = u.id
            WHERE s.assignment_id = %s
            ORDER BY s.submission_date DESC
        """
        
        print(f"🔍 DEBUG: Executing query: {query}")
        cursor.execute(query, (assignment_id,))
        submissions = cursor.fetchall()
        
        print(f"🔍 DEBUG: Query returned {len(submissions)} submissions")
        for i, sub in enumerate(submissions):
            print(f"  Submission {i+1}: ID={sub.get('id')}, Student={sub.get('student_name')}, Student ID={sub.get('student_id')}")
        
        # Get assignment details
        cursor.execute(
            """SELECT a.*, u.fullName as teacher_name 
               FROM assignments a 
               JOIN users u ON a.teacher_id = u.id 
               WHERE a.id = %s""",
            (assignment_id,)
        )
        assignment_details = cursor.fetchone()
        
        cursor.close()
        db.close()
        
        print(f"🔍 DEBUG: Final response - Assignment: {assignment_details.get('title') if assignment_details else 'Not found'}")
        print(f"🔍 DEBUG: Final response - Submissions count: {len(submissions)}")
        
        # Convert decimal to float for JSON serialization
        for sub in submissions:
            if 'marks_obtained' in sub and sub['marks_obtained'] is not None:
                sub['marks_obtained'] = float(sub['marks_obtained'])
        
        return {
            "assignment": assignment_details,
            "submissions": submissions,
            "total_submissions": len(submissions),
            "success": True,
            "debug": {
                "raw_count": count_result['count'],
                "assignment_id": assignment_id,
                "teacher_userId": teacher_userId,
                "query_used": query
            }
        }
        
    except Exception as e:
        print(f"🔍 DEBUG: ERROR in get_assignment_submissions: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "error": f"Error fetching submissions: {str(e)}",
            "success": False
        }

# Debug endpoint to check database directly
@app.get("/debug/direct-submissions/{assignment_id}")
def debug_direct_submissions(assignment_id: int):
    """Direct debug endpoint to check submissions without authorization"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Check if assignment exists
        cursor.execute("SELECT * FROM assignments WHERE id = %s", (assignment_id,))
        assignment = cursor.fetchone()
        
        if not assignment:
            return {"error": "Assignment not found", "success": False}
        
        # Get all submissions without JOIN first
        cursor.execute("SELECT * FROM assignment_submissions WHERE assignment_id = %s", (assignment_id,))
        raw_submissions = cursor.fetchall()
        
        # Try to get student info
        submissions_with_student = []
        for sub in raw_submissions:
            student_id = sub.get('student_id')
            if student_id:
                cursor.execute("SELECT userId, fullName, email FROM users WHERE id = %s", (student_id,))
                student = cursor.fetchone()
                if student:
                    sub['student_userId'] = student['userId']
                    sub['student_name'] = student['fullName']
                    sub['student_email'] = student['email']
                else:
                    sub['student_userId'] = 'Unknown'
                    sub['student_name'] = 'Student Not Found'
                    sub['student_email'] = ''
            submissions_with_student.append(sub)
        
        # Get teacher info
        teacher_id = assignment.get('teacher_id')
        teacher_info = {}
        if teacher_id:
            cursor.execute("SELECT userId, fullName FROM users WHERE id = %s", (teacher_id,))
            teacher = cursor.fetchone()
            if teacher:
                teacher_info = teacher
        
        cursor.close()
        db.close()
        
        return {
            "success": True,
            "assignment": assignment,
            "teacher": teacher_info,
            "submissions": submissions_with_student,
            "raw_submissions": raw_submissions,
            "submission_count": len(raw_submissions),
            "assignment_id": assignment_id,
            "teacher_id": teacher_id
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e), "success": False}

@app.get("/submission/{submission_id}")
def get_submission_details(submission_id: int, teacher_userId: str = None):
    """Get details of a specific submission"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        print(f"DEBUG: Getting submission {submission_id}")
        
        # Get submission with student info
        query = """
            SELECT 
                s.*,
                u.userId as student_userId,
                u.fullName as student_name,
                u.email as student_email,
                a.title as assignment_title,
                a.subject_name,
                a.teacher_id,
                t.userId as teacher_userId,
                t.fullName as teacher_name
            FROM assignment_submissions s
            LEFT JOIN users u ON s.student_id = u.id
            LEFT JOIN assignments a ON s.assignment_id = a.id
            LEFT JOIN users t ON a.teacher_id = t.id
            WHERE s.id = %s
        """
        
        cursor.execute(query, (submission_id,))
        submission = cursor.fetchone()
        
        if not submission:
            cursor.close()
            db.close()
            return {"error": "Submission not found", "success": False}
        
        # If teacher_userId provided, verify ownership
        if teacher_userId:
            if submission['teacher_userId'] != teacher_userId:
                cursor.close()
                db.close()
                return {
                    "error": "Not authorized to view this submission",
                    "success": False
                }
        
        cursor.close()
        db.close()
        
        return {
            "submission": submission,
            "success": True
        }
        
    except Exception as e:
        print(f"Error in get_submission_details: {str(e)}")
        return {"error": str(e), "success": False}

# Add these imports at the top
import os
from fastapi.responses import FileResponse
from fastapi import HTTPException

# Add this endpoint to handle file downloads
@app.get("/assignments/submissions/{submission_id}/download")
def download_submission_file(submission_id: int, teacher_userId: str = None):
    """Download a submission file"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Get submission details
        cursor.execute(
            """SELECT s.*, a.teacher_id, u.userId as student_userId 
               FROM assignment_submissions s
               JOIN assignments a ON s.assignment_id = a.id
               LEFT JOIN users u ON s.student_id = u.id
               WHERE s.id = %s""",
            (submission_id,)
        )
        submission = cursor.fetchone()
        
        if not submission:
            cursor.close()
            db.close()
            raise HTTPException(status_code=404, detail="Submission not found")
        
        # Verify teacher owns this assignment if teacher_userId is provided
        if teacher_userId:
            cursor.execute(
                """SELECT u.userId FROM users u 
                   WHERE u.id = %s AND u.userId = %s""",
                (submission['teacher_id'], teacher_userId)
            )
            teacher = cursor.fetchone()
            
            if not teacher:
                cursor.close()
                db.close()
                raise HTTPException(status_code=403, detail="Not authorized to download this file")
        
        cursor.close()
        db.close()
        
        # Get file path
        file_path = submission.get('file_path')
        if not file_path or not os.path.exists(file_path):
            print(f"DEBUG: File not found at path: {file_path}")
            print(f"DEBUG: Current working directory: {os.getcwd()}")
            print(f"DEBUG: Submission file_name: {submission.get('file_name')}")
            
            # Try alternative paths
            base_path = os.path.join(os.getcwd(), 'uploads', 'assignment_submissions')
            possible_paths = [
                file_path,
                os.path.join(base_path, str(submission_id), submission.get('file_name', '')),
                os.path.join(base_path, str(submission['assignment_id']), submission.get('file_name', '')),
                os.path.join(base_path, submission.get('file_name', ''))
            ]
            
            for path in possible_paths:
                if path and os.path.exists(path):
                    file_path = path
                    break
            
            if not file_path or not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="File not found on server")
        
        # Get file name for download
        file_name = submission.get('file_name', 'submission_file')
        
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"ERROR: File does not exist at: {file_path}")
            raise HTTPException(status_code=404, detail="File not found")
        
        print(f"DEBUG: Serving file from: {file_path}")
        
        # Serve the file
        return FileResponse(
            path=file_path,
            filename=file_name,
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in download_submission_file: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")

# Add this endpoint to get file for viewing in browser
@app.get("/assignments/submissions/{submission_id}/view")
def view_submission_file(submission_id: int, teacher_userId: str = None):
    """View a submission file in browser (for PDFs, images, etc.)"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Get submission details
        cursor.execute(
            """SELECT s.*, a.teacher_id, u.userId as student_userId 
               FROM assignment_submissions s
               JOIN assignments a ON s.assignment_id = a.id
               LEFT JOIN users u ON s.student_id = u.id
               WHERE s.id = %s""",
            (submission_id,)
        )
        submission = cursor.fetchone()
        
        if not submission:
            cursor.close()
            db.close()
            raise HTTPException(status_code=404, detail="Submission not found")
        
        # Verify teacher owns this assignment if teacher_userId is provided
        if teacher_userId:
            cursor.execute(
                """SELECT u.userId FROM users u 
                   WHERE u.id = %s AND u.userId = %s""",
                (submission['teacher_id'], teacher_userId)
            )
            teacher = cursor.fetchone()
            
            if not teacher:
                cursor.close()
                db.close()
                raise HTTPException(status_code=403, detail="Not authorized to view this file")
        
        cursor.close()
        db.close()
        
        # Get file path
        file_path = submission.get('file_path')
        file_name = submission.get('file_name', '')
        
        if not file_path or not os.path.exists(file_path):
            # Try to find the file
            base_path = os.path.join(os.getcwd(), 'uploads', 'assignment_submissions')
            possible_paths = [
                file_path,
                os.path.join(base_path, str(submission_id), file_name),
                os.path.join(base_path, str(submission['assignment_id']), file_name),
                os.path.join(base_path, file_name)
            ]
            
            for path in possible_paths:
                if path and os.path.exists(path):
                    file_path = path
                    break
        
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found on server")
        
        # Determine content type based on file extension
        file_ext = os.path.splitext(file_name)[1].lower()
        
        content_type_map = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.txt': 'text/plain',
            '.text': 'text/plain',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.mp4': 'video/mp4',
            '.avi': 'video/x-msvideo',
            '.mov': 'video/quicktime'
        }
        
        content_type = content_type_map.get(file_ext, 'application/octet-stream')
        
        return FileResponse(
            path=file_path,
            filename=file_name,
            media_type=content_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in view_submission_file: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error viewing file: {str(e)}")

# Debug endpoint to check file paths
@app.get("/debug/submission/{submission_id}/file-info")
def debug_submission_file_info(submission_id: int):
    """Debug endpoint to check file information"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute(
            "SELECT id, assignment_id, student_id, file_name, file_path FROM assignment_submissions WHERE id = %s",
            (submission_id,)
        )
        submission = cursor.fetchone()
        
        cursor.close()
        db.close()
        
        if not submission:
            return {"error": "Submission not found", "success": False}
        
        # Check file existence
        file_exists = False
        actual_path = None
        
        if submission['file_path'] and os.path.exists(submission['file_path']):
            file_exists = True
            actual_path = submission['file_path']
        else:
            # Try to find it
            base_path = os.path.join(os.getcwd(), 'uploads', 'assignment_submissions')
            possible_paths = [
                submission['file_path'],
                os.path.join(base_path, str(submission_id), submission['file_name']),
                os.path.join(base_path, str(submission['assignment_id']), submission['file_name']),
                os.path.join(base_path, submission['file_name'])
            ]
            
            for path in possible_paths:
                if path and os.path.exists(path):
                    file_exists = True
                    actual_path = path
                    break
        
        return {
            "success": True,
            "submission_id": submission_id,
            "file_name": submission['file_name'],
            "file_path": submission['file_path'],
            "file_exists": file_exists,
            "actual_path": actual_path,
            "current_directory": os.getcwd(),
            "uploads_directory_exists": os.path.exists(os.path.join(os.getcwd(), 'uploads'))
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e), "success": False}

# Endpoint to grade a submission

@app.post("/assignments/submissions/{submission_id}/grade")
def grade_submission(submission_id: int, teacher_userId: str, grade_data: AssignmentGradeUpdate):
    """Grade a student submission"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        print(f"DEBUG: Grading submission {submission_id} by teacher {teacher_userId}")
        print(f"DEBUG: Grade data: {grade_data}")
        
        # 1. Get submission details WITHOUT total_marks column
        cursor.execute("""
            SELECT s.*, a.teacher_id, a.title as assignment_title
            FROM assignment_submissions s
            JOIN assignments a ON s.assignment_id = a.id
            WHERE s.id = %s
        """, (submission_id,))
        
        submission = cursor.fetchone()
        
        if not submission:
            cursor.close()
            db.close()
            return {
                "error": "Submission not found",
                "success": False
            }
        
        # 2. Verify teacher owns this assignment
        cursor.execute("""
            SELECT u.id, u.userId, u.fullName 
            FROM users u 
            WHERE u.id = %s AND u.userId = %s AND u.role = 'teacher'
        """, (submission['teacher_id'], teacher_userId))
        
        teacher = cursor.fetchone()
        
        if not teacher:
            cursor.close()
            db.close()
            return {
                "error": "Not authorized to grade this submission",
                "success": False,
                "debug": {
                    "teacher_id_in_assignment": submission['teacher_id'],
                    "teacher_userId_provided": teacher_userId
                }
            }
        
        # 3. Use default total marks (100) since column doesn't exist
        total_marks = 100  # Default value since column doesn't exist
        
        if grade_data.marks_obtained < 0 or grade_data.marks_obtained > total_marks:
            cursor.close()
            db.close()
            return {
                "error": f"Marks must be between 0 and {total_marks}",
                "success": False
            }
        
        # 4. Update the submission with grade AND status
        update_query = """
            UPDATE assignment_submissions 
            SET marks_obtained = %s,
                feedback = %s,
                graded_by = %s,
                graded_date = NOW(),
                status = 'graded'
            WHERE id = %s
        """
        
        print(f"DEBUG: Updating submission with marks: {grade_data.marks_obtained}")
        
        cursor.execute(update_query, (
            float(grade_data.marks_obtained),
            grade_data.feedback or "",
            teacher['id'],  # Use teacher's database ID
            submission_id
        ))
        
        # 5. Update assignment submissions count (removed total_marks reference)
        cursor.execute("""
            UPDATE assignments 
            SET submissions = (
                SELECT COUNT(*) 
                FROM assignment_submissions 
                WHERE assignment_id = %s AND status IN ('submitted', 'graded', 'late')
            )
            WHERE id = %s
        """, (submission['assignment_id'], submission['assignment_id']))
        
        db.commit()
        
        # 6. Get updated submission for response (without total_marks)
        cursor.execute("""
            SELECT 
                s.*,
                u.fullName as student_name,
                u.email as student_email,
                t.fullName as teacher_name,
                a.title as assignment_title
            FROM assignment_submissions s
            JOIN users u ON s.student_id = u.id
            JOIN assignments a ON s.assignment_id = a.id
            LEFT JOIN users t ON s.graded_by = t.id
            WHERE s.id = %s
        """, (submission_id,))
        
        updated_submission = cursor.fetchone()
        
        # 7. Add total marks to response (using default)
        if updated_submission:
            updated_submission['assignment_total_marks'] = total_marks
        
        # 8. Create notification for student (optional)
        try:
            cursor.execute("""
                INSERT INTO notifications (teacher_id, subject_name, title, message, priority)
                VALUES (%s, %s, %s, %s, 'high')
            """, (
                teacher['id'],
                "Assignment Graded",
                f"Your assignment '{submission['assignment_title']}' has been graded",
                f"Teacher {teacher['fullName']} has graded your assignment. You received {grade_data.marks_obtained}/{total_marks} marks.",
                'high'
            ))
            db.commit()
        except Exception as e:
            print(f"Note: Could not create notification: {e}")
        
        cursor.close()
        db.close()
        
        return {
            "success": True,
            "message": "Grade submitted successfully",
            "submission": updated_submission,
            "debug": {
                "submission_id": submission_id,
                "marks_set": grade_data.marks_obtained,
                "status_set": "graded",
                "total_marks_used": total_marks
            }
        }
        
    except Exception as e:
        print(f"Error in grade_submission: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "error": f"Error submitting grade: {str(e)}",
            "success": False
        }


# Endpoint for student to get their submissions for a specific subject
@app.get("/student/{student_userId}/assignment_submissions")
def get_student_submissions(student_userId: str, subject_name: str = None):
    """Get all submissions for a student, optionally filtered by subject"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        print(f"DEBUG: Getting submissions for student {student_userId}, subject: {subject_name}")
        
        # Get student ID from userId
        cursor.execute("SELECT id FROM users WHERE userId = %s AND role = 'student'", (student_userId,))
        student = cursor.fetchone()
        
        if not student:
            cursor.close()
            db.close()
            return {
                "error": "Student not found",
                "success": False
            }
        
        student_id = student['id']
        
        # Build query based on whether subject_name is provided
        if subject_name:
            query = """
                SELECT 
                    s.*,
                    a.title as assignment_title,
                    a.description as assignment_description,
                    a.subject_name,
                    a.due_date as assignment_due_date,
                    t.fullName as teacher_name,
                    t.userId as teacher_userId,
                    g.fullName as graded_by_name
                FROM assignment_submissions s
                JOIN assignments a ON s.assignment_id = a.id
                JOIN users t ON a.teacher_id = t.id
                LEFT JOIN users g ON s.graded_by = g.id
                WHERE s.student_id = %s 
                AND a.subject_name = %s
                ORDER BY s.submission_date DESC
            """
            cursor.execute(query, (student_id, subject_name))
        else:
            query = """
                SELECT 
                    s.*,
                    a.title as assignment_title,
                    a.description as assignment_description,
                    a.subject_name,
                    a.due_date as assignment_due_date,
                    t.fullName as teacher_name,
                    t.userId as teacher_userId,
                    g.fullName as graded_by_name
                FROM assignment_submissions s
                JOIN assignments a ON s.assignment_id = a.id
                JOIN users t ON a.teacher_id = t.id
                LEFT JOIN users g ON s.graded_by = g.id
                WHERE s.student_id = %s
                ORDER BY s.submission_date DESC
            """
            cursor.execute(query, (student_id,))
        
        submissions = cursor.fetchall()
        
        # Convert decimal to float for JSON serialization
        for sub in submissions:
            if 'marks_obtained' in sub and sub['marks_obtained'] is not None:
                sub['marks_obtained'] = float(sub['marks_obtained'])
        
        cursor.close()
        db.close()
        
        return {
            "success": True,
            "submissions": submissions,
            "total_submissions": len(submissions)
        }
        
    except Exception as e:
        print(f"Error in get_student_submissions: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "error": f"Error fetching submissions: {str(e)}",
            "success": False
        }

# Also, let's add an endpoint for getting assignment details with subject filtering
@app.get("/assignments/{teacher_userId}/{subject_name}")
def get_assignments_by_subject(teacher_userId: str, subject_name: str):
    """Get assignments for a specific teacher and subject"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        print(f"DEBUG: Getting assignments for teacher {teacher_userId}, subject: {subject_name}")
        
        # Get teacher ID
        cursor.execute("SELECT id FROM users WHERE userId = %s AND role = 'teacher'", (teacher_userId,))
        teacher = cursor.fetchone()
        
        if not teacher:
            cursor.close()
            db.close()
            return {
                "error": "Teacher not found",
                "success": False
            }
        
        # Get assignments for this teacher and subject
        query = """
            SELECT 
                a.*,
                COUNT(s.id) as submissions_count
            FROM assignments a
            LEFT JOIN assignment_submissions s ON a.id = s.assignment_id
            WHERE a.teacher_id = %s 
            AND a.subject_name = %s
            GROUP BY a.id
            ORDER BY a.due_date DESC
        """
        
        cursor.execute(query, (teacher['id'], subject_name))
        assignments = cursor.fetchall()
        
        cursor.close()
        db.close()
        
        return {
            "success": True,
            "assignments": assignments,
            "total_assignments": len(assignments)
        }
        
    except Exception as e:
        print(f"Error in get_assignments_by_subject: {str(e)}")
        return {
            "error": f"Error fetching assignments: {str(e)}",
            "success": False
        }

# Endpoint for student to view their graded submission
@app.get("/student/{student_userId}/assignment_submission/{submission_id}")
def get_student_submission_details(student_userId: str, submission_id: int):
    """Get detailed submission info for a student"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Get submission with assignment and teacher info
        query = """
            SELECT 
                s.*,
                a.title as assignment_title,
                a.description as assignment_description,
                a.total_marks as assignment_total_marks,
                a.due_date as assignment_due_date,
                t.fullName as teacher_name,
                t.userId as teacher_userId,
                u.fullName as student_name
            FROM assignment_submissions s
            JOIN assignments a ON s.assignment_id = a.id
            JOIN users u ON s.student_id = u.id
            JOIN users t ON a.teacher_id = t.id
            WHERE s.id = %s AND u.userId = %s
        """
        
        cursor.execute(query, (submission_id, student_userId))
        submission = cursor.fetchone()
        
        if not submission:
            cursor.close()
            db.close()
            return {
                "error": "Submission not found or not authorized",
                "success": False
            }
        
        cursor.close()
        db.close()
        
        return {
            "success": True,
            "submission": submission
        }
        
    except Exception as e:
        print(f"Error in get_student_submission_details: {str(e)}")
        return {"error": str(e), "success": False}
    

# Add these imports if not already there
from datetime import datetime, timezone

# Endpoint for auto-grading overdue assignments
@app.post("/assignments/auto-grade-overdue")
def auto_grade_overdue_assignment(request_data: dict):
    """Auto-grade an overdue assignment with 0 marks (NO late submissions allowed)"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        student_userId = request_data.get('student_userId')
        assignment_id = request_data.get('assignment_id')
        teacher_userId = request_data.get('teacher_userId')
        subject_name = request_data.get('subject_name')
        
        print(f"DEBUG: Auto-grading assignment {assignment_id} for student {student_userId}")
        
        # Get student ID
        cursor.execute(
            "SELECT id FROM users WHERE userId = %s AND role = 'student'",
            (student_userId,)
        )
        student = cursor.fetchone()
        
        if not student:
            cursor.close()
            db.close()
            return {"success": False, "error": "Student not found"}
        
        student_id = student['id']
        
        # Get teacher ID
        cursor.execute(
            "SELECT id FROM users WHERE userId = %s AND role = 'teacher'",
            (teacher_userId,)
        )
        teacher = cursor.fetchone()
        
        if not teacher:
            cursor.close()
            db.close()
            return {"success": False, "error": "Teacher not found"}
        
        teacher_id = teacher['id']
        
        # Get assignment details
        cursor.execute("""
            SELECT a.*, u.userId as teacher_userId
            FROM assignments a
            JOIN users u ON a.teacher_id = u.id
            WHERE a.id = %s 
            AND a.teacher_id = %s 
            AND a.subject_name = %s
        """, (assignment_id, teacher_id, subject_name))
        
        assignment = cursor.fetchone()
        
        if not assignment:
            cursor.close()
            db.close()
            return {"success": False, "error": "Assignment not found"}
        
        # Check if assignment is overdue
        current_time = datetime.now(timezone.utc)
        due_date = assignment['due_date']
        
        if due_date.tzinfo is None:
            due_date = due_date.replace(tzinfo=timezone.utc)
        
        is_overdue = current_time > due_date
        
        if not is_overdue:
            cursor.close()
            db.close()
            return {"success": False, "error": "Assignment is not yet overdue"}
        
        # Check if already has a submission
        cursor.execute("""
            SELECT id, auto_graded, marks_obtained 
            FROM assignment_submissions 
            WHERE assignment_id = %s 
            AND student_id = %s
        """, (assignment_id, student_id))
        
        existing_submission = cursor.fetchone()
        
        if existing_submission:
            cursor.close()
            db.close()
            return {
                "success": False, 
                "error": "Already has a submission", 
                "submission": existing_submission
            }
        
        # Auto-grade with 0 marks
        total_marks = assignment.get('total_marks', 100)
        
        # Insert auto-graded submission
        insert_query = """
            INSERT INTO assignment_submissions 
            (assignment_id, student_id, submission_text, submission_date,
             marks_obtained, feedback, graded_by, graded_date, status,
             auto_graded)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_query, (
            assignment_id,
            student_id,
            'Auto-graded: No submission received before deadline',
            current_time,
            0.0,
            f'Automatically graded with 0 marks. Assignment was due on {due_date.strftime("%Y-%m-%d %H:%M")}. Late submissions are not accepted.',
            teacher_id,
            current_time,
            'graded',
            True
        ))
        
        submission_id = cursor.lastrowid
        
        # Update assignment submissions count
        cursor.execute("""
            UPDATE assignments 
            SET submissions = (
                SELECT COUNT(*) 
                FROM assignment_submissions 
                WHERE assignment_id = %s
            )
            WHERE id = %s
        """, (assignment_id, assignment_id))
        
        db.commit()
        
        # Get the created submission for response
        cursor.execute("""
            SELECT s.*, u.fullName as student_name, u.email as student_email,
                   a.title as assignment_title
            FROM assignment_submissions s
            JOIN users u ON s.student_id = u.id
            JOIN assignments a ON s.assignment_id = a.id
            WHERE s.id = %s
        """, (submission_id,))
        
        new_submission = cursor.fetchone()
        
        cursor.close()
        db.close()
        
        print(f"DEBUG: Successfully auto-graded assignment {assignment_id}")
        
        return {
            "success": True,
            "message": "Assignment auto-graded with 0 marks",
            "submission_id": submission_id,
            "submission": new_submission,
            "marks_obtained": 0,
            "total_marks": total_marks
        }
        
    except Exception as e:
        print(f"Error in auto_grade_overdue_assignment: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

# Update the submit_assignment endpoint to reject late submissions
@app.post("/student/submit_assignment")
def submit_assignment(submission: AssignmentSubmissionCreate):
    """Submit an assignment - REJECTS late submissions"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        print(f"DEBUG: Submitting assignment for student {submission.student_userId}")
        
        # Get student ID
        cursor.execute(
            "SELECT id FROM users WHERE userId = %s AND role = 'student'",
            (submission.student_userId,)
        )
        student = cursor.fetchone()
        
        if not student:
            cursor.close()
            db.close()
            return {
                "error": "Student not found",
                "success": False
            }
        
        student_id = student['id']
        
        # Get assignment details including due date
        cursor.execute("""
            SELECT a.*, u.userId as teacher_userId, u.fullName as teacher_name
            FROM assignments a
            JOIN users u ON a.teacher_id = u.id
            WHERE a.id = %s
        """, (submission.assignment_id,))
        
        assignment = cursor.fetchone()
        
        if not assignment:
            cursor.close()
            db.close()
            return {
                "error": "Assignment not found",
                "success": False
            }
        
        # Check if assignment is overdue
        current_time = datetime.now(timezone.utc)
        due_date = assignment['due_date']
        
        if due_date.tzinfo is None:
            due_date = due_date.replace(tzinfo=timezone.utc)
        
        is_overdue = current_time > due_date
        
        # REJECT late submissions
        if is_overdue:
            cursor.close()
            db.close()
            return {
                "error": "Late submissions are not accepted. Assignment deadline has passed.",
                "success": False,
                "due_date": due_date.isoformat(),
                "current_time": current_time.isoformat()
            }
        
        # Check if already submitted
        cursor.execute("""
            SELECT id, auto_graded 
            FROM assignment_submissions 
            WHERE assignment_id = %s 
            AND student_id = %s
        """, (submission.assignment_id, student_id))
        
        existing_submission = cursor.fetchone()
        
        if existing_submission:
            # If it's auto-graded (0 marks), allow resubmission
            if existing_submission['auto_graded']:
                # Delete auto-graded submission to allow fresh submission
                cursor.execute(
                    "DELETE FROM assignment_submissions WHERE id = %s",
                    (existing_submission['id'],)
                )
            else:
                cursor.close()
                db.close()
                return {
                    "error": "Assignment already submitted",
                    "success": False,
                    "submission_id": existing_submission['id']
                }
        
        # Insert submission (not overdue, so status is 'submitted')
        insert_query = """
            INSERT INTO assignment_submissions 
            (assignment_id, student_id, submission_text, file_name, file_path, 
             submission_date, status, auto_graded)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_query, (
            submission.assignment_id,
            student_id,
            submission.submission_text,
            submission.file_name,
            submission.file_path,
            current_time,
            'submitted',
            False  # Not auto-graded
        ))
        
        submission_id = cursor.lastrowid
        
        # Update assignment submissions count
        cursor.execute("""
            UPDATE assignments 
            SET submissions = (
                SELECT COUNT(*) 
                FROM assignment_submissions 
                WHERE assignment_id = %s
            )
            WHERE id = %s
        """, (submission.assignment_id, submission.assignment_id))
        
        db.commit()
        
        # Get the created submission
        cursor.execute("""
            SELECT s.*, u.fullName as student_name, u.email as student_email,
                   a.title as assignment_title, a.subject_name,
                   t.fullName as teacher_name
            FROM assignment_submissions s
            JOIN users u ON s.student_id = u.id
            JOIN assignments a ON s.assignment_id = a.id
            JOIN users t ON a.teacher_id = t.id
            WHERE s.id = %s
        """, (submission_id,))
        
        new_submission = cursor.fetchone()
        
        cursor.close()
        db.close()
        
        return {
            "success": True,
            "message": "Assignment submitted successfully",
            "submission_id": submission_id,
            "submission": new_submission,
            "due_date": due_date.isoformat(),
            "submitted_at": current_time.isoformat()
        }
        
    except Exception as e:
        print(f"Error in submit_assignment: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "error": f"Error submitting assignment: {str(e)}",
            "success": False
        }
    
# Add this endpoint for auto-grading
@app.post("/auto-grade/check-and-grade")
def check_and_auto_grade(request_data: dict):
    """Check if assignment needs auto-grading and do it"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        student_userId = request_data.get('student_userId')
        assignment_id = request_data.get('assignment_id')
        teacher_userId = request_data.get('teacher_userId')
        subject_name = request_data.get('subject_name')
        
        # Get student ID
        cursor.execute(
            "SELECT id FROM users WHERE userId = %s AND role = 'student'",
            (student_userId,)
        )
        student = cursor.fetchone()
        
        if not student:
            return {"success": False, "error": "Student not found"}
        
        student_id = student['id']
        
        # Get teacher ID
        cursor.execute(
            "SELECT id FROM users WHERE userId = %s AND role = 'teacher'",
            (teacher_userId,)
        )
        teacher = cursor.fetchone()
        
        if not teacher:
            return {"success": False, "error": "Teacher not found"}
        
        teacher_id = teacher['id']
        
        # Check if already submitted
        cursor.execute("""
            SELECT id, marks_obtained 
            FROM assignment_submissions 
            WHERE assignment_id = %s 
            AND student_id = %s
        """, (assignment_id, student_id))
        
        existing = cursor.fetchone()
        
        if existing:
            return {
                "success": True, 
                "auto_graded": False, 
                "message": "Already submitted",
                "submission": existing
            }
        
        # Check if assignment is overdue
        cursor.execute("""
            SELECT a.*, 
                   CASE WHEN a.due_date < NOW() THEN 1 ELSE 0 END as is_overdue
            FROM assignments a
            WHERE a.id = %s 
            AND a.teacher_id = %s 
            AND a.subject_name = %s
        """, (assignment_id, teacher_id, subject_name))
        
        assignment = cursor.fetchone()
        
        if not assignment:
            return {"success": False, "error": "Assignment not found"}
        
        # If overdue, auto-grade with 0 marks
        if assignment['is_overdue'] == 1:
            try:
                # First, check if auto_graded column exists
                cursor.execute("SHOW COLUMNS FROM assignment_submissions LIKE 'auto_graded'")
                has_auto_graded = cursor.fetchone()
                
                # Insert auto-graded submission
                if has_auto_graded:
                    insert_query = """
                        INSERT INTO assignment_submissions 
                        (assignment_id, student_id, submission_text, submission_date,
                         marks_obtained, feedback, graded_by, graded_date, status,
                         auto_graded)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (
                        assignment_id,
                        student_id,
                        'Auto-graded: No submission before deadline',
                        datetime.now(timezone.utc),
                        0.0,
                        'Automatically graded with 0 marks. Late submissions not accepted.',
                        teacher_id,
                        datetime.now(timezone.utc),
                        'graded',
                        True
                    ))
                else:
                    # Fallback without auto_graded column
                    insert_query = """
                        INSERT INTO assignment_submissions 
                        (assignment_id, student_id, submission_text, submission_date,
                         marks_obtained, feedback, graded_by, graded_date, status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (
                        assignment_id,
                        student_id,
                        'Auto-graded: No submission before deadline',
                        datetime.now(timezone.utc),
                        0.0,
                        'Automatically graded with 0 marks. Late submissions not accepted.',
                        teacher_id,
                        datetime.now(timezone.utc),
                        'graded'
                    ))
                
                submission_id = cursor.lastrowid
                
                # Update submissions count
                cursor.execute("""
                    UPDATE assignments 
                    SET submissions = (
                        SELECT COUNT(*) 
                        FROM assignment_submissions 
                        WHERE assignment_id = %s
                    )
                    WHERE id = %s
                """, (assignment_id, assignment_id))
                
                db.commit()
                
                return {
                    "success": True,
                    "auto_graded": True,
                    "message": "Auto-graded with 0 marks",
                    "submission_id": submission_id
                }
                
            except Exception as e:
                db.rollback()
                return {"success": False, "error": f"Error auto-grading: {str(e)}"}
        else:
            return {
                "success": True, 
                "auto_graded": False, 
                "message": "Not overdue yet"
            }
        
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        cursor.close()
        db.close()

# Add this endpoint to get student by userId
@app.get("/users")
def get_user_by_userId(userId: str = None):
    """Get user by userId (works for both students and teachers)"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        print(f"🔍 DEBUG: Looking for user with userId: {userId}")
        
        if userId:
            cursor.execute("SELECT * FROM users WHERE userId = %s", (userId,))
        else:
            cursor.execute("SELECT * FROM users WHERE role = 'student'")
        
        users = cursor.fetchall()
        
        cursor.close()
        db.close()
        
        if not users:
            return {"success": False, "error": "User not found"}
        
        # Convert date fields to string for JSON serialization
        for user in users:
            if user.get('dob'):
                user['dob'] = str(user['dob'])
            if user.get('created_at'):
                user['created_at'] = str(user['created_at'])
        
        return {"success": True, "users": users}
        
    except Exception as e:
        print(f"Error in get_user_by_userId: {str(e)}")
        return {"success": False, "error": str(e)}


# REPLACE the entire /student/{student_userId}/dashboard/stats endpoint with this FIXED version:

@app.get("/student/{student_userId}/dashboard/stats")
def get_student_dashboard_stats(student_userId: str):
    """Get comprehensive dashboard statistics for a student - FIXED VERSION"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        print(f"🔍 DEBUG DASHBOARD: Getting stats for student: {student_userId}")
        
        # 1. Get student basic info
        cursor.execute("""
            SELECT id, userId, fullName, current_year, email, phone
            FROM users 
            WHERE userId = %s AND role = 'student'
        """, (student_userId,))
        
        student = cursor.fetchone()
        
        if not student:
            print(f"❌ Student not found: {student_userId}")
            cursor.close()
            db.close()
            return {"success": False, "error": "Student not found"}
        
        student_id = student['id']
        student_name = student['fullName']
        student_year = student['current_year']
        
        print(f"✅ Found student: {student_name} (ID: {student_id}, Year: {student_year})")
        
        # 2. Get student's subjects based on their year (simplified)
        student_subjects = []
        if student_year:
            if "first" in student_year.lower() or "1" in student_year:
                if 1 in predefined_subjects:
                    student_subjects = predefined_subjects[1]
            elif "second" in student_year.lower() or "2" in student_year:
                if 2 in predefined_subjects:
                    student_subjects = predefined_subjects[2]
            elif "third" in student_year.lower() or "3" in student_year:
                if 3 in predefined_subjects:
                    student_subjects = predefined_subjects[3]
            elif "fourth" in student_year.lower() or "4" in student_year:
                if 4 in predefined_subjects:
                    student_subjects = predefined_subjects[4]
            elif "fifth" in student_year.lower() or "5" in student_year:
                if 5 in predefined_subjects:
                    student_subjects = predefined_subjects[5]
        
        print(f"📚 Student subjects count: {len(student_subjects)}")
        
        # 3. Get assignments data - SIMPLIFIED
        current_date = datetime.now().date()
        
        # Pending assignments (not submitted and not overdue)
        cursor.execute("""
            SELECT COUNT(DISTINCT a.id) as pending_count
            FROM assignments a
            WHERE a.due_date >= %s 
            AND a.id NOT IN (
                SELECT s.assignment_id 
                FROM assignment_submissions s 
                WHERE s.student_id = %s
            )
        """, (current_date, student_id))
        
        pending_result = cursor.fetchone()
        pending_assignments = pending_result['pending_count'] if pending_result else 0
        print(f"📝 Pending assignments: {pending_assignments}")
        
        # Total submitted assignments
        cursor.execute("""
            SELECT COUNT(DISTINCT assignment_id) as submitted_count
            FROM assignment_submissions 
            WHERE student_id = %s
        """, (student_id,))
        
        submitted_result = cursor.fetchone()
        submitted_assignments = submitted_result['submitted_count'] if submitted_result else 0
        print(f"✅ Submitted assignments: {submitted_assignments}")
        
        # Graded assignments with scores
        cursor.execute("""
            SELECT COUNT(*) as graded_count, 
                   COALESCE(AVG(marks_obtained), 0) as avg_score
            FROM assignment_submissions 
            WHERE student_id = %s 
            AND marks_obtained IS NOT NULL
        """, (student_id,))
        
        graded_result = cursor.fetchone()
        graded_assignments = graded_result['graded_count'] if graded_result else 0
        avg_assignment_score = float(graded_result['avg_score']) if graded_result and graded_result['avg_score'] else 0
        print(f"📊 Graded assignments: {graded_assignments}, Avg score: {avg_assignment_score}")
        
        # 4. Get quizzes data - SIMPLIFIED
        # Upcoming quizzes (not attempted and not expired)
        cursor.execute("""
            SELECT COUNT(DISTINCT q.id) as upcoming_count
            FROM quizzes q
            WHERE q.is_published = 1 
            AND q.end_date >= %s 
            AND q.id NOT IN (
                SELECT sa.quiz_id 
                FROM student_attempts sa 
                WHERE sa.student_id = %s
            )
        """, (current_date, student_id))
        
        upcoming_result = cursor.fetchone()
        upcoming_quizzes = upcoming_result['upcoming_count'] if upcoming_result else 0
        print(f"📅 Upcoming quizzes: {upcoming_quizzes}")
        
        # Total available quizzes
        cursor.execute("""
            SELECT COUNT(DISTINCT q.id) as total_count
            FROM quizzes q
            WHERE q.is_published = 1 
            AND q.end_date >= %s
        """, (current_date,))
        
        total_result = cursor.fetchone()
        total_quizzes = total_result['total_count'] if total_result else 0
        print(f"📋 Total quizzes: {total_quizzes}")
        
        # Completed quizzes
        cursor.execute("""
            SELECT COUNT(DISTINCT quiz_id) as completed_count,
                   COALESCE(AVG(total_score), 0) as avg_score
            FROM student_attempts 
            WHERE student_id = %s
        """, (student_id,))
        
        completed_result = cursor.fetchone()
        completed_quizzes = completed_result['completed_count'] if completed_result else 0
        avg_quiz_score = float(completed_result['avg_score']) if completed_result and completed_result['avg_score'] else 0
        print(f"🏆 Completed quizzes: {completed_quizzes}, Avg score: {avg_quiz_score}")
        
        # 5. Get recent activities
        recent_activities = []
        try:
            cursor.execute("""
                (SELECT 
                    'assignment_submission' as activity_type,
                    '📝 Submitted Assignment' as title,
                    a.title as description,
                    a.subject_name,
                    s.submission_date as timestamp,
                    s.marks_obtained as score,
                    NULL as max_score
                FROM assignment_submissions s
                JOIN assignments a ON s.assignment_id = a.id
                WHERE s.student_id = %s
                ORDER BY s.submission_date DESC
                LIMIT 2)
                
                UNION ALL
                
                (SELECT 
                    'quiz_attempt' as activity_type,
                    '📊 Attempted Quiz' as title,
                    q.title as description,
                    q.subject_name,
                    sa.submitted_at as timestamp,
                    sa.total_score as score,
                    q.total_marks as max_score
                FROM student_attempts sa
                JOIN quizzes q ON sa.quiz_id = q.id
                WHERE sa.student_id = %s
                ORDER BY sa.submitted_at DESC
                LIMIT 2)
                
                ORDER BY timestamp DESC
                LIMIT 3
            """, (student_id, student_id))
            
            recent_activities = cursor.fetchall()
            print(f"📈 Recent activities: {len(recent_activities)}")
        except Exception as e:
            print(f"⚠️ Could not fetch recent activities: {e}")
        
        # 6. Calculate overall progress - SIMPLIFIED
        overall_progress = 0
        
        # Count total assignments available for student's year
        total_assignments_available = 0
        if student_subjects:
            subject_names = [subj["subject_name"] for subj in student_subjects]
            placeholders = ', '.join(['%s'] * len(subject_names))
            cursor.execute(f"""
                SELECT COUNT(*) as total 
                FROM assignments 
                WHERE subject_name IN ({placeholders})
                AND due_date >= %s
            """, (*subject_names, current_date))
            
            total_result = cursor.fetchone()
            total_assignments_available = total_result['total'] if total_result else 0
        
        # Calculate progress
        assignment_progress = 0
        quiz_progress = 0
        
        if total_assignments_available > 0:
            assignment_progress = (submitted_assignments / total_assignments_available) * 50
        
        if total_quizzes > 0:
            quiz_progress = (completed_quizzes / total_quizzes) * 50
        
        overall_progress = min(assignment_progress + quiz_progress, 100)
        
        # If no activities yet, set base progress
        if overall_progress == 0:
            if student_year:
                if "first" in student_year.lower() or "1" in student_year:
                    overall_progress = 20
                elif "second" in student_year.lower() or "2" in student_year:
                    overall_progress = 40
                elif "third" in student_year.lower() or "3" in student_year:
                    overall_progress = 60
                elif "fourth" in student_year.lower() or "4" in student_year:
                    overall_progress = 80
                elif "fifth" in student_year.lower() or "5" in student_year:
                    overall_progress = 95
                else:
                    overall_progress = 30
        
        # 7. Get subject performance - SIMPLIFIED
        subject_performance = []
        try:
            if student_subjects:
                for subject_data in student_subjects[:3]:  # Limit to 3 subjects
                    subject_name = subject_data["subject_name"]
                    
                    # Assignment stats
                    cursor.execute("""
                        SELECT 
                            COUNT(DISTINCT s.id) as submitted,
                            COALESCE(AVG(s.marks_obtained), 0) as avg_score
                        FROM assignment_submissions s
                        JOIN assignments a ON s.assignment_id = a.id
                        WHERE s.student_id = %s 
                        AND a.subject_name = %s
                    """, (student_id, subject_name))
                    
                    assignment_stats = cursor.fetchone()
                    
                    # Quiz stats
                    cursor.execute("""
                        SELECT 
                            COUNT(DISTINCT sa.id) as attempted,
                            COALESCE(AVG(sa.total_score), 0) as avg_score
                        FROM student_attempts sa
                        JOIN quizzes q ON sa.quiz_id = q.id
                        WHERE sa.student_id = %s 
                        AND q.subject_name = %s
                    """, (student_id, subject_name))
                    
                    quiz_stats = cursor.fetchone()
                    
                    # Calculate average
                    assignments_submitted = assignment_stats['submitted'] if assignment_stats else 0
                    assignments_avg = float(assignment_stats['avg_score']) if assignment_stats and assignment_stats['avg_score'] else 0
                    quizzes_attempted = quiz_stats['attempted'] if quiz_stats else 0
                    quizzes_avg = float(quiz_stats['avg_score']) if quiz_stats and quiz_stats['avg_score'] else 0
                    
                    # Overall average
                    if assignments_submitted > 0 or quizzes_attempted > 0:
                        total_avg = 0
                        count = 0
                        if assignments_submitted > 0:
                            total_avg += assignments_avg
                            count += 1
                        if quizzes_attempted > 0:
                            total_avg += quizzes_avg
                            count += 1
                        average_score = total_avg / count
                    else:
                        average_score = 0
                    
                    subject_performance.append({
                        "subject_name": subject_name,
                        "assignments_submitted": assignments_submitted,
                        "assignments_graded": assignments_submitted,  # Simplified
                        "quizzes_attempted": quizzes_attempted,
                        "average_score": round(average_score, 1),
                        "performance_percentage": min(round(average_score, 1), 100)
                    })
        except Exception as e:
            print(f"⚠️ Could not fetch subject performance: {e}")
        
        cursor.close()
        db.close()
        
        print(f"🎉 Dashboard stats calculated successfully!")
        print(f"   Overall progress: {overall_progress}%")
        print(f"   Subjects: {len(subject_performance)}")
        print(f"   Activities: {len(recent_activities)}")
        
        return {
            "success": True,
            "student_info": {
                "userId": student_userId,
                "fullName": student_name,
                "current_year": student_year,
                "email": student.get('email'),
                "phone": student.get('phone')
            },
            "stats": {
                "pending_assignments": pending_assignments,
                "submitted_assignments": submitted_assignments,
                "graded_assignments": graded_assignments,
                "avg_assignment_score": round(avg_assignment_score, 1),
                "upcoming_quizzes": upcoming_quizzes,
                "total_quizzes": total_quizzes,
                "completed_quizzes": completed_quizzes,
                "avg_quiz_score": round(avg_quiz_score, 1),
                "recent_notifications": 0,  # Placeholder
                "overall_progress": round(overall_progress, 1)
            },
            "subject_performance": subject_performance,
            "recent_activities": recent_activities,
            "subjects_count": len(student_subjects)
        }
        
    except Exception as e:
        print(f"❌ ERROR in get_student_dashboard_stats: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

# ------------------- TEACHER DASHBOARD ENDPOINTS -------------------

@app.get("/teacher/{teacher_userId}/dashboard/stats")
def get_teacher_dashboard_stats(teacher_userId: str):
    """Get comprehensive dashboard statistics for a teacher"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        print(f"🔍 TEACHER DASHBOARD: Getting stats for teacher: {teacher_userId}")
        
        # 1. Get teacher basic info
        cursor.execute("""
            SELECT id, userId, fullName, subject, email, phone
            FROM users 
            WHERE userId = %s AND role = 'teacher'
        """, (teacher_userId,))
        
        teacher = cursor.fetchone()
        
        if not teacher:
            print(f"❌ Teacher not found: {teacher_userId}")
            cursor.close()
            db.close()
            return {"success": False, "error": "Teacher not found"}
        
        teacher_id = teacher['id']
        teacher_name = teacher['fullName']
        teacher_subjects = teacher.get('subject', '').split(',') if teacher.get('subject') else []
        
        print(f"✅ Found teacher: {teacher_name} (ID: {teacher_id})")
        print(f"📚 Assigned subjects: {teacher_subjects}")
        
        # 2. Get assigned subjects data
        assigned_subjects_data = []
        for subject in teacher_subjects:
            subject = subject.strip()
            if subject:
                assigned_subjects_data.append({"subject_name": subject})
        
        # If no subjects assigned, get from predefined based on name matching
        if not assigned_subjects_data:
            # Get all subjects for matching
            all_subjects_set = set()
            for year_subjects in predefined_subjects.values():
                for subj in year_subjects:
                    all_subjects_set.add(subj["subject_name"])
            
            # Try to match teacher's subject field
            if teacher.get('subject'):
                teacher_subj = teacher.get('subject')
                for available_subj in all_subjects_set:
                    if is_subject_match(teacher_subj, available_subj):
                        assigned_subjects_data.append({"subject_name": available_subj})
                        break
        
        print(f"📊 Processing {len(assigned_subjects_data)} assigned subjects")
        
        # 3. Get lectures statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_lectures,
                COALESCE(SUM(downloads), 0) as total_downloads,
                COALESCE(SUM(views), 0) as total_views,
                COUNT(DISTINCT subject_name) as subjects_with_lectures
            FROM lectures 
            WHERE teacher_id = %s
        """, (teacher_id,))
        
        lectures_stats = cursor.fetchone()
        
        # 4. Get assignments statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_assignments,
                COALESCE(SUM(submissions), 0) as total_submissions,
                COUNT(DISTINCT subject_name) as subjects_with_assignments,
                SUM(CASE WHEN due_date < CURDATE() THEN 1 ELSE 0 END) as past_due,
                SUM(CASE WHEN due_date >= CURDATE() THEN 1 ELSE 0 END) as upcoming
            FROM assignments 
            WHERE teacher_id = %s
        """, (teacher_id,))
        
        assignments_stats = cursor.fetchone()
        
        # 5. Get quizzes statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_quizzes,
                COALESCE(SUM(attempts), 0) as total_attempts,
                COALESCE(AVG(average_score), 0) as avg_quiz_score,
                COUNT(DISTINCT subject_name) as subjects_with_quizzes,
                SUM(CASE WHEN is_published = 1 THEN 1 ELSE 0 END) as published,
                SUM(CASE WHEN is_published = 0 THEN 1 ELSE 0 END) as draft
            FROM quizzes 
            WHERE teacher_id = %s
        """, (teacher_id,))
        
        quizzes_stats = cursor.fetchone()
        
        # 6. Get materials statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_materials,
                COALESCE(SUM(downloads), 0) as total_downloads,
                COUNT(DISTINCT subject_name) as subjects_with_materials
            FROM materials 
            WHERE teacher_id = %s
        """, (teacher_id,))
        
        materials_stats = cursor.fetchone()
        
        # 7. Get notifications statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_notifications,
                COUNT(DISTINCT subject_name) as subjects_with_notifications
            FROM notifications 
            WHERE teacher_id = %s
        """, (teacher_id,))
        
        notifications_stats = cursor.fetchone()
        
        # 8. Get recent student submissions (for grading)
        cursor.execute("""
            SELECT 
                s.*,
                a.title as assignment_title,
                a.subject_name,
                u.fullName as student_name,
                u.userId as student_userId,
                DATEDIFF(NOW(), s.submission_date) as days_ago
            FROM assignment_submissions s
            JOIN assignments a ON s.assignment_id = a.id
            JOIN users u ON s.student_id = u.id
            WHERE a.teacher_id = %s 
            AND s.marks_obtained IS NULL
            ORDER BY s.submission_date DESC
            LIMIT 5
        """, (teacher_id,))
        
        pending_grading = cursor.fetchall()
        
        # 9. Get recent quiz attempts
        cursor.execute("""
            SELECT 
                sa.*,
                q.title as quiz_title,
                q.subject_name,
                u.fullName as student_name,
                u.userId as student_userId,
                DATEDIFF(NOW(), sa.submitted_at) as days_ago
            FROM student_attempts sa
            JOIN quizzes q ON sa.quiz_id = q.id
            JOIN users u ON sa.student_id = u.id
            WHERE q.teacher_id = %s
            ORDER BY sa.submitted_at DESC
            LIMIT 5
        """, (teacher_id,))
        
        recent_quiz_attempts = cursor.fetchall()
        
        # 10. Get upcoming assignment deadlines
        cursor.execute("""
            SELECT 
                a.*,
                DATEDIFF(a.due_date, CURDATE()) as days_left,
                CASE 
                    WHEN DATEDIFF(a.due_date, CURDATE()) = 0 THEN 'Due Today'
                    WHEN DATEDIFF(a.due_date, CURDATE()) = 1 THEN 'Due Tomorrow'
                    WHEN DATEDIFF(a.due_date, CURDATE()) < 7 THEN CONCAT('Due in ', DATEDIFF(a.due_date, CURDATE()), ' days')
                    ELSE 'Upcoming'
                END as deadline_text
            FROM assignments a
            WHERE a.teacher_id = %s 
            AND a.due_date >= CURDATE()
            ORDER BY a.due_date ASC
            LIMIT 5
        """, (teacher_id,))
        
        upcoming_deadlines = cursor.fetchall()
        
        # 11. Get subject-wise performance
        subject_performance = []
        for subject_data in assigned_subjects_data[:5]:  # Limit to 5 subjects
            subject_name = subject_data["subject_name"]
            
            # Assignments for this subject
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_assignments,
                    COALESCE(SUM(submissions), 0) as total_submissions,
                    COALESCE(AVG(submissions), 0) as avg_submissions
                FROM assignments 
                WHERE teacher_id = %s 
                AND subject_name = %s
            """, (teacher_id, subject_name))
            
            assignment_stats = cursor.fetchone()
            
            # Quizzes for this subject
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_quizzes,
                    COALESCE(SUM(attempts), 0) as total_attempts,
                    COALESCE(AVG(average_score), 0) as avg_score
                FROM quizzes 
                WHERE teacher_id = %s 
                AND subject_name = %s
            """, (teacher_id, subject_name))
            
            quiz_stats = cursor.fetchone()
            
            # Lectures for this subject
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_lectures,
                    COALESCE(SUM(downloads), 0) as total_downloads,
                    COALESCE(AVG(downloads), 0) as avg_downloads
                FROM lectures 
                WHERE teacher_id = %s 
                AND subject_name = %s
            """, (teacher_id, subject_name))
            
            lecture_stats = cursor.fetchone()
            
            subject_performance.append({
                "subject_name": subject_name,
                "assignments": {
                    "total": assignment_stats['total_assignments'] or 0,
                    "submissions": assignment_stats['total_submissions'] or 0,
                    "avg_submissions": round(float(assignment_stats['avg_submissions'] or 0), 1)
                },
                "quizzes": {
                    "total": quiz_stats['total_quizzes'] or 0,
                    "attempts": quiz_stats['total_attempts'] or 0,
                    "avg_score": round(float(quiz_stats['avg_score'] or 0), 1)
                },
                "lectures": {
                    "total": lecture_stats['total_lectures'] or 0,
                    "downloads": lecture_stats['total_downloads'] or 0,
                    "avg_downloads": round(float(lecture_stats['avg_downloads'] or 0), 1)
                }
            })
        
        cursor.close()
        db.close()
        
        # Calculate engagement score
        total_students = 30  # Assuming 30 students per class
        
        engagement_score = 0
        if total_students > 0:
            # Based on submissions and attempts
            total_engagement = (
                (assignments_stats['total_submissions'] or 0) +
                (quizzes_stats['total_attempts'] or 0)
            )
            max_possible_engagement = (
                (assignments_stats['total_assignments'] or 0) * total_students +
                (quizzes_stats['total_quizzes'] or 0) * total_students
            )
            
            if max_possible_engagement > 0:
                engagement_score = (total_engagement / max_possible_engagement) * 100
        
        print(f"🎉 Teacher dashboard stats calculated successfully!")
        print(f"   Engagement score: {engagement_score:.1f}%")
        print(f"   Pending grading: {len(pending_grading)}")
        
        return {
            "success": True,
            "teacher_info": {
                "userId": teacher_userId,
                "fullName": teacher_name,
                "subject": teacher.get('subject'),
                "email": teacher.get('email'),
                "phone": teacher.get('phone'),
                "assigned_subjects": assigned_subjects_data
            },
            "stats": {
                "lectures": {
                    "total": lectures_stats['total_lectures'] or 0,
                    "downloads": lectures_stats['total_downloads'] or 0,
                    "views": lectures_stats['total_views'] or 0,
                    "subjects": lectures_stats['subjects_with_lectures'] or 0
                },
                "assignments": {
                    "total": assignments_stats['total_assignments'] or 0,
                    "submissions": assignments_stats['total_submissions'] or 0,
                    "subjects": assignments_stats['subjects_with_assignments'] or 0,
                    "past_due": assignments_stats['past_due'] or 0,
                    "upcoming": assignments_stats['upcoming'] or 0
                },
                "quizzes": {
                    "total": quizzes_stats['total_quizzes'] or 0,
                    "attempts": quizzes_stats['total_attempts'] or 0,
                    "avg_score": round(float(quizzes_stats['avg_quiz_score'] or 0), 1),
                    "subjects": quizzes_stats['subjects_with_quizzes'] or 0,
                    "published": quizzes_stats['published'] or 0,
                    "draft": quizzes_stats['draft'] or 0
                },
                "materials": {
                    "total": materials_stats['total_materials'] or 0,
                    "downloads": materials_stats['total_downloads'] or 0,
                    "subjects": materials_stats['subjects_with_materials'] or 0
                },
                "notifications": {
                    "total": notifications_stats['total_notifications'] or 0,
                    "subjects": notifications_stats['subjects_with_notifications'] or 0
                },
                "engagement_score": round(engagement_score, 1)
            },
            "pending_grading": pending_grading,
            "recent_quiz_attempts": recent_quiz_attempts,
            "upcoming_deadlines": upcoming_deadlines,
            "subject_performance": subject_performance
        }
        
    except Exception as e:
        print(f"❌ ERROR in get_teacher_dashboard_stats: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

@app.get("/teacher/{teacher_userId}/dashboard/quick-stats")
def get_teacher_quick_stats(teacher_userId: str):
    """Get quick stats for teacher dashboard header"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Get teacher ID
        cursor.execute("SELECT id FROM users WHERE userId = %s AND role = 'teacher'", (teacher_userId,))
        teacher = cursor.fetchone()
        
        if not teacher:
            return {"success": False, "error": "Teacher not found"}
        
        teacher_id = teacher['id']
        
        # Get counts
        cursor.execute("SELECT COUNT(*) as lectures FROM lectures WHERE teacher_id = %s", (teacher_id,))
        lectures = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(*) as assignments FROM assignments WHERE teacher_id = %s", (teacher_id,))
        assignments = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(*) as quizzes FROM quizzes WHERE teacher_id = %s", (teacher_id,))
        quizzes = cursor.fetchone()
        
        cursor.execute("""
            SELECT COUNT(*) as pending 
            FROM assignment_submissions s
            JOIN assignments a ON s.assignment_id = a.id
            WHERE a.teacher_id = %s AND s.marks_obtained IS NULL
        """, (teacher_id,))
        
        pending = cursor.fetchone()
        
        cursor.close()
        db.close()
        
        return {
            "success": True,
            "quick_stats": {
                "lectures": lectures['lectures'] or 0,
                "assignments": assignments['assignments'] or 0,
                "quizzes": quizzes['quizzes'] or 0,
                "pending_grading": pending['pending'] or 0
            }
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/teacher/{teacher_userId}/dashboard/recent-activity")
def get_teacher_recent_activity(teacher_userId: str, limit: int = 10):
    """Get recent activity for teacher"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Get teacher ID
        cursor.execute("SELECT id FROM users WHERE userId = %s AND role = 'teacher'", (teacher_userId,))
        teacher = cursor.fetchone()
        
        if not teacher:
            return {"success": False, "error": "Teacher not found"}
        
        teacher_id = teacher['id']
        
        # Get combined recent activity
        query = """
            (SELECT 
                'assignment_submission' as activity_type,
                '📝 New Submission' as title,
                a.title as description,
                a.subject_name,
                s.submission_date as timestamp,
                u.fullName as student_name,
                s.id as item_id,
                'assignment' as item_type
            FROM assignment_submissions s
            JOIN assignments a ON s.assignment_id = a.id
            JOIN users u ON s.student_id = u.id
            WHERE a.teacher_id = %s
            ORDER BY s.submission_date DESC
            LIMIT 5)
            
            UNION ALL
            
            (SELECT 
                'quiz_attempt' as activity_type,
                '📊 Quiz Attempt' as title,
                q.title as description,
                q.subject_name,
                sa.submitted_at as timestamp,
                u.fullName as student_name,
                sa.id as item_id,
                'quiz' as item_type
            FROM student_attempts sa
            JOIN quizzes q ON sa.quiz_id = q.id
            JOIN users u ON sa.student_id = u.id
            WHERE q.teacher_id = %s
            ORDER BY sa.submitted_at DESC
            LIMIT 5)
            
            UNION ALL
            
            (SELECT 
                'assignment_created' as activity_type,
                '📝 Assignment Created' as title,
                title as description,
                subject_name,
                created_date as timestamp,
                NULL as student_name,
                id as item_id,
                'assignment' as item_type
            FROM assignments 
            WHERE teacher_id = %s
            ORDER BY created_date DESC
            LIMIT 5)
            
            ORDER BY timestamp DESC
            LIMIT %s
        """
        
        cursor.execute(query, (teacher_id, teacher_id, teacher_id, limit))
        activities = cursor.fetchall()
        
        cursor.close()
        db.close()
        
        return {
            "success": True,
            "activities": activities,
            "total_activities": len(activities)
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}