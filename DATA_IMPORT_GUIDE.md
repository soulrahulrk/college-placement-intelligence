# Data Import Guide

## 📥 How to Import Student & Company Data

The Placement Intelligence System now supports **bulk data import** via Excel/CSV files. This is perfect for placement officers who want to import real student and company data.

---

## Quick Start

### Step 1: Run the Dashboard
```bash
streamlit run app.py
```

### Step 2: Navigate to Data Import
- Click **"📥 Data Import"** in the sidebar
- You'll see 3 tabs: Import Students, Import Companies, Download Templates

### Step 3: Download Templates
1. Go to the **"📄 Download Templates"** tab
2. Download **Student Template.xlsx** or **Company Template.xlsx**
3. Open the template in Excel/Google Sheets

### Step 4: Fill Your Data
- Keep the same column headers
- Follow the format examples
- See format specifications below

### Step 5: Upload & Import
1. Go to **"📚 Import Students"** or **"🏢 Import Companies"** tab
2. Upload your filled Excel/CSV file
3. Preview the data
4. Click **"✅ Validate & Import"**
5. System validates and saves to JSON files

---

## Student Data Format

### Required Columns

| Column | Type | Range/Format | Example |
|--------|------|--------------|---------|
| `student_id` | String | Unique ID | S001, S002 |
| `name` | String | Full name | Rahul Kumar |
| `branch` | String | CSE/IT/AI/ECE/ME | CSE |
| `cgpa` | Float | 5.0 to 9.8 | 8.5 |
| `active_backlogs` | Integer | 0 to 5 | 0 |
| `communication_score` | Integer | 1 to 10 | 8 |
| `mock_interview_score` | Integer | 1 to 10 | 7 |
| `email` | String | Email address | rahul@college.edu |
| `phone` | String | Phone number | +91-9876543210 |
| `skills` | String | Special format (see below) | Python:advanced:github=True,projects=3... |

### Skills Format

**Format:** `SkillName:level:github=bool,projects=int,certifications=int,internship=bool`

**Multiple skills:** Separate with `|` (pipe symbol)

**Example:**
```
Python:advanced:github=True,projects=3,certifications=2,internship=True|DSA:intermediate:github=True,projects=2,certifications=1,internship=False
```

**Skill Levels:** beginner, intermediate, advanced

**Evidence Fields:**
- `github`: True/False (has GitHub repos for this skill)
- `projects`: 0-5 (number of projects)
- `certifications`: 0-3 (number of certifications)
- `internship`: True/False (has internship experience)

---

## Company Data Format

### Required Columns

| Column | Type | Range/Format | Example |
|--------|------|--------------|---------|
| `company_id` | String | Unique ID | C001, C002 |
| `company_name` | String | Company name | TCS, Infosys |
| `company_type` | String | MNC/Startup/Product/Service | MNC |
| `role` | String | Job title | Software Engineer |
| `open_positions` | Integer | 1 to 50 | 5 |
| `min_cgpa` | Float | 6.0 to 8.5 | 7.5 |
| `max_backlogs` | Integer | 0 to 2 | 0 |
| `mandatory_skills` | String | Comma-separated | DSA,Python |
| `preferred_skills` | String | Comma-separated | Git,Docker |
| `gpa_weight` | Float | 0.2 to 0.5 | 0.3 |
| `skill_weight` | Float | 0.3 to 0.6 | 0.4 |
| `communication_weight` | Float | 0.1 to 0.3 | 0.2 |
| `mock_interview_weight` | Float | 0.0 to 0.2 | 0.1 |
| `risk_tolerance` | String | low/medium/high | low |

### Weight Policy Rules

**Weights must sum to approximately 1.0:**
- GPA weight: 0.2 to 0.5
- Skill weight: 0.3 to 0.6 (most important for tech roles)
- Communication weight: 0.1 to 0.3
- Mock interview weight: 0.0 to 0.2

**Example:** 0.3 + 0.4 + 0.2 + 0.1 = 1.0 ✅

---

## Sample Excel Templates

### Student Template (student_template.xlsx)

```
| student_id | name          | branch | cgpa | active_backlogs | communication_score | mock_interview_score | email                | phone            | skills |
|------------|---------------|--------|------|-----------------|---------------------|---------------------|---------------------|-----------------|--------|
| S999       | Rahul Kumar   | CSE    | 8.5  | 0               | 8                   | 7                   | rahul@college.edu   | +91-9876543210  | Python:advanced:github=True,projects=3,certifications=2,internship=True|DSA:intermediate:github=True,projects=2,certifications=1,internship=False |
| S998       | Priya Sharma  | IT     | 7.8  | 1               | 7                   | 6                   | priya@college.edu   | +91-9876543211  | Java:intermediate:github=True,projects=2,certifications=1,internship=False|React:beginner:github=False,projects=1,certifications=0,internship=False |
```

