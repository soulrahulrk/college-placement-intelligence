"""
PostgreSQL Database Configuration and Operations
Handles all database connections and CRUD operations
"""

import psycopg2
from psycopg2.extras import RealDictCursor, Json
import json
from typing import List, Optional
from data_engine import StudentProfile, JobDescription, PlacementLog
from pydantic import ValidationError
import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "placement_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "rk00"),
    "port": os.getenv("DB_PORT", "5432")
}


class DatabaseManager:
    """Manages PostgreSQL database operations"""
    
    def __init__(self):
        self.config = DB_CONFIG
    
    def get_connection(self):
        """Create and return a database connection"""
        try:
            conn = psycopg2.connect(**self.config)
            return conn
        except psycopg2.Error as e:
            raise Exception(f"Database connection failed: {e}")
    
    def create_tables(self):
        """Create all required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Students table - matches StudentProfile model
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    student_id VARCHAR(10) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    branch VARCHAR(10) NOT NULL,
                    cgpa DECIMAL(3,2) NOT NULL CHECK (cgpa BETWEEN 5.0 AND 9.8),
                    active_backlogs INTEGER DEFAULT 0 CHECK (active_backlogs BETWEEN 0 AND 5),
                    skills JSONB NOT NULL,
                    communication_score INTEGER CHECK (communication_score BETWEEN 1 AND 10),
                    mock_interview_score INTEGER CHECK (mock_interview_score BETWEEN 1 AND 10),
                    resume_trust_score DECIMAL(3,2) CHECK (resume_trust_score BETWEEN 0 AND 1),
                    email VARCHAR(255),
                    phone VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Companies/Jobs table - matches JobDescription model
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS companies (
                    company_id VARCHAR(20) PRIMARY KEY,
                    company_name VARCHAR(100) NOT NULL,
                    company_type VARCHAR(20) NOT NULL,
                    role VARCHAR(100) NOT NULL,
                    open_positions INTEGER DEFAULT 5,
                    risk_tolerance VARCHAR(20),
                    eligibility_rules JSONB NOT NULL,
                    weight_policy JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Placement Logs table - matches PlacementLog model
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS placement_logs (
                    log_id VARCHAR(20) PRIMARY KEY,
                    student_id VARCHAR(10),
                    company_id VARCHAR(20),
                    shortlisted BOOLEAN,
                    interview_result VARCHAR(20),
                    failure_reason VARCHAR(100),
                    timestamp VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_branch ON students(branch)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_cgpa ON students(cgpa)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_companies_type ON companies(company_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_student ON placement_logs(student_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_result ON placement_logs(interview_result)")
            
            conn.commit()
            print("✅ Database tables created successfully!")
            
        except psycopg2.Error as e:
            conn.rollback()
            raise Exception(f"Failed to create tables: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def save_student(self, student: StudentProfile):
        """Save or update a student record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO students (
                    student_id, name, branch, cgpa, active_backlogs,
                    communication_score, mock_interview_score, resume_trust_score,
                    email, phone, skills
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (student_id) 
                DO UPDATE SET
                    name = EXCLUDED.name,
                    branch = EXCLUDED.branch,
                    cgpa = EXCLUDED.cgpa,
                    active_backlogs = EXCLUDED.active_backlogs,
                    communication_score = EXCLUDED.communication_score,
                    mock_interview_score = EXCLUDED.mock_interview_score,
                    resume_trust_score = EXCLUDED.resume_trust_score,
                    email = EXCLUDED.email,
                    phone = EXCLUDED.phone,
                    skills = EXCLUDED.skills,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                student.student_id,
                student.name,
                student.branch,
                student.cgpa,
                student.active_backlogs,
                student.communication_score,
                student.mock_interview_score,
                student.resume_trust_score,
                student.email,
                student.phone,
                Json([s.model_dump() for s in student.skills])
            ))
            
            conn.commit()
        except psycopg2.Error as e:
            conn.rollback()
            raise Exception(f"Failed to save student: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def save_company(self, company: JobDescription):
        """Save or update a company/job record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO companies (
                    company_id, company_name, company_type, role,
                    open_positions, risk_tolerance, eligibility_rules, weight_policy
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (company_id)
                DO UPDATE SET
                    company_name = EXCLUDED.company_name,
                    company_type = EXCLUDED.company_type,
                    role = EXCLUDED.role,
                    open_positions = EXCLUDED.open_positions,
                    risk_tolerance = EXCLUDED.risk_tolerance,
                    eligibility_rules = EXCLUDED.eligibility_rules,
                    weight_policy = EXCLUDED.weight_policy
            """, (
                company.company_id,
                company.company_name,
                company.company_type,
                company.role,
                company.open_positions,
                company.risk_tolerance,
                Json(company.eligibility_rules.model_dump()),
                Json(company.weight_policy.model_dump())
            ))
            
            conn.commit()
        except psycopg2.Error as e:
            conn.rollback()
            raise Exception(f"Failed to save company: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def save_log(self, log: PlacementLog):
        """Save a placement log record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO placement_logs (
                    log_id, student_id, company_id, shortlisted,
                    interview_result, failure_reason, timestamp
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (log_id) DO NOTHING
            """, (
                log.log_id,
                log.student_id,
                log.company_id,
                log.shortlisted,
                log.interview_result,
                log.failure_reason,
                log.timestamp
            ))
            
            conn.commit()
        except psycopg2.Error as e:
            conn.rollback()
            raise Exception(f"Failed to save log: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def get_all_students(self) -> List[StudentProfile]:
        """Retrieve all students from database"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            cursor.execute("SELECT * FROM students ORDER BY student_id")
            rows = cursor.fetchall()
            
            students = []
            for row in rows:
                # Convert JSONB back to Pydantic models
                student_data = dict(row)
                students.append(StudentProfile(**student_data))
            
            return students
        except Exception as e:
            raise Exception(f"Failed to fetch students: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def get_all_companies(self) -> List[JobDescription]:
        """Retrieve all companies from database"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            cursor.execute("SELECT * FROM companies ORDER BY company_name")
            rows = cursor.fetchall()
            
            companies = []
            for row in rows:
                company_data = dict(row)
                # Remove database-specific fields
                company_data.pop('created_at', None)
                companies.append(JobDescription(**company_data))
            
            return companies
        except Exception as e:
            raise Exception(f"Failed to fetch companies: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def get_all_logs(self) -> List[PlacementLog]:
        """Retrieve all placement logs from database"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            cursor.execute("SELECT * FROM placement_logs ORDER BY timestamp DESC")
            rows = cursor.fetchall()
            
            logs = []
            for row in rows:
                log_data = dict(row)
                # Remove database-specific fields
                log_data.pop('created_at', None)
                logs.append(PlacementLog(**log_data))
            
            return logs
        except Exception as e:
            raise Exception(f"Failed to fetch logs: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def bulk_save_students(self, students: List[StudentProfile]):
        """Save multiple students efficiently"""
        for student in students:
            self.save_student(student)
        print(f"✅ Saved {len(students)} students to database")
    
    def bulk_save_companies(self, companies: List[JobDescription]):
        """Save multiple companies efficiently"""
        for company in companies:
            self.save_company(company)
        print(f"✅ Saved {len(companies)} companies to database")
    
    def bulk_save_logs(self, logs: List[PlacementLog]):
        """Save multiple logs efficiently"""
        for log in logs:
            self.save_log(log)
        print(f"✅ Saved {len(logs)} placement logs to database")
    
    def clear_all_data(self):
        """Clear all data from tables (for testing)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("TRUNCATE TABLE placement_logs, companies, students CASCADE")
            conn.commit()
            print("✅ All data cleared from database")
        except psycopg2.Error as e:
            conn.rollback()
            raise Exception(f"Failed to clear data: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def test_connection(self):
        """Test database connection"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT version()")
            version = cursor.fetchone()
            cursor.close()
            conn.close()
            print(f"✅ PostgreSQL connection successful!")
            print(f"Database version: {version[0]}")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False


if __name__ == "__main__":
    # Test database connection and setup
    db = DatabaseManager()
    
    print("Testing PostgreSQL connection...")
    if db.test_connection():
        print("\nCreating database tables...")
        db.create_tables()
        print("\n✅ Database setup complete!")
    else:
        print("\n❌ Database setup failed. Check your configuration.")
