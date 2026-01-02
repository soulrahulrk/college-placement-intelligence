"""
Intelligence Core for College Placement Intelligence Agent
Realistic Indian Placement Cell Decision System

ROLE & MINDSET:
Senior placement-analytics engineer solving real placement problems.
Focus: Resume credibility, Risk assessment, Explainable decisions.
No assumptions. No shortcuts. Just working logic.
"""

from typing import List, Dict, Tuple, Optional
from data_engine import StudentProfile, JobDescription, PlacementLog, Skill
from collections import defaultdict
import math


# ==================== RESUME CREDIBILITY CHECKER ====================

class CredibilityResult:
    """Resume credibility analysis result"""
    def __init__(self, score: float, level: str, red_flags: List[str], strengths: List[str]):
        self.score = round(score, 2)
        self.level = level
        self.red_flags = red_flags
        self.strengths = strengths
    
    def to_dict(self) -> Dict:
        return {
            "score": self.score,
            "level": self.level,
            "red_flags": self.red_flags,
            "strengths": self.strengths
        }


def calculate_credibility(student: StudentProfile) -> CredibilityResult:
    """
    Calculate resume credibility based on evidence
    
    Returns CredibilityResult with score (0-1), level (LOW/MEDIUM/HIGH)
    """
    if not student.skills:
        return CredibilityResult(0.5, "MEDIUM", ["No skills listed"], [])
    
    evidence_count = 0
    total_skills = len(student.skills)
    inflation_penalty = 0
    red_flags = []
    strengths = []
    
    github_count = 0
    advanced_no_proof = 0
    strong_evidence = 0
    
    for skill in student.skills:
        skill_evidence = 0
        
        # Calculate evidence score
        if skill.evidence.github:
            skill_evidence += 0.4
            github_count += 1
        if skill.evidence.projects > 0:
            skill_evidence += 0.3 * (skill.evidence.projects / 5)
        if skill.evidence.certifications > 0:
            skill_evidence += 0.2 * (skill.evidence.certifications / 3)
        if skill.evidence.internship:
            skill_evidence += 0.3
        
        # Check for skill inflation
        if skill.claimed_level == "advanced":
            if not (skill.evidence.github or skill.evidence.projects >= 2):
                inflation_penalty += 0.3
                advanced_no_proof += 1
                red_flags.append(f"{skill.name}: Claimed 'advanced' but no GitHub/projects")
        
        if skill_evidence >= 0.8:
            strong_evidence += 1
        
        evidence_count += min(1.0, skill_evidence)
    
    # Calculate final score
    base_score = evidence_count / total_skills
    final_score = max(0.0, min(1.0, base_score - inflation_penalty))
    
    # Determine level
    if final_score >= 0.7:
        level = "HIGH"
    elif final_score >= 0.4:
        level = "MEDIUM"
    else:
        level = "LOW"
    
    # Identify strengths
    if github_count >= 3:
        strengths.append(f"{github_count} skills backed by GitHub")
    if strong_evidence >= 2:
        strengths.append(f"{strong_evidence} skills with strong evidence")
    if student.resume_trust_score >= 0.7:
        strengths.append("High overall trust score")
    
    # Additional red flags
    if advanced_no_proof >= 3:
        red_flags.append(f"{advanced_no_proof} advanced claims without proof - MAJOR INFLATION")
    if final_score < 0.3:
        red_flags.append("Critically low credibility - High risk candidate")
    
    return CredibilityResult(final_score, level, red_flags, strengths)


# ==================== RISK ASSESSMENT ENGINE ====================

class RiskResult:
    """Risk assessment result"""
    def __init__(self, risk_level: str, risk_score: int, factors: List[str]):
        self.risk_level = risk_level
        self.risk_score = risk_score
        self.factors = factors
    
    def to_dict(self) -> Dict:
        return {
            "risk_level": self.risk_level,
            "risk_score": self.risk_score,
            "factors": self.factors
        }


