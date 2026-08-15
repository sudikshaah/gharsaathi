from datetime import datetime
from app import db

class Application(db.Model):
    """Job application tracker."""
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False)
    helper_id = db.Column(db.Integer, db.ForeignKey('helpers.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.Enum('applied', 'shortlisted', 'interviewed', 'offered', 'hired', 'rejected', 'withdrawn', name='app_status'), default='applied')
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Application id={self.id} job_id={self.job_id} helper_id={self.helper_id} status={self.status}>"


class Shortlist(db.Model):
    """Employer's list of shortlisted Helpers."""
    __tablename__ = 'shortlists'

    id = db.Column(db.Integer, primary_key=True)
    employer_id = db.Column(db.Integer, db.ForeignKey('employers.id', ondelete='CASCADE'), nullable=False)
    helper_id = db.Column(db.Integer, db.ForeignKey('helpers.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Shortlist employer_id={self.employer_id} helper_id={self.helper_id}>"


class SavedJob(db.Model):
    """Helper's list of saved jobs."""
    __tablename__ = 'saved_jobs'

    id = db.Column(db.Integer, primary_key=True)
    helper_id = db.Column(db.Integer, db.ForeignKey('helpers.id', ondelete='CASCADE'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<SavedJob helper_id={self.helper_id} job_id={self.job_id}>"


class Review(db.Model):
    """Two-way rating & review system."""
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    reviewer_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    reviewee_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id', ondelete='SET NULL'), nullable=True)
    rating = db.Column(db.Integer, nullable=False)  # 1 to 5 stars
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Simple validation helper could be added, but standard constraint is in forms.
    def __repr__(self):
        return f"<Review from={self.reviewer_user_id} to={self.reviewee_user_id} rating={self.rating}>"


class Message(db.Model):
    """Direct in-app messaging."""
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Message id={self.id} sender={self.sender_id} recipient={self.recipient_id}>"


class Complaint(db.Model):
    """Disputes and Reporting mechanism."""
    __tablename__ = 'complaints'

    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    reported_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    category = db.Column(db.Enum('abuse', 'no_show', 'theft', 'payment_dispute', 'other', name='complaint_cat'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum('pending', 'investigating', 'resolved', 'dismissed', name='complaint_status'), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Complaint id={self.id} reporter={self.reporter_id} status={self.status}>"
