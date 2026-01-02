# College Placement Intelligence Agent

A sophisticated Multi-Agent System for optimizing college placement decisions using semantic reasoning, hard constraints, and explainable AI.

## 🎯 Overview

This system uses advanced matching algorithms to connect students with the best job opportunities based on:
- **Hard Constraints**: GPA, backlogs, and experience requirements
- **Skill Matching**: Semantic analysis of must-have and good-to-have skills
- **Proficiency Depth**: Evidence-based skill scoring (GitHub, certifications, projects)
- **Feedback Loop**: Historical data analysis for continuous improvement

## 🏗️ Architecture

### Tech Stack
- **Python 3.10+**
- **Pydantic**: Data validation and schema enforcement
- **Streamlit**: Interactive web dashboard
- **Plotly**: Advanced visualizations
- **Faker**: Synthetic data generation

### Core Components

1. **Data Engine** (`data_engine.py`)
   - Pydantic models for Students, Jobs, and Placement Logs
   - Synthetic data generator with realistic distributions
   - JSON storage for quick prototyping

2. **Intelligence Core** (`intelligence.py`)
   - Proficiency calculation algorithm
   - Hybrid matching engine with configurable weights
   - Feedback loop for weight optimization
   - Batch processing capabilities

3. **Streamlit Dashboard** (`app.py`)
   - Job-based student ranking
   - Student-based job recommendations
   - Analytics dashboard
   - Feedback loop visualization

## 🚀 Quick Start

### Installation

```bash
# Clone or navigate to the project directory
cd "placement llm"

# Install dependencies
pip install -r requirements.txt
```

### Generate Synthetic Data

```bash
# Generate 30 students, 10 jobs, and 50 placement logs
python data_engine.py
```

This creates:
- `students.json`: 30 diverse student profiles
- `jobs.json`: 10 varied job descriptions
- `logs.json`: 50 historical placement records

### Run the Dashboard

```bash
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`

## 📊 Features

### 1. Job-Based Matching
- Select a company/job
- View all students ranked by match score
- Color-coded recommendations:
  - 🟢 Green: Highly Recommended
  - 🔵 Blue: Recommended
  - 🟡 Yellow: Marginal
  - 🔴 Red: Hard Constraint Failures

### 2. Student-Based Recommendations
- Select a student
- See their best job matches
- View skill proficiency breakdowns
- Understand why each job is recommended/rejected

### 3. Analytics Dashboard
- Overall placement success rates
- Top rejection reasons
- Company-wise performance
- Student distribution analysis

### 4. Feedback Loop
- Historical data analysis
- Company-specific weight adjustments
- Insight generation

## 🧮 Matching Algorithm

### Formula

```
Score = 0 if Hard Constraint Failed
Score = (0.5 × Must_Have_Match) + (0.3 × Good_To_Have_Match) + (0.2 × Proficiency_Depth)
```

### Hard Constraints (Strict 0 if Failed)
1. GPA ≥ Minimum Required
2. Backlogs ≤ Maximum Allowed
3. Experience ≥ Minimum Required

### Skill Matching
- **Must-Have Skills**: 50% weight (critical for role)
- **Good-To-Have Skills**: 30% weight (preferred but not mandatory)
- **Proficiency Depth**: 20% weight (average proficiency of matched skills)

### Proficiency Scoring (0-10 scale)
- **8-10**: GitHub projects, certifications, production code
- **6-9**: Internships, professional projects
- **5-7**: University projects
- **3-5**: Listed in resume without evidence
- **0**: Not mentioned

## 📁 Project Structure

```
placement llm/
│
├── data_engine.py          # Data models and synthetic generation
├── intelligence.py         # Matching algorithms and logic
├── app.py                 # Streamlit dashboard
├── requirements.txt       # Python dependencies
├── README.md             # This file
│
├── students.json         # Generated student data
├── jobs.json            # Generated job data
└── logs.json            # Generated placement history
```

## 🧪 Testing

### Test Data Engine
```bash
python data_engine.py
```

### Test Intelligence Engine
```bash
python intelligence.py
```

### Test Dashboard
```bash
streamlit run app.py
```

## 💡 Key Design Decisions

### 1. Why Pydantic?
- Strong type validation
- Automatic data serialization
- Self-documenting schemas

### 2. Why Synthetic Data?
- Immediate testing without real student data
- Privacy-preserving development
- Controlled test scenarios (star students, at-risk students)

### 3. Why Hard Constraints?
- Reflects real-world placement policies
- Prevents false positives
- Ensures explainability

### 4. Why Evidence-Based Proficiency?
- Goes beyond keyword matching
- Values demonstrated competence
- Reduces resume inflation bias

## 🔮 Future Enhancements

### Phase 2 (Planned)
- [ ] LangChain integration for semantic matching
- [ ] ChromaDB vector store for skill embeddings
- [ ] PostgreSQL for production data storage
- [ ] Resume parsing agent
- [ ] Job description parsing agent

### Phase 3 (Advanced)
- [ ] Multi-agent orchestration
- [ ] Natural language explanations
- [ ] Cultural fit analysis
- [ ] Interview scheduling automation
- [ ] Real-time feedback integration

## 📝 Example Usage

```python
from data_engine import load_from_json
from intelligence import match_student_to_job

# Load data
students, jobs, logs = load_from_json()

# Match first student to first job
result = match_student_to_job(students[0], jobs[0])

print(f"Score: {result.score}/10")
print(f"Status: {result.status}")
print(f"Reason: {result.detailed_reason}")
```

## 🎓 Student Distribution

The synthetic data generator creates:
- **30% Star Students**: GPA > 8.5, No backlogs, High proficiency
- **50% Average Students**: GPA 7.0-8.5, Occasional backlogs
- **20% At-Risk Students**: GPA < 7.0 or Multiple backlogs (but can have good skills!)

## 🏢 Company Types

- **MNCs**: Strict GPA (7.5+), No backlogs
- **Startups**: Lenient GPA (6.0+), Skill-focused
- **Service Companies**: Moderate requirements
- **Product Companies**: Balanced approach

## ⚠️ Important Notes

1. **Hard Constraints are STRICT**: If GPA < minimum, score = 0 (no exceptions)
2. **Explainability First**: Every match has a detailed reason
3. **Evidence Matters**: Skills with proof (GitHub, certs) score higher
4. **No Simple Keyword Matching**: Uses semantic reasoning

## 🤝 Contributing

This is a prototype system. Key areas for contribution:
- Improving matching algorithms
- Adding more company types
- Enhancing visualization
- Integrating real data sources

## 📄 License

This project is for educational purposes.

## 📧 Contact

For questions or suggestions, please open an issue.

---

**Built with ❤️ for better college placements**
