"""
UPGRADE MODULE - College Placement Intelligence System V2
Implements 5 critical upgrades for realistic placement simulation

UPGRADES:
1. Company Seat Allocation & Ranking
2. Profile Improvement & Temporal Drift  
3. Learning-Based Success Probability (Logistic Regression)
4. Credibility Penalty Bug Fix
5. Bias & Fairness Audit

Author: Senior Systems Engineer + Placement Analytics Consultant
"""

from typing import List, Dict, Optional, Tuple
from pydantic import BaseModel, Field
from collections import defaultdict
import random
import json
from datetime import datetime
import math

# ==================== UPGRADE 1: SEAT ALLOCATION MODELS ====================

class SeatAllocationResult:
    """Result of company seat allocation"""
    def __init__(
        self,
        company_id: str,
        company_name: str,
        open_positions: int,
        total_applicants: int,
        selected_students: List[Dict],
        waitlisted_students: List[Dict],
        rejected_students: List[Dict],
        cutoff_score: float
    ):
        self.company_id = company_id
        self.company_name = company_name
        self.open_positions = open_positions
        self.total_applicants = total_applicants
        self.selected_students = selected_students
        self.waitlisted_students = waitlisted_students
        self.rejected_students = rejected_students
        self.cutoff_score = cutoff_score
    
    def to_dict(self) -> Dict:
        return {
            "company_id": self.company_id,
            "company_name": self.company_name,
            "open_positions": self.open_positions,
            "total_applicants": self.total_applicants,
            "selected_count": len(self.selected_students),
            "waitlisted_count": len(self.waitlisted_students),
            "rejected_count": len(self.rejected_students),
            "cutoff_score": self.cutoff_score,
            "selected_students": self.selected_students,
            "waitlisted_students": self.waitlisted_students
        }


def allocate_seats(
    students: List,
    company,
    logs: List,
    match_function,
    open_positions: int = None
) -> SeatAllocationResult:
    """
    UPGRADE 1: Company Seat Allocation with Ranking
    
    Real-life problem: Companies have limited hiring slots.
    Not all eligible students get selected.
    
    Logic:
    1. Match all eligible students to company
    2. Sort by: final_score (desc), risk_score (asc for ties)
    3. Select top N = open_positions
    4. Remaining  REJECTED (reason: seat_limit)
    """
    positions = open_positions or getattr(company, 'open_positions', 5)
    
    # Get all matches
    all_matches = []
    for student in students:
        match = match_function(student, company, logs)
        all_matches.append({
            "student_id": student.student_id,
            "name": student.name,
            "branch": student.branch,
            "cgpa": student.cgpa,
            "match_score": match.match_score,
            "risk_score": match.risk.risk_score,
            "risk_level": match.risk.risk_level,
            "credibility_score": match.credibility.score,
            "credibility_level": match.credibility.level,
            "original_decision": match.decision,
            "failure_reason": match.failure_reason
        })
    
    # Separate eligible and ineligible
    eligible = [m for m in all_matches if m["original_decision"] != "rejected" or m["failure_reason"] in ["seat_limit", None]]
    ineligible = [m for m in all_matches if m["original_decision"] == "rejected" and m["failure_reason"] not in ["seat_limit", None]]
    
    # Re-evaluate: include all who passed basic eligibility
    eligible_for_ranking = [m for m in all_matches if m["failure_reason"] not in ["cgpa", "backlogs", "low_dsa"]]
    
    # Sort by match_score (descending), then by risk_score (ascending for ties)
    eligible_for_ranking.sort(key=lambda x: (-x["match_score"], x["risk_score"]))
    
    # Allocate seats
    selected = []
    waitlisted = []
    rejected_due_to_seats = []
    
    for i, match in enumerate(eligible_for_ranking):
        rank = i + 1
        match["rank"] = rank
        match["total_applicants"] = len(eligible_for_ranking)
        
        if i < positions:
            match["final_decision"] = "selected"
            match["selection_reason"] = f"Rank {rank}/{len(eligible_for_ranking)} - Within top {positions} positions"
            selected.append(match)
        elif i < positions + 3:  # Waitlist next 3
            match["final_decision"] = "waitlisted"
            match["selection_reason"] = f"Rank {rank}/{len(eligible_for_ranking)} - Waitlisted (positions {positions+1}-{positions+3})"
            waitlisted.append(match)
        else:
            match["final_decision"] = "rejected"
            match["failure_reason"] = "seat_limit"
            match["selection_reason"] = f"Rank {rank}/{len(eligible_for_ranking)} - Rejected due to seat limitation"
            rejected_due_to_seats.append(match)
    
    # Determine cutoff score
    cutoff_score = selected[-1]["match_score"] if selected else 0.0
    
    # Add ineligible students to rejected
    for match in ineligible:
        match["rank"] = None
        match["final_decision"] = "rejected"
        match["selection_reason"] = f"Ineligible: {match['failure_reason']}"
        rejected_due_to_seats.append(match)
    
    return SeatAllocationResult(
        company_id=company.company_id,
        company_name=company.company_name,
        open_positions=positions,
        total_applicants=len(all_matches),
        selected_students=selected,
        waitlisted_students=waitlisted,
        rejected_students=rejected_due_to_seats,
        cutoff_score=cutoff_score
    )


