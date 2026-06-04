from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Float
from sqlalchemy.orm import relationship
import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    membership_until = Column(DateTime, nullable=True)
    is_admin = Column(Boolean, default=False)

    payments = relationship("Payment", back_populates="user")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    reference = Column(String, unique=True, index=True)
    amount = Column(Float)
    plan_days = Column(Integer)
    status = Column(String, default="pending") # pending, approved, rejected
    date = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="payments")

class Animal(Base):
    __tablename__ = "animals"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String, unique=True, index=True) # string because of "00"
    name = Column(String)
    image_url = Column(String, nullable=True)

class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, index=True) # YYYY-MM-DD
    time = Column(String, index=True) # HH:MM AM/PM
    animal_number = Column(String, ForeignKey("animals.number"))
