from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.profiles import Helper, Employer
from app.models.job import Job
from app.models.interaction import Complaint
from app.models.verification import VerificationRequest
from app.views import roles_required
from app.services.verification_service import approve_document, reject_document

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
@roles_required('admin')
def dashboard():
    """Admin analytics and general status overview."""
    total_users = User.query.count()
    employers_count = Employer.query.count()
    helpers_count = Helper.query.count()
    active_jobs = Job.query.filter_by(status='open').count()
    
    pending_docs_count = VerificationRequest.query.filter_by(status='Pending').count()
    pending_complaints_count = Complaint.query.filter_by(status='pending').count()

    # Get recent complaints and all users for moderation directory
    recent_complaints = Complaint.query.order_by(db.desc(db.text('created_at'))).limit(5).all()
    users = User.query.limit(50).all()

    return render_template(
        'admin/dashboard.html',
        total_users=total_users,
        employers_count=employers_count,
        helpers_count=helpers_count,
        active_jobs=active_jobs,
        pending_docs_count=pending_docs_count,
        pending_complaints_count=pending_complaints_count,
        recent_complaints=recent_complaints,
        users=users
    )

@admin_bp.route('/verification/queue')
@login_required
@roles_required('admin')
def verification_queue():
    """Display pending document verifications."""
    pending_docs = VerificationRequest.query.filter_by(status='Pending').all()
    return render_template('admin/verification_queue.html', pending_docs=pending_docs)

@admin_bp.route('/verification/<int:doc_id>/approve', methods=['POST'])
@login_required
@roles_required('admin')
def approve_doc(doc_id):
    """Approve a helper verification request."""
    remarks = request.form.get('remarks', '').strip() or None
    success, message = approve_document(current_user.id, doc_id, remarks)
    if success:
        flash(message, "success")
    else:
        flash(message, "danger")
    return redirect(url_for('admin.verification_queue'))

@admin_bp.route('/verification/<int:doc_id>/reject', methods=['POST'])
@login_required
@roles_required('admin')
def reject_doc(doc_id):
    """Reject a helper document with reason."""
    reason = request.form.get('reason', '').strip()
    if not reason:
        flash("Rejection reason is required.", "warning")
        return redirect(url_for('admin.verification_queue'))
        
    success, message = reject_document(current_user.id, doc_id, reason)
    if success:
        flash(message, "success")
    else:
        flash(message, "danger")
    return redirect(url_for('admin.verification_queue'))

@admin_bp.route('/disputes')
@login_required
@roles_required('admin')
def complaints_queue():
    """List all dispute logs filed by users."""
    complaints = Complaint.query.order_by(db.desc(db.text('created_at'))).all()
    return render_template('admin/complaints_queue.html', complaints=complaints)

@admin_bp.route('/dispute/<int:comp_id>/status/<string:status_val>', methods=['POST'])
@login_required
@roles_required('admin')
def resolve_dispute(comp_id, status_val):
    """Move complaint to investigating, resolved, or dismissed."""
    complaint = Complaint.query.get_or_404(comp_id)
    
    if status_val in ['investigating', 'resolved', 'dismissed']:
        complaint.status = status_val
        db.session.commit()
        flash(f"Dispute status updated to {status_val.title()}.", "success")
        
        # Notify the reporter
        from app.models.verification import Notification
        notification = Notification(
            user_id=complaint.reporter_id,
            title="Dispute Status Updated",
            message=f"The complaint you filed (ID: {complaint.id}) has been updated to: {status_val.title()}."
        )
        db.session.add(notification)
        db.session.commit()
        
    return redirect(url_for('admin.complaints_queue'))

@admin_bp.route('/user/<int:user_id>/toggle-active', methods=['POST'])
@login_required
@roles_required('admin')
def toggle_user_active(user_id):
    """Moderation suspension toggle."""
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot suspend your own account.", "danger")
        return redirect(request.referrer or url_for('admin.dashboard'))
        
    user.is_active = not user.is_active
    db.session.commit()
    
    status_text = "activated" if user.is_active else "suspended"
    flash(f"User profile associated with {user.phone_number} has been {status_text}.", "info")
    return redirect(request.referrer or url_for('admin.dashboard'))
