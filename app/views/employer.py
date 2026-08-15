from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models.profiles import Employer, Helper
from app.models.job import Job, Skill, job_skills
from app.models.interaction import Application, Shortlist, Review, Complaint
from app.forms import EmployerProfileForm, JobForm, ReviewForm, ComplaintForm
from app.views import roles_required
from app.services.match_engine import calculate_match_score

employer_bp = Blueprint('employer', __name__)

@employer_bp.route('/setup-profile', methods=['GET', 'POST'])
@login_required
@roles_required('employer')
def setup_profile():
    """Create or edit Employer Profile."""
    profile = current_user.employer_profile
    form = EmployerProfileForm(obj=profile)
    
    if form.validate_on_submit():
        if not profile:
            profile = Employer(user_id=current_user.id)
            db.session.add(profile)
            
        form.populate_obj(profile)
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('employer.dashboard'))
        
    return render_template('employer/setup_profile.html', form=form, is_edit=bool(profile))

@employer_bp.route('/dashboard')
@login_required
@roles_required('employer')
def dashboard():
    """Employer Dashboard displaying jobs, shortlists, applications, and matching helpers."""
    profile = current_user.employer_profile
    if not profile:
        return redirect(url_for('employer.setup_profile'))

    jobs = profile.jobs.all()
    shortlisted = profile.shortlists.all()
    
    # Fetch applications filed against this employer's jobs
    job_ids = [j.id for j in jobs]
    applications = Application.query.filter(Application.job_id.in_(job_ids)).all() if job_ids else []

    # Get recommended helpers across active jobs
    recommendations = {}
    active_jobs = [j for j in jobs if j.status == 'open']
    
    # Limit calculation to active jobs, finding top compatible helpers
    all_helpers = Helper.query.all()
    for job in active_jobs:
        scored = []
        for helper in all_helpers:
            score = calculate_match_score(job, helper)
            if score >= 50.0:  # Only show helpers with 50%+ match
                scored.append((helper, score))
        # Sort by score descending and take top 5
        scored.sort(key=lambda x: x[1], reverse=True)
        recommendations[job.id] = scored[:5]

    return render_template(
        'employer/dashboard.html',
        employer=profile,
        jobs=jobs,
        shortlisted=shortlisted,
        applications=applications,
        recommendations=recommendations
    )

@employer_bp.route('/job/post', methods=['GET', 'POST'])
@login_required
@roles_required('employer')
def post_job():
    """Post a new job listing."""
    profile = current_user.employer_profile
    if not profile:
        return redirect(url_for('employer.setup_profile'))
        
    form = JobForm()
    
    # Load available skills categories
    if request.method == 'GET':
        pass # standard rendering
        
    if form.validate_on_submit():
        job = Job(
            employer_id=profile.id,
            title=form.title.data,
            category=form.category.data,
            salary_offered=form.salary_offered.data,
            working_hours_start=form.working_hours_start.data,
            working_hours_end=form.working_hours_end.data,
            gender_preference=form.gender_preference.data,
            language_requirements=form.language_requirements.data,
            experience_required_years=form.experience_required_years.data,
            accommodation_provided=form.accommodation_provided.data,
            food_provided=form.food_provided.data,
            weekly_off_day=form.weekly_off_day.data,
            address_pincode=form.address_pincode.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            description=form.description.data,
            status='open'
        )
        
        # Add basic default skills matching the category if they exist
        # E.g., if category is cook, look up cook skills and associate
        default_skills = Skill.query.filter_by(category=job.category).all()
        job.skills.extend(default_skills)
        
        db.session.add(job)
        db.session.commit()
        flash("Job posted successfully!", "success")
        return redirect(url_for('employer.dashboard'))
        
    return render_template('employer/post_job.html', form=form)

