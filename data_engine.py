"""
Data Engine for College Placement Intelligence Agent
Handles schema definitions and synthetic data generation
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field, field_validator
from faker import Faker
import random
import json
from datetime import datetime

fake = Faker()


# ==================== PYDANTIC MODELS ====================

class Skill(BaseModel):
    """Individual skill with proficiency tracking"""
    name: str
    proficiency_score: float = Field(ge=0, le=10, description="Evidence-based proficiency (0-10)")
    evidence_source: str = Field(description="Source of evidence (GitHub, Project, Certificate, Listed)")


class StudentProfile(BaseModel):
    """Student data model with validation"""
    id: str
    name: str
    gpa: float = Field(ge=0, le=10, description="GPA on 10-point scale")
    backlogs: int = Field(ge=0, description="Number of active backlogs")
    skills: List[Skill]
    experience_years: float = Field(ge=0, description="Years of professional experience")
    email: str
    phone: str
    
    @field_validator('gpa')
    @classmethod
    def validate_gpa(cls, v):
        if v < 0 or v > 10:
            raise ValueError('GPA must be between 0 and 10')
        return round(v, 2)


class JobDescription(BaseModel):
    """Job description model with constraints"""
    id: str
    company_name: str
    role: str
    must_have_skills: List[str] = Field(description="Critical skills required")
    good_to_have_skills: List[str] = Field(description="Preferred but not mandatory")
    min_gpa: float = Field(ge=0, le=10)
    max_backlogs_allowed: int = Field(ge=0)
    min_experience_years: float = Field(ge=0, default=0)
    company_type: str = Field(description="MNC, Startup, Service, Product")
    
    @field_validator('min_gpa')
    @classmethod
    def validate_min_gpa(cls, v):
        if v < 0 or v > 10:
            raise ValueError('Min GPA must be between 0 and 10')
        return round(v, 2)


class PlacementLog(BaseModel):
    """Historical placement record"""
    log_id: str
    student_id: str
    company_id: str
    status: str = Field(description="Hired or Rejected")
    reason: str
    timestamp: str
    student_score: Optional[float] = None


# ==================== SYNTHETIC DATA GENERATOR ====================

class SyntheticDataGenerator:
    """Generate realistic fake data for testing"""
    
    # Skill pools by category
    PROGRAMMING_SKILLS = ["Python", "Java", "C++", "JavaScript", "TypeScript", "Go", "Rust", "C#"]
    WEB_SKILLS = ["React", "Angular", "Vue.js", "Node.js", "Django", "Flask", "FastAPI", "Spring Boot"]
    DATA_SKILLS = ["SQL", "MongoDB", "PostgreSQL", "Pandas", "NumPy", "Apache Spark", "Tableau", "Power BI"]
    ML_AI_SKILLS = ["Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Scikit-learn", "NLP", "Computer Vision"]
    CLOUD_SKILLS = ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "CI/CD"]
    OTHER_SKILLS = ["Git", "Agile", "REST API", "GraphQL", "Microservices", "System Design", "Data Structures"]
    
    EVIDENCE_SOURCES = ["GitHub Project", "Internship", "Certification", "University Project", "Hackathon", "Listed in Resume"]
    
    COMPANY_TYPES = {
        "MNC": ["Google", "Microsoft", "Amazon", "Meta", "Apple", "Oracle", "IBM", "SAP"],
        "Startup": ["TechNova", "DataFusion", "CloudScale", "AI Ventures", "DevStream"],
        "Service": ["TCS", "Infosys", "Wipro", "Accenture", "Cognizant"],
        "Product": ["Atlassian", "Adobe", "Salesforce", "Slack", "Zoom"]
    }
    
    ROLES = [
        "Software Engineer", "Data Scientist", "Full Stack Developer", 
        "Backend Developer", "Frontend Developer", "ML Engineer",
        "DevOps Engineer", "Cloud Engineer", "Data Analyst"
    ]
    
    def __init__(self, seed: int = 42):
        random.seed(seed)
        Faker.seed(seed)
    
    def _generate_skill(self, skill_name: str, student_type: str) -> Skill:
        """Generate skill with evidence-based proficiency"""
        if student_type == "Star":
            evidence = random.choice(["GitHub Project", "Internship", "Certification", "Hackathon"])
            score = random.uniform(7.5, 10.0)
        elif student_type == "Average":
            evidence = random.choice(["University Project", "Certification", "Listed in Resume"])
            score = random.uniform(5.0, 7.5)
        else:  # At Risk
            evidence = random.choice(["Listed in Resume", "University Project"])
            score = random.uniform(3.0, 6.0)
        
        return Skill(
            name=skill_name,
            proficiency_score=round(score, 1),
            evidence_source=evidence
        )
    
    def generate_students(self, count: int = 30) -> List[StudentProfile]:
        """Generate diverse student profiles"""
        students = []
        
        # Distribution: 30% Star, 50% Average, 20% At Risk
        star_count = int(count * 0.3)
        average_count = int(count * 0.5)
        at_risk_count = count - star_count - average_count
        
        student_types = (
            ["Star"] * star_count +
            ["Average"] * average_count +
            ["At Risk"] * at_risk_count
        )
        random.shuffle(student_types)
        
        all_skills = (
            self.PROGRAMMING_SKILLS + self.WEB_SKILLS + 
            self.DATA_SKILLS + self.ML_AI_SKILLS + 
            self.CLOUD_SKILLS + self.OTHER_SKILLS
        )
        
        for i, student_type in enumerate(student_types):
            # GPA distribution based on type
            if student_type == "Star":
                gpa = random.uniform(8.5, 10.0)
                backlogs = 0
                skill_count = random.randint(8, 12)
                experience = random.uniform(0, 2)
            elif student_type == "Average":
                gpa = random.uniform(7.0, 8.5)
                backlogs = random.choice([0, 0, 0, 1])  # Mostly 0, sometimes 1
                skill_count = random.randint(5, 8)
                experience = random.uniform(0, 1)
            else:  # At Risk - High skills but low GPA (the critical test case)
                gpa = random.uniform(5.5, 7.0)
                backlogs = random.randint(1, 3)
                skill_count = random.randint(6, 10)  # Can have good skills!
                experience = random.uniform(0, 0.5)
            
            # Select random skills
            selected_skills = random.sample(all_skills, skill_count)
            skills = [self._generate_skill(skill, student_type) for skill in selected_skills]
            
            student = StudentProfile(
                id=f"STU_{i+1:03d}",
                name=fake.name(),
                gpa=round(gpa, 2),
                backlogs=backlogs,
                skills=skills,
                experience_years=round(experience, 1),
                email=fake.email(),
                phone=fake.phone_number()
            )
            students.append(student)
        
        return students
    
    def generate_jobs(self, count: int = 10) -> List[JobDescription]:
        """Generate varied job descriptions"""
        jobs = []
        
        for i in range(count):
            company_type = random.choice(list(self.COMPANY_TYPES.keys()))
            company_name = random.choice(self.COMPANY_TYPES[company_type])
            role = random.choice(self.ROLES)
            
            # Company type determines constraints
            if company_type == "MNC":
                min_gpa = random.uniform(7.5, 8.5)
                max_backlogs = 0
                min_experience = random.choice([0, 0, 0.5])
            elif company_type == "Startup":
                min_gpa = random.uniform(6.0, 7.0)  # More lenient
                max_backlogs = random.choice([0, 1])
                min_experience = random.uniform(0, 1)
            elif company_type == "Service":
                min_gpa = random.uniform(6.5, 7.5)
                max_backlogs = random.choice([0, 1, 2])
                min_experience = 0
            else:  # Product
                min_gpa = random.uniform(7.0, 8.0)
                max_backlogs = random.choice([0, 1])
                min_experience = random.choice([0, 0.5, 1])
            
            # Select skills based on role
            if "Data" in role or "ML" in role:
                skill_pool = self.PROGRAMMING_SKILLS + self.DATA_SKILLS + self.ML_AI_SKILLS
            elif "DevOps" in role or "Cloud" in role:
                skill_pool = self.PROGRAMMING_SKILLS + self.CLOUD_SKILLS + self.OTHER_SKILLS
            elif "Full Stack" in role:
                skill_pool = self.PROGRAMMING_SKILLS + self.WEB_SKILLS + self.OTHER_SKILLS
            else:
                skill_pool = self.PROGRAMMING_SKILLS + self.WEB_SKILLS + self.OTHER_SKILLS
            
            must_have_count = random.randint(3, 5)
            good_to_have_count = random.randint(2, 4)
            
            must_haves = random.sample(skill_pool, must_have_count)
            remaining_skills = [s for s in skill_pool if s not in must_haves]
            good_to_haves = random.sample(remaining_skills, min(good_to_have_count, len(remaining_skills)))
            
            job = JobDescription(
                id=f"JOB_{i+1:03d}",
                company_name=company_name,
                role=role,
                must_have_skills=must_haves,
                good_to_have_skills=good_to_haves,
                min_gpa=round(min_gpa, 2),
                max_backlogs_allowed=max_backlogs,
                min_experience_years=round(min_experience, 1),
                company_type=company_type
            )
            jobs.append(job)
        
        return jobs
    
    def generate_placement_logs(
        self, 
        students: List[StudentProfile], 
        jobs: List[JobDescription],
        log_count: int = 50
    ) -> List[PlacementLog]:
        """Generate historical placement data with realistic patterns"""
        logs = []
        
        for i in range(log_count):
            student = random.choice(students)
            job = random.choice(jobs)
            
            # Determine outcome based on constraints
            meets_gpa = student.gpa >= job.min_gpa
            meets_backlogs = student.backlogs <= job.max_backlogs_allowed
            meets_experience = student.experience_years >= job.min_experience_years
            
            # Check skill match
            student_skill_names = {s.name for s in student.skills}
            must_have_match = sum(1 for skill in job.must_have_skills if skill in student_skill_names)
            must_have_ratio = must_have_match / len(job.must_have_skills) if job.must_have_skills else 1
            
            # Decision logic
            if not meets_gpa:
                status = "Rejected"
                reason = f"Hard Constraint: GPA {student.gpa} < Required {job.min_gpa}"
                score = 0.0
            elif not meets_backlogs:
                status = "Rejected"
                reason = f"Hard Constraint: {student.backlogs} backlogs > Allowed {job.max_backlogs_allowed}"
                score = 0.0
            elif not meets_experience:
                status = "Rejected"
                reason = f"Hard Constraint: Experience {student.experience_years}y < Required {job.min_experience_years}y"
                score = 0.0
            elif must_have_ratio < 0.5:  # Less than 50% must-haves
                status = "Rejected"
                reason = f"Insufficient Must-Have Skills: {must_have_match}/{len(job.must_have_skills)} matched"
                score = round(must_have_ratio * 5, 2)
            else:
                # Randomize outcome with bias toward hiring
                hire_probability = min(0.9, must_have_ratio * 0.8 + random.uniform(0, 0.2))
                if random.random() < hire_probability:
                    status = "Hired"
                    reason = f"Strong match: {must_have_match}/{len(job.must_have_skills)} must-haves, GPA: {student.gpa}"
                    score = round(random.uniform(7, 10), 2)
                else:
                    status = "Rejected"
                    reason = random.choice([
                        "Cultural fit concerns during interview",
                        "Better candidates in pool",
                        "Insufficient depth in technical round"
                    ])
                    score = round(random.uniform(5, 7), 2)
            
            log = PlacementLog(
                log_id=f"LOG_{i+1:04d}",
                student_id=student.id,
                company_id=job.id,
                status=status,
                reason=reason,
                timestamp=fake.date_time_between(start_date="-1y", end_date="now").isoformat(),
                student_score=score
            )
            logs.append(log)
        
        return logs


# ==================== DATA EXPORT ====================

def save_to_json(students: List[StudentProfile], jobs: List[JobDescription], logs: List[PlacementLog]):
    """Save generated data to JSON files"""
    
    students_data = [s.model_dump() for s in students]
    jobs_data = [j.model_dump() for j in jobs]
    logs_data = [l.model_dump() for l in logs]
    
    with open('students.json', 'w', encoding='utf-8') as f:
        json.dump(students_data, f, indent=2, ensure_ascii=False)
    
    with open('jobs.json', 'w', encoding='utf-8') as f:
        json.dump(jobs_data, f, indent=2, ensure_ascii=False)
    
    with open('logs.json', 'w', encoding='utf-8') as f:
        json.dump(logs_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Generated {len(students)} students → students.json")
    print(f"✅ Generated {len(jobs)} jobs → jobs.json")
    print(f"✅ Generated {len(logs)} placement logs → logs.json")


def load_from_json() -> tuple:
    """Load data from JSON files"""
    try:
        with open('students.json', 'r', encoding='utf-8') as f:
            students_data = json.load(f)
            students = [StudentProfile(**s) for s in students_data]
        
        with open('jobs.json', 'r', encoding='utf-8') as f:
            jobs_data = json.load(f)
            jobs = [JobDescription(**j) for j in jobs_data]
        
        with open('logs.json', 'r', encoding='utf-8') as f:
            logs_data = json.load(f)
            logs = [PlacementLog(**l) for l in logs_data]
        
        return students, jobs, logs
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("Run generate_data() first to create the data files.")
        return [], [], []


# ==================== MAIN EXECUTION ====================

def generate_data():
    """Main function to generate all synthetic data"""
    print("🚀 Starting Synthetic Data Generation...")
    print("=" * 60)
    
    generator = SyntheticDataGenerator(seed=42)
    
    print("\n📊 Generating Students...")
    students = generator.generate_students(count=30)
    
    print("💼 Generating Job Descriptions...")
    jobs = generator.generate_jobs(count=10)
    
    print("📝 Generating Placement Logs...")
    logs = generator.generate_placement_logs(students, jobs, log_count=50)
    
    print("\n💾 Saving to JSON files...")
    save_to_json(students, jobs, logs)
    
    print("\n" + "=" * 60)
    print("✨ Data generation complete!")
    print("\n📈 Summary Statistics:")
    print(f"   - Star Students (GPA > 8.5, No Backlogs): {sum(1 for s in students if s.gpa >= 8.5 and s.backlogs == 0)}")
    print(f"   - Average Students: {sum(1 for s in students if 7.0 <= s.gpa < 8.5)}")
    print(f"   - At-Risk Students (GPA < 7.0 or Backlogs): {sum(1 for s in students if s.gpa < 7.0 or s.backlogs > 0)}")
    print(f"\n   - Strict MNC Jobs (GPA > 7.5): {sum(1 for j in jobs if j.min_gpa >= 7.5)}")
    print(f"   - Lenient Startup Jobs (GPA < 7.0): {sum(1 for j in jobs if j.min_gpa < 7.0)}")
    print(f"\n   - Hired: {sum(1 for l in logs if l.status == 'Hired')}")
    print(f"   - Rejected: {sum(1 for l in logs if l.status == 'Rejected')}")
    print(f"   - Hard Constraint Rejections: {sum(1 for l in logs if 'Hard Constraint' in l.reason)}")


if __name__ == "__main__":
    generate_data()
