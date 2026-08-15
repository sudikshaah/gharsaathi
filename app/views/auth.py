from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.forms import LoginForm, RegisterForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user (Employer or Helper)."""
    if current_user.is_authenticated:
        return redirect_to_dashboard(current_user)
        
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            phone_number=form.phone_number.data,
            role=form.role.data,
            is_active=True
        )
        user.password = form.password.data  # Triggers hashing setter
        
        db.session.add(user)
        db.session.commit()
        
        # Log the user in automatically
        login_user(user)
        flash("Registration successful! Let's complete your profile setup.", "success")
        
        if user.role == 'employer':
            return redirect(url_for('employer.setup_profile'))
        else:
            return redirect(url_for('helper.setup_profile'))
            
    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login an existing user."""
    if current_user.is_authenticated:
        return redirect_to_dashboard(current_user)
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(phone_number=form.phone_number.data).first()
        
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash("Your account has been deactivated. Please contact support.", "danger")
                return redirect(url_for('auth.login'))
                
            login_user(user, remember=form.remember_me.data)
            flash("Logged in successfully!", "success")
            
            # Check for next parameter in query string
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect_to_dashboard(user)
        else:
            flash("Invalid phone number or password.", "danger")
            
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """Log out current user."""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('public.index'))

def redirect_to_dashboard(user):
    """Helper method to redirect users to their role-specific dashboard."""
    if user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    elif user.role == 'employer':
        # Check if employer has set up profile
        if not user.employer_profile:
            return redirect(url_for('employer.setup_profile'))
        return redirect(url_for('employer.dashboard'))
    elif user.role == 'helper':
        # Check if helper has set up profile
        if not user.helper_profile:
            return redirect(url_for('helper.setup_profile'))
        return redirect(url_for('helper.dashboard'))
    return redirect(url_for('public.index'))