@employer_bp.route('/job/<int:job_id>/status/<string:status_val>', methods=['POST'])
@login_required
@roles_required('employer')
def update_job_status(job_id, status_val):
    """Toggle job between open, paused, closed."""
    profile = current_user.employer_profile
    job = Job.query.get_or_404(job_id)
    if job.employer_id != profile.id:
        abort(403)
        
    if status_val in ['open', 'paused', 'closed']:
        job.status = status_val
        db.session.commit()
        flash(f"Job status updated to {status_val}.", "success")
    return redirect(url_for('employer.dashboard'))

@employer_bp.route('/application/<int:app_id>/status/<string:new_status>', methods=['POST'])
@login_required
@roles_required('employer')
def update_application_status(app_id, new_status):
    """Update applicant status."""
    profile = current_user.employer_profile
    application = Application.query.get_or_404(app_id)
    job = Job.query.get(application.job_id)
    
    if job.employer_id != profile.id:
        abort(403)
        
    valid_statuses = ['applied', 'shortlisted', 'interviewed', 'offered', 'hired', 'rejected']
    if new_status in valid_statuses:
        application.status = new_status
        db.session.commit()
        flash(f"Applicant status updated to {new_status}.", "success")
        
        # Notify the helper
        from app.models.verification import Notification
        notification = Notification(
            user_id=application.helper.user_id,
            title="Application Status Updated",
            message=f"Your application for '{job.title}' has been moved to status: {new_status.title()}."
        )
        db.session.add(notification)
        db.session.commit()
        
    return redirect(url_for('employer.dashboard'))

@employer_bp.route('/helper/<int:helper_id>/shortlist', methods=['POST'])
@login_required
@roles_required('employer')
def toggle_shortlist(helper_id):
    """Add or remove helper from employer's shortlist."""
    profile = current_user.employer_profile
    helper = Helper.query.get_or_404(helper_id)
    
    shortlist_item = Shortlist.query.filter_by(employer_id=profile.id, helper_id=helper.id).first()
    if shortlist_item:
        db.session.delete(shortlist_item)
        db.session.commit()
        flash(f"{helper.full_name} removed from your shortlist.", "info")
    else:
        new_item = Shortlist(employer_id=profile.id, helper_id=helper.id)
        db.session.add(new_item)
        db.session.commit()
        flash(f"{helper.full_name} added to your shortlist.", "success")
        
    return redirect(request.referrer or url_for('employer.dashboard'))

@employer_bp.route('/helper/<int:helper_id>/review', methods=['GET', 'POST'])
@login_required
@roles_required('employer')
def leave_review(helper_id):
    """Leave review rating for a helper."""
    helper = Helper.query.get_or_404(helper_id)
    form = ReviewForm()
    
    if form.validate_on_submit():
        review = Review(
            reviewer_user_id=current_user.id,
            reviewee_user_id=helper.user_id,
            rating=form.rating.data,
            comment=form.comment.data
        )
        db.session.add(review)
        
        # Re-calculate overall average rating for helper
        reviews = Review.query.filter_by(reviewee_user_id=helper.user_id).all()
        ratings = [r.rating for r in reviews] + [form.rating.data]
        helper.overall_rating = sum(ratings) / len(ratings)
        
        db.session.commit()
        flash("Review submitted successfully!", "success")
        return redirect(url_for('public.helper_detail', helper_id=helper.id))
        
    return render_template('employer/leave_review.html', form=form, helper=helper)

@employer_bp.route('/dispute/<int:reported_user_id>/new', methods=['GET', 'POST'])
@login_required
@roles_required('employer')
def file_dispute(reported_user_id):
    """Submit a complaint ticket against a helper."""
    reported_user = Helper.query.filter_by(user_id=reported_user_id).first_or_404()
    form = ComplaintForm()
    
    if form.validate_on_submit():
        complaint = Complaint(
            reporter_id=current_user.id,
            reported_user_id=reported_user.user_id,
            category=form.category.data,
            description=form.description.data,
            status='pending'
        )
        db.session.add(complaint)
        db.session.commit()
        flash("Dispute submitted successfully. Administration will review it shortly.", "warning")
        return redirect(url_for('employer.dashboard'))
        
    return render_template('employer/file_dispute.html', form=form, helper=reported_user)