def generate_allocation_officer_report(allocation: SeatAllocationResult, student_id: str) -> str:
    """Generate officer explanation for seat allocation"""
    
    # Find student in results
    student_data = None
    for s in allocation.selected_students + allocation.waitlisted_students + allocation.rejected_students:
        if s["student_id"] == student_id:
            student_data = s
            break
    
    if not student_data:
        return f"Student {student_id} not found in allocation results."
    
    report = f"""
=== SEAT ALLOCATION REPORT ===
Company: {allocation.company_name}
Open Positions: {allocation.open_positions}
Total Applicants: {allocation.total_applicants}
Cutoff Score: {allocation.cutoff_score:.2f}

--- STUDENT STATUS ---
Student: {student_data['name']} ({student_data['student_id']})
Branch: {student_data['branch']}
CGPA: {student_data['cgpa']}

Match Score: {student_data['match_score']:.2f}
Risk Level: {student_data['risk_level']} (Score: {student_data['risk_score']}/10)
Credibility: {student_data['credibility_level']} ({student_data['credibility_score']:.2f})

--- ALLOCATION RESULT ---
Final Decision: {student_data['final_decision'].upper()}
"""
    
    if student_data.get('rank'):
        report += f"Rank: {student_data['rank']} / {student_data['total_applicants']} applicants\n"
    
    report += f"Reason: {student_data['selection_reason']}\n"
    
    if student_data['final_decision'] == 'rejected' and student_data.get('failure_reason') == 'seat_limit':
        report += f"""
--- SEAT LIMITATION DETAILS ---
Your Score: {student_data['match_score']:.2f}
Cutoff Score: {allocation.cutoff_score:.2f}
Gap: {allocation.cutoff_score - student_data['match_score']:.2f}

Recommendation: Improve profile for next recruitment cycle
- Add 2+ GitHub projects
- Improve communication score
- Target companies with more open positions
"""
    
    return report



# ==================== UPGRADE 2: TEMPORAL DRIFT & PROFILE IMPROVEMENT ====================

class StudentProfileSnapshot(BaseModel):
    """Snapshot of student profile at a specific semester"""
    semester: int = Field(ge=5, le=8)
    cgpa: float
    communication_score: int
    mock_interview_score: int
    skills_count: int
    github_projects: int
    certifications: int
    resume_trust_score: float
    credibility_level: str
    timestamp: str


class TemporalProfile:
    """Track student improvement over semesters"""
    def __init__(self, student_id: str, name: str, branch: str):
        self.student_id = student_id
        self.name = name
        self.branch = branch
        self.history: List[StudentProfileSnapshot] = []
        self.improvement_events: List[Dict] = []
    
    def add_snapshot(self, snapshot: StudentProfileSnapshot, event: str = None):
        self.history.append(snapshot)
        if event:
            self.improvement_events.append({
                "semester": snapshot.semester,
                "event": event,
                "timestamp": snapshot.timestamp
            })
    
    def get_growth_summary(self) -> Dict:
        if len(self.history) < 2:
            return {"growth": "insufficient_data"}
        
        first = self.history[0]
        last = self.history[-1]
        
        return {
            "student_id": self.student_id,
            "name": self.name,
            "semesters_tracked": f"{first.semester} to {last.semester}",
            "cgpa_change": round(last.cgpa - first.cgpa, 2),
            "communication_change": last.communication_score - first.communication_score,
            "github_projects_added": last.github_projects - first.github_projects,
            "certifications_added": last.certifications - first.certifications,
            "credibility_change": f"{first.credibility_level} -> {last.credibility_level}",
            "trust_score_change": round(last.resume_trust_score - first.resume_trust_score, 2),
            "improvement_events": self.improvement_events
        }
    
    def to_dict(self) -> Dict:
        return {
            "student_id": self.student_id,
            "name": self.name,
            "branch": self.branch,
            "history": [h.model_dump() for h in self.history],
            "improvement_events": self.improvement_events
        }


def simulate_student_growth(
    student,
    calculate_credibility_func,
    semesters: List[int] = [5, 6, 7, 8],
    is_motivated: bool = None
) -> TemporalProfile:
    """
    UPGRADE 2: Simulate student profile improvement over time
    
    Real-life problem: Students improve over time
    - Add GitHub projects
    - Improve communication
    - Reduce risk
    
    Simulation rules:
    - Motivated students: +1 project/semester, +1 communication every 2 semesters
    - Shortlisted students: +1 communication after feedback
    - All students: slight CGPA drift (+/- 0.1 per semester)
    """
    import copy
    
    temporal = TemporalProfile(student.student_id, student.name, student.branch)
    
    # Determine if student is motivated (based on existing traits or random)
    if is_motivated is None:
        is_motivated = student.cgpa >= 7.5 or student.communication_score >= 6
    
    # Current state
    current_cgpa = student.cgpa
    current_communication = student.communication_score
    current_mock = student.mock_interview_score
    current_skills = copy.deepcopy(student.skills)
    
    for sem in semesters:
        event = None
        
        # Simulate improvements
        if is_motivated:
            # Add projects to random skill
            if sem > semesters[0] and random.random() > 0.3:
                skill_to_improve = random.choice(current_skills)
                if skill_to_improve.evidence.projects < 5:
                    skill_to_improve.evidence.projects += 1
                    event = f"Added project to {skill_to_improve.name}"
            
            # Add GitHub repo
            if sem > semesters[0] and random.random() > 0.5:
                skill_to_improve = random.choice([s for s in current_skills if not s.evidence.github] or current_skills)
                if not skill_to_improve.evidence.github:
                    skill_to_improve.evidence.github = True
                    event = f"Created GitHub repo for {skill_to_improve.name}"
            
            # Communication improvement every 2 semesters
            if sem in [6, 8] and current_communication < 10:
                current_communication += 1
                event = "Communication improved through mock interviews"
        
        # CGPA drift (slight changes)
        cgpa_drift = random.uniform(-0.1, 0.15)
        current_cgpa = max(5.0, min(9.8, current_cgpa + cgpa_drift))
        
        # Mock interview improvement
        if sem > semesters[0] and random.random() > 0.6 and current_mock < 10:
            current_mock += 1
        
        # Calculate current credibility
        # Create temporary student for credibility calculation
        class TempStudent:
            def __init__(self, skills, trust_score):
                self.skills = skills
                self.resume_trust_score = trust_score
        
        temp_student = TempStudent(current_skills, 0.5)
        cred = calculate_credibility_func(temp_student)
        
        # Calculate trust score
        total_evidence = sum(
            (0.4 if s.evidence.github else 0) +
            0.3 * (s.evidence.projects / 5) +
            0.2 * (s.evidence.certifications / 3) +
            (0.3 if s.evidence.internship else 0)
            for s in current_skills
        )
        trust_score = min(1.0, total_evidence / len(current_skills)) if current_skills else 0.5
        
        github_count = sum(1 for s in current_skills if s.evidence.github)
        cert_count = sum(s.evidence.certifications for s in current_skills)
        
        snapshot = StudentProfileSnapshot(
            semester=sem,
            cgpa=round(current_cgpa, 2),
            communication_score=current_communication,
            mock_interview_score=current_mock,
            skills_count=len(current_skills),
            github_projects=github_count,
            certifications=cert_count,
            resume_trust_score=round(trust_score, 2),
            credibility_level=cred.level,
            timestamp=datetime.now().isoformat()
        )
        
        temporal.add_snapshot(snapshot, event)
    
    return temporal


