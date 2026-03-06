from sqlalchemy import Column, Integer, String, Text, Date, Time, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    timezone = Column(String(50), default="UTC")
    daily_hours_available = Column(Integer, default=8)
    wake_time = Column(String(10), default="07:00")
    sleep_time = Column(String(10), default="23:00")
    current_skills = Column(Text, default="")
    constraints = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    schedules = relationship("DailySchedule", back_populates="user", cascade="all, delete-orphan")
    reflections = relationship("WeeklyReflection", back_populates="user", cascade="all, delete-orphan")

class Goal(Base):
    __tablename__ = "goals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    goal_text = Column(Text, nullable=False)
    goal_summary = Column(Text)
    deadline = Column(Date)
    priority = Column(String(20), default="medium")
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="goals")
    milestones = relationship("Milestone", back_populates="goal", cascade="all, delete-orphan")

class Milestone(Base):
    __tablename__ = "milestones"
    
    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("goals.id", ondelete="CASCADE"), index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    deadline = Column(Date)
    progress = Column(Float, default=0.0)
    estimated_duration_weeks = Column(Integer)
    status = Column(String(20), default="active")
    
    goal = relationship("Goal", back_populates="milestones")
    tasks = relationship("Task", back_populates="milestone", cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    milestone_id = Column(Integer, ForeignKey("milestones.id", ondelete="CASCADE"), index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    estimated_time_minutes = Column(Integer)
    difficulty = Column(String(20))
    priority = Column(String(20))
    category = Column(String(50))
    deadline = Column(DateTime)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    milestone = relationship("Milestone", back_populates="tasks")
    schedules = relationship("DailySchedule", back_populates="task", cascade="all, delete-orphan")
    performance_logs = relationship("PerformanceLog", back_populates="task", cascade="all, delete-orphan")

class DailySchedule(Base):
    __tablename__ = "daily_schedule"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), index=True)
    schedule_date = Column(Date, nullable=False, index=True)
    start_time = Column(String(10))
    end_time = Column(String(10))
    status = Column(String(20), default="pending")
    completion_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="schedules")
    task = relationship("Task", back_populates="schedules")

class PerformanceLog(Base):
    __tablename__ = "performance_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), index=True)
    completion_rate = Column(Float)
    delay_minutes = Column(Integer)
    feedback = Column(Text)
    logged_at = Column(DateTime, default=datetime.utcnow)
    
    task = relationship("Task", back_populates="performance_logs")

class WeeklyReflection(Base):
    __tablename__ = "weekly_reflections"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    week_start = Column(Date, nullable=False, index=True)
    went_well = Column(Text)
    challenges = Column(Text)
    changes_needed = Column(Text)
    ai_analysis = Column(Text)
    completion_rate = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="reflections")
