from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(150),nullable=False)
    email = db.Column(db.String(150),unique=True, nullable=False)
    password_hash = db.Column(db.String(128),nullable=False)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text, nullable = True)
    due_date = db.Column(db.DateTime, nullable=True)
    is_completed = db.Column(db.Boolean,default=False)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
