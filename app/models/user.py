from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(db.Model, UserMixin):
    """Base User model for Authentication and Authorization."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=True)  # Helper registration might not require email
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('admin', 'employer', 'helper', name='user_roles'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_phone_verified = db.Column(db.Boolean, default=False)
    is_email_verified = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    employer_profile = db.relationship('Employer', backref='user', uselist=False, cascade="all, delete-orphan")
    helper_profile = db.relationship('Helper', backref='user', uselist=False, cascade="all, delete-orphan")
    verification_requests = db.relationship('VerificationRequest', foreign_keys='VerificationRequest.user_id', backref='user', lazy='dynamic', cascade="all, delete-orphan")
    reviewed_requests = db.relationship('VerificationRequest', foreign_keys='VerificationRequest.reviewed_by', backref='reviewer', lazy='dynamic')

    # Sent and Received Messages
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy='dynamic')
    received_messages = db.relationship('Message', foreign_keys='Message.recipient_id', backref='recipient', lazy='dynamic')

    # Reported and Filed complaints
    filed_complaints = db.relationship('Complaint', foreign_keys='Complaint.reporter_id', backref='reporter', lazy='dynamic')
    received_complaints = db.relationship('Complaint', foreign_keys='Complaint.reported_user_id', backref='reported_user', lazy='dynamic')

    notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade="all, delete-orphan")

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def is_employer(self):
        return self.role == 'employer'

    def is_helper(self):
        return self.role == 'helper'

    def __repr__(self):
        return f"<User id={self.id} phone_number={self.phone_number} role={self.role}>"
