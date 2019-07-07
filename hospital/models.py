from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from hospital import db
from hospital import login


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    email = db.Column(db.String(120), index=True, unique=True)
    specialization = db.Column(db.String(120), nullable=True)
    checked = db.Column(db.Boolean)
    password_hash = db.Column(db.String(128))
    doctor = db.relationship('User', backref='assigned_patients', remote_side=[id])
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    diagnosis = db.relationship('Diagnosis', backref='patient')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @login.user_loader
    def load_user(id):
        return User.query.get(int(id))


class Diagnosis(UserMixin, db.Model):
    __tablename__ = 'diagnosis'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    explanation = db.Column(db.String(1024))
    diagnosed_by = db.Column(db.String(64))
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
