from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from memory_layer.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    age = Column(Integer)
    hobbies = Column(String)
    language = Column(String)


class FlaggedResponse(Base):
    __tablename__ = "flagged_responses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    input_text = Column(Text, nullable=False)
    response_text = Column(Text, nullable=False)
    reason = Column(String, nullable=False)
    confidence_score = Column(Float)

    conversation_id = Column(String, index=True, nullable=True)  # Add this line

    context = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")
    replacement_text = Column(Text, nullable=True)

    user = relationship("User")
