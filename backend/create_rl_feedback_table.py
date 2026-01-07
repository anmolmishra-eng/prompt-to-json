#!/usr/bin/env python3
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine
from app.models import RLLiveFeedback

RLLiveFeedback.__table__.create(engine, checkfirst=True)
print("RLLiveFeedback table created successfully")