def calculate_risk(
    student: StudentProfile,
    company: JobDescription,
    placement_logs: List[PlacementLog],
    credibility: CredibilityResult
) -> RiskResult:
    """
    Calculate placement risk based on historical patterns
    
    Returns: RiskResult with level (LOW/MEDIUM/HIGH) and contributing factors
    """
    risk_score = 0
    factors = []
    
    # 1. Historical pattern analysis
    similar_failures = count_similar_profile_failures(
        student, company, placement_logs
    )
    
    if similar_failures >= 3:
        risk_score += 4
        factors.append(f"Similar profiles failed {similar_failures} times at this company")
    elif similar_failures >= 1:
        risk_score += 2
        factors.append(f"Similar profiles failed {similar_failures} time(s)")
    
    # 2. Resume credibility check
    if credibility.level == "LOW":
        risk_score += 3
        factors.append(f"Low resume credibility ({credibility.score:.2f}) - Skill inflation detected")
    elif credibility.level == "MEDIUM":
        risk_score += 1
        factors.append(f"Medium resume credibility ({credibility.score:.2f})")
    
    # 3. Communication gap analysis
    company_avg_comm = get_avg_communication_for_company(placement_logs, company.company_id)
    
    if company_avg_comm > 0:  # If we have historical data
        if student.communication_score < company_avg_comm - 2:
            risk_score += 2
            factors.append(
                f"Communication score ({student.communication_score}/10) below company average ({company_avg_comm:.1f}/10)"
            )
        elif student.communication_score < 5:
            risk_score += 1
            factors.append(f"Low communication score: {student.communication_score}/10")
    else:
        # No historical data, use absolute threshold
        if student.communication_score < 5:
            risk_score += 2
            factors.append(f"Low communication score: {student.communication_score}/10")
    
    # 4. Mock interview performance
    if student.mock_interview_score < 5:
        risk_score += 1
        factors.append(f"Poor mock interview performance: {student.mock_interview_score}/10")
    
    # 5. Company risk tolerance
    if company.risk_tolerance == "low":
        # Strict companies are less forgiving
        if risk_score >= 3:
            risk_score += 1
            factors.append("Company has LOW risk tolerance - stricter evaluation")
    
    # Final classification
    if risk_score >= 6:
        risk_level = "HIGH"
    elif risk_score >= 3:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    
    return RiskResult(risk_level, risk_score, factors)


def count_similar_profile_failures(
    student: StudentProfile,
    company: JobDescription,
    logs: List[PlacementLog]
) -> int:
    """Count failures of similar student profiles at this company"""
    
    # Load student map for lookup
    from data_engine import load_from_json
    try:
        students, _, _ = load_from_json()
        student_map = {s.student_id: s for s in students}
    except:
        return 0
    
    failures = 0
    
    for log in logs:
        if log.company_id != company.company_id:
            continue
        
        if log.interview_result != "selected" and log.student_id in student_map:
            other = student_map[log.student_id]
            
            # Check similarity (same branch, similar CGPA range, similar communication)
            same_branch = other.branch == student.branch
            similar_cgpa = abs(other.cgpa - student.cgpa) < 1.0
            similar_comm = abs(other.communication_score - student.communication_score) < 2
            
            if same_branch and similar_cgpa and similar_comm:
                failures += 1
    
    return failures


def get_avg_communication_for_company(logs: List[PlacementLog], company_id: str) -> float:
    """Get average communication score for selected candidates at this company"""
    from data_engine import load_from_json
    try:
        students, _, _ = load_from_json()
        student_map = {s.student_id: s for s in students}
    except:
        return 0
    
    selected_logs = [
        log for log in logs 
        if log.company_id == company_id and log.interview_result == "selected"
    ]
    
    if not selected_logs:
        return 0
    
    comm_scores = [
        student_map[log.student_id].communication_score 
        for log in selected_logs 
        if log.student_id in student_map
    ]
    
    return sum(comm_scores) / len(comm_scores) if comm_scores else 0



# ==================== EXPLAINABILITY SYSTEM ====================

