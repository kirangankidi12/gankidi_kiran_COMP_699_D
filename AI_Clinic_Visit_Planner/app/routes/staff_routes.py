from flask import Blueprint, render_template, request, redirect, session, flash
from app.utils.decorators import login_required, role_required
from app import db

from app.models.user import User
from app.models.staff import ClinicStaff
from app.models.symptom import SymptomRecord
from app.models.recommendation import Recommendation

staff_bp = Blueprint('staff', __name__, url_prefix='/staff')


# ---------------- HELPER ----------------
def get_current_staff():
    user_id = session.get('user_id')
    return ClinicStaff.query.filter_by(user_id=user_id).first()


# ---------------- DASHBOARD ----------------
@staff_bp.route('/dashboard')
@login_required
@role_required("STAFF")
def dashboard():

    staff = get_current_staff()

    if not staff or not staff.is_approved:
        flash("Unauthorized access")
        return redirect('/login')

    # Simple stats
    total_visits = SymptomRecord.query.count()

    return render_template(
        'staff/dashboard.html',
        total_visits=total_visits
    )


# ---------------- TRENDS ----------------
@staff_bp.route('/trends')
@login_required
@role_required("STAFF")
def trends():

    staff = get_current_staff()

    if not staff or not staff.is_approved:
        flash("Unauthorized access")
        return redirect('/login')

    records = SymptomRecord.query.all()

    total_visits = len(records)
    high_cases = 0
    medium_cases = 0
    low_cases = 0

    for r in records:
        if r.recommendation:
            if r.recommendation.urgency_level == "High":
                high_cases += 1
            elif r.recommendation.urgency_level == "Medium":
                medium_cases += 1
            else:
                low_cases += 1

    return render_template(
        'staff/trends.html',
        total_visits=total_visits,
        high_cases=high_cases,
        medium_cases=medium_cases,
        low_cases=low_cases,
        records=records
    )


# ---------------- AVAILABILITY ----------------
@staff_bp.route('/availability', methods=['GET', 'POST'])
@login_required
@role_required("STAFF")
def availability():

    staff = get_current_staff()

    if not staff:
        flash("Staff profile not found")
        return redirect('/login')

    if request.method == 'POST':

        services = request.form.get('services')
        hours = request.form.get('hours')

        if not services or not hours:
            flash("All fields are required")
            return redirect('/staff/availability')

        staff.services = services
        staff.operating_hours = hours

        db.session.commit()
        flash("Availability updated successfully")

    return render_template(
        'staff/availability.html',
        staff=staff
    )