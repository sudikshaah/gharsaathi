from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, IntegerField, DecimalField, TimeField, TextAreaField, FileField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, NumberRange, Optional
from app.models.user import User

class LoginForm(FlaskForm):
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=8, max=15)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')

class RegisterForm(FlaskForm):
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=8, max=15)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=50)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    role = SelectField('Register As', choices=[('employer', 'Household Employer'), ('helper', 'Domestic Helper')], validators=[DataRequired()])

    def validate_phone_number(self, phone_number):
        user = User.query.filter_by(phone_number=phone_number.data).first()
        if user:
            raise ValidationError('Phone number is already registered.')

class EmployerProfileForm(FlaskForm):
    family_name = StringField('Family Name', validators=[DataRequired(), Length(max=100)])
    address_line1 = StringField('Address Line 1', validators=[DataRequired(), Length(max=255)])
    address_line2 = StringField('Address Line 2 (Optional)', validators=[Length(max=255)])
    city = StringField('City', validators=[DataRequired(), Length(max=100)])
    state = StringField('State', validators=[DataRequired(), Length(max=100)])
    pincode = StringField('Pincode / Zipcode', validators=[DataRequired(), Length(min=4, max=10)])
    latitude = DecimalField('Latitude (Optional)', places=8, validators=[Optional()])
    longitude = DecimalField('Longitude (Optional)', places=8, validators=[Optional()])

class HelperProfileForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=150)])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=18, max=75)])
    gender = SelectField('Gender', choices=[('female', 'Female'), ('male', 'Male'), ('other', 'Other')], validators=[DataRequired()])
    religion = StringField('Religion', validators=[Optional(), Length(max=50)])
    languages_spoken = StringField('Languages Spoken (comma separated)', validators=[Optional()])
    experience_years = IntegerField('Years of Experience', validators=[DataRequired(), NumberRange(min=0, max=50)])
    education_level = StringField('Education Level', validators=[Optional(), Length(max=100)])
    expected_salary = DecimalField('Expected Salary (per month)', places=2, validators=[DataRequired()])
    work_type = SelectField('Work Style', choices=[('live_out', 'Live-Out (Part Time / Daily)'), ('live_in', 'Live-In (Full Time Stay)'), ('both', 'Open to Both')], validators=[DataRequired()])
    location_pincode = StringField('Pincode / Zipcode', validators=[DataRequired(), Length(min=4, max=10)])
    latitude = DecimalField('Latitude (Optional)', places=8, validators=[Optional()])
    longitude = DecimalField('Longitude (Optional)', places=8, validators=[Optional()])

class JobForm(FlaskForm):
    title = StringField('Job Title', validators=[DataRequired(), Length(max=150)])
    category = SelectField('Job Category', choices=[
        ('cook', 'Cook / Chef'),
        ('maid', 'House Maid / Cleaning'),
        ('driver', 'Driver'),
        ('babysitter', 'Babysitter / Nanny'),
        ('caregiver', 'Elderly Caregiver')
    ], validators=[DataRequired()])
    salary_offered = DecimalField('Salary Offered (per month)', places=2, validators=[DataRequired()])
    working_hours_start = TimeField('Work Hours Start Time', validators=[Optional()])
    working_hours_end = TimeField('Work Hours End Time', validators=[Optional()])
    gender_preference = SelectField('Gender Preference', choices=[
        ('no_preference', 'No Preference'),
        ('female', 'Female'),
        ('male', 'Male')
    ], default='no_preference')
    language_requirements = StringField('Language Requirements', validators=[Optional(), Length(max=255)])
    experience_required_years = IntegerField('Minimum Experience Required (Years)', default=0, validators=[NumberRange(min=0, max=50)])
    accommodation_provided = BooleanField('Accommodation / Stay Provided')
    food_provided = BooleanField('Food Provided')
    weekly_off_day = StringField('Weekly Off Day (e.g. Sunday)', validators=[Optional(), Length(max=50)])
    address_pincode = StringField('Pincode / Zipcode', validators=[DataRequired(), Length(min=4, max=10)])
    latitude = DecimalField('Latitude (Optional)', places=8, validators=[Optional()])
    longitude = DecimalField('Longitude (Optional)', places=8, validators=[Optional()])
    description = TextAreaField('Job Description / Responsibilities', validators=[Optional()])

class DocumentUploadForm(FlaskForm):
    document_type = SelectField('Document Type', choices=[
        ('aadhaar', 'Aadhaar Card / ID Proof'),
        ('police_clearance', 'Police Clearance Certificate (PCC)'),
        ('address_proof', 'Utility Bill / Rent Agreement (Address Proof)'),
        ('vaccine_cert', 'COVID-19 Vaccination Certificate')
    ], validators=[DataRequired()])
    document_file = FileField('Upload Document (PDF, PNG, JPG)', validators=[DataRequired()])

class ReviewForm(FlaskForm):
    rating = IntegerField('Rating (1-5 Stars)', validators=[DataRequired(), NumberRange(min=1, max=5)])
    comment = TextAreaField('Feedback Comment', validators=[Optional(), Length(max=500)])

class ComplaintForm(FlaskForm):
    category = SelectField('Dispute Category', choices=[
        ('abuse', 'Abusive Behavior / Harassment'),
        ('no_show', 'Continuous Absence / No-Show'),
        ('theft', 'Theft or Property Damage'),
        ('payment_dispute', 'Salary Payment Issue'),
        ('other', 'Other Issue')
    ], validators=[DataRequired()])
    description = TextAreaField('Dispute Details', validators=[DataRequired(), Length(min=10, max=1000)])
