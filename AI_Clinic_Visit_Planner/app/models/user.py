from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(db.Model):
    __tablename__ = "users"

    # ---------------- PRIMARY FIELDS ----------------
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)

    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(20), nullable=False)  # PATIENT, STAFF, ADMIN
    status = db.Column(db.String(20), default="ACTIVE")  # ACTIVE / PENDING / LOCKED

    failed_attempts = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ---------------- RELATIONSHIPS ----------------
    patient = db.relationship(
        "Patient",
        backref="user",
        uselist=False,
        cascade="all, delete"
    )

    staff = db.relationship(
        "ClinicStaff",
        backref="user",
        uselist=False,
        cascade="all, delete"
    )

    admin = db.relationship(
        "SystemAdmin",
        backref="user",
        uselist=False,
        cascade="all, delete"
    )

    # ---------------- PASSWORD METHODS ----------------
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # ---------------- STATUS METHODS ----------------
    def is_active(self):
        return self.status == "ACTIVE"

    def lock_account(self):
        self.status = "LOCKED"

    def reset_attempts(self):
        self.failed_attempts = 0

    def increment_attempts(self):
        self.failed_attempts += 1
        if self.failed_attempts >= 5:
            self.lock_account()

    # ---------------- ROLE CHECKS ----------------
    def is_patient(self):
        return self.role == "PATIENT"

    def is_staff(self):
        return self.role == "STAFF"

    def is_admin(self):
        return self.role == "ADMIN"

    # ---------------- STRING ----------------
    def __repr__(self):
        return f"<User {self.email} ({self.role})>"