def generate_student_explanation(
    student: StudentProfile,
    company: JobDescription,
    credibility: CredibilityResult,
    risk: RiskResult,
    decision: str,
    failure_reason: Optional[str] = None
) -> str:
    """
    Generate student-friendly explanation for placement decision
    
    Args:
        decision: 'selected', 'shortlisted', or 'rejected'
    """
    if decision == "selected":
        return f""" Congratulations {student.name}!

You have been SELECTED for {company.role} at {company.company_name}.

Why you were selected:
 Strong resume credibility: {credibility.level} ({credibility.score:.2f})
 Low placement risk: {risk.risk_level}
{' ' + chr(10).join('  ' + s for s in credibility.strengths) if credibility.strengths else ''}

Next steps: HR will contact you within 48 hours for offer details.
"""
    
    elif decision == "shortlisted":
        return f""" Good news {student.name}!

You are SHORTLISTED for {company.role} at {company.company_name}.

Your profile:
 Resume credibility: {credibility.level} ({credibility.score:.2f})
 Placement risk: {risk.risk_level}

Next steps: Prepare for technical interview. Check your email for schedule.
"""
    
    else:  # rejected
        reason_msg = ""
        if failure_reason:
            reason_map = {
                "cgpa": "Your CGPA does not meet the minimum requirement",
                "low_dsa": "DSA skill level needs improvement",
                "fake_skill": "Resume credibility concerns - some skills lack supporting evidence",
                "poor_communication": "Communication skills need development",
                "failed_interview": "Interview performance below company standards"
            }
            reason_msg = reason_map.get(failure_reason, failure_reason)
        
        tips = []
        if credibility.red_flags:
            tips.append(" Resume credibility issues:")
            for flag in credibility.red_flags[:2]:  # Top 2 red flags
                tips.append(f"   {flag}")
        
        if risk.risk_level in ["MEDIUM", "HIGH"]:
            tips.append(f" Risk assessment: {risk.risk_level}")
            for factor in risk.factors[:2]:  # Top 2 factors
                tips.append(f"   {factor}")
        
        return f"""Thank you for applying, {student.name}.

Unfortunately, we are unable to move forward with your application for {company.role} at {company.company_name}.

Reason: {reason_msg}

Areas for improvement:
{chr(10).join(tips) if tips else ' Focus on building strong project portfolio with GitHub repos'}
 Improve communication skills through mock interviews
 Earn certifications to validate your technical skills

Don't give up! Use this feedback to strengthen your profile for future opportunities.
"""


def generate_officer_explanation(
    student: StudentProfile,
    company: JobDescription,
    credibility: CredibilityResult,
    risk: RiskResult,
    decision: str,
    failure_reason: Optional[str] = None
) -> str:
    """
    Generate detailed placement officer report
    
    Provides full analysis for placement cell decision-making
    """
    report = f"""
=== PLACEMENT OFFICER ANALYSIS ===
Student: {student.name} ({student.student_id})
Company: {company.company_name} - {company.role}
Decision: {decision.upper()}
{'Failure Reason: ' + failure_reason if failure_reason else ''}

--- RESUME CREDIBILITY ANALYSIS ---
Score: {credibility.score:.2f} / 1.00
Level: {credibility.level}

Red Flags ({len(credibility.red_flags)}):
{chr(10).join('   ' + flag for flag in credibility.red_flags) if credibility.red_flags else '  None'}

Strengths ({len(credibility.strengths)}):
{chr(10).join('   ' + strength for strength in credibility.strengths) if credibility.strengths else '  None'}

--- RISK ASSESSMENT ---
Risk Level: {risk.risk_level}
Risk Score: {risk.risk_score}/10

Contributing Factors:
{chr(10).join('   ' + factor for factor in risk.factors) if risk.factors else '  None'}

--- STUDENT PROFILE SUMMARY ---
Branch: {student.branch}
CGPA: {student.cgpa}
Communication Score: {student.communication_score}/10
Mock Interview Score: {student.mock_interview_score}/10
Resume Trust Score: {student.resume_trust_score:.2f}

Skills ({len(student.skills)}):
"""
    
    # Add skill breakdown
    for skill in student.skills[:5]:  # Top 5 skills
        evidence_str = []
        if skill.evidence.github:
            evidence_str.append("GitHub")
        if skill.evidence.projects > 0:
            evidence_str.append(f"{skill.evidence.projects} projects")
        if skill.evidence.certifications > 0:
            evidence_str.append(f"{skill.evidence.certifications} certs")
        if skill.evidence.internship:
            evidence_str.append("Internship")
        
        evidence_display = ", ".join(evidence_str) if evidence_str else "NO EVIDENCE"
        report += f"   {skill.name} ({skill.claimed_level}): {evidence_display}\n"
    
    report += f"\n--- COMPANY REQUIREMENTS ---\n"
    report += f"Risk Tolerance: {company.risk_tolerance.upper()}\n"
    report += f"Min CGPA: {company.eligibility_rules.min_cgpa}\n"
    report += f"Required Skills: {', '.join(company.eligibility_rules.mandatory_skills)}\n"
    
    report += f"\n--- RECOMMENDATION ---\n"
    if decision == "selected":
        report += " APPROVED - Strong candidate with verified credentials\n"
    elif decision == "shortlisted":
        report += " SHORTLISTED - Proceed with caution, monitor interview performance\n"
    else:
        report += " REJECTED - Does not meet criteria or high risk of failure\n"
    
    return report


# ==================== ENHANCED MATCHING ENGINE ====================