def generate_growth_timeline(temporal: TemporalProfile) -> str:
    """Generate human-readable growth timeline"""
    
    timeline = f"""
=== STUDENT GROWTH TIMELINE ===
Student: {temporal.name} ({temporal.student_id})
Branch: {temporal.branch}

"""
    
    for snapshot in temporal.history:
        level_emoji = {"HIGH": "[OK]", "MEDIUM": "[--]", "LOW": "[!!]"}.get(snapshot.credibility_level, "[??]")
        
        timeline += f"""Semester {snapshot.semester}:
  CGPA: {snapshot.cgpa}
  Communication: {snapshot.communication_score}/10
  Mock Interview: {snapshot.mock_interview_score}/10
  GitHub Projects: {snapshot.github_projects}
  Certifications: {snapshot.certifications}
  Credibility: {level_emoji} {snapshot.credibility_level} ({snapshot.resume_trust_score:.2f})
"""
    
    # Summary
    growth = temporal.get_growth_summary()
    if growth.get("growth") != "insufficient_data":
        timeline += f"""
--- GROWTH SUMMARY ---
Semesters: {growth['semesters_tracked']}
CGPA Change: {growth['cgpa_change']:+.2f}
Communication Change: {growth['communication_change']:+d}
GitHub Projects Added: {growth['github_projects_added']}
Certifications Added: {growth['certifications_added']}
Credibility Evolution: {growth['credibility_change']}
Trust Score Change: {growth['trust_score_change']:+.2f}
"""
    
    if temporal.improvement_events:
        timeline += "\n--- KEY EVENTS ---\n"
        for event in temporal.improvement_events:
            timeline += f"Sem {event['semester']}: {event['event']}\n"
    
    return timeline



# ==================== UPGRADE 3: ML SUCCESS PROBABILITY ====================

class MLPredictionResult:
    """Result of ML-based success probability prediction"""
    def __init__(
        self,
        student_id: str,
        company_id: str,
        probability: float,
        confidence: str,
        feature_importance: Dict[str, float],
        model_used: str = "LogisticRegression"
    ):
        self.student_id = student_id
        self.company_id = company_id
        self.probability = round(probability, 3)
        self.confidence = confidence
        self.feature_importance = feature_importance
        self.model_used = model_used
    
    def to_dict(self) -> Dict:
        return {
            "student_id": self.student_id,
            "company_id": self.company_id,
            "predicted_success_probability": self.probability,
            "decision_confidence": self.confidence,
            "feature_importance": self.feature_importance,
            "model": self.model_used
        }


