import os
import time
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models.profiles import Helper
from app.models.job import Job, Skill
from app.models.interaction import Application, SavedJob, Complaint
from app.models.verification import VerificationRequest
from app.forms import HelperProfileForm, DocumentUploadForm, ComplaintForm
from app.views import roles_required

helper_bp = Blueprint('helper', __name__)

def allowed_file(filename):
    """Helper function to check if the uploaded document has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@helper_bp.route('/setup-profile', methods=['GET', 'POST'])
@login_required
@roles_required('helper')
def setup_profile():
    """Create or update Helper Profile details."""
    profile = current_user.helper_profile
    form = HelperProfileForm(obj=profile)
    
    # Pre-fill skills if they exist
    selected_skills = []
    if profile:
        selected_skills = [s.id for s in profile.skills]
        
    # Fetch all skills from the master table to let the helper pick
    skills_list = Skill.query.all()
    
    if form.validate_on_submit():
        if not profile:
            profile = Helper(user_id=current_user.id)
            db.session.add(profile)
            
        form.populate_obj(profile)
        
        # Sync Skills
        skill_ids = request.form.getlist('skills')
        chosen_skills = Skill.query.filter(Skill.id.in_(skill_ids)).all()
        profile.skills = chosen_skills
        
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('helper.dashboard'))
        
    return render_template(
        'helper/setup_profile.html', 
        form=form, 
        skills_list=skills_list, 
        selected_skills=selected_skills,
        is_edit=bool(profile)
    )

@helper_bp.route('/dashboard')
@login_required
@roles_required('helper')
def dashboard():
    """Helper Dashboard displaying profile information, upload queues, and applications."""
    profile = current_user.helper_profile
    if not profile:
        return redirect(url_for('helper.setup_profile'))

    verification_requests = current_user.verification_requests.all()
    applications = profile.applications.all()
    saved_jobs = profile.saved_jobs.all()
    notifications = current_user.notifications.order_by(db.desc(db.text('created_at'))).limit(5).all()

    return render_template(
        'helper/dashboard.html',
        helper=profile,
        verification_requests=verification_requests,
        applications=applications,
        saved_jobs=saved_jobs,
        notifications=notifications
    )

@helper_bp.route('/document/upload', methods=['GET', 'POST'])
@login_required
@roles_required('helper')
def upload_document():
    """Upload helper verification credentials, triggering automatic OCR simulation."""
    profile = current_user.helper_profile
    if not profile:
        return redirect(url_for('helper.setup_profile'))
        
    form = DocumentUploadForm()
    if form.validate_on_submit():
        file = form.document_file.data
        if file and allowed_file(file.filename):
            # Formulate safe unique file name
            ext = file.filename.rsplit('.', 1)[1].lower()
            safe_name = f"user_{current_user.id}_{form.document_type.data}_{int(time.time())}.{ext}"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], safe_name)
            
            # Save actual file to static uploads folder
            file.save(filepath)
            
            # Simulate automatic OCR Extraction to reduce admin effort
            # Human-in-the-loop review will follow
            ocr_name = profile.full_name
            ocr_dob = f"{2026 - profile.age}-05-15"
            
            if form.document_type.data == 'aadhaar':
                ocr_num = f"9876-5432-{1000 + current_user.id}"
            elif form.document_type.data == 'police_clearance':
                ocr_num = f"PCC-2026-{800000 + current_user.id}"
            elif form.document_type.data == 'address_proof':
                ocr_num = f"ADDR-{2000 + current_user.id}"
            else:
                ocr_num = f"VACC-COV-{9000 + current_user.id}"
            
            # Remove any old request of same type for the user
            old_req = VerificationRequest.query.filter_by(
                user_id=current_user.id, 
                document_type=form.document_type.data
            ).first()
            if old_req:
                db.session.delete(old_req)
            
            new_req = VerificationRequest(
                user_id=current_user.id,
                document_type=form.document_type.data,
                document_path=f"/static/uploads/{safe_name}",
                ocr_name=ocr_name,
                ocr_document_number=ocr_num,
                ocr_dob=ocr_dob,
                status='Pending'
            )
            
            db.session.add(new_req)
            db.session.commit()
            
            flash(
                f"{form.document_type.data.replace('_', ' ').title()} uploaded successfully. "
                f"OCR extracted details: {ocr_name} | {ocr_num}. Verification pending manual admin approval.", 
                "success"
            )
            return redirect(url_for('helper.dashboard'))
        else:
            flash("Invalid file format. Allowed extensions are: PDF, PNG, JPG, JPEG", "danger")
            
    return render_template('helper/upload_document.html', form=form)

@helper_bp.route('/job/<int:job_id>/apply', methods=['POST'])
@login_required
@roles_required('helper')
def apply_job(job_id):
    """Apply to a job listing."""
    profile = current_user.helper_profile
    if not profile:
        return redirect(url_for('helper.setup_profile'))
        
    job = Job.query.get_or_404(job_id)
    if job.status != 'open':
        flash("This job is no longer accepting applications.", "warning")
        return redirect(url_for('public.job_detail', job_id=job.id))
        
    # Check if helper already applied
    existing_app = Application.query.filter_by(job_id=job.id, helper_id=profile.id).first()
    if existing_app:
        flash("You have already applied to this job listing.", "info")
    else:
        new_app = Application(job_id=job.id, helper_id=profile.id, status='applied')
        db.session.add(new_app)
        db.session.commit()
        flash("Successfully applied to job!", "success")
        
        # Notify Employer
        from app.models.verification import Notification
        employer_user_id = job.employer.user_id
        notification = Notification(
            user_id=employer_user_id,
            title="New Job Application Received",
            message=f"{profile.full_name} has applied to your job listing: '{job.title}'."
        )
        db.session.add(notification)
        db.session.commit()

    return redirect(url_for('public.job_detail', job_id=job.id))

@helper_bp.route('/job/<int:job_id>/save', methods=['POST'])
@login_required
@roles_required('helper')
def toggle_save_job(job_id):
    """Bookmark or save a job posting."""
    profile = current_user.helper_profile
    if not profile:
        return redirect(url_for('helper.setup_profile'))
        
    job = Job.query.get_or_404(job_id)
    
    saved_item = SavedJob.query.filter_by(helper_id=profile.id, job_id=job.id).first()
    if saved_item:
        db.session.delete(saved_item)
        db.session.commit()
        flash("Job removed from saved listings.", "info")
    else:
        new_save = SavedJob(helper_id=profile.id, job_id=job.id)
        db.session.add(new_save)
        db.session.commit()
        flash("Job bookmarked successfully!", "success")
        
    return redirect(request.referrer or url_for('public.job_detail', job_id=job.id))

@helper_bp.route('/dispute/<int:reported_user_id>/new', methods=['GET', 'POST'])
@login_required
@roles_required('helper')
def file_dispute(reported_user_id):
    """Submit a complaint ticket against an employer."""
    reported_user = Employer.query.filter_by(user_id=reported_user_id).first_or_404()
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
        flash("Complaint submitted. Administrative review pending.", "warning")
        return redirect(url_for('helper.dashboard'))
        
    return render_template('helper/file_dispute.html', form=form, employer=reported_user)
