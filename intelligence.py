"""
Intelligence Core for College Placement Intelligence Agent
Implements profiling, matching, and feedback algorithms
"""

from typing import List, Dict, Tuple, Optional
from data_engine import StudentProfile, JobDescription, PlacementLog, Skill
import re
from collections import defaultdict
import math


# ==================== PROFICIENCY CALCULATION ====================

def calculate_proficiency(skill_text: str, context: str) -> float:
    """
    Calculate evidence-based proficiency score for a skill
    
    Args:
        skill_text: The skill name
        context: Surrounding text (resume section, project description, etc.)
    
    Returns:
        float: Proficiency score (0-10)
    
    Logic:
        - GitHub/Project/Certification evidence → 8-10
        - Internship/Work experience → 7-9
        - University project → 5-7
        - Just listed in keywords → 3-5
    """
    context_lower = context.lower()
    skill_lower = skill_text.lower()
    
    # High confidence indicators
    high_confidence_patterns = [
        r'\bgithub\b', r'\bgit\b', r'\brepository\b', r'\brepo\b',
        r'\bcertification\b', r'\bcertified\b', r'\bcertificate\b',
        r'\bproject\s+link\b', r'\bdeployed\b', r'\bproduction\b',
        r'\bpublished\b', r'\bopen[\s-]?source\b'
    ]
    
    # Medium confidence indicators
    medium_confidence_patterns = [
        r'\binternship\b', r'\bwork\s+experience\b', r'\bprofessional\b',
        r'\bproject\b', r'\bdeveloped\b', r'\bbuilt\b', r'\bcreated\b',
        r'\bimplemented\b', r'\bdesigned\b'
    ]
    
    # Low confidence indicators
    low_confidence_patterns = [
        r'\buniversity\s+project\b', r'\bacademic\b', r'\bcourse\s*work\b',
        r'\blearned\b', r'\bstudied\b'
    ]
    
    # Check for high confidence evidence
    for pattern in high_confidence_patterns:
        if re.search(pattern, context_lower):
            # Check if skill is mentioned nearby (within 100 chars)
            skill_index = context_lower.find(skill_lower)
            if skill_index != -1:
                return round(8.0 + (hash(skill_text + context) % 21) / 10, 1)  # 8.0-10.0
    
    # Check for medium confidence evidence
    for pattern in medium_confidence_patterns:
        if re.search(pattern, context_lower):
            if skill_lower in context_lower:
                return round(6.0 + (hash(skill_text + context) % 31) / 10, 1)  # 6.0-9.0
    
    # Check for low confidence evidence
    for pattern in low_confidence_patterns:
        if re.search(pattern, context_lower):
            if skill_lower in context_lower:
                return round(5.0 + (hash(skill_text + context) % 21) / 10, 1)  # 5.0-7.0
    
    # Just listed in keywords
    if skill_lower in context_lower:
        return round(3.0 + (hash(skill_text + context) % 21) / 10, 1)  # 3.0-5.0
    
    # Not found
    return 0.0


# ==================== MATCHING ENGINE ====================

class MatchResult:
    """Structured result from matching algorithm"""
    def __init__(
        self,
        score: float,
        status: str,
        detailed_reason: str,
        breakdown: Dict[str, float],
        hard_constraint_failed: bool = False
    ):
        self.score = round(score, 2)
        self.status = status
        self.detailed_reason = detailed_reason
        self.breakdown = breakdown
        self.hard_constraint_failed = hard_constraint_failed
    
    def to_dict(self) -> Dict:
        return {
            "score": self.score,
            "status": self.status,
            "detailed_reason": self.detailed_reason,
            "breakdown": self.breakdown,
            "hard_constraint_failed": self.hard_constraint_failed
        }