class MatchResult:
    """Enhanced matching result with credibility and risk"""
    def __init__(
        self,
        student_id: str,
        company_id: str,
        match_score: float,
        decision: str,
        credibility: CredibilityResult,
        risk: RiskResult,
        failure_reason: Optional[str] = None
    ):
        self.student_id = student_id
        self.company_id = company_id
        self.match_score = round(match_score, 2)
        self.decision = decision
        self.credibility = credibility
        self.risk = risk
        self.failure_reason = failure_reason
    
    def to_dict(self) -> Dict:
        return {
            "student_id": self.student_id,
            "company_id": self.company_id,
            "match_score": self.match_score,
            "decision": self.decision,
            "credibility": self.credibility.to_dict(),
            "risk": self.risk.to_dict(),
            "failure_reason": self.failure_reason
        }


def match_student_to_job(
    student: StudentProfile,
    company: JobDescription,
    placement_logs: List[PlacementLog],
    apply_credibility_penalty: bool = True
) -> MatchResult:
    """
    Enhanced matching with credibility and risk assessment
    
    Returns: MatchResult with decision (selected/shortlisted/rejected)
    """
    
    # Step 1: Calculate credibility
    credibility = calculate_credibility(student)
    
    # Step 2: Calculate risk
    risk = calculate_risk(student, company, placement_logs, credibility)
    
    # Step 3: Check basic eligibility
    if student.cgpa < company.eligibility_rules.min_cgpa:
        return MatchResult(
            student.student_id,
            company.company_id,
            0.0,
            "rejected",
            credibility,
            risk,
            "cgpa"
        )
    
    # Check backlogs
    if student.active_backlogs > company.eligibility_rules.max_backlogs:
        return MatchResult(
            student.student_id,
            company.company_id,
            0.0,
            "rejected",
            credibility,
            risk,
            "backlogs"
        )
    
    # Step 4: Calculate skill match score
    student_skill_names = {s.name.lower() for s in student.skills}
    required_skills_met = sum(
        1 for req_skill in company.eligibility_rules.mandatory_skills
        if req_skill.lower() in student_skill_names
    )
    
    total_required = len(company.eligibility_rules.mandatory_skills)
    skill_match_ratio = required_skills_met / total_required if total_required > 0 else 0
    
    # Check DSA requirement for tech roles
    has_dsa = any(
        "dsa" in s.name.lower() or "algorithm" in s.name.lower()
        for s in student.skills
    )
    
    if "software" in company.role.lower() or "developer" in company.role.lower():
        if not has_dsa:
            return MatchResult(
                student.student_id,
                company.company_id,
                0.0,
                "rejected",
                credibility,
                risk,
                "low_dsa"
            )
    
    # Step 5: Apply weight policy
    weights = company.weight_policy
    
    base_score = (
        (student.cgpa / 10.0) * weights.gpa_weight +
        skill_match_ratio * weights.skill_weight +
        (student.communication_score / 10.0) * weights.communication_weight +
        (student.mock_interview_score / 10.0) * weights.mock_interview_weight
    )
    
    # Step 6: Apply credibility penalty
    final_score = base_score
    if apply_credibility_penalty:
        if credibility.level == "LOW":
            final_score *= 0.6  # 40% penalty
            if final_score < 0.5:
                return MatchResult(
                    student.student_id,
                    company.company_id,
                    final_score,
                    "rejected",
                    credibility,
                    risk,
                    "fake_skill"
                )
        elif credibility.level == "MEDIUM":
            final_score *= 0.85  # 15% penalty
    
    # Step 7: Risk-based decision
    if risk.risk_level == "HIGH":
        if final_score < 0.7:  # High bar for risky candidates
            return MatchResult(
                student.student_id,
                company.company_id,
                final_score,
                "rejected",
                credibility,
                risk,
                "failed_interview"
            )
        else:
            decision = "shortlisted"  # Even high scores get shortlisted if high risk
    elif risk.risk_level == "MEDIUM":
        decision = "shortlisted" if final_score >= 0.55 else "rejected"
        failure_reason = "poor_communication" if final_score < 0.55 else None
    else:  # LOW risk
        if final_score >= 0.7:
            decision = "selected"
        elif final_score >= 0.5:
            decision = "shortlisted"
        else:
            decision = "rejected"
        failure_reason = "failed_interview" if decision == "rejected" else None
    
    return MatchResult(
        student.student_id,
        company.company_id,
        final_score,
        decision,
        credibility,
        risk,
        failure_reason
    )


# ==================== FEEDBACK LEARNING SYSTEM ====================

