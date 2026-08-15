import math
from decimal import Decimal

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees).
    Returns distance in kilometers.
    """
    if None in (lat1, lon1, lat2, lon2):
        return None
        
    try:
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371  # Radius of earth in kilometers.
        return c * r
    except Exception:
        return None

def calculate_match_score(job, helper):
    """
    Calculate match compatibility percentage (0 - 100%) between a Job and a Helper.
    Weights:
      - Location Proximity: 30%
      - Salary Expectation: 25%
      - Skill Overlap: 20%
      - Experience Requirement: 15%
      - Verification Bonus: 10%
    """
    # 1. Location Proximity (30% Weight)
    location_score = 0.0
    dist = haversine_distance(job.latitude, job.longitude, helper.latitude, helper.longitude)
    
    if dist is not None:
        if dist <= 1.0:
            location_score = 100.0
        elif dist >= 5.0:
            location_score = 0.0
        else:
            # Drops linearly after 1km and hits 0 at 5km
            location_score = 100.0 - ((dist - 1.0) / 4.0 * 100.0)
    else:
        # Fallback to exact Pincode matching
        job_pincode = (job.address_pincode or "").strip()
        helper_pincode = (helper.location_pincode or "").strip()
        if job_pincode and helper_pincode and job_pincode == helper_pincode:
            location_score = 100.0
        else:
            location_score = 0.0

    # 2. Salary Expectation (25% Weight)
    salary_score = 0.0
    expected = float(helper.expected_salary or 0.0)
    offered = float(job.salary_offered or 0.0)
    
    if offered > 0:
        if expected <= offered:
            salary_score = 100.0
        else:
            # Drop proportionally, hits 0 if expected is 50% or more above offered
            diff_pct = (expected - offered) / offered
            if diff_pct >= 0.5:
                salary_score = 0.0
            else:
                salary_score = 100.0 - (diff_pct / 0.5 * 100.0)
    else:
        salary_score = 100.0 if expected == 0 else 0.0

    # 3. Skill Overlap (20% Weight)
    skill_score = 0.0
    job_skill_names = {s.skill_name.lower().strip() for s in job.skills}
    helper_skill_names = {s.skill_name.lower().strip() for s in helper.skills}
    
    if job_skill_names or helper_skill_names:
        intersection = job_skill_names.intersection(helper_skill_names)
        union = job_skill_names.union(helper_skill_names)
        if union:
            skill_score = (len(intersection) / len(union)) * 100.0
    else:
        # If neither specifies skills (e.g. general workers), defaults to 100% overlap
        skill_score = 100.0

    # 4. Experience Requirement (15% Weight)
    exp_score = 0.0
    helper_exp = float(helper.experience_years or 0)
    job_req_exp = float(job.experience_required_years or 0)
    
    if job_req_exp <= 0:
        exp_score = 100.0
    else:
        if helper_exp >= job_req_exp:
            exp_score = 100.0
        else:
            exp_score = (helper_exp / job_req_exp) * 100.0

    # 5. Verification Bonus (10% Weight)
    verify_score = 0.0
    
    # Check approved Identity Document (Aadhaar)
    from app.models.verification import VerificationRequest
    aadhaar_approved = helper.user.verification_requests.filter_by(
        document_type='aadhaar', 
        status='Approved'
    ).first() is not None
    
    if aadhaar_approved:
        verify_score += 50.0  # 50% of the verification component = 5% overall
        
    # Check Police clearance document approved, or direct helper fields
    police_approved = helper.user.verification_requests.filter_by(
        document_type='police_clearance', 
        status='Approved'
    ).first() is not None
    
    if police_approved or helper.is_police_verified or helper.is_background_checked:
        verify_score += 50.0  # 50% of the verification component = 5% overall

    # Total Score calculation
    weighted_score = (
        (location_score * 0.30) +
        (salary_score * 0.25) +
        (skill_score * 0.20) +
        (exp_score * 0.15) +
        (verify_score * 0.10)
    )
    
    return round(weighted_score, 1)
