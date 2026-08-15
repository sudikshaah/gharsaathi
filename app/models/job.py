from datetime import datetime
from app import db

# Junction Table for Helper & Skill
helper_skills = db.Table('helper_skills',
    db.Column('helper_id', db.Integer, db.ForeignKey('helpers.id', ondelete='CASCADE'), primary_key=True),
    db.Column('skill_id', db.Integer, db.ForeignKey('skills.id', ondelete='CASCADE'), primary_key=True)
)

# Junction Table for Job & Skill
job_skills = db.Table('job_skills',
    db.Column('job_id', db.Integer, db.ForeignKey('jobs.id', ondelete='CASCADE'), primary_key=True),
    db.Column('skill_id', db.Integer, db.ForeignKey('skills.id', ondelete='CASCADE'), primary_key=True)
)


class Skill(db.Model):
    """Master Skills lookup table."""
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)  # e.g., 'cook', 'maid', 'driver'
    skill_name = db.Column(db.String(100), unique=True, nullable=False)

    # Relationships
    helpers = db.relationship('Helper', secondary=helper_skills, back_populates='skills')
    jobs = db.relationship('Job', secondary=job_skills, back_populates='skills')

    def __repr__(self):
        return f"<Skill category={self.category} name={self.skill_name}>"


class HelperExperience(db.Model):
    """Past employment references of Helpers."""
    __tablename__ = 'helper_experience'

    id = db.Column(db.Integer, primary_key=True)
    helper_id = db.Column(db.Integer, db.ForeignKey('helpers.id', ondelete='CASCADE'), nullable=False)
    employer_name = db.Column(db.String(150), nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    role_description = db.Column(db.Text, nullable=True)
    verification_status = db.Column(db.Enum('pending', 'verified', 'invalid', name='exp_verification_status'), default='pending')

    def __repr__(self):
        return f"<HelperExperience helper_id={self.helper_id} employer={self.employer_name}>"


class Job(db.Model):
    """Job listing model posted by Employers."""
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    employer_id = db.Column(db.Integer, db.ForeignKey('employers.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # e.g., 'cook', 'maid', 'driver'
    salary_offered = db.Column(db.Numeric(10, 2), nullable=False)
    working_hours_start = db.Column(db.Time, nullable=True)
    working_hours_end = db.Column(db.Time, nullable=True)
    gender_preference = db.Column(db.Enum('male', 'female', 'no_preference', name='gender_pref'), default='no_preference')
    language_requirements = db.Column(db.String(255), nullable=True)
    experience_required_years = db.Column(db.Integer, default=0)
    accommodation_provided = db.Column(db.Boolean, default=False)
    food_provided = db.Column(db.Boolean, default=False)
    weekly_off_day = db.Column(db.String(50), nullable=True)
    address_pincode = db.Column(db.String(20), nullable=False)
    latitude = db.Column(db.Numeric(10, 8), nullable=True)
    longitude = db.Column(db.Numeric(11, 8), nullable=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.Enum('open', 'closed', 'paused', name='job_status'), default='open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    skills = db.relationship('Skill', secondary=job_skills, back_populates='jobs')
    applications = db.relationship('Application', backref='job', lazy='dynamic', cascade="all, delete-orphan")
    saved_by_helpers = db.relationship('SavedJob', backref='job', lazy='dynamic', cascade="all, delete-orphan")
    reviews = db.relationship('Review', backref='job', lazy='dynamic')

    def __repr__(self):
        return f"<Job id={self.id} title={self.title} status={self.status}>"