class PlacementSuccessPredictor:
    """
    UPGRADE 3: ONE Real ML Model - Logistic Regression
    
    Predicts: Probability of Selection (0-1)
    
    Features (from existing data only):
    - CGPA (normalized)
    - Resume credibility score
    - Communication score
    - Risk score
    - Skill match ratio
    
    Rule: Use ML as decision confidence, NOT decision maker
    """
    
    def __init__(self):
        self.weights = None
        self.bias = 0.0
        self.feature_means = {}
        self.feature_stds = {}
        self.is_trained = False
    
    def _sigmoid(self, z: float) -> float:
        """Sigmoid activation function"""
        z = max(-500, min(500, z))  # Prevent overflow
        return 1.0 / (1.0 + math.exp(-z))
    
    def _normalize(self, value: float, mean: float, std: float) -> float:
        """Normalize feature value"""
        if std == 0:
            return 0.0
        return (value - mean) / std
    
    def _extract_features(
        self,
        student,
        company,
        credibility_score: float,
        risk_score: int,
        skill_match_ratio: float
    ) -> Dict[str, float]:
        """Extract features for ML model"""
        return {
            "cgpa": student.cgpa,
            "credibility_score": credibility_score,
            "communication_score": student.communication_score,
            "risk_score": risk_score,
            "skill_match_ratio": skill_match_ratio,
            "mock_interview_score": student.mock_interview_score
        }
    
    def train(self, training_data: List[Dict], learning_rate: float = 0.1, epochs: int = 100):
        """
        Train logistic regression using gradient descent
        
        training_data format:
        [
            {
                "cgpa": 8.5,
                "credibility_score": 0.72,
                "communication_score": 7,
                "risk_score": 2,
                "skill_match_ratio": 0.8,
                "mock_interview_score": 7,
                "outcome": 1  # 1=selected, 0=rejected
            }
        ]
        """
        if not training_data:
            return
        
        # Calculate means and stds for normalization
        features = ["cgpa", "credibility_score", "communication_score", 
                   "risk_score", "skill_match_ratio", "mock_interview_score"]
        
        for feat in features:
            values = [d[feat] for d in training_data]
            self.feature_means[feat] = sum(values) / len(values)
            variance = sum((v - self.feature_means[feat])**2 for v in values) / len(values)
            self.feature_stds[feat] = max(0.001, variance ** 0.5)
        
        # Initialize weights
        self.weights = {feat: random.uniform(-0.1, 0.1) for feat in features}
        self.bias = 0.0
        
        # Gradient descent
        for epoch in range(epochs):
            total_loss = 0
            
            for data in training_data:
                # Forward pass
                z = self.bias
                for feat in features:
                    norm_val = self._normalize(data[feat], self.feature_means[feat], self.feature_stds[feat])
                    z += self.weights[feat] * norm_val
                
                pred = self._sigmoid(z)
                actual = data["outcome"]
                
                # Calculate loss
                epsilon = 1e-7
                loss = -(actual * math.log(pred + epsilon) + (1-actual) * math.log(1-pred + epsilon))
                total_loss += loss
                
                # Backward pass (gradient descent)
                error = pred - actual
                
                for feat in features:
                    norm_val = self._normalize(data[feat], self.feature_means[feat], self.feature_stds[feat])
                    self.weights[feat] -= learning_rate * error * norm_val
                
                self.bias -= learning_rate * error
        
        self.is_trained = True
    
    def predict(
        self,
        student,
        company,
        credibility_score: float,
        risk_score: int,
        skill_match_ratio: float
    ) -> MLPredictionResult:
        """Predict success probability for a student-company match"""
        
        if not self.is_trained:
            # Use heuristic if not trained
            base_prob = (
                0.2 * (student.cgpa / 10) +
                0.25 * credibility_score +
                0.2 * (student.communication_score / 10) +
                0.15 * (1 - risk_score / 10) +
                0.2 * skill_match_ratio
            )
            probability = min(0.95, max(0.05, base_prob))
        else:
            # Use trained model
            features = self._extract_features(
                student, company, credibility_score, risk_score, skill_match_ratio
            )
            
            z = self.bias
            for feat, val in features.items():
                norm_val = self._normalize(val, self.feature_means[feat], self.feature_stds[feat])
                z += self.weights[feat] * norm_val
            
            probability = self._sigmoid(z)
        
        # Determine confidence level
        if probability >= 0.75 or probability <= 0.25:
            confidence = "HIGH"
        elif probability >= 0.6 or probability <= 0.4:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"
        
        # Feature importance (absolute weight values)
        feature_importance = {}
        if self.weights:
            total_weight = sum(abs(w) for w in self.weights.values())
            if total_weight > 0:
                feature_importance = {
                    feat: round(abs(w) / total_weight, 3)
                    for feat, w in self.weights.items()
                }
        
        return MLPredictionResult(
            student_id=student.student_id,
            company_id=company.company_id,
            probability=probability,
            confidence=confidence,
            feature_importance=feature_importance
        )


def prepare_training_data(students: List, companies: List, logs: List, calculate_credibility_func) -> List[Dict]:
    """Prepare training data from placement logs"""
    
    student_map = {s.student_id: s for s in students}
    company_map = {c.company_id: c for c in companies}
    
    training_data = []
    
    for log in logs:
        if log.student_id not in student_map or log.company_id not in company_map:
            continue
        
        student = student_map[log.student_id]
        company = company_map[log.company_id]
        
        # Calculate credibility
        cred = calculate_credibility_func(student)
        
        # Calculate skill match ratio
        student_skills = {s.name.lower() for s in student.skills}
        required_skills = set(s.lower() for s in company.eligibility_rules.mandatory_skills)
        match_ratio = len(student_skills & required_skills) / len(required_skills) if required_skills else 0.5
        
        # Determine outcome
        outcome = 1 if log.interview_result == "selected" else 0
        
        training_data.append({
            "cgpa": student.cgpa,
            "credibility_score": cred.score,
            "communication_score": student.communication_score,
            "risk_score": 0,  # Will be calculated separately
            "skill_match_ratio": match_ratio,
            "mock_interview_score": student.mock_interview_score,
            "outcome": outcome
        })
    
    return training_data


def generate_ml_prediction_report(prediction: MLPredictionResult, student_name: str, company_name: str) -> str:
    """Generate ML prediction explanation"""
    
    confidence_indicator = {
        "HIGH": "[***]",
        "MEDIUM": "[**-]",
        "LOW": "[*--]"
    }
    
    report = f"""
=== ML SUCCESS PROBABILITY PREDICTION ===
Model: {prediction.model_used}
Student: {student_name} ({prediction.student_id})
Company: {company_name} ({prediction.company_id})

--- PREDICTION ---
Success Probability: {prediction.probability:.1%}
Decision Confidence: {confidence_indicator[prediction.confidence]} {prediction.confidence}

--- FEATURE IMPORTANCE ---
"""
    
    if prediction.feature_importance:
        sorted_features = sorted(prediction.feature_importance.items(), key=lambda x: -x[1])
        for feat, importance in sorted_features:
            bar = "#" * int(importance * 20)
            report += f"  {feat:25s}: {importance:.1%} {bar}\n"
    
    report += f"""
--- INTERPRETATION ---
"""
    
    if prediction.probability >= 0.7:
        report += "Strong candidate. High likelihood of selection.\n"
    elif prediction.probability >= 0.5:
        report += "Moderate candidate. Outcome depends on interview performance.\n"
    elif prediction.probability >= 0.3:
        report += "Weak candidate. Significant improvement needed.\n"
    else:
        report += "Very low chance. Consider targeting different companies.\n"
    
    report += "\nNote: ML prediction is for decision CONFIDENCE, not the decision itself.\n"
    
    return report



