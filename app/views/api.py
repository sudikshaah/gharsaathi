from flask import Blueprint, jsonify, abort
from flask_login import login_required, current_user
from app.models.job import Job
from app.models.profiles import Helper
from app.services.match_engine import calculate_match_score
from app.views import roles_required

api_bp = Blueprint('api', __name__)

@api_bp.route('/match/job/<int:job_id>/helper/<int:helper_id>')
@login_required
def get_match_score(job_id, helper_id):
    """Fetch matching percentage score for a specific job and helper."""
    job = Job.query.get_or_404(job_id)
    helper = Helper.query.get_or_404(helper_id)
    
    # Check permissions: only admin or the job owner or the helper themselves can see details
    is_authorized = (
        current_user.role == 'admin' or 
        (current_user.role == 'employer' and current_user.employer_profile and job.employer_id == current_user.employer_profile.id) or
        (current_user.role == 'helper' and current_user.helper_profile and helper.id == current_user.helper_profile.id)
    )
    if not is_authorized:
        abort(403)
        
    score = calculate_match_score(job, helper)
    return jsonify({
        'job_id': job.id,
        'helper_id': helper.id,
        'match_score': score
    })

@api_bp.route('/match/job/<int:job_id>')
@login_required
@roles_required('employer', 'admin')
def get_job_matches(job_id):
    """Fetch all matching helpers ranked by score for a job posting."""
    job = Job.query.get_or_404(job_id)
    
    # Check owner authorization
    if current_user.role == 'employer' and current_user.employer_profile:
        if job.employer_id != current_user.employer_profile.id:
            abort(403)
            
    helpers = Helper.query.all()
    results = []
    
    for helper in helpers:
        score = calculate_match_score(job, helper)
        results.append({
            'helper_id': helper.id,
            'full_name': helper.full_name,
            'age': helper.age,
            'gender': helper.gender,
            'experience_years': helper.experience_years,
            'expected_salary': float(helper.expected_salary),
            'location_pincode': helper.location_pincode,
            'is_police_verified': helper.is_police_verified,
            'is_background_checked': helper.is_background_checked,
            'overall_rating': helper.overall_rating,
            'match_score': score
        })
        
    # Sort results by score in descending order
    results.sort(key=lambda x: x['match_score'], reverse=True)
    
    return jsonify({
        'job_id': job.id,
        'matches': results
    })
