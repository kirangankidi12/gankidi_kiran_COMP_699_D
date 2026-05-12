from app import create_app, db
from app.models.user import User
from app.models.staff import ClinicStaff


def create_staff():

    app = create_app()

    with app.app_context():

        #  STANDARD GANKIDI STAFF DETAILS
        staff_accounts = [
            {
                "name": "Gankidi Nurse",
                "email": "nurse@gankidi.com",
                "password": "gankidi123",
                "role": "Nurse"
            },
            {
                "name": "Gankidi Reception",
                "email": "reception@gankidi.com",
                "password": "gankidi123",
                "role": "Receptionist"
            }
        ]

        for acc in staff_accounts:

            existing = User.query.filter_by(email=acc["email"]).first()
            if existing:
                print(f"⚠️ {acc['email']} already exists")
                continue

            # Create user
            user = User(
                name=acc["name"],
                email=acc["email"],
                role="STAFF",
                status="ACTIVE"
            )
            user.set_password(acc["password"])

            db.session.add(user)
            db.session.commit()

            # Create staff profile (NOT approved yet)
            staff = ClinicStaff(
                user_id=user.id,
                role=acc["role"],
                is_approved=False   # IMPORTANT for workflow
            )

            db.session.add(staff)
            db.session.commit()

            print(f"✅ Staff created: {acc['email']} (Pending approval)")

        print("\n🔐 Default Password for all staff: gankidi123")


if __name__ == "__main__":
    create_staff()