# ==================== UPGRADE 4: CREDIBILITY PENALTY BUG FIX ====================

def calculate_credibility_v2(student) -> Dict:
    """
    UPGRADE 4: Fixed Credibility Calculation
    
    Bug in original: Unfairly penalizes students with many skills
    
    Fixes:
    1. Apply inflation penalty PER inflated skill (not cumulative)
    2. Cap total penalty at 0.6
    3. Normalize by quality-weighted skills, not count
    
    Validation:
    - Student A: 3 strong skills should rank HIGHER than
    - Student B: 8 weak inflated skills
    """
    if not student.skills:
        return {
            "score": 0.5,
            "level": "MEDIUM",
            "red_flags": ["No skills listed"],
            "strengths": [],
            "penalty_breakdown": {}
        }
    
    total_skills = len(student.skills)
    red_flags = []
    strengths = []
    
    # Track quality scores per skill
    quality_scores = []
    inflation_penalties = []
    
    for skill in student.skills:
        # Calculate evidence-based quality score for THIS skill
        evidence_score = 0.0
        
        if skill.evidence.github:
            evidence_score += 0.35
        if skill.evidence.projects > 0:
            evidence_score += 0.25 * min(1.0, skill.evidence.projects / 3)
        if skill.evidence.certifications > 0:
            evidence_score += 0.2 * min(1.0, skill.evidence.certifications / 2)
        if skill.evidence.internship:
            evidence_score += 0.2
        
        # Check for inflation on THIS skill
        skill_penalty = 0.0
        if skill.claimed_level == "advanced":
            if not (skill.evidence.github or skill.evidence.projects >= 2):
                skill_penalty = 0.15  # Per-skill penalty (was 0.3 cumulative)
                inflation_penalties.append(skill.name)
                red_flags.append(f"{skill.name}: Claimed 'advanced' without evidence")
        elif skill.claimed_level == "intermediate":
            if evidence_score < 0.2:
                skill_penalty = 0.05  # Smaller penalty for intermediate
                red_flags.append(f"{skill.name}: Claimed 'intermediate' with weak evidence")
        
        # Quality score for this skill (evidence minus penalty)
        skill_quality = max(0.0, evidence_score - skill_penalty)
        quality_scores.append(skill_quality)
        
        # Track strengths
        if evidence_score >= 0.6:
            strengths.append(f"{skill.name}: Strong evidence ({evidence_score:.0%})")
    
    # Calculate weighted average quality (not simple average)
    # High-quality skills should boost score more than low-quality skills drag it down
    if quality_scores:
        # Weight by quality itself (better skills count more)
        weighted_sum = sum(q * (1 + q) for q in quality_scores)  # q * (1+q) gives more weight to high scores
        weight_total = sum(1 + q for q in quality_scores)
        base_score = weighted_sum / weight_total if weight_total > 0 else 0.5
    else:
        base_score = 0.5
    
    # Apply capped total inflation penalty
    total_inflation_penalty = min(0.6, len(inflation_penalties) * 0.1)  # Cap at 0.6
    final_score = max(0.0, min(1.0, base_score - total_inflation_penalty))
    
    # Determine level
    if final_score >= 0.7:
        level = "HIGH"
    elif final_score >= 0.4:
        level = "MEDIUM"
    else:
        level = "LOW"
    
    # Additional strength detection
    github_count = sum(1 for s in student.skills if s.evidence.github)
    if github_count >= 3:
        strengths.append(f"{github_count} skills backed by GitHub")
    
    return {
        "score": round(final_score, 2),
        "level": level,
        "red_flags": red_flags,
        "strengths": strengths,
        "penalty_breakdown": {
            "inflated_skills": inflation_penalties,
            "total_penalty": round(total_inflation_penalty, 2),
            "penalty_cap_applied": total_inflation_penalty >= 0.6
        }
    }


def validate_credibility_fix(create_test_student_func=None) -> Dict:
    """
    Validate that credibility fix works correctly
    
    Test: Student A (3 strong) should rank higher than Student B (8 weak inflated)
    """
    from data_engine import Skill, SkillEvidence
    
    # Student A: 3 strong skills with good evidence
    student_a_skills = [
        Skill(
            name="Python",
            claimed_level="advanced",
            evidence=SkillEvidence(github=True, projects=4, certifications=2, internship=True)
        ),
        Skill(
            name="DSA",
            claimed_level="advanced",
            evidence=SkillEvidence(github=True, projects=3, certifications=1, internship=False)
        ),
        Skill(
            name="SQL",
            claimed_level="intermediate",
            evidence=SkillEvidence(github=True, projects=2, certifications=1, internship=False)
        ),
    ]
    
    # Student B: 8 weak inflated skills
    student_b_skills = [
        Skill(
            name=f"Skill_{i}",
            claimed_level="advanced",
            evidence=SkillEvidence(github=False, projects=0, certifications=0, internship=False)
        )
        for i in range(8)
    ]
    
    class MockStudent:
        def __init__(self, skills, resume_trust_score=0.5):
            self.skills = skills
            self.resume_trust_score = resume_trust_score
    
    student_a = MockStudent(student_a_skills)
    student_b = MockStudent(student_b_skills)
    
    cred_a = calculate_credibility_v2(student_a)
    cred_b = calculate_credibility_v2(student_b)
    
    result = {
        "student_a": {
            "description": "3 strong skills with GitHub, projects, certs",
            "skills_count": len(student_a_skills),
            "credibility_score": cred_a["score"],
            "credibility_level": cred_a["level"],
            "strengths": cred_a["strengths"],
            "red_flags": cred_a["red_flags"]
        },
        "student_b": {
            "description": "8 weak inflated skills (advanced with no evidence)",
            "skills_count": len(student_b_skills),
            "credibility_score": cred_b["score"],
            "credibility_level": cred_b["level"],
            "strengths": cred_b["strengths"],
            "red_flags_count": len(cred_b["red_flags"]),
            "penalty_breakdown": cred_b["penalty_breakdown"]
        },
        "validation_passed": cred_a["score"] > cred_b["score"],
        "conclusion": "PASS - Quality beats quantity" if cred_a["score"] > cred_b["score"] else "FAIL - Bug still exists"
    }
    
    return result


