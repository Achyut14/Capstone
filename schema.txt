
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)

class CreateUsers(db.Model):
    """Users Model"""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(120),  nullable=False)
    lastname = db.Column(db.String(120),  nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


    @classmethod
    def register(cls, first_name, last_name, email, username, password):
        """Register User and add to database"""

        hashed = generate_password_hash(password, method="sha256")

        user = cls(firstname=first_name,
                   lastname=last_name,
                   email=email,
                   username=username,
                   password=hashed)
        
        try:
            db.session.add(user)
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            print(f"Error during registration: {e}")
            return None

