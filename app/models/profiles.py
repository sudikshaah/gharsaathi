from datetime import datetime
from app import db

class Employer(db.Model):
    """Employer Profile model."""
    __tablename__ = 'employers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    family_name = db.Column(db.String(100), nullable=False)
    address_line1 = db.Column(db.String(255), nullable=False)
    address_line2 = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=False, default="Kathmandu")
    state = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(20), nullable=False)
    latitude = db.Column(db.Numeric(10, 8), nullable=True)
    longitude = db.Column(db.Numeric(11, 8), nullable=True)
    verified_status = db.Column(db.Enum('pending', 'verified', 'rejected', name='employer_verification_status'), default='pending')

    # Relationships
    jobs = db.relationship('Job', backref='employer', lazy='dynamic', cascade="all, delete-orphan")
    shortlists = db.relationship('Shortlist', backref='employer', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Employer id={self.id} family_name={self.family_name}>"


class Helper(db.Model):
    """Helper Profile model."""
    __tablename__ = 'helpers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    full_name = db.Column(db.String(150), nullable=False)
    profile_photo = db.Column(db.String(255), nullable=True)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.Enum('male', 'female', 'other', name='genders'), nullable=False)
    religion = db.Column(db.String(50), nullable=True)
    languages_spoken = db.Column(db.Text, nullable=True)  # Comma separated or string representation
    experience_years = db.Column(db.Integer, default=0)
    education_level = db.Column(db.String(100), nullable=True)
    expected_salary = db.Column(db.Numeric(10, 2), nullable=False)
    available_from = db.Column(db.Date, nullable=True, default=datetime.utcnow().date)
    preferred_hours_start = db.Column(db.Time, nullable=True)
    preferred_hours_end = db.Column(db.Time, nullable=True)
    work_type = db.Column(db.Enum('live_in', 'live_out', 'both', name='work_types'), default='live_out')
    location_pincode = db.Column(db.String(20), nullable=False)
    latitude = db.Column(db.Numeric(10, 8), nullable=True)
    longitude = db.Column(db.Numeric(11, 8), nullable=True)
    is_vaccinated = db.Column(db.Boolean, default=False)
    is_police_verified = db.Column(db.Boolean, default=False)
    is_background_checked = db.Column(db.Boolean, default=False)
    overall_rating = db.Column(db.Float, default=0.0)

    # Verification requests are managed via helper.user.verification_requests
    skills = db.relationship('Skill', secondary='helper_skills', back_populates='helpers')
    experience_history = db.relationship('HelperExperience', backref='helper', lazy='dynamic', cascade="all, delete-orphan")
    applications = db.relationship('Application', backref='helper', lazy='dynamic', cascade="all, delete-orphan")
    saved_jobs = db.relationship('SavedJob', backref='helper', lazy='dynamic', cascade="all, delete-orphan")
    shortlisted_by = db.relationship('Shortlist', backref='helper', lazy='dynamic', cascade="all, delete-orphan")
    admin_verifications = db.relationship('Verification', backref='helper', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Helper id={self.id} full_name={self.full_name}>"