def analyze_placement_outcomes(placement_logs: List[PlacementLog]) -> Dict:
    """
    Analyze placement outcomes to adjust weight policies
    
    Returns insights for continuous improvement
    """
    from data_engine import load_from_json
    students, companies, _ = load_from_json()
    student_map = {s.student_id: s for s in students}
    company_map = {c.company_id: c for c in companies}
    
    company_stats = defaultdict(lambda: {
        "total": 0, "selected": 0, "avg_cgpa": [], "avg_comm": []
    })
    
    for log in placement_logs:
        company_stats[log.company_id]["total"] += 1
        
        if log.interview_result == "selected" and log.student_id in student_map:
            company_stats[log.company_id]["selected"] += 1
            student = student_map[log.student_id]
            company_stats[log.company_id]["avg_cgpa"].append(student.cgpa)
            company_stats[log.company_id]["avg_comm"].append(student.communication_score)
    
    insights = {}
    for company_id, stats in company_stats.items():
        if company_id not in company_map:
            continue
        
        company = company_map[company_id]
        success_rate = stats["selected"] / stats["total"] if stats["total"] > 0 else 0
        
        insights[company.company_name] = {
            "success_rate": round(success_rate, 2),
            "total_applicants": stats["total"],
            "selected_count": stats["selected"],
            "avg_selected_cgpa": round(sum(stats["avg_cgpa"]) / len(stats["avg_cgpa"]), 2) if stats["avg_cgpa"] else 0,
            "avg_selected_communication": round(sum(stats["avg_comm"]) / len(stats["avg_comm"]), 2) if stats["avg_comm"] else 0,
            "recommendation": "Increase communication weight" if stats["avg_comm"] and sum(stats["avg_comm"]) / len(stats["avg_comm"]) > 7 else "Focus on CGPA screening"
        }
    
    return insights


if __name__ == "__main__":
    from data_engine import load_from_json, SyntheticDataGenerator, save_to_json
    
    # Generate sample data
    print("Generating sample placement data...")
    generator = SyntheticDataGenerator()
    students = generator.generate_students(50)
    companies = generator.generate_jobs(12)
    logs = generator.generate_placement_logs(students, companies, 120)
    save_to_json(students, companies, logs)
    
    print(f"\nGenerated {len(students)} students, {len(companies)} companies, {len(logs)} logs")
    
    print(f"\nLoaded {len(students)} students, {len(companies)} companies, {len(logs)} logs")
        # Load from JSON
    students, companies, logs = load_from_json()
        # Test credibility calculation
    print("\n=== CREDIBILITY TEST ===")
    test_student = students[0]
    cred = calculate_credibility(test_student)
    print(f"Student: {test_student.name}")
    print(f"Credibility: {cred.level} ({cred.score:.2f})")
    print(f"Red flags: {cred.red_flags}")
    print(f"Strengths: {cred.strengths}")
    
    # Test risk assessment
    print("\n=== RISK ASSESSMENT TEST ===")
    test_company = companies[0]
    risk = calculate_risk(test_student, test_company, logs, cred)
    print(f"Company: {test_company.company_name}")
    print(f"Risk: {risk.risk_level} (Score: {risk.risk_score}/10)")
    print(f"Factors: {risk.factors}")
    
    # Test matching
    print("\n=== MATCHING TEST ===")
    match = match_student_to_job(test_student, test_company, logs)
    print(f"Decision: {match.decision}")
    print(f"Match Score: {match.match_score}")
    print(f"Failure Reason: {match.failure_reason}")
    
    # Test explainability
    print("\n=== STUDENT EXPLANATION ===")
    student_msg = generate_student_explanation(
        test_student, test_company, cred, risk, match.decision, match.failure_reason
    )
    print(student_msg)
    
    print("\n=== OFFICER REPORT ===")
    officer_report = generate_officer_explanation(
        test_student, test_company, cred, risk, match.decision, match.failure_reason
    )
    print(officer_report)
    
    # Analyze outcomes
    print("\n=== PLACEMENT OUTCOME ANALYSIS ===")
    insights = analyze_placement_outcomes(logs)
    for company_name, data in list(insights.items())[:3]:
        print(f"\n{company_name}:")
        print(f"  Success Rate: {data['success_rate']*100:.1f}%")
        print(f"  Selected: {data['selected_count']}/{data['total_applicants']}")
        print(f"  Avg CGPA of selected: {data['avg_selected_cgpa']}")
        print(f"  Recommendation: {data['recommendation']}")
    
    print("\n Intelligence engine test complete!")