### Company Template (company_template.xlsx)

```
| company_id | company_name     | company_type | role                    | open_positions | min_cgpa | max_backlogs | mandatory_skills | preferred_skills | gpa_weight | skill_weight | communication_weight | mock_interview_weight | risk_tolerance |
|------------|------------------|--------------|------------------------|----------------|----------|--------------|------------------|------------------|------------|--------------|---------------------|----------------------|----------------|
| C999       | TechCorp India   | MNC          | Software Engineer       | 5              | 7.5      | 0            | DSA,Python       | Git,Docker       | 0.3        | 0.4          | 0.2                 | 0.1                  | low            |
| C998       | InnoSoft         | Startup      | Full Stack Developer    | 3              | 7.0      | 1            | JavaScript,React | Node.js,MongoDB  | 0.25       | 0.5          | 0.15                | 0.1                  | medium         |
```

---

## Validation & Error Handling

### What Gets Validated?

✅ **Required Columns:** All required columns must be present  
✅ **Data Types:** CGPA must be float, backlogs must be integer, etc.  
✅ **Ranges:** CGPA between 5.0-9.8, communication 1-10, etc.  
✅ **Skills Format:** Validates skill parsing (SkillName:level:evidence)  
✅ **Pydantic Models:** Full validation against StudentProfile/JobDescription models

### Error Messages

If validation fails, you'll see:
```
⚠️ Row 3: CGPA must be between 5.0 and 9.8
⚠️ Row 5: Invalid skill format - missing evidence field
⚠️ Row 8: Communication score must be between 1 and 10
```

**Tip:** Fix errors in your Excel file and re-upload

---

## After Import

### What Happens?

1. **Validation:** System validates all rows using Pydantic models
2. **Appending:** New data is **appended** to existing students.json/jobs.json
3. **Saving:** Updated JSON files are saved
4. **Summary:** Shows metrics (students added, avg CGPA, credibility distribution)

### Viewing Imported Data

**Refresh the page** to see your imported data in:
- 🏠 Overview Dashboard
- 👤 Student Analysis
- 🎯 Credibility Dashboard
- ⚠️ Risk Assessment

---

## Tips & Best Practices

### 1. **Start with Templates**
- Always download templates first
- Don't change column headers
- Follow format examples exactly

### 2. **Test with Small Batches**
- Upload 2-3 students first to test
- Verify data appears correctly
- Then upload full dataset

### 3. **Skills Format is Critical**
```
✅ CORRECT: Python:advanced:github=True,projects=3,certifications=2,internship=True
❌ WRONG: Python, Advanced, GitHub
❌ WRONG: Python:advanced (missing evidence)
```

### 4. **Use CSV for Large Datasets**
- Excel has row limits (~1 million)
- CSV files are faster to process
- Both formats supported

### 5. **Validate Before Upload**
- Check CGPA ranges (5.0-9.8)
- Verify branch names (CSE/IT/AI/ECE/ME)
- Ensure weights sum to ~1.0

---

## Troubleshooting

### "Missing required columns"
**Fix:** Ensure all column headers match the template exactly (case-sensitive)

### "Invalid skill format"
**Fix:** Follow format: `SkillName:level:github=bool,projects=int,certifications=int,internship=bool`

### "CGPA must be between 5.0 and 9.8"
**Fix:** Check for typos (e.g., 85 instead of 8.5)

### "No data visible after import"
**Fix:** Refresh the page (Streamlit caches data)

### "Weights don't sum to 1.0"
**Fix:** Ensure gpa_weight + skill_weight + communication_weight + mock_interview_weight ≈ 1.0

---

## Advanced Features

### Bulk Import
- Upload 100+ students at once
- Upload 20+ companies at once
- System validates each row individually

### Data Merging
- New data is **appended** to existing data
- Duplicate IDs will create duplicate entries (be careful!)
- Consider unique student_id/company_id values

### Resume Trust Score
- Student `resume_trust_score` is initially set to 0.5
- System recalculates based on skill evidence after import
- View in Credibility Dashboard

---

## Support

For issues or questions:
- Check format examples in templates
- Verify all required columns are present
- Ensure data types match specifications
- Check validation error messages

**GitHub:** [soulrahulrk/college-placement-intelligence](https://github.com/soulrahulrk/college-placement-intelligence)

---

**Built with ❤️ for better, fairer, and more transparent college placements**