# ==================== UPGRADE 5: BIAS & FAIRNESS AUDIT ====================

class BiasAuditResult:
    """Result of bias and fairness audit"""
    def __init__(
        self,
        cgpa_analysis: Dict,
        credibility_analysis: Dict,
        skill_vs_gpa_analysis: Dict,
        branch_analysis: Dict,
        communication_analysis: Dict,
        overall_fairness_score: float,
        recommendations: List[str]
    ):
        self.cgpa_analysis = cgpa_analysis
        self.credibility_analysis = credibility_analysis
        self.skill_vs_gpa_analysis = skill_vs_gpa_analysis
        self.branch_analysis = branch_analysis
        self.communication_analysis = communication_analysis
        self.overall_fairness_score = overall_fairness_score
        self.recommendations = recommendations
    
    def to_dict(self) -> Dict:
        return {
            "cgpa_analysis": self.cgpa_analysis,
            "credibility_analysis": self.credibility_analysis,
            "skill_vs_gpa_analysis": self.skill_vs_gpa_analysis,
            "branch_analysis": self.branch_analysis,
            "communication_analysis": self.communication_analysis,
            "overall_fairness_score": self.overall_fairness_score,
            "recommendations": self.recommendations
        }


def conduct_bias_audit(
    students: List,
    companies: List,
    logs: List,
    calculate_credibility_func
) -> BiasAuditResult:
    """
    UPGRADE 5: Bias & Fairness Audit
    
    Real-life problem: Students accuse placement cell of:
    - CGPA bias
    - Skill neglect
    - Communication favoritism
    
    Analysis:
    1. Selection rate vs CGPA bucket
    2. Selection rate vs credibility level
    3. Skill-heavy vs GPA-heavy success comparison
    4. Branch-wise fairness
    5. Communication score impact
    """
    student_map = {s.student_id: s for s in students}
    
    # Initialize counters
    cgpa_buckets = {
        "low (5.0-6.5)": {"total": 0, "selected": 0},
        "medium (6.5-7.5)": {"total": 0, "selected": 0},
        "high (7.5-8.5)": {"total": 0, "selected": 0},
        "star (8.5+)": {"total": 0, "selected": 0}
    }
    
    cred_levels = {
        "LOW": {"total": 0, "selected": 0},
        "MEDIUM": {"total": 0, "selected": 0},
        "HIGH": {"total": 0, "selected": 0}
    }
    
    # Track skill-heavy vs GPA-heavy
    skill_heavy = {"total": 0, "selected": 0}  # HIGH cred, medium CGPA
    gpa_heavy = {"total": 0, "selected": 0}    # HIGH CGPA, LOW/MEDIUM cred
    
    branch_stats = defaultdict(lambda: {"total": 0, "selected": 0})
    comm_buckets = {
        "low (1-4)": {"total": 0, "selected": 0},
        "medium (5-7)": {"total": 0, "selected": 0},
        "high (8-10)": {"total": 0, "selected": 0}
    }
    
    # Process logs
    for log in logs:
        if log.student_id not in student_map:
            continue
        
        student = student_map[log.student_id]
        cred = calculate_credibility_func(student)
        cred_level = cred.level if hasattr(cred, 'level') else cred.get('level', 'MEDIUM')
        is_selected = log.interview_result == "selected"
        
        # CGPA bucket
        if student.cgpa >= 8.5:
            bucket = "star (8.5+)"
        elif student.cgpa >= 7.5:
            bucket = "high (7.5-8.5)"
        elif student.cgpa >= 6.5:
            bucket = "medium (6.5-7.5)"
        else:
            bucket = "low (5.0-6.5)"
        
        cgpa_buckets[bucket]["total"] += 1
        if is_selected:
            cgpa_buckets[bucket]["selected"] += 1
        
        # Credibility level
        cred_levels[cred_level]["total"] += 1
        if is_selected:
            cred_levels[cred_level]["selected"] += 1
        
        # Skill-heavy vs GPA-heavy analysis
        if cred_level == "HIGH" and 6.5 <= student.cgpa < 8.0:
            skill_heavy["total"] += 1
            if is_selected:
                skill_heavy["selected"] += 1
        elif student.cgpa >= 8.0 and cred_level in ["LOW", "MEDIUM"]:
            gpa_heavy["total"] += 1
            if is_selected:
                gpa_heavy["selected"] += 1
        
        # Branch
        branch_stats[student.branch]["total"] += 1
        if is_selected:
            branch_stats[student.branch]["selected"] += 1
        
        # Communication bucket
        if student.communication_score >= 8:
            comm_bucket = "high (8-10)"
        elif student.communication_score >= 5:
            comm_bucket = "medium (5-7)"
        else:
            comm_bucket = "low (1-4)"
        
        comm_buckets[comm_bucket]["total"] += 1
        if is_selected:
            comm_buckets[comm_bucket]["selected"] += 1
    
    # Calculate rates
    def calc_rate(data):
        return round(data["selected"] / data["total"] * 100, 1) if data["total"] > 0 else 0
    
    cgpa_analysis = {k: {"count": v["total"], "selected": v["selected"], "rate": calc_rate(v)} for k, v in cgpa_buckets.items()}
    cred_analysis = {k: {"count": v["total"], "selected": v["selected"], "rate": calc_rate(v)} for k, v in cred_levels.items()}
    branch_analysis = {k: {"count": v["total"], "selected": v["selected"], "rate": calc_rate(v)} for k, v in branch_stats.items()}
    comm_analysis = {k: {"count": v["total"], "selected": v["selected"], "rate": calc_rate(v)} for k, v in comm_buckets.items()}
    
    skill_vs_gpa = {
        "skill_heavy": {"description": "HIGH credibility + Medium CGPA (6.5-8.0)", "rate": calc_rate(skill_heavy), "count": skill_heavy["total"]},
        "gpa_heavy": {"description": "HIGH CGPA (8.0+) + LOW/MEDIUM credibility", "rate": calc_rate(gpa_heavy), "count": gpa_heavy["total"]}
    }
    
    # Calculate fairness score
    # Lower variance in branch rates = more fair
    branch_rates = [v["rate"] for v in branch_analysis.values() if v["count"] > 0]
    branch_variance = sum((r - sum(branch_rates)/len(branch_rates))**2 for r in branch_rates) / len(branch_rates) if branch_rates else 0
    
    # Check if skill evidence outweighs pure CGPA
    skill_advantage = skill_vs_gpa["skill_heavy"]["rate"] - skill_vs_gpa["gpa_heavy"]["rate"]
    
    fairness_score = max(0, min(100, 
        70 +  # Base score
        (10 if skill_advantage > 0 else -10) +  # Bonus if skills matter
        (-branch_variance * 0.5) +  # Penalty for branch bias
        (5 if cred_analysis["HIGH"]["rate"] > cred_analysis["LOW"]["rate"] else -5)  # Bonus if credibility matters
    ))
    
    # Generate recommendations
    recommendations = []
    
    if skill_advantage < 0:
        recommendations.append("CGPA appears overweighted. Consider increasing skill_weight in company policies.")
    
    if branch_variance > 100:
        low_branch = min(branch_analysis.items(), key=lambda x: x[1]["rate"] if x[1]["count"] > 0 else float('inf'))
        recommendations.append(f"Branch bias detected: {low_branch[0]} has significantly lower selection rate ({low_branch[1]['rate']}%). Review for fairness.")
    
    if cred_analysis["HIGH"]["rate"] < cred_analysis["LOW"]["rate"]:
        recommendations.append("WARNING: LOW credibility students have higher success rate than HIGH credibility. System may not be properly validating skills.")
    
    if comm_analysis["high (8-10)"]["rate"] > 2 * comm_analysis["low (1-4)"]["rate"]:
        recommendations.append("Communication score has strong impact on selection. Consider if this aligns with role requirements.")
    
    if not recommendations:
        recommendations.append("No significant bias detected. System appears fair across dimensions.")
    
    return BiasAuditResult(
        cgpa_analysis=cgpa_analysis,
        credibility_analysis=cred_analysis,
        skill_vs_gpa_analysis=skill_vs_gpa,
        branch_analysis=branch_analysis,
        communication_analysis=comm_analysis,
        overall_fairness_score=round(fairness_score, 1),
        recommendations=recommendations
    )


