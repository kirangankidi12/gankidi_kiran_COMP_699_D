from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from app.utils.decorators import login_required, role_required
from app import db

from app.models.user import User
from app.models.patient import Patient
from app.models.symptom import SymptomRecord
from app.models.recommendation import Recommendation
from app.models.reminder import Reminder

from app.services.ml_engine import MLEngine
from app.services.risk_calculator import RiskCalculator
from app.services.rule_engine import RuleEngine
from app.services.reminder_service import ReminderService

from datetime import datetime

patient_bp = Blueprint('patient', __name__, url_prefix='/patient')


# ---------------- HELPER ----------------
def get_current_patient():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return Patient.query.filter_by(user_id=user_id).first()


# ---------------- DASHBOARD ----------------
@patient_bp.route('/dashboard')
@login_required
@role_required("PATIENT")
def dashboard():
    patient = get_current_patient()

    if not patient:
        flash("Patient profile not found")
        return redirect('/login')

    symptoms = SymptomRecord.query.filter_by(patient_id=patient.id).all()
    reminders = Reminder.query.filter_by(patient_id=patient.id).all()

    return render_template(
        'patient/dashboard.html',
        patient=patient,
        symptoms=symptoms,
        reminders=reminders
    )


# ---------------- IMPROVED LLM REASONING ----------------
def llm_reasoning(symptom_text):
    text = symptom_text.lower()

    # 🔴 Strong cardiac detection
    if (
        ("heart" in text or "chest" in text or "left side" in text)
        and ("pain" in text or "hurting" in text or "pressure" in text)
    ):
        return "High"

    # 🔴 Breathing related
    if "breathing" in text or "shortness" in text:
        return "High"

    # 🔴 Severe indicators
    if "severe" in text or "extreme" in text:
        return "High"

    # 🟡 Moderate indicators
    if "moderate" in text:
        return "Medium"

    # 🟢 Mild indicators
    if "mild" in text or "slight" in text:
        return "Low"

    return "Low"


# ---------------- ENTER SYMPTOMS ----------------
@patient_bp.route('/symptoms', methods=['GET', 'POST'])
@login_required
@role_required("PATIENT")
def symptoms():

    patient = get_current_patient()
    if not patient:
        flash("Invalid session")
        return redirect('/login')

    if request.method == 'POST':

        symptom_text = request.form.get('symptom_text')
        duration = request.form.get('duration')
        age = request.form.get('age')
        history_factor = request.form.get('history', "1")
        consent = request.form.get('consent')

        # ---------------- VALIDATION ----------------
        if not symptom_text or not symptom_text.strip():
            flash("Symptoms cannot be empty")
            return redirect('/patient/symptoms')

        if not duration:
            flash("Please select duration")
            return redirect('/patient/symptoms')

        if not age or not age.isdigit():
            flash("Invalid age")
            return redirect('/patient/symptoms')

        age = int(age)
        if age < 1 or age > 120:
            flash("Age must be between 1 and 120")
            return redirect('/patient/symptoms')

        try:
            history_factor = int(history_factor)
        except:
            history_factor = 1

        if not consent:
            flash("Please accept disclaimer")
            return redirect('/patient/symptoms')

        # ---------------- SAVE SYMPTOM ----------------
        symptom = SymptomRecord(
            patient_id=patient.id,
            symptom_text=symptom_text,
            duration=duration,
            severity=1
        )
        db.session.add(symptom)
        db.session.commit()

        # ---------------- AI PROCESSING ----------------
        risk_service = RiskCalculator()
        ml_engine = MLEngine()
        rule_engine = RuleEngine()

        risk_score, severity = risk_service.calculate(symptom_text, history_factor)
        risk_level = risk_service.risk_level(risk_score)

        ml_prediction = ml_engine.classify(symptom_text, duration, age, history_factor)

        llm_level = llm_reasoning(symptom_text)

        # 🔥 Duration intelligence
        long_duration = duration.lower() in ["1 week", "2 weeks", "chronic"]

        # ---------------- FINAL DECISION ----------------
        if llm_level == "High":
            final_level = "High"

        elif risk_level == "High":
            final_level = "High"

        elif long_duration and risk_level == "Low":
            final_level = "Medium"

        elif risk_level == "Medium":
            final_level = "Medium"

        else:
            final_level = "Low"

        # ---------------- GUIDANCE ----------------
        guidance_data = rule_engine.generate_guidance(final_level)

        # ---------------- SAVE RESULT ----------------
        symptom.severity = severity

        recommendation = Recommendation(
            symptom_id=symptom.id,
            risk_score=risk_score,
            urgency_level=final_level,
            care_option=guidance_data["care"],
            explanation=guidance_data["explanation"]
        )

        db.session.add(recommendation)
        db.session.commit()

        return redirect(url_for('patient.result', symptom_id=symptom.id))

    return render_template('patient/symptoms.html')


