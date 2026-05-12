from flask import Blueprint, render_template, redirect, request, session, flash
from app.utils.decorators import login_required, role_required
from app import db

from app.models.user import User
from app.models.staff import ClinicStaff
from app.models.patient import Patient
from app.models.symptom import SymptomRecord

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# ---------------- HELPER ----------------
def is_admin():
    return session.get('role') == "ADMIN"


# ---------------- DASHBOARD ----------------
@admin_bp.route('/dashboard')
@login_required
@role_required("ADMIN")
def dashboard():

    total_users = User.query.count()
    total_patients = Patient.query.count()
    total_staff = ClinicStaff.query.count()

    return render_template(
        'admin/dashboard.html',
        total_users=total_users,
        total_patients=total_patients,
        total_staff=total_staff
    )


# ---------------- USER MANAGEMENT ----------------
@admin_bp.route('/users')
@login_required
@role_required("ADMIN")
def users():

    users = User.query.all()

    return render_template(
        'admin/users.html',
        users=users
    )


# ---------------- APPROVE STAFF ----------------
@admin_bp.route('/approve_staff/<int:user_id>')
@login_required
@role_required("ADMIN")
def approve_staff(user_id):

    staff = ClinicStaff.query.filter_by(user_id=user_id).first()

    if not staff:
        flash("Staff record not found")
        return redirect('/admin/users')

    staff.is_approved = True
    db.session.commit()

    flash("Staff approved successfully")
    return redirect('/admin/users')


# ---------------- LOGS ----------------
@admin_bp.route('/logs')
@login_required
@role_required("ADMIN")
def logs():

    # Simulated logs (can be replaced with real logging later)
    logs = [
        {"time": "2026-04-23 10:30", "event": "Model Prediction", "status": "Success"},
        {"time": "2026-04-23 10:35", "event": "Reminder Trigger", "status": "Success"},
        {"time": "2026-04-23 10:40", "event": "User Login Attempt", "status": "Success"},
    ]

    return render_template(
        'admin/logs.html',
        logs=logs
    )


# ---------------- SETTINGS ----------------
@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@role_required("ADMIN")
def settings():

    if request.method == 'POST':
        max_users = request.form.get('max_users')
        response_time = request.form.get('response_time')

        # For now, just simulate save
        flash("Settings updated successfully")

    return render_template('admin/settings.html')


# ---------------- REFRESH MODEL ----------------
@admin_bp.route('/refresh_model', methods=['POST'])
@login_required
@role_required("ADMIN")
def refresh_model():

    # Simulated model refresh
    flash("Model refreshed successfully")

    return redirect('/admin/settings')