def generate_bias_audit_report(audit: BiasAuditResult) -> str:
    """Generate human-readable bias audit report"""
    
    report = """
=== BIAS & FAIRNESS AUDIT REPORT ===
This report analyzes placement outcomes for potential bias.

--- CGPA BUCKET ANALYSIS ---
"""
    
    for bucket, data in audit.cgpa_analysis.items():
        bar = "#" * int(data["rate"] / 5)
        report += f"  {bucket:20s}: {data['rate']:5.1f}% selected ({data['selected']}/{data['count']}) {bar}\n"
    
    report += "\n--- CREDIBILITY LEVEL ANALYSIS ---\n"
    for level, data in audit.credibility_analysis.items():
        bar = "#" * int(data["rate"] / 5)
        report += f"  {level:20s}: {data['rate']:5.1f}% selected ({data['selected']}/{data['count']}) {bar}\n"
    
    report += "\n--- SKILL vs GPA COMPARISON ---\n"
    skill_data = audit.skill_vs_gpa_analysis["skill_heavy"]
    gpa_data = audit.skill_vs_gpa_analysis["gpa_heavy"]
    report += f"  Skill-heavy students: {skill_data['rate']:.1f}% success (n={skill_data['count']})\n"
    report += f"    ({skill_data['description']})\n"
    report += f"  GPA-heavy students:   {gpa_data['rate']:.1f}% success (n={gpa_data['count']})\n"
    report += f"    ({gpa_data['description']})\n"
    
    if skill_data['rate'] > gpa_data['rate']:
        report += "  Conclusion: Skill evidence outweighs GPA in final outcomes [GOOD]\n"
    else:
        report += "  Conclusion: GPA outweighs skill evidence [REVIEW NEEDED]\n"
    
    report += "\n--- BRANCH-WISE ANALYSIS ---\n"
    for branch, data in audit.branch_analysis.items():
        bar = "#" * int(data["rate"] / 5)
        report += f"  {branch:10s}: {data['rate']:5.1f}% selected ({data['selected']}/{data['count']}) {bar}\n"
    
    report += "\n--- COMMUNICATION IMPACT ---\n"
    for bucket, data in audit.communication_analysis.items():
        bar = "#" * int(data["rate"] / 5)
        report += f"  {bucket:15s}: {data['rate']:5.1f}% selected ({data['selected']}/{data['count']}) {bar}\n"
    
    report += f"\n--- OVERALL FAIRNESS SCORE ---\n"
    report += f"  Score: {audit.overall_fairness_score}/100\n"
    
    if audit.overall_fairness_score >= 80:
        report += "  Rating: EXCELLENT - System is fair\n"
    elif audit.overall_fairness_score >= 60:
        report += "  Rating: GOOD - Minor improvements possible\n"
    elif audit.overall_fairness_score >= 40:
        report += "  Rating: FAIR - Review recommendations\n"
    else:
        report += "  Rating: POOR - Significant bias detected\n"
    
    report += "\n--- RECOMMENDATIONS ---\n"
    for i, rec in enumerate(audit.recommendations, 1):
        report += f"  {i}. {rec}\n"
    
    report += "\nThis audit protects the institution AND the students.\n"
    
    return report