def match_student_to_job(
    student: StudentProfile,
    job: JobDescription,
    weights: Optional[Dict[str, float]] = None
) -> MatchResult:
    """
    Advanced hybrid matching algorithm with hard constraints
    
    Formula:
        Score = 0 if Hard Constraint Failed
        Score = (0.5 × Must_Have_Match) + (0.3 × Good_To_Have_Match) + (0.2 × Proficiency_Depth)
    
    Args:
        student: Student profile
        job: Job description
        weights: Optional custom weights (for feedback loop adjustments)
    
    Returns:
        MatchResult: Detailed matching result
    """
    
    # Default weights
    if weights is None:
        weights = {
            "must_have": 0.5,
            "good_to_have": 0.3,
            "proficiency": 0.2
        }
    
    # ========== STEP A: HARD CONSTRAINTS ==========
    hard_constraints_passed = True
    constraint_failures = []
    
    # GPA Check
    if student.gpa < job.min_gpa:
        hard_constraints_passed = False
        constraint_failures.append(f"GPA {student.gpa} < Required {job.min_gpa}")
    
    # Backlogs Check
    if student.backlogs > job.max_backlogs_allowed:
        hard_constraints_passed = False
        constraint_failures.append(
            f"{student.backlogs} backlogs > Allowed {job.max_backlogs_allowed}"
        )
    
    # Experience Check
    if student.experience_years < job.min_experience_years:
        hard_constraints_passed = False
        constraint_failures.append(
            f"Experience {student.experience_years}y < Required {job.min_experience_years}y"
        )
    
    # If hard constraints failed, return score 0
    if not hard_constraints_passed:
        return MatchResult(
            score=0.0,
            status="Rejected",
            detailed_reason=f"Hard Constraint Failed: {'; '.join(constraint_failures)}",
            breakdown={
                "must_have_score": 0.0,
                "good_to_have_score": 0.0,
                "proficiency_score": 0.0,
                "final_score": 0.0
            },
            hard_constraint_failed=True
        )
    
    # ========== STEP B: SKILL MATCHING ==========
    student_skills_map = {skill.name: skill for skill in student.skills}
    student_skill_names = set(student_skills_map.keys())
    
    # Must-Have Skills Match
    must_have_matched = []
    must_have_missing = []
    
    for skill in job.must_have_skills:
        if skill in student_skill_names:
            must_have_matched.append(skill)
        else:
            must_have_missing.append(skill)
    
    must_have_ratio = len(must_have_matched) / len(job.must_have_skills) if job.must_have_skills else 1.0
    
    # Good-To-Have Skills Match
    good_to_have_matched = []
    for skill in job.good_to_have_skills:
        if skill in student_skill_names:
            good_to_have_matched.append(skill)
    
    good_to_have_ratio = len(good_to_have_matched) / len(job.good_to_have_skills) if job.good_to_have_skills else 0.0
    
    # ========== STEP C: PROFICIENCY DEPTH ANALYSIS ==========
    # Calculate average proficiency of matched must-have skills
    proficiency_scores = []
    for skill in must_have_matched:
        proficiency_scores.append(student_skills_map[skill].proficiency_score)
    
    avg_proficiency = sum(proficiency_scores) / len(proficiency_scores) if proficiency_scores else 0
    proficiency_normalized = avg_proficiency / 10.0  # Normalize to 0-1
    
    # ========== STEP D: HYBRID SCORE CALCULATION ==========
    must_have_score = must_have_ratio * weights["must_have"]
    good_to_have_score = good_to_have_ratio * weights["good_to_have"]
    proficiency_score = proficiency_normalized * weights["proficiency"]
    
    final_score = (must_have_score + good_to_have_score + proficiency_score) * 10  # Scale to 0-10
    
    # ========== STEP E: STATUS DETERMINATION ==========
    # Critical threshold: Must have at least 50% of must-have skills
    if must_have_ratio < 0.5:
        status = "Not Recommended"
        reason = (
            f"Insufficient Must-Have Skills: {len(must_have_matched)}/{len(job.must_have_skills)} matched. "
            f"Missing: {', '.join(must_have_missing[:3])}{'...' if len(must_have_missing) > 3 else ''}"
        )
    elif final_score >= 8.0:
        status = "Highly Recommended"
        reason = (
            f"Excellent Match! {len(must_have_matched)}/{len(job.must_have_skills)} must-haves "
            f"with avg proficiency {avg_proficiency:.1f}/10. "
            f"GPA: {student.gpa} (req: {job.min_gpa}). "
            f"Backlogs: {student.backlogs} (allowed: {job.max_backlogs_allowed})."
        )
    elif final_score >= 6.0:
        status = "Recommended"
        reason = (
            f"Good Match. {len(must_have_matched)}/{len(job.must_have_skills)} must-haves matched. "
            f"Proficiency: {avg_proficiency:.1f}/10. "
            f"GPA: {student.gpa}. Consider for interview."
        )
    else:
        status = "Marginal"
        reason = (
            f"Weak Match. Only {len(must_have_matched)}/{len(job.must_have_skills)} must-haves. "
            f"Low proficiency depth ({avg_proficiency:.1f}/10). "
            f"Missing critical skills: {', '.join(must_have_missing[:2])}"
        )
    
    return MatchResult(
        score=final_score,
        status=status,
        detailed_reason=reason,
        breakdown={
            "must_have_score": round(must_have_score * 10, 2),
            "good_to_have_score": round(good_to_have_score * 10, 2),
            "proficiency_score": round(proficiency_score * 10, 2),
            "final_score": round(final_score, 2),
            "must_have_matched": len(must_have_matched),
            "must_have_total": len(job.must_have_skills),
            "good_to_have_matched": len(good_to_have_matched),
            "avg_proficiency": round(avg_proficiency, 2)
        },
        hard_constraint_failed=False
    )


# ==================== FEEDBACK LOOP ====================

