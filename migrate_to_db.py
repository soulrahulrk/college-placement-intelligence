"""
Migrate data from JSON files to PostgreSQL database
Run this once to import existing student/company/log data
"""

import json
from database import DatabaseManager
from data_engine import StudentProfile, JobDescription, PlacementLog

def migrate_json_to_postgresql():
    """Import all JSON data into PostgreSQL"""
    
    db = DatabaseManager()
    
    print("🔄 Starting data migration from JSON to PostgreSQL...\n")
    
    # Import Students
    try:
        with open("students.json", "r") as f:
            students_data = json.load(f)
            students = [StudentProfile(**s) for s in students_data]
            db.bulk_save_students(students)
    except FileNotFoundError:
        print("⚠️ students.json not found - skipping students")
    except Exception as e:
        print(f"❌ Error importing students: {e}")
    
    # Import Companies
    try:
        with open("jobs.json", "r") as f:
            jobs_data = json.load(f)
            companies = [JobDescription(**j) for j in jobs_data]
            db.bulk_save_companies(companies)
    except FileNotFoundError:
        print("⚠️ jobs.json not found - skipping companies")
    except Exception as e:
        print(f"❌ Error importing companies: {e}")
    
    # Import Logs
    try:
        with open("logs.json", "r") as f:
            logs_data = json.load(f)
            logs = [PlacementLog(**l) for l in logs_data]
            db.bulk_save_logs(logs)
    except FileNotFoundError:
        print("⚠️ logs.json not found - skipping logs")
    except Exception as e:
        print(f"❌ Error importing logs: {e}")
    
    print("\n✅ Data migration complete!")
    
    # Verify import
    print("\n📊 Database Summary:")
    students = db.get_all_students()
    companies = db.get_all_companies()
    logs = db.get_all_logs()
    
    print(f"  - Students: {len(students)}")
    print(f"  - Companies: {len(companies)}")
    print(f"  - Placement Logs: {len(logs)}")


if __name__ == "__main__":
    migrate_json_to_postgresql()
