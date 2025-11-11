from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Spec(Base):
    __tablename__ = "specs"
    spec_id = Column(String, primary_key=True)
    user_id = Column(String, index=True)
    project_id = Column(String, index=True)
    prompt = Column(Text)
    spec_json = Column(JSON)
    spec_version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class Evaluation(Base):
    __tablename__ = "evaluations"
    eval_id = Column(String, primary_key=True)
    spec_id = Column(String, ForeignKey("specs.spec_id"))
    user_id = Column(String, index=True)
    score = Column(Integer)
    notes = Column(Text)
    ts = Column(DateTime, default=datetime.datetime.utcnow)

class Iteration(Base):
    __tablename__ = "iterations"
    iter_id = Column(String, primary_key=True)
    spec_id = Column(String, ForeignKey("specs.spec_id"))
    before_spec = Column(JSON)
    after_spec = Column(JSON)
    feedback = Column(Text)
    ts = Column(DateTime, default=datetime.datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    event = Column(String)
    user_id = Column(String)
    ts = Column(DateTime, default=datetime.datetime.utcnow)

class RLHFFeedback(Base):
    __tablename__ = "rlhf_feedback"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, index=True)
    spec_a_id = Column(String, ForeignKey("specs.spec_id"))  # First design
    spec_b_id = Column(String, ForeignKey("specs.spec_id"))  # Second design
    preference = Column(String)  # "A", "B", or "tie"
    feedback_text = Column(Text)  # Optional text feedback
    rating_a = Column(Integer)  # 1-5 rating for design A
    rating_b = Column(Integer)  # 1-5 rating for design B
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class RLHFPreferences(Base):
    __tablename__ = "rlhf_preferences"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, index=True)
    prompt = Column(Text)  # Original prompt
    chosen_spec = Column(JSON)  # Preferred design spec
    rejected_spec = Column(JSON)  # Rejected design spec
    preference_strength = Column(Integer)  # 1-5 how strong the preference
    created_at = Column(DateTime, default=datetime.datetime.utcnow)