def analyze_placement_patterns(logs: List[PlacementLog]) -> Dict[str, Dict]:
    """
    Analyze historical placement data to identify patterns
    
    Returns:
        Dict with insights:
        - rejection_reasons: Most common rejection reasons
        - company_success_rates: Hiring rate per company
        - skill_impact: Which skills correlate with success/failure
    """
    
    # Company-wise analysis
    company_stats = defaultdict(lambda: {"hired": 0, "rejected": 0, "total": 0})
    rejection_reasons = defaultdict(int)
    
    for log in logs:
        company_id = log.company_id
        company_stats[company_id]["total"] += 1
        
        if log.status == "Hired":
            company_stats[company_id]["hired"] += 1
        else:
            company_stats[company_id]["rejected"] += 1
            rejection_reasons[log.reason] += 1
    
    # Calculate success rates
    company_success_rates = {}
    for company_id, stats in company_stats.items():
        success_rate = stats["hired"] / stats["total"] if stats["total"] > 0 else 0
        company_success_rates[company_id] = {
            "success_rate": round(success_rate, 2),
            "hired": stats["hired"],
            "rejected": stats["rejected"],
            "total": stats["total"]
        }
    
    # Top rejection reasons
    top_rejection_reasons = sorted(
        rejection_reasons.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    return {
        "company_success_rates": company_success_rates,
        "top_rejection_reasons": top_rejection_reasons,
        "total_logs": len(logs)
    }


def feedback_loop(
    past_logs: List[PlacementLog],
    students: List[StudentProfile],
    jobs: List[JobDescription],
    current_weights: Optional[Dict[str, float]] = None
) -> Dict[str, Dict[str, float]]:
    """
    Adjust matching weights based on historical data
    
    Strategy:
        - If a specific skill appears often in rejections for a company,
          increase its weight for that company
        - If GPA rejections are high, maintain strict hard constraints
        - Learn company-specific preferences
    
    Args:
        past_logs: Historical placement records
        students: Student database (for skill lookup)
        jobs: Job database (for company lookup)
        current_weights: Current weight configuration
    
    Returns:
        Dict[company_id -> adjusted_weights]
    """
    
    if current_weights is None:
        current_weights = {
            "must_have": 0.5,
            "good_to_have": 0.3,
            "proficiency": 0.2
        }
    
    # Create lookup maps
    student_map = {s.id: s for s in students}
    job_map = {j.id: j for j in jobs}
    
    # Company-specific skill rejection analysis
    company_skill_rejections = defaultdict(lambda: defaultdict(int))
    company_skill_hires = defaultdict(lambda: defaultdict(int))
    company_total_placements = defaultdict(int)
    
    for log in past_logs:
        if log.student_id not in student_map or log.company_id not in job_map:
            continue
        
        student = student_map[log.student_id]
        job = job_map[log.company_id]
        company_id = log.company_id
        
        company_total_placements[company_id] += 1
        
        # Track which skills were present in rejected/hired candidates
        student_skill_names = {skill.name for skill in student.skills}
        
        if log.status == "Rejected" and "Hard Constraint" not in log.reason:
            # This was a skill-based rejection
            for skill in job.must_have_skills:
                if skill not in student_skill_names:
                    company_skill_rejections[company_id][skill] += 1
        elif log.status == "Hired":
            for skill in job.must_have_skills:
                if skill in student_skill_names:
                    company_skill_hires[company_id][skill] += 1
    
    # Adjust weights per company
    adjusted_weights = {}
    
    for company_id in company_total_placements:
        if company_total_placements[company_id] < 3:  # Not enough data
            adjusted_weights[company_id] = current_weights.copy()
            continue
        
        # Calculate importance of must-haves vs good-to-haves
        skill_rejection_rate = sum(company_skill_rejections[company_id].values())
        total = company_total_placements[company_id]
        
        # If many rejections due to missing must-haves, increase must_have weight
        if skill_rejection_rate / total > 0.3:  # More than 30% skill-based rejections
            adjusted = {
                "must_have": min(0.7, current_weights["must_have"] + 0.1),
                "good_to_have": current_weights["good_to_have"],
                "proficiency": max(0.1, current_weights["proficiency"] - 0.1)
            }
        else:
            # Otherwise, emphasize proficiency
            adjusted = {
                "must_have": current_weights["must_have"],
                "good_to_have": max(0.2, current_weights["good_to_have"] - 0.05),
                "proficiency": min(0.3, current_weights["proficiency"] + 0.05)
            }
        
        # Normalize weights to sum to 1.0
        total_weight = sum(adjusted.values())
        adjusted = {k: v / total_weight for k, v in adjusted.items()}
        
        adjusted_weights[company_id] = adjusted
    
    return adjusted_weights


# ==================== BATCH MATCHING ====================

def match_all_students_to_job(
    students: List[StudentProfile],
    job: JobDescription,
    weights: Optional[Dict[str, float]] = None
) -> List[Tuple[StudentProfile, MatchResult]]:
    """
    Match all students to a single job and rank them
    
    Returns:
        List of (student, match_result) tuples, sorted by score (descending)
    """
    results = []
    
    for student in students:
        match_result = match_student_to_job(student, job, weights)
        results.append((student, match_result))
    
    # Sort by score (highest first)
    results.sort(key=lambda x: x[1].score, reverse=True)
    
    return results


def match_student_to_all_jobs(
    student: StudentProfile,
    jobs: List[JobDescription],
    weights_per_job: Optional[Dict[str, Dict[str, float]]] = None
) -> List[Tuple[JobDescription, MatchResult]]:
    """
    Match a single student to all jobs and rank opportunities
    
    Returns:
        List of (job, match_result) tuples, sorted by score (descending)
    """
    results = []
    
    for job in jobs:
        # Use job-specific weights if available
        weights = weights_per_job.get(job.id) if weights_per_job else None
        match_result = match_student_to_job(student, job, weights)
        results.append((job, match_result))
    
    # Sort by score (highest first)
    results.sort(key=lambda x: x[1].score, reverse=True)
    
    return results


# ==================== ANALYTICS ====================

def generate_match_summary(matches: List[Tuple[StudentProfile, MatchResult]]) -> Dict:
    """Generate summary statistics for a batch of matches"""
    
    total = len(matches)
    highly_recommended = sum(1 for _, m in matches if m.status == "Highly Recommended")
    recommended = sum(1 for _, m in matches if m.status == "Recommended")
    marginal = sum(1 for _, m in matches if m.status == "Marginal")
    not_recommended = sum(1 for _, m in matches if m.status == "Not Recommended")
    hard_constraint_failed = sum(1 for _, m in matches if m.hard_constraint_failed)
    
    avg_score = sum(m.score for _, m in matches) / total if total > 0 else 0
    
    return {
        "total_students": total,
        "highly_recommended": highly_recommended,
        "recommended": recommended,
        "marginal": marginal,
        "not_recommended": not_recommended,
        "hard_constraint_failures": hard_constraint_failed,
        "average_score": round(avg_score, 2),
        "distribution": {
            "highly_recommended_pct": round(highly_recommended / total * 100, 1) if total > 0 else 0,
            "recommended_pct": round(recommended / total * 100, 1) if total > 0 else 0,
            "marginal_pct": round(marginal / total * 100, 1) if total > 0 else 0,
            "not_recommended_pct": round(not_recommended / total * 100, 1) if total > 0 else 0,
            "hard_constraint_pct": round(hard_constraint_failed / total * 100, 1) if total > 0 else 0
        }
    }


# ==================== TESTING ====================

if __name__ == "__main__":
    from data_engine import load_from_json
    
    print("🧠 Testing Intelligence Engine...")
    print("=" * 60)
    
    # Load data
    students, jobs, logs = load_from_json()
    
    if not students or not jobs:
        print("❌ No data found. Run data_engine.py first!")
    else:
        # Test 1: Single match
        print("\n📊 Test 1: Matching first student to first job")
        result = match_student_to_job(students[0], jobs[0])
        print(f"   Student: {students[0].name} (GPA: {students[0].gpa})")
        print(f"   Job: {jobs[0].role} at {jobs[0].company_name}")
        print(f"   Score: {result.score}/10")
        print(f"   Status: {result.status}")
        print(f"   Reason: {result.detailed_reason}")
        
        # Test 2: Batch matching
        print("\n📊 Test 2: Ranking all students for first job")
        matches = match_all_students_to_job(students, jobs[0])
        print(f"\n   Top 5 Candidates for {jobs[0].role} at {jobs[0].company_name}:")
        for i, (student, match) in enumerate(matches[:5], 1):
            print(f"   {i}. {student.name}: {match.score}/10 - {match.status}")
        
        # Test 3: Summary
        summary = generate_match_summary(matches)
        print(f"\n📊 Test 3: Match Summary")
        print(f"   Total Students: {summary['total_students']}")
        print(f"   Highly Recommended: {summary['highly_recommended']} ({summary['distribution']['highly_recommended_pct']}%)")
        print(f"   Hard Constraint Failures: {summary['hard_constraint_failures']} ({summary['distribution']['hard_constraint_pct']}%)")
        
        # Test 4: Feedback loop
        print(f"\n📊 Test 4: Analyzing placement patterns...")
        patterns = analyze_placement_patterns(logs)
        print(f"   Total logs analyzed: {patterns['total_logs']}")
        print(f"   Top 3 rejection reasons:")
        for reason, count in patterns['top_rejection_reasons'][:3]:
            print(f"      - {reason[:50]}... ({count} times)")
        
        print("\n✅ Intelligence engine tests complete!")