# ==================== DEMONSTRATION & MAIN EXECUTION ====================

def run_all_upgrades_demo():
    """
    Run demonstration of all 5 upgrades
    Generates the required deliverables:
    1. Company allocation example
    2. Student growth timeline
    3. ML probability output
    4. Bias audit report
    """
    from data_engine import SyntheticDataGenerator
    from intelligence import calculate_credibility
    
    print("=" * 70)
    print("COLLEGE PLACEMENT INTELLIGENCE SYSTEM - UPGRADES DEMO")
    print("=" * 70)
    
    # Generate synthetic data
    print("\n[1/6] Generating synthetic data...")
    generator = SyntheticDataGenerator(seed=42)
    students = generator.generate_students(100)
    companies = generator.generate_jobs(15)
    logs = generator.generate_placement_logs(students, companies, 200)
    print(f"    Generated: {len(students)} students, {len(companies)} companies, {len(logs)} logs")
    
    # Import match function
    from intelligence import match_student_to_job
    
    # --- UPGRADE 1: SEAT ALLOCATION ---
    print("\n[2/6] Running Upgrade 1: Seat Allocation...")
    company = companies[0]
    allocation = allocate_seats(
        students=students[:30],  # Top 30 eligible
        company=company,
        logs=logs,
        match_function=match_student_to_job,
        open_positions=5
    )
    # Show allocation summary
    print(f"\n    === ALLOCATION SUMMARY FOR {allocation.company_name} ===")
    print(f"    Open Positions: {allocation.open_positions}")
    print(f"    Total Applicants: {allocation.total_applicants}")
    print(f"    Cutoff Score: {allocation.cutoff_score:.2f}")
    print(f"\n    Selected ({len(allocation.selected_students)}):")
    for s in allocation.selected_students[:3]:
        print(f"      - {s['name']} (Rank {s['rank']}, Score: {s['match_score']:.2f})")
    print(f"\n    Rejected due to seat limit ({len(allocation.rejected_students)}):")
    for s in allocation.rejected_students[:3]:
        print(f"      - {s['name']} (Score: {s['match_score']:.2f})")
    
    # Show detailed report for one student
    sample_student = students[0]
    print(generate_allocation_officer_report(allocation, sample_student.student_id))
    
    # --- UPGRADE 2: TEMPORAL DRIFT ---
    print("\n[3/6] Running Upgrade 2: Temporal Profile...")
    student = students[0]
    profile = simulate_student_growth(student, calculate_credibility, semesters=[5, 6, 7, 8])
    print(generate_growth_timeline(profile))
    
    # --- UPGRADE 3: ML PREDICTION ---
    print("\n[4/6] Running Upgrade 3: ML Success Prediction...")
    predictor = PlacementSuccessPredictor()
    training_data = prepare_training_data(students, companies, logs, calculate_credibility)
    
    if len(training_data) >= 10:
        predictor.train(training_data)
        
        # Predict for a new student
        test_student = students[5]
        test_company = companies[0]
        cred = calculate_credibility(test_student)
        cred_score = cred.score if hasattr(cred, 'score') else cred.get('score', 0.5)
        
        # Calculate skill match ratio
        student_skills = {s.name.lower() for s in test_student.skills}
        required_skills = set(s.lower() for s in test_company.eligibility_rules.mandatory_skills)
        skill_match = len(student_skills & required_skills) / len(required_skills) if required_skills else 0.5
        
        prediction = predictor.predict(
            student=test_student,
            company=test_company,
            credibility_score=cred_score,
            risk_score=5,  # Moderate risk
            skill_match_ratio=skill_match
        )
        print(generate_ml_prediction_report(prediction, test_student.name, test_company.company_name))
    else:
        print("    Insufficient training data for ML model")
    
    # --- UPGRADE 4: CREDIBILITY FIX VALIDATION ---
    print("\n[5/6] Running Upgrade 4: Credibility Fix Validation...")
    validation = validate_credibility_fix()
    print("\n    === CREDIBILITY FIX TEST ===")
    print(f"    Student A (3 strong skills): Score = {validation['student_a']['credibility_score']}, Level = {validation['student_a']['credibility_level']}")
    print(f"    Student B (8 weak skills):   Score = {validation['student_b']['credibility_score']}, Level = {validation['student_b']['credibility_level']}")
    print(f"    Penalty cap applied: {validation['student_b']['penalty_breakdown']['penalty_cap_applied']}")
    print(f"    Result: {validation['conclusion']}")
    
    # --- UPGRADE 5: BIAS AUDIT ---
    print("\n[6/6] Running Upgrade 5: Bias & Fairness Audit...")
    audit = conduct_bias_audit(students, companies, logs, calculate_credibility_v2)
    print(generate_bias_audit_report(audit))
    
    print("\n" + "=" * 70)
    print("ALL UPGRADES COMPLETED SUCCESSFULLY")
    print("=" * 70)
    
    return {
        "allocation": allocation,
        "profile": profile,
        "prediction": prediction if len(training_data) >= 10 else None,
        "validation": validation,
        "audit": audit
    }


if __name__ == "__main__":
    run_all_upgrades_demo()

