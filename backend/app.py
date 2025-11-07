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


# Health check endpoint
@app.get("/")
def read_root():
    return {"message": "Islamic Center API is running!"}

