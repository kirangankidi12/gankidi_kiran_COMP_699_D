from app import create_app, db
from app.models.user import User
from app.models.admin import SystemAdmin


def create_admin():

    app = create_app()

    with app.app_context():

        # 🔹 CHANGE THESE DETAILS
        name = "Gankid"
        email = "gankid@company.com"
        password = "admin123"

        # Check if admin already exists
        existing = User.query.filter_by(email=email).first()
        if existing:
            print("⚠️ Admin already exists!")
            return

        # Create user
        user = User(
            name=name,
            email=email,
            role="ADMIN",
            status="ACTIVE"
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        # Create admin profile
        admin = SystemAdmin(user_id=user.id)
        db.session.add(admin)
        db.session.commit()

        print("✅ Admin created successfully!")
        print(f"Email: {email}")
        print(f"Password: {password}")


if __name__ == "__main__":
    create_admin()