# ---------------- RESULT ----------------
@patient_bp.route('/result/<int:symptom_id>')
@login_required
@role_required("PATIENT")
def result(symptom_id):

    patient = get_current_patient()
    symptom = SymptomRecord.query.get(symptom_id)

    if not symptom or symptom.patient_id != patient.id:
        flash("Invalid access")
        return redirect('/patient/dashboard')

    recommendation = Recommendation.query.filter_by(symptom_id=symptom_id).first()

    return render_template(
        'patient/result.html',
        symptom=symptom,
        recommendation=recommendation
    )


# ---------------- HISTORY ----------------
@patient_bp.route('/history')
@login_required
@role_required("PATIENT")
def history():

    patient = get_current_patient()
    records = SymptomRecord.query.filter_by(patient_id=patient.id).all()

    return render_template('patient/history.html', records=records)


# ---------------- DELETE ----------------
@patient_bp.route('/delete/<int:symptom_id>')
@login_required
@role_required("PATIENT")
def delete_record(symptom_id):

    patient = get_current_patient()
    record = SymptomRecord.query.get(symptom_id)

    if record and record.patient_id == patient.id:
        db.session.delete(record)
        db.session.commit()
        flash("Record deleted successfully")
    else:
        flash("Unauthorized action")

    return redirect('/patient/history')


# ---------------- REMINDERS ----------------
@patient_bp.route('/reminders', methods=['GET', 'POST'])
@login_required
@role_required("PATIENT")
def reminders():

    patient = get_current_patient()
    reminder_service = ReminderService()

    if request.method == 'POST':
        reminder_time = request.form.get('reminder_time')

        if not reminder_time:
            flash("Please select date and time")
            return redirect('/patient/reminders')

        try:
            reminder_time = datetime.strptime(reminder_time, "%Y-%m-%dT%H:%M")
        except:
            flash("Invalid date format")
            return redirect('/patient/reminders')

        reminder_service.create_reminder(patient.id, reminder_time)
        flash("Reminder set successfully")

    reminders = reminder_service.get_active_reminders(patient.id)

    return render_template('patient/reminders.html', reminders=reminders)


# ---------------- CANCEL REMINDER ----------------
@patient_bp.route('/cancel_reminder/<int:reminder_id>')
@login_required
@role_required("PATIENT")
def cancel_reminder(reminder_id):

    reminder_service = ReminderService()
    reminder_service.cancel_reminder(reminder_id)

    flash("Reminder cancelled")
    return redirect('/patient/reminders')


# ---------------- PROFILE ----------------
@patient_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@role_required("PATIENT")
def profile():

    user_id = session.get('user_id')
    user = User.query.get(user_id)
    patient = get_current_patient()

    if request.method == 'POST':

        name = request.form.get('name')
        age = request.form.get('age')
        health_info = request.form.get('health_info')

        if not name:
            flash("Name cannot be empty")
            return redirect('/patient/profile')

        user.name = name

        if age:
            try:
                patient.age = int(age)
            except:
                flash("Invalid age")

        patient.health_info = health_info

        db.session.commit()
        flash("Profile updated successfully")

    return render_template('patient/profile.html', user=user, patient=patient)