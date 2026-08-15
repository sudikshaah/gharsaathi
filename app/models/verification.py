from datetime import datetime
from app import db

class VerificationRequest(db.Model):
    """Verification Request containing OCR extracted data and admin review tracking."""
    __tablename__ = 'verification_requests'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    document_type = db.Column(db.Enum('aadhaar', 'police_clearance', 'address_proof', 'vaccine_cert', name='doc_types'), nullable=False)
    document_path = db.Column(db.String(255), nullable=False)  # Path to saved file
    ocr_name = db.Column(db.String(150), nullable=True)
    ocr_document_number = db.Column(db.String(100), nullable=True)
    ocr_dob = db.Column(db.String(50), nullable=True)
    status = db.Column(db.Enum('Pending', 'Approved', 'Rejected', name='verification_status'), default='Pending')
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    remarks = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<VerificationRequest id={self.id} user_id={self.user_id} type={self.document_type} status={self.status}>"


class Verification(db.Model):
    """Admin action audits queue log."""
    __tablename__ = 'verifications'

    id = db.Column(db.Integer, primary_key=True)
    admin_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    helper_id = db.Column(db.Integer, db.ForeignKey('helpers.id', ondelete='CASCADE'), nullable=True)
    action_taken = db.Column(db.Text, nullable=False)  # Action summary (e.g. "Approved Aadhaar Document ID 3")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Verification admin={self.admin_user_id} action={self.action_taken[:30]}>"


class Notification(db.Model):
    """User in-app notifications."""
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Notification user_id={self.user_id} title={self.title} read={self.is_read}>"


class Announcement(db.Model):
    """Admin-published news and announcements."""
    __tablename__ = 'announcements'

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    target_role = db.Column(db.Enum('all', 'employer', 'helper', name='announcement_roles'), default='all')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Announcement title={self.title} target={self.target_role}>"
