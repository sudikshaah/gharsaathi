from datetime import datetime
from app import db
from app.models.verification import VerificationRequest, Verification, Notification
from app.models.profiles import Helper

def approve_document(admin_user_id, request_id, remarks=None):
    """
    Approve a verification request, update helper profile badges,
    log audit trailing, and notify helper.
    """
    req = VerificationRequest.query.get(request_id)
    if not req:
        return False, "Verification request not found"

    req.status = 'Approved'
    req.reviewed_by = admin_user_id
    req.reviewed_at = datetime.utcnow()
    req.remarks = remarks or "Approved by administrator"
    
    # Load associated helper profile
    helper = Helper.query.filter_by(user_id=req.user_id).first()
    helper_id = helper.id if helper else None
    
    if helper:
        # Update badges based on document type
        if req.document_type == 'police_clearance':
            helper.is_police_verified = True
            helper.is_background_checked = True

    # Audit Log entry
    audit = Verification(
        admin_user_id=admin_user_id,
        helper_id=helper_id,
        action_taken=f"Approved VerificationRequest ID {req.id} ({req.document_type})"
    )
    db.session.add(audit)
    
    # User Notification
    notification = Notification(
        user_id=req.user_id,
        title="Verification Approved",
        message=f"Your {req.document_type.replace('_', ' ').title()} document has been verified and approved."
    )
    db.session.add(notification)
    
    db.session.commit()
    return True, "Verification request approved successfully"

def reject_document(admin_user_id, request_id, remarks):
    """
    Reject a verification request, reset helper badges if applicable,
    log audit trails, and notify helper.
    """
    if not remarks or not remarks.strip():
        return False, "Remarks / Rejection reason is required"

    req = VerificationRequest.query.get(request_id)
    if not req:
        return False, "Verification request not found"

    req.status = 'Rejected'
    req.reviewed_by = admin_user_id
    req.reviewed_at = datetime.utcnow()
    req.remarks = remarks
    
    # Load associated helper profile
    helper = Helper.query.filter_by(user_id=req.user_id).first()
    helper_id = helper.id if helper else None
    
    if helper:
        # Reset badges if the document was previously approved
        if req.document_type == 'police_clearance':
            helper.is_police_verified = False
            helper.is_background_checked = False
    
    # Audit Log entry
    audit = Verification(
        admin_user_id=admin_user_id,
        helper_id=helper_id,
        action_taken=f"Rejected VerificationRequest ID {req.id} ({req.document_type}). Reason: {remarks}"
    )
    db.session.add(audit)
    
    # User Notification
    notification = Notification(
        user_id=req.user_id,
        title="Verification Rejected",
        message=f"Your {req.document_type.replace('_', ' ').title()} document was rejected. Reason: {remarks}"
    )
    db.session.add(notification)
    
    db.session.commit()
    return True, "Verification request rejected successfully"
