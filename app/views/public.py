from flask import Blueprint, render_template, request, flash
from app.models.profiles import Helper
from app.models.job import Job, Skill
from app import db

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def index():
    """GharSaathi Homepage / Landing Page."""
    # Fetch some stats for the visual dashboard
    total_helpers = Helper.query.count()
    verified_helpers = Helper.query.filter_by(is_police_verified=True).count()
    total_jobs = Job.query.filter_by(status='open').count()
    
    # Get 3 featured verified helpers to display
    featured_helpers = Helper.query.filter_by(is_police_verified=True).limit(3).all()
    
    return render_template(
        'public/index.html',
        total_helpers=total_helpers,
        verified_helpers=verified_helpers,
        total_jobs=total_jobs,
        featured_helpers=featured_helpers
    )

@public_bp.route('/faq')
def faq():
    """FAQ page."""
    return render_template('public/faq.html')

@public_bp.route('/search/helpers')
def search_helpers():
    """Search & Filter helpers."""
    category = request.args.get('category', '').strip()
    pincode = request.args.get('pincode', '').strip()
    min_exp = request.args.get('min_experience', type=int)
    
    query = Helper.query
    
    if category:
        # Filter helper profiles matching skills in that category
        query = query.join(Helper.skills).filter(Skill.category == category)
    if pincode:
        query = query.filter(Helper.location_pincode == pincode)
    if min_exp is not None:
        query = query.filter(Helper.experience_years >= min_exp)
        
    helpers = query.all()
    
    # Get unique categories for dropdowns
    categories = db.session.query(Skill.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    
    return render_template(
        'public/search_helpers.html', 
        helpers=helpers, 
        categories=categories,
        selected_category=category,
        selected_pincode=pincode,
        selected_exp=min_exp
    )

@public_bp.route('/search/jobs')
def search_jobs():
    """Search & Filter jobs."""
    category = request.args.get('category', '').strip()
    pincode = request.args.get('pincode', '').strip()
    
    query = Job.query.filter_by(status='open')
    
    if category:
        query = query.filter(Job.category == category)
    if pincode:
        query = query.filter(Job.address_pincode == pincode)
        
    jobs = query.all()
    
    # Get unique job categories
    categories = db.session.query(Job.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    
    return render_template(
        'public/search_jobs.html',
        jobs=jobs,
        categories=categories,
        selected_category=category,
        selected_pincode=pincode
    )

@public_bp.route('/helper/<int:helper_id>')
def helper_detail(helper_id):
    """Public details of helper profile."""
    helper = Helper.query.get_or_404(helper_id)
    return render_template('public/helper_detail.html', helper=helper)

@public_bp.route('/job/<int:job_id>')
def job_detail(job_id):
    """Public details of a job posting."""
    job = Job.query.get_or_404(job_id)
    return render_template('public/job_detail.html', job=job)
