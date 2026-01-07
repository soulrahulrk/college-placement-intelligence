# College Placement Intelligence System

**A Realistic Indian Engineering College Placement Cell System with Resume Credibility Detection, Risk Assessment, ML-Based Predictions, AI Chatbot, and Explainable AI Decisions**

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![Pydantic V2](https://img.shields.io/badge/pydantic-V2-green.svg)](https://docs.pydantic.dev/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.51.0-red.svg)](https://streamlit.io/)
[![Version](https://img.shields.io/badge/version-2.0-orange.svg)](https://github.com/soulrahulrk/college-placement-intelligence)

---

## 🎯 ROLE & MINDSET

**Act as a senior placement-analytics engineer** working with a real Indian engineering college placement cell.

**Your job is NOT to impress with buzzwords.**  
**Your job is to solve REAL placement problems using data, logic, and explainability.**

### Real Problems We Solve:
- ✅ **30% of students inflate skills** (claim "advanced" without GitHub/projects)
- ✅ **Resume credibility scoring** (0-1 scale based on evidence)
- ✅ **Risk assessment** (LOW/MEDIUM/HIGH based on historical failures)
- ✅ **Explainable decisions** (student + officer views)
- ✅ **Indian context** (11 branches: CSE/IT/AI/DS/ECE/EEE/ME/CE/CHE/BT/IE)
- ✅ **Seat allocation with ranking** (limited positions per company)
- ✅ **ML-based success prediction** (custom Logistic Regression)
- ✅ **Bias & fairness auditing** (CGPA vs skills analysis)
- ✅ **🤖 AI Chatbot Assistant** (Grok-powered agentic AI for natural queries)

**No assumptions. No shortcuts. Just working logic.**

---

## 🆕 Version 2.0 - Major Features

### 5 Mandatory Upgrades + AI Assistant

| Feature | Description | Status |
|---------|-------------|--------|
| **1** | Company Seat Allocation & Ranking | ✅ Complete |
| **2** | Profile Improvement & Temporal Drift | ✅ Complete |
| **3** | Learning-Based Success Probability | ✅ Complete |
| **4** | Credibility Penalty Bug Fix | ✅ Complete |
| **5** | Bias & Fairness Audit | ✅ Complete |
| **🆕** | **AI Chatbot Assistant (Grok API)** | ✅ Complete |
| **🆕** | **11 Engineering Branches** | ✅ Complete |
| **🆕** | **Data Import (Excel/CSV)** | ✅ Complete |

### 🤖 NEW: AI Chatbot Assistant

Intelligent AI-powered assistant using **Grok API** with **agentic capabilities**. Users can chat naturally to:

- 📊 Get student/company statistics
- 🔍 Search students by name/branch/ID
- 💼 View company information
- 🎯 Get placement recommendations
- 📈 Analyze credibility and risks
- ❓ Ask natural language questions

**Agentic Tools (5 Functions):**
1. `get_student_statistics` - Overall stats (total, avg CGPA, branches, credibility)
2. `get_company_statistics` - Company analytics (types, positions, requirements)
3. `search_students` - Search by name/branch/student_id
4. `get_student_details` - Detailed student info with credibility analysis
5. `match_student_to_companies` - Smart matching with scores and rankings

**Example Queries:**
- "How many students are there?"
- "Show me CSE students with high CGPA"
- "Match student S001 to all companies"
- "Which companies are MNCs?"
- "Get details for Rahul Kumar"

### 🏆 Upgrade 1: Company Seat Allocation & Ranking
Companies have **limited hiring slots** (not all eligible students get selected).

```python
from upgrades import allocate_seats

allocation = allocate_seats(
    students=eligible_students,
    company=google_india,
    logs=placement_logs,
    match_function=match_student_to_job,
    open_positions=5
)

# Output:
# Selected (5): Luke Lanka (Rank 1), Neel Zacharia (Rank 2)...
# Rejected due to seat limit (23): Aryan Maharaj, Rushil Saini...
# Cutoff Score: 0.66
```

**Key Features:**
- `open_positions` field added to JobDescription (MNCs: 3-8, Startups: 2-5, Service: 15-50)
- Ranking by: match_score (desc) + risk_score (asc for ties)
- Produces: Selected, Waitlisted, Rejected states with cutoff score

#### 📈 Upgrade 2: Profile Improvement & Temporal Drift
Track student growth over semesters 5-8.

```python
from upgrades import simulate_student_growth, generate_growth_timeline

profile = simulate_student_growth(student, calculate_credibility, semesters=[5, 6, 7, 8])
print(generate_growth_timeline(profile))

# Output:
# Semester 5: CGPA 7.2, Communication 5/10, GitHub Projects: 1
# Semester 6: CGPA 7.4, Communication 6/10, GitHub Projects: 2
# ...
# Growth Summary: CGPA +0.3, Communication +2, GitHub +3
```

**Key Features:**
- `StudentProfileSnapshot` tracks semester-by-semester progress
- Simulates: CGPA drift, communication improvement, GitHub project addition
- Credibility evolution tracking (LOW → MEDIUM → HIGH)

#### 🤖 Upgrade 3: Learning-Based Success Probability
Custom **Logistic Regression** (no sklearn dependency!) trained on historical placement data.

```python
from upgrades import PlacementSuccessPredictor, prepare_training_data

predictor = PlacementSuccessPredictor()
training_data = prepare_training_data(students, companies, logs, calculate_credibility)
predictor.train(training_data)

prediction = predictor.predict(student, company, credibility_score, risk_score, skill_match)

# Output:
# Success Probability: 73.2%
# Confidence: HIGH
# Feature Importance:
#   skill_match_ratio: 41.3%
#   cgpa: 22.2%
#   credibility_score: 19.5%
```

**Key Features:**
- Pure Python implementation with gradient descent
- Returns: probability + confidence (HIGH/MEDIUM/LOW) + feature importance
- Insight: skill_match_ratio is the most important predictor (41.3%)

#### 🔧 Upgrade 4: Credibility Penalty Bug Fix
**Bug in v1**: Unfairly penalized students with many skills.

**Fix:**
1. Apply inflation penalty **per inflated skill** (not cumulative)
2. **Cap total penalty at 0.6** (prevents over-penalization)
3. **Quality-weighted normalization** (not simple average)

```python
from upgrades import validate_credibility_fix

result = validate_credibility_fix()

# Output:
# Student A (3 strong skills): Score = 0.79, Level = HIGH
# Student B (8 weak inflated): Score = 0.00, Level = LOW
# Result: PASS - Quality beats quantity ✅
```

#### ⚖️ Upgrade 5: Bias & Fairness Audit
Analyze placement outcomes for potential bias.

```python
from upgrades import conduct_bias_audit, generate_bias_audit_report

audit = conduct_bias_audit(students, companies, logs, calculate_credibility_v2)
print(generate_bias_audit_report(audit))

# Output:
# CGPA Bucket Analysis:
#   low (5.0-6.5): 0.0% selected
#   star (8.5+): 38.0% selected
#
# Skill vs GPA Comparison:
#   Skill-heavy students: 33.3% success
#   GPA-heavy students: 20.7% success
#   Conclusion: Skill evidence outweighs GPA ✅
#
# Overall Fairness Score: 80.4/100 - EXCELLENT
```

**Key Features:**
- Selection rate by: CGPA bucket, credibility level, branch, communication
- Skill-heavy vs GPA-heavy comparison
- Actionable recommendations for placement cell

---

## 🚀 Features

### 1. **Resume Credibility Detection** 🔍
- **Evidence-based validation**: GitHub repos, projects, certifications, internships
- **Skill inflation penalty**: 40% score reduction for "advanced" claims without proof
- **Trust scoring**: 0-1 scale with LOW/MEDIUM/HIGH classification
- **Red flag detection**: "Claimed 5 advanced skills, 0 GitHub repos, 0 projects"

### 2. **Risk Assessment Engine** ⚠️
- **Historical pattern analysis**: Similar profile failures at same company
- **Communication gap detection**: Student score vs company average
- **Credibility-based risk**: LOW credibility → +3 risk points
- **Risk levels**: LOW (safe) / MEDIUM (monitor) / HIGH (reject if score < 0.7)

### 3. **Explainable AI** 💬

**Student View:**
```
Thank you for applying, Rahul Kumar.

Unfortunately, we are unable to move forward with your application 
for Software Developer at TCS.

Reason: Resume credibility concerns - some skills lack supporting evidence

Areas for improvement:
📌 Resume credibility issues:
  • Python: Claimed 'advanced' but no GitHub/projects
  • DSA: Claimed 'advanced' but no GitHub/projects
📌 Risk assessment: MEDIUM
  • Low resume credibility (0.28) - Skill inflation detected

Don't give up! Use this feedback to strengthen your profile.
```

**Officer View:**
```
=== PLACEMENT OFFICER ANALYSIS ===
Student: Rahul Kumar (S042)
Company: TCS - Software Developer
Decision: REJECTED
Failure Reason: fake_skill

--- RESUME CREDIBILITY ANALYSIS ---
Score: 0.28 / 1.00
Level: LOW

Red Flags (2):
  ⚠ Python: Claimed 'advanced' but no GitHub/projects
  ⚠ DSA: Claimed 'advanced' but no GitHub/projects

--- RISK ASSESSMENT ---
Risk Level: HIGH
Risk Score: 7/10

Contributing Factors:
  • Similar profiles failed 4 times at this company
  • Low resume credibility (0.28) - Skill inflation detected
  • Communication score (4/10) below company average (7.2/10)

--- RECOMMENDATION ---
❌ REJECTED - Does not meet criteria or high risk of failure
```

### 4. **Realistic Indian Placement Data** 🇮🇳
- **50 students** with Indian names (Faker 'en_IN': Priya Sharma, Arjun Patel, Anjali Singh)
- **5 branches**: CSE, IT, AI-ML, ECE, Mechanical Engineering
- **12 companies**: 4 MNCs (Microsoft IDC, TCS, Infosys), 3 Startups (CRED, Razorpay), 3 Product, 2 Service
- **120 placement logs** with realistic outcomes (12.5% success rate)

### 5. **Interactive Streamlit Dashboard** 📊

#### **9 Dashboard Pages:**
1. **🏠 Overview Dashboard** - Credibility distribution, branch-wise stats, company types
2. **👤 Student Analysis** - Individual student matching with all companies
3. **🎯 Credibility Dashboard** - Resume trust scores, skill inflation detection
4. **⚠️ Risk Assessment** - Company-specific risk analysis for all students
5. **🚨 Fake Skill Detection** - Flag students with suspicious claims (CSV export)
6. **📊 Placement Analytics** - Success rates, avg CGPA/communication of selected students
7. **📥 Data Import** - Upload Excel/CSV files for students/companies (with templates)
8. **🤖 AI Assistant** - Grok-powered chatbot for natural queries (NEW!)
9. **🏢 Company Analysis** - (Coming soon)

---

## 🏗️ Architecture

### Tech Stack
- **Python 3.13** - Core language
- **Pydantic V2** - Data validation with `@field_validator`
- **Streamlit 1.51.0** - Interactive dashboards
- **Plotly** - Advanced visualizations
- **Faker ('en_IN')** - Indian name generation
- **Pandas** - Data manipulation
- **Grok API** - AI-powered chatbot with agentic capabilities
- **python-dotenv** - Secure API key management

### Project Structure
```
placement llm/
├── data_engine.py         # Data models + synthetic generator (11 branches)
├── intelligence.py        # Credibility, risk, matching logic
├── upgrades.py           # 5 mandatory upgrades (v2.0)
├── app.py                # Streamlit dashboard (9 pages + AI chatbot)
├── .env                  # API keys (DO NOT COMMIT)
├── .env.example          # Template for environment variables
├── students.json         # 50 students with evidence data
├── jobs.json            # 12 companies with eligibility rules
├── logs.json            # 120 placement outcomes
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

### Core Components

#### 1. **Data Engine** ([data_engine.py](data_engine.py))
**Pydantic Models:**
- `SkillEvidence`: GitHub (bool), projects (0-5), certifications (0-3), internship (bool)
- `Skill`: name, claimed_level (beginner/intermediate/advanced), evidence
- `StudentProfile`: student_id, name, branch, cgpa, active_backlogs, skills, **communication_score**, **mock_interview_score**, **resume_trust_score**
- `EligibilityRules`: min_cgpa, max_backlogs, mandatory_skills, preferred_skills
- `WeightPolicy`: gpa_weight, skill_weight, communication_weight, mock_interview_weight
- `JobDescription`: company_id, company_name, company_type, role, eligibility_rules, weight_policy, risk_tolerance
- `PlacementLog`: log_id, student_id, company_id, interview_result, failure_reason, placement_date

**Data Generator:**
```python
generator = SyntheticDataGenerator()
students = generator.generate_students(50)  # 10 star, 24 average, 21 weak
companies = generator.generate_jobs(12)     # 4 MNC, 3 Startup, 3 Product, 2 Service
logs = generator.generate_placement_logs(students, companies, 120)
```

**Key Feature: Skill Inflation**
- 30% of students get `inflate_skill=True`
- Claim "advanced" but no GitHub, projects < 2
- Resume trust score penalized: `score - (inflation_count * 0.3)`

#### 2. **Intelligence Core** ([intelligence.py](intelligence.py))

**Functions:**

1. **`calculate_credibility(student) -> CredibilityResult`**
   - Evidence score: GitHub (0.4) + Projects (0.3) + Certs (0.2) + Internship (0.3)
   - Inflation penalty: Advanced claim without proof → -0.3
   - Returns: score (0-1), level (LOW/MEDIUM/HIGH), red_flags, strengths

2. **`calculate_risk(student, company, logs, credibility) -> RiskResult`**
   - Historical failures: Similar profiles at same company → +2 to +4 points
   - Credibility check: LOW → +3 points, MEDIUM → +1 point
   - Communication gap: Below company avg → +2 points
   - Mock interview: Score < 5 → +1 point
   - Company tolerance: LOW tolerance + risk ≥ 3 → +1 point
   - Returns: risk_level (LOW/MEDIUM/HIGH), risk_score (0-10), factors

3. **`match_student_to_job(student, company, logs) -> MatchResult`**
   - **Step 1**: Check eligibility (CGPA, backlogs) → Reject if fail
   - **Step 2**: Calculate credibility and risk
   - **Step 3**: Check DSA for tech roles → Reject if missing
   - **Step 4**: Calculate base score with weight policy
   - **Step 5**: Apply credibility penalty (LOW: 40% reduction, MEDIUM: 15%)
   - **Step 6**: Risk-based decision (HIGH risk + score < 0.7 → Reject)
   - Returns: decision (selected/shortlisted/rejected), match_score, credibility, risk, failure_reason

4. **`generate_student_explanation(...)` → Student-friendly message**

5. **`generate_officer_explanation(...)` → Detailed officer report**

6. **`analyze_placement_outcomes(logs)` → Company insights + recommendations**

#### 3. **Streamlit Dashboard** ([app.py](app.py))

**7 Interactive Pages:**

**Overview Dashboard:**
- Total students/companies/placements metrics
- Credibility distribution pie chart (HIGH/MEDIUM/LOW)
- Branch-wise student distribution
- Company type breakdown

**Student Analysis:**
- Select student → View profile + credibility
- Skills portfolio table (GitHub, Projects, Certs, Internship)
- Matching results with all 12 companies (color-coded)

**Credibility Dashboard:**
- All students with credibility scores
- Filters: Level (HIGH/MEDIUM/LOW), Branch
- Histogram: Score distribution
- Detect 30% skill inflation

**Risk Assessment:**
- Select company → Risk analysis for all students
- Risk level distribution (LOW/MEDIUM/HIGH)
- Top risk factors for each student

**Fake Skill Detection:**
- Flag students with advanced claims + no evidence
- Export CSV report
- Critical cases (LOW credibility)

**Placement Analytics:**
- Company performance summary
- Success rates, avg CGPA/communication of selected students
- Recommendations (increase communication weight / focus on CGPA screening)

---

## 🚀 Quick Start

### Installation

```bash
# Navigate to project directory
cd "c:\Users\rahul\Documents\code\projects\placement llm"

# Install all dependencies
pip install -r requirements.txt
```

### Setup Grok API (for AI Chatbot)

1. Get your Grok API key from [console.x.ai](https://console.x.ai/)
2. Copy `.env.example` to `.env`
3. Add your API key to `.env`:

```bash
GROK_API_KEY=your_actual_grok_api_key_here
```

**⚠️ Important:** Never commit `.env` to Git. It's already in `.gitignore`.

### Generate Data

```bash
python data_engine.py
```

**Output:**
```
[OK] Generated 50 students -> students.json
  10 star students (CGPA ≥ 8.5)
  24 average students (7.0 ≤ CGPA < 8.5)
  21 weak students (CGPA < 7.0)

Resume credibility: 8 HIGH, 14 MEDIUM, 28 LOW
Skill inflation detected: 30% of students

[OK] Generated 12 jobs -> jobs.json
  4 MNC (strict: min_cgpa 8.0+, no backlogs)
  3 Startup (flexible: min_cgpa 6.5+)
  3 Product (balanced)
  2 Service (moderate)

[OK] Generated 120 placement logs -> logs.json
  32 shortlisted (26.7%)
  15 selected (12.5%)
  100 rejected (83.3%)

Top rejection reasons:
  cgpa: 43.3%
  low_dsa: 31.7%
  fake_skill: 7.5%
```

### Test Intelligence Engine

```bash
python intelligence.py
```

**Output:**
```
=== CREDIBILITY TEST ===
Student: Aryan Maharaj
Credibility: HIGH (0.81)
Red flags: []
Strengths: ['4 skills backed by GitHub', '2 skills with strong evidence']

=== RISK ASSESSMENT TEST ===
Company: Microsoft IDC
Risk: LOW (Score: 0/10)
Factors: []

=== MATCHING TEST ===
Decision: rejected
Match Score: 0.0
Failure Reason: low_dsa
```

### Run Dashboard

```bash
streamlit run app.py
```

Open browser: **http://localhost:8501**

---

## 🧮 Algorithms

### Resume Credibility Formula

```python
for each skill:
    evidence_score = (
        0.4 if github else 0.0 +
        0.3 * (projects / 5) +
        0.2 * (certifications / 3) +
        0.3 if internship else 0.0
    )
    
    # Inflation check
    if claimed_level == "advanced":
        if not (github or projects >= 2):
            inflation_penalty += 0.3
            red_flags.append("Advanced claim without proof")

credibility_score = (sum(evidence_scores) / total_skills) - inflation_penalty

# Classification
if score >= 0.7: level = "HIGH"
elif score >= 0.4: level = "MEDIUM"
else: level = "LOW"
```

### Risk Assessment Formula

```python
risk_score = 0

# Historical patterns
similar_failures = count_failures(same_branch, similar_cgpa, similar_communication)
if similar_failures >= 3: risk_score += 4
elif similar_failures >= 1: risk_score += 2

# Resume credibility
if credibility == "LOW": risk_score += 3
elif credibility == "MEDIUM": risk_score += 1

# Communication gap
if student.communication < company_avg_communication - 2: risk_score += 2

# Mock interview
if student.mock_interview_score < 5: risk_score += 1

# Company tolerance
if company.risk_tolerance == "low" and risk_score >= 3: risk_score += 1

# Classification
if risk_score >= 6: level = "HIGH"
elif risk_score >= 3: level = "MEDIUM"
else: level = "LOW"
```

### Matching Algorithm

```python
# Step 1: Hard constraints (STRICT - NO EXCEPTIONS)
if student.cgpa < company.min_cgpa:
    return REJECT (reason: "cgpa")

if student.active_backlogs > company.max_backlogs:
    return REJECT (reason: "backlogs")

# Step 2: DSA requirement for tech roles
if "software" in role.lower() or "developer" in role.lower():
    if not has_dsa_skill:
        return REJECT (reason: "low_dsa")

# Step 3: Calculate base score
base_score = (
    (student.cgpa / 10) * company.gpa_weight +
    skill_match_ratio * company.skill_weight +
    (student.communication / 10) * company.communication_weight +
    (student.mock_interview / 10) * company.mock_interview_weight
)

# Step 4: Apply credibility penalty
if credibility == "LOW": 
    final_score = base_score * 0.6  # 40% penalty
    if final_score < 0.5: return REJECT (reason: "fake_skill")
elif credibility == "MEDIUM": 
    final_score = base_score * 0.85  # 15% penalty

# Step 5: Risk-based decision
if risk == "HIGH":
    if final_score < 0.7: return REJECT (reason: "failed_interview")
    else: return SHORTLISTED
elif risk == "MEDIUM":
    return SHORTLISTED if final_score >= 0.55 else REJECT
else:  # LOW risk
    if final_score >= 0.7: return SELECTED
    elif final_score >= 0.5: return SHORTLISTED
    else: return REJECT
```

---

## 📊 Sample Data Statistics

### Student Distribution (50 students)
- **10 star students** (20%): CGPA ≥ 8.5, high credibility, strong evidence
- **24 average students** (48%): 7.0 ≤ CGPA < 8.5, mixed credibility
- **16 weak students** (32%): CGPA < 7.0 OR low credibility

### Credibility Breakdown
- **8 HIGH credibility** (16%): Score ≥ 0.7, strong GitHub/projects
- **14 MEDIUM credibility** (28%): 0.4 ≤ Score < 0.7, some evidence gaps
- **28 LOW credibility** (56%): Score < 0.4, **skill inflation detected**

### Company Distribution (12 companies)
- **4 MNC** (Microsoft IDC, TCS, Infosys, Accenture): min_cgpa 8.0+, risk_tolerance LOW
- **3 Startup** (CRED, Razorpay, Dunzo): min_cgpa 6.5+, risk_tolerance HIGH
- **3 Product** (Flipkart, Paytm, Swiggy): min_cgpa 7.5+, risk_tolerance MEDIUM
- **2 Service** (VMware India, Oracle India): min_cgpa 7.2+, risk_tolerance MEDIUM

### Placement Outcomes (120 logs)
- **15 selected** (12.5%)
- **17 shortlisted** (14.2%)
- **88 rejected** (73.3%)

**Rejection Reasons:**
- CGPA too low: 43.3%
- DSA skill missing: 31.7%
- Fake skill detected: 7.5%
- Poor communication: 0.8%
- Failed interview: 16.7%

---

## 🧪 Testing

### Test Data Generation
```bash
python data_engine.py
```
**Expected output:** 50 students, 12 jobs, 120 logs with realistic distributions

### Test Intelligence Engine
```bash
python intelligence.py
```
**Expected output:** Credibility test, risk test, matching test, student/officer explanations

### Test v2.0 Upgrades
```bash
python upgrades.py
```
**Expected output:** All 5 upgrades demo with:
- Seat allocation summary (Selected/Rejected with cutoff)
- Student growth timeline (Semester 5-8)
- ML prediction with confidence and feature importance
- Credibility fix validation (PASS - Quality beats quantity)
- Bias audit report (Fairness score: 80+/100)

### Test Dashboard
```bash
streamlit run app.py
```
**Expected:** Dashboard opens at localhost:8501 with 7 pages

### Verify Skill Inflation
```bash
python -c "from intelligence import *; from data_engine import load_from_json; students, _, _ = load_from_json(); low_cred = [s for s in students if calculate_credibility(s).level == 'LOW']; print(f'{len(low_cred)}/{len(students)} students have LOW credibility ({len(low_cred)/len(students)*100:.1f}%)')"
```
**Expected:** ~28/50 students (56%) have LOW credibility

---

## 💡 Key Design Decisions

### 1. **Why Evidence-Based Validation?**
- Real placement cells verify GitHub repos, projects, certifications
- Reduces bias from keyword-stuffed resumes
- 30% skill inflation is realistic in Indian colleges

### 2. **Why Risk Scoring?**
- Placement officers need to know: "Will this student actually get placed?"
- Historical pattern analysis prevents repeated failures
- Communication gap detection catches weak interview candidates

### 3. **Why Explainable AI?**
- **Students need actionable feedback**: "Build DSA projects" vs "Rejected"
- **Officers need decision support**: "Similar profiles failed 4x" vs score alone
- Transparency builds trust in the system

### 4. **Why Indian Context?**
- Branches (CSE/IT/AI vs generic CS)
- Companies (TCS/Infosys vs generic tech companies)
- Realistic CGPA ranges (6.0-9.8 on 10-point scale)
- Communication scores (critical for Indian placements)

### 5. **Why Pydantic V2?**
- Strong type validation (`@field_validator`)
- Automatic JSON serialization
- Self-documenting data models
- Catches errors at data creation time

---

## 📁 Data Models

### StudentProfile
```python
{
  "student_id": "S001",
  "name": "Priya Sharma",
  "branch": "CSE",
  "cgpa": 8.45,
  "active_backlogs": 0,
  "communication_score": 8,
  "mock_interview_score": 7,
  "resume_trust_score": 0.72,
  "skills": [
    {
      "name": "Python",
      "claimed_level": "advanced",
      "evidence": {
        "github": true,
        "projects": 3,
        "certifications": 2,
        "internship": true
      }
    }
  ]
}
```

### JobDescription
```python
{
  "company_id": "C001",
  "company_name": "Microsoft IDC",
  "company_type": "MNC",
  "role": "Full Stack Developer",
  "open_positions": 5,  # NEW in v2.0
  "eligibility_rules": {
    "min_cgpa": 8.3,
    "max_backlogs": 0,
    "mandatory_skills": ["DSA", "Python"],
    "preferred_skills": ["React", "Node.js"]
  },
  "weight_policy": {
    "gpa_weight": 0.3,
    "skill_weight": 0.4,
    "communication_weight": 0.2,
    "mock_interview_weight": 0.1
  },
  "risk_tolerance": "low"
}
```

### PlacementLog
```python
{
  "log_id": "L001",
  "student_id": "S001",
  "company_id": "C001",
  "interview_result": "selected",
  "failure_reason": null,
  "placement_date": "2025-09-15"
}
```

---

## 🔮 Future Enhancements

### Completed in v2.0 ✅
- [x] Company seat allocation with ranking
- [x] Student profile temporal tracking (semester 5-8)
- [x] ML-based success probability prediction
- [x] Credibility penalty bug fix (quality > quantity)
- [x] Bias & fairness auditing

### Phase 3 (Planned)
- [ ] Company analysis dashboard (7th page)
- [ ] Student profile editing
- [ ] Batch job matching (match all students to all jobs)
- [ ] Excel/CSV import for real student data
- [ ] Email notification system
- [ ] LangChain integration for semantic skill matching
- [ ] ChromaDB vector store for skill embeddings
- [ ] PostgreSQL for production deployment
- [ ] Resume PDF parsing (extract skills, projects, GitHub)
- [ ] Interview scheduling automation

---

## 📝 Example Usage

### Python API

```python
from data_engine import load_from_json
from intelligence import (
    calculate_credibility,
    calculate_risk,
    match_student_to_job,
    generate_student_explanation
)

# Load data
students, companies, logs = load_from_json()

# Select student and company
student = students[0]
company = companies[0]

# Calculate credibility
cred = calculate_credibility(student)
print(f"Credibility: {cred.level} ({cred.score:.2f})")
print(f"Red flags: {cred.red_flags}")

# Calculate risk
risk = calculate_risk(student, company, logs, cred)
print(f"Risk: {risk.risk_level} (Score: {risk.risk_score}/10)")
print(f"Factors: {risk.factors}")

# Match
match = match_student_to_job(student, company, logs)
print(f"Decision: {match.decision}")
print(f"Match Score: {match.match_score}")

# Generate explanation
explanation = generate_student_explanation(
    student, company, cred, risk, match.decision, match.failure_reason
)
print(explanation)
```

### Dashboard Usage

1. **Run app**: `streamlit run app.py`
2. **Navigate**: Use sidebar radio buttons
3. **Credibility Dashboard**: See which students have skill inflation
4. **Fake Skill Detection**: Export CSV report for placement cell review
5. **Risk Assessment**: Select company → see risky students
6. **Student Analysis**: Select student → see all job matches

---

## ⚠️ Important Notes

1. **Hard constraints are STRICT**: CGPA < min → Score = 0 (no exceptions)
2. **Credibility penalty is REAL**: LOW credibility → 40% score reduction
3. **Risk matters**: HIGH risk + score < 0.7 → Automatic rejection
4. **Evidence is VALIDATED**: GitHub, projects, certifications checked
5. **Explainability first**: Every decision has student + officer explanations

---

## 🤝 Contributing

This is a production-ready prototype. Key areas for contribution:
- Improve credibility algorithm (weight tuning)
- Add more company types (consulting, analytics, core engineering)
- Enhance dashboard visualizations
- Integrate with real college placement portals

---

## 📄 License

This project is for educational and research purposes.

---

## 📧 Contact

**GitHub Repository**: [soulrahulrk/college-placement-intelligence](https://github.com/soulrahulrk/college-placement-intelligence)

For questions, issues, or feature requests, please open a GitHub issue.

---

**Built with ❤️ for better, fairer, and more transparent college placements**

**No assumptions. No shortcuts. Just working logic.**
