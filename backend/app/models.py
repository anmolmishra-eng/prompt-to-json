import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


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
