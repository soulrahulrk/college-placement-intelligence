"""
Data Engine for College Placement Intelligence Agent
Realistic Indian Engineering College Placement System

ROLE & MINDSET:
Act as a senior placement-analytics engineer working with a real Indian 
engineering college placement cell. Focus on solving real placement problems 
using data, logic, and explainability. No assumptions. No shortcuts.
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field, field_validator
from faker import Faker
import random
import json
from datetime import datetime

fake = Faker('en_IN')  # Indian locale for realistic names


# ==================== PYDANTIC MODELS ====================

class SkillEvidence(BaseModel):
    """Evidence backing up skill claims"""
    github: bool = False
    projects: int = Field(ge=0, le=5, default=0)
    certifications: int = Field(ge=0, le=3, default=0)
    internship: bool = False


class Skill(BaseModel):
    """Individual skill with claim level and verifiable evidence"""
    name: str
    claimed_level: str = Field(description="beginner, intermediate, advanced")
    evidence: SkillEvidence


class StudentProfile(BaseModel):
    """Student data model - Indian engineering college context"""
    student_id: str
    name: str
    branch: str = Field(description="CSE, IT, AI, DS, ECE, EEE, ME, CE, CHE, BT, IE")
    cgpa: float = Field(ge=5.0, le=9.8, description="CGPA on 10-point scale")
    active_backlogs: int = Field(ge=0, le=5, description="Number of active backlogs")
    skills: List[Skill]
    communication_score: int = Field(ge=1, le=10, description="Communication ability (1-10)")
    mock_interview_score: int = Field(ge=1, le=10, description="Mock interview performance (1-10)")
    resume_trust_score: float = Field(ge=0, le=1, description="Resume credibility (0-1)")
    email: str
    phone: str
    
    @field_validator('cgpa')
    @classmethod
    def validate_cgpa(cls, v):
        if v < 5.0 or v > 9.8:
            raise ValueError('CGPA must be between 5.0 and 9.8')
        return round(v, 2)


class EligibilityRules(BaseModel):
    """Company eligibility criteria"""
    min_cgpa: float = Field(ge=6.0, le=8.5)
    max_backlogs: int = Field(ge=0, le=2)
    mandatory_skills: List[str]
    preferred_skills: List[str]


class WeightPolicy(BaseModel):
    """Company-specific scoring weights"""
    gpa_weight: float = Field(ge=0.2, le=0.5)
    skill_weight: float = Field(ge=0.3, le=0.6)
    communication_weight: float = Field(ge=0.1, le=0.3)
    mock_interview_weight: float = Field(ge=0.0, le=0.2, default=0.1)


class JobDescription(BaseModel):
    """Job/Company description - Indian placement context"""
    company_id: str
    company_name: str
    company_type: str = Field(description="MNC, Startup, Product, Service")
    role: str
    eligibility_rules: EligibilityRules
    weight_policy: WeightPolicy
    risk_tolerance: str = Field(description="low, medium, high")
    open_positions: int = Field(ge=1, le=50, default=5, description="Number of open positions for this role")


class PlacementLog(BaseModel):
    """Historical placement outcome record"""
    log_id: str
    student_id: str
    company_id: str
    shortlisted: bool
    interview_result: str = Field(description="selected, rejected, no_show")
    failure_reason: Optional[str] = Field(default=None, description="low_dsa, poor_communication, fake_skill, cgpa, none")
    timestamp: str


# ==================== SYNTHETIC DATA GENERATOR ====================

class SyntheticDataGenerator:
    """Generate realistic Indian placement data with skill inflation patterns"""
    
    # Indian engineering branches (expanded)
    BRANCHES = [
        "CSE",      # Computer Science Engineering
        "IT",       # Information Technology
        "AI",       # Artificial Intelligence
        "DS",       # Data Science
        "ECE",      # Electronics & Communication
        "EEE",      # Electrical & Electronics
        "ME",       # Mechanical Engineering
        "CE",       # Civil Engineering
        "CHE",      # Chemical Engineering
        "BT",       # Biotechnology
        "IE"        # Industrial Engineering
    ]
    
    # Skill pools
    PROGRAMMING_SKILLS = ["Python", "Java", "C++", "JavaScript", "DSA", "SQL"]
    WEB_SKILLS = ["React", "Angular", "Node.js", "Django", "Flask"]
    DATA_SKILLS = ["Machine Learning", "Data Structures", "Pandas", "NumPy"]
    OTHER_SKILLS = ["Git", "Docker", "AWS", "MongoDB", "REST API"]
    
    ALL_SKILLS = PROGRAMMING_SKILLS + WEB_SKILLS + DATA_SKILLS + OTHER_SKILLS
    
    # Indian companies
    MNCS = [
        "Google India", "Microsoft IDC", "Amazon Development Centre",
        "Goldman Sachs", "Morgan Stanley", "Cisco India"
    ]
    
    STARTUPS = [
        "Zerodha", "CRED", "Razorpay", "Swiggy", "PhonePe",
        "Groww", "Meesho"
    ]
    
    PRODUCT_COMPANIES = [
        "Adobe India", "Atlassian", "Salesforce", "Oracle India",
        "SAP Labs", "VMware India"
    ]
    
    SERVICE_COMPANIES = [
        "TCS", "Infosys", "Wipro", "Cognizant", "Accenture"
    ]
    
    ROLES = [
        "Software Engineer", "SDE-1", "Data Analyst", "Full Stack Developer",
        "Backend Developer", "Frontend Developer", "ML Engineer", "DevOps Engineer"
    ]
    
    def __init__(self, seed: int = 42):
        random.seed(seed)
        Faker.seed(seed)
    
    def _calculate_resume_trust_score(self, skills: List[Skill]) -> float:
        """Calculate resume credibility based on evidence"""
        if not skills:
            return 0.5
        
        total_evidence = 0
        total_claims = len(skills)
        
        for skill in skills:
            evidence_score = 0
            if skill.evidence.github:
                evidence_score += 0.4
            if skill.evidence.projects > 0:
                evidence_score += 0.3 * (skill.evidence.projects / 5)
            if skill.evidence.certifications > 0:
                evidence_score += 0.2 * (skill.evidence.certifications / 3)
            if skill.evidence.internship:
                evidence_score += 0.3
            
            # Penalty for claiming advanced without evidence
            if skill.claimed_level == "advanced":
                if not (skill.evidence.github or skill.evidence.projects >= 2):
                    evidence_score -= 0.3
            
            total_evidence += min(1.0, evidence_score)
        
        trust_score = max(0.0, min(1.0, total_evidence / total_claims))
        return round(trust_score, 2)
    
    def _generate_skill(self, skill_name: str, student_type: str, inflate_skill: bool) -> Skill:
        """Generate skill with evidence based on student type"""
        
        if student_type == "star":
            # Star students: genuine skills with strong evidence
            claimed_level = random.choice(["intermediate", "advanced"])
            evidence = SkillEvidence(
                github=random.choice([True, True, False]),
                projects=random.randint(2, 5),
                certifications=random.randint(1, 3),
                internship=random.choice([True, False])
            )
        
        elif student_type == "average":
            # Average students: mix of genuine and some inflation
            if inflate_skill:
                # Inflate this skill
                claimed_level = "advanced"
                evidence = SkillEvidence(
                    github=False,
                    projects=random.randint(0, 1),
                    certifications=0,
                    internship=False
                )
            else:
                claimed_level = random.choice(["beginner", "intermediate"])
                evidence = SkillEvidence(
                    github=random.choice([True, False]),
                    projects=random.randint(1, 3),
                    certifications=random.randint(0, 2),
                    internship=random.choice([True, False])
                )
        
        else:  # weak student
            if inflate_skill:
                # Inflate skills heavily
                claimed_level = random.choice(["intermediate", "advanced"])
                evidence = SkillEvidence(
                    github=False,
                    projects=0,
                    certifications=0,
                    internship=False
                )
            else:
                claimed_level = "beginner"
                evidence = SkillEvidence(
                    github=False,
                    projects=random.randint(0, 1),
                    certifications=0,
                    internship=False
                )
        
        return Skill(name=skill_name, claimed_level=claimed_level, evidence=evidence)
    
    def generate_students(self, count: int = 50) -> List[StudentProfile]:
        """Generate 50 realistic students with skill inflation patterns"""
        students = []
        
        # 30% inflate skills, as per requirement
        inflate_count = int(count * 0.3)
        inflate_indices = set(random.sample(range(count), inflate_count))
        
        for i in range(count):
            student_id = f"S{i+1:03d}"
            name = fake.name()
            branch = random.choice(self.BRANCHES)
            
            # Determine student type (affects skill generation)
            rand = random.random()
            if rand < 0.25:  # 25% star students
                student_type = "star"
                cgpa = round(random.uniform(8.5, 9.8), 2)
                active_backlogs = 0
                communication_score = random.randint(7, 10)
                mock_interview_score = random.randint(7, 10)
            elif rand < 0.65:  # 40% average students
                student_type = "average"
                cgpa = round(random.uniform(7.0, 8.5), 2)
                active_backlogs = random.choice([0, 0, 1])
                communication_score = random.randint(5, 8)
                mock_interview_score = random.randint(5, 8)
            else:  # 35% weak students
                student_type = "weak"
                cgpa = round(random.uniform(5.0, 7.0), 2)
                active_backlogs = random.randint(1, 5)
                communication_score = random.randint(3, 6)
                mock_interview_score = random.randint(3, 6)
            
            # Generate skills
            skill_count = random.randint(4, 8)
            selected_skills = random.sample(self.ALL_SKILLS, skill_count)
            
            skills = []
            will_inflate = i in inflate_indices
            
            for j, skill_name in enumerate(selected_skills):
                # If student inflates, inflate 2-3 skills
                inflate_this_skill = will_inflate and j < random.randint(2, 3)
                skill = self._generate_skill(skill_name, student_type, inflate_this_skill)
                skills.append(skill)
            
            # Some edge cases: low CGPA but strong skills (realistic scenario)
            if random.random() < 0.15 and student_type == "weak":
                # This student has low CGPA but actually has good skills
                for skill in skills[:2]:  # Make first 2 skills genuine
                    skill.evidence.github = True
                    skill.evidence.projects = random.randint(2, 4)
            
            # Some edge cases: high CGPA but poor communication
            if random.random() < 0.1 and student_type == "star":
                communication_score = random.randint(4, 6)
                mock_interview_score = random.randint(4, 6)
            
            # Calculate trust score
            resume_trust_score = self._calculate_resume_trust_score(skills)
            
            student = StudentProfile(
                student_id=student_id,
                name=name,
                branch=branch,
                cgpa=cgpa,
                active_backlogs=active_backlogs,
                skills=skills,
                communication_score=communication_score,
                mock_interview_score=mock_interview_score,
                resume_trust_score=resume_trust_score,
                email=fake.email(),
                phone=fake.phone_number()
            )
            students.append(student)
        
        return students
    
    def generate_jobs(self, count: int = 12) -> List[JobDescription]:
        """Generate 12 companies with varied hiring behaviors"""
        jobs = []
        
        # 4 MNCs - strict
        for i in range(4):
            company_id = f"C{len(jobs)+1:03d}"
            company_name = random.choice(self.MNCS)
            role = random.choice(self.ROLES)
            
            eligibility = EligibilityRules(
                min_cgpa=round(random.uniform(7.5, 8.5), 1),
                max_backlogs=0,
                mandatory_skills=random.sample(["DSA", "Python", "Java", "SQL"], 2),
                preferred_skills=random.sample(["Git", "Docker", "AWS", "React"], 2)
            )
            
            weights = WeightPolicy(
                gpa_weight=round(random.uniform(0.4, 0.5), 2),
                skill_weight=round(random.uniform(0.3, 0.4), 2),
                communication_weight=round(random.uniform(0.1, 0.2), 2)
            )
            
            job = JobDescription(
                company_id=company_id,
                company_name=company_name,
                company_type="MNC",
                role=role,
                eligibility_rules=eligibility,
                weight_policy=weights,
                risk_tolerance="low",
                open_positions=random.randint(3, 8)  # MNCs: selective hiring
            )
            jobs.append(job)
        
        # 3 Startups - flexible, skill-focused
        for i in range(3):
            company_id = f"C{len(jobs)+1:03d}"
            company_name = random.choice(self.STARTUPS)
            role = random.choice(self.ROLES)
            
            eligibility = EligibilityRules(
                min_cgpa=round(random.uniform(6.0, 6.5), 1),
                max_backlogs=random.choice([1, 2]),
                mandatory_skills=random.sample(["Python", "JavaScript", "React", "DSA"], 2),
                preferred_skills=random.sample(["Machine Learning", "AWS", "Docker"], 2)
            )
            
            weights = WeightPolicy(
                gpa_weight=round(random.uniform(0.2, 0.3), 2),
                skill_weight=round(random.uniform(0.5, 0.6), 2),
                communication_weight=round(random.uniform(0.1, 0.2), 2)
            )
            
            job = JobDescription(
                company_id=company_id,
                company_name=company_name,
                company_type="Startup",
                role=role,
                eligibility_rules=eligibility,
                weight_policy=weights,
                risk_tolerance="high",
                open_positions=random.randint(2, 5)  # Startups: small teams
            )
            jobs.append(job)
        
        # 3 Product companies - balanced
        for i in range(3):
            company_id = f"C{len(jobs)+1:03d}"
            company_name = random.choice(self.PRODUCT_COMPANIES)
            role = random.choice(self.ROLES)
            
            eligibility = EligibilityRules(
                min_cgpa=round(random.uniform(7.0, 7.5), 1),
                max_backlogs=random.choice([0, 1]),
                mandatory_skills=random.sample(["DSA", "Python", "Java", "C++"], 2),
                preferred_skills=random.sample(["React", "SQL", "Git"], 2)
            )
            
            weights = WeightPolicy(
                gpa_weight=round(random.uniform(0.3, 0.4), 2),
                skill_weight=round(random.uniform(0.4, 0.5), 2),
                communication_weight=round(random.uniform(0.2, 0.3), 2)
            )
            
            job = JobDescription(
                company_id=company_id,
                company_name=company_name,
                company_type="Product",
                role=role,
                eligibility_rules=eligibility,
                weight_policy=weights,
                risk_tolerance="medium",
                open_positions=random.randint(5, 12)  # Product: moderate hiring
            )
            jobs.append(job)
        
        # 2 Service companies - moderate
        for i in range(2):
            company_id = f"C{len(jobs)+1:03d}"
            company_name = random.choice(self.SERVICE_COMPANIES)
            role = random.choice(self.ROLES)
            
            eligibility = EligibilityRules(
                min_cgpa=round(random.uniform(6.5, 7.0), 1),
                max_backlogs=random.choice([1, 2]),
                mandatory_skills=random.sample(["Java", "Python", "SQL"], 2),
                preferred_skills=random.sample(["React", "Angular", "DSA"], 2)
            )
            
            weights = WeightPolicy(
                gpa_weight=0.3,
                skill_weight=0.4,
                communication_weight=0.3
            )
            
            job = JobDescription(
                company_id=company_id,
                company_name=company_name,
                company_type="Service",
                role=role,
                eligibility_rules=eligibility,
                weight_policy=weights,
                risk_tolerance="medium",
                open_positions=random.randint(15, 50)  # Service: mass hiring
            )
            jobs.append(job)
        
        return jobs
    
    def generate_placement_logs(
        self, 
        students: List[StudentProfile], 
        jobs: List[JobDescription],
        log_count: int = 120
    ) -> List[PlacementLog]:
        """Generate 120 historical placement records with realistic patterns"""
        logs = []
        
        for i in range(log_count):
            student = random.choice(students)
            job = random.choice(jobs)
            
            log_id = f"LOG{i+1:04d}"
            
            # Eligibility check
            meets_cgpa = student.cgpa >= job.eligibility_rules.min_cgpa
            meets_backlogs = student.active_backlogs <= job.eligibility_rules.max_backlogs
            
            # Skill match check
            student_skills = {s.name for s in student.skills}
            mandatory_match = sum(
                1 for skill in job.eligibility_rules.mandatory_skills 
                if skill in student_skills
            )
            mandatory_ratio = mandatory_match / len(job.eligibility_rules.mandatory_skills)
            
            # Decision logic
            if not meets_cgpa:
                shortlisted = False
                interview_result = "rejected"
                failure_reason = "cgpa"
            
            elif not meets_backlogs:
                shortlisted = False
                interview_result = "rejected"
                failure_reason = "cgpa"
            
            elif mandatory_ratio < 0.5:
                shortlisted = False
                interview_result = "rejected"
                failure_reason = "low_dsa"
            
            else:
                # Shortlisted
                shortlisted = True
                
                # Interview outcome based on:
                # 1. Resume trust (fake skills fail more)
                # 2. Communication score
                # 3. Mock interview score
                
                success_probability = 0.3  # Base
                
                # Resume trust impact
                if student.resume_trust_score >= 0.7:
                    success_probability += 0.3
                elif student.resume_trust_score >= 0.4:
                    success_probability += 0.1
                else:
                    success_probability -= 0.2  # Fake skills penalize
                
                # Communication impact
                if student.communication_score >= 8:
                    success_probability += 0.2
                elif student.communication_score >= 6:
                    success_probability += 0.1
                elif student.communication_score < 5:
                    success_probability -= 0.2
                
                # Mock interview impact
                if student.mock_interview_score >= 8:
                    success_probability += 0.1
                elif student.mock_interview_score < 5:
                    success_probability -= 0.1
                
                # Random outcome
                if random.random() < success_probability:
                    interview_result = "selected"
                    failure_reason = None
                else:
                    interview_result = "rejected"
                    
                    # Determine failure reason
                    if student.resume_trust_score < 0.4:
                        failure_reason = "fake_skill"
                    elif student.communication_score < 6:
                        failure_reason = "poor_communication"
                    else:
                        failure_reason = "low_dsa"
                
                # Small chance of no-show
                if random.random() < 0.05:
                    interview_result = "no_show"
                    failure_reason = None
            
            log = PlacementLog(
                log_id=log_id,
                student_id=student.student_id,
                company_id=job.company_id,
                shortlisted=shortlisted,
                interview_result=interview_result,
                failure_reason=failure_reason,
                timestamp=fake.date_time_between(start_date="-1y", end_date="now").isoformat()
            )
            logs.append(log)
        
        return logs


# ==================== DATA EXPORT/IMPORT ====================

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
    
    print(f"[OK] Generated {len(students)} students -> students.json")
    print(f"[OK] Generated {len(jobs)} jobs -> jobs.json")
    print(f"[OK] Generated {len(logs)} placement logs -> logs.json")


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
    """Main function to generate realistic Indian placement data"""
    print("🚀 Starting Realistic Indian Placement Data Generation...")
    print("=" * 70)
    print("ROLE: Senior Placement-Analytics Engineer")
    print("FOCUS: Real problems, Real solutions, Real explanations")
    print("=" * 70)
    
    generator = SyntheticDataGenerator(seed=42)
    
    print("\n📊 Generating 50 Students (Indian Names, Realistic Profiles)...")
    students = generator.generate_students(count=50)
    
    print("💼 Generating 12 Companies (MNC/Startup/Product/Service)...")
    jobs = generator.generate_jobs(count=12)
    
    print("📝 Generating 120 Placement Logs (Historical Outcomes)...")
    logs = generator.generate_placement_logs(students, jobs, log_count=120)
    
    print("\n💾 Saving to JSON files...")
    save_to_json(students, jobs, logs)
    
    # Analytics
    print("\n" + "=" * 70)
    print("✨ Data Generation Complete!")
    print("=" * 70)
    
    print("\n📈 Student Distribution:")
    star = sum(1 for s in students if s.cgpa >= 8.5 and s.active_backlogs == 0)
    average = sum(1 for s in students if 7.0 <= s.cgpa < 8.5)
    weak = sum(1 for s in students if s.cgpa < 7.0 or s.active_backlogs > 0)
    print(f"   ⭐ Star Students (CGPA ≥ 8.5, No Backlogs): {star}")
    print(f"   📚 Average Students (CGPA 7.0-8.5): {average}")
    print(f"   ⚠️  Weak Students (CGPA < 7.0 or Backlogs): {weak}")
    
    print("\n📊 Resume Credibility:")
    high_trust = sum(1 for s in students if s.resume_trust_score >= 0.7)
    medium_trust = sum(1 for s in students if 0.4 <= s.resume_trust_score < 0.7)
    low_trust = sum(1 for s in students if s.resume_trust_score < 0.4)
    print(f"   ✅ HIGH Credibility (≥0.7): {high_trust} students")
    print(f"   ⚠️  MEDIUM Credibility (0.4-0.7): {medium_trust} students")
    print(f"   ❌ LOW Credibility (<0.4): {low_trust} students - SKILL INFLATION DETECTED")
    
    print("\n💼 Company Distribution:")
    print(f"   🏢 MNCs (Strict CGPA ≥ 7.5): 4 companies")
    print(f"   🚀 Startups (Flexible CGPA ≥ 6.0): 3 companies")
    print(f"   📦 Product (Balanced CGPA ≥ 7.0): 3 companies")
    print(f"   🔧 Service (Moderate CGPA ≥ 6.5): 2 companies")
    
    print("\n📝 Placement Outcomes:")
    shortlisted = sum(1 for l in logs if l.shortlisted)
    selected = sum(1 for l in logs if l.interview_result == "selected")
    rejected = sum(1 for l in logs if l.interview_result == "rejected")
    print(f"   📋 Total Attempts: {len(logs)}")
    print(f"   ✅ Shortlisted: {shortlisted} ({shortlisted/len(logs)*100:.1f}%)")
    print(f"   🎉 Selected: {selected} ({selected/len(logs)*100:.1f}%)")
    print(f"   ❌ Rejected: {rejected} ({rejected/len(logs)*100:.1f}%)")
    
    print("\n🔍 Top Rejection Reasons:")
    reasons = {}
    for log in logs:
        if log.failure_reason:
            reasons[log.failure_reason] = reasons.get(log.failure_reason, 0) + 1
    
    for reason, count in sorted(reasons.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {reason}: {count} ({count/len(logs)*100:.1f}%)")
    
    print("\n" + "=" * 70)
    print("✅ Realistic Indian placement data ready for analysis!")
    print("=" * 70)


if __name__ == "__main__":
    generate_data()
