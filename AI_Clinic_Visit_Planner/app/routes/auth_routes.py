from flask import Blueprint, render_template, request, redirect, session, flash
from app import db
from app.models.user import User
from app.models.patient import Patient
from app.models.staff import ClinicStaff
from app.models.admin import SystemAdmin
from app.utils.auth import login_user, logout_user

auth_bp = Blueprint('auth', __name__)


# ---------------- HOME (DEFAULT ROUTE) ----------------
# When app starts, open login page automatically
@auth_bp.route('/')
def home():
    return redirect('/login')


# ---------------- REGISTER (PATIENT ONLY) ----------------
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        # Validation
        if not name or not email or not password:
            flash("All fields are required")
            return redirect('/register')

        # Check existing user
        existing = User.query.filter_by(email=email).first()
        if existing:
            flash("User already exists")
            return redirect('/register')

        # Create user
        user = User(
            name=name,
            email=email,
            role="PATIENT",
            status="ACTIVE"
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        # Create patient profile
        patient = Patient(user_id=user.id)
        db.session.add(patient)
        db.session.commit()

        flash("Registration successful. Please login.")
        return redirect('/login')

    return render_template('register.html')


# ---------------- LOGIN ----------------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form.get('email')
        password = request.form.get('password')

        # Validation
        if not email or not password:
            flash("Please enter email and password")
            return redirect('/login')

        user = User.query.filter_by(email=email).first()

        # Check user exists
        if not user:
            flash("User not found")
            return redirect('/login')

        # Account lock check
        if user.failed_attempts >= 5:
            flash("Account locked due to multiple failed attempts")
            return redirect('/login')

        # Password check
        if not user.check_password(password):
            user.failed_attempts += 1
            db.session.commit()
            flash("Invalid credentials")
            return redirect('/login')

        # Reset failed attempts
        user.failed_attempts = 0
        db.session.commit()

        # Create session
        login_user(user)
        session['user_id'] = user.id
        session['role'] = user.role

        # ---------------- ROLE-BASED REDIRECT ----------------
        if user.role == "PATIENT":
            return redirect('/patient/dashboard')

        elif user.role == "STAFF":
            staff = ClinicStaff.query.filter_by(user_id=user.id).first()

            if not staff or not staff.is_approved:
                logout_user()
                session.clear()
                flash("Staff account not approved by admin")
                return redirect('/login')

            return redirect('/staff/dashboard')

        elif user.role == "ADMIN":
            return redirect('/admin/dashboard')

        else:
            logout_user()
            session.clear()
            flash("Invalid role")
            return redirect('/login')

    return render_template('login.html')


# ---------------- LOGOUT ----------------
@auth_bp.route('/logout')
def logout():
    logout_user()
    session.clear()
    flash("Logged out successfully")
    return redirect('/login')