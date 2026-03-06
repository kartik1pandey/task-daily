"""FastAPI Backend for AI Life OS"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

from .database import get_db, init_db
from .services import LifeOSService
from .models import User

# Load environment variables
load_dotenv()

app = FastAPI(title="AI Life OS API", version="1.0.0")

# CORS - allow frontend
allowed_origins = [
    "http://localhost:3000",
    "https://*.vercel.app",
    os.getenv("FRONTEND_URL", "")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, use specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()

# Initialize planner (lazy loading)
planner = None

def get_planner():
    global planner
    if planner is None:
        from .planner import AIPlanner
        planner = AIPlanner(provider="groq")
    return planner

def get_service(db: Session = Depends(get_db)):
    """Get service instance"""
    return LifeOSService(db, get_planner())

# Pydantic Models
class UserCreate(BaseModel):
    email: str
    name: str = "User"
    daily_hours_available: int = 8
    current_skills: str = ""
    constraints: str = ""

class UserUpdate(BaseModel):
    name: Optional[str] = None
    daily_hours_available: Optional[int] = None
    wake_time: Optional[str] = None
    sleep_time: Optional[str] = None
    current_skills: Optional[str] = None
    constraints: Optional[str] = None

class GoalCreate(BaseModel):
    user_id: int
    goal_text: str
    deadline: Optional[date] = None

class TaskStatusUpdate(BaseModel):
    status: str  # completed, skipped, partial
    notes: str = ""

class DailyTaskRequest(BaseModel):
    user_id: int
    target_date: date

# Routes
@app.get("/")
def root():
    return {
        "message": "AI Life OS API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
def health_check():
    """Health check endpoint for deployment"""
    return {"status": "healthy"}

# User Management
@app.post("/users")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create or get user"""
    service = LifeOSService(db, get_planner())
    db_user = service.create_or_get_user(user.email, user.name)
    
    # Update user details
    if user.daily_hours_available:
        db_user.daily_hours_available = user.daily_hours_available
    if user.current_skills:
        db_user.current_skills = user.current_skills
    if user.constraints:
        db_user.constraints = user.constraints
    
    db.commit()
    db.refresh(db_user)
    
    return {
        "id": db_user.id,
        "email": db_user.email,
        "name": db_user.name,
        "daily_hours_available": db_user.daily_hours_available
    }

@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user details"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "daily_hours_available": user.daily_hours_available,
        "wake_time": user.wake_time,
        "sleep_time": user.sleep_time,
        "current_skills": user.current_skills,
        "constraints": user.constraints
    }

@app.put("/users/{user_id}")
def update_user(user_id: int, updates: UserUpdate, db: Session = Depends(get_db)):
    """Update user details"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if updates.name:
        user.name = updates.name
    if updates.daily_hours_available:
        user.daily_hours_available = updates.daily_hours_available
    if updates.wake_time:
        user.wake_time = updates.wake_time
    if updates.sleep_time:
        user.sleep_time = updates.sleep_time
    if updates.current_skills is not None:
        user.current_skills = updates.current_skills
    if updates.constraints is not None:
        user.constraints = updates.constraints
    
    db.commit()
    db.refresh(user)
    
    return {"message": "User updated", "user_id": user.id}

# Goal Management
@app.post("/goals")
def create_goal(goal: GoalCreate, service: LifeOSService = Depends(get_service)):
    """Create goal and generate AI-powered plan"""
    try:
        db_goal = service.create_goal_with_plan(
            user_id=goal.user_id,
            goal_text=goal.goal_text,
            deadline=goal.deadline
        )
        
        return {
            "goal_id": db_goal.id,
            "goal_text": db_goal.goal_text,
            "goal_summary": db_goal.goal_summary,
            "milestones_count": len(db_goal.milestones),
            "total_tasks": sum(len(m.tasks) for m in db_goal.milestones)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/goals/{goal_id}")
def get_goal(goal_id: int, db: Session = Depends(get_db)):
    """Get goal with milestones and tasks"""
    from .models import Goal
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    milestones = []
    for milestone in goal.milestones:
        tasks = []
        for task in milestone.tasks:
            tasks.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "estimated_time_minutes": task.estimated_time_minutes,
                "priority": task.priority,
                "category": task.category,
                "status": task.status
            })
        
        milestones.append({
            "id": milestone.id,
            "title": milestone.title,
            "description": milestone.description,
            "progress": milestone.progress,
            "status": milestone.status,
            "tasks": tasks
        })
    
    return {
        "id": goal.id,
        "goal_text": goal.goal_text,
        "goal_summary": goal.goal_summary,
        "status": goal.status,
        "milestones": milestones
    }

@app.get("/users/{user_id}/goals")
def get_user_goals(user_id: int, db: Session = Depends(get_db)):
    """Get all goals for a user"""
    from .models import Goal
    goals = db.query(Goal).filter(Goal.user_id == user_id).all()
    
    return [{
        "id": g.id,
        "goal_text": g.goal_text,
        "goal_summary": g.goal_summary,
        "status": g.status,
        "milestones_count": len(g.milestones),
        "created_at": g.created_at.isoformat()
    } for g in goals]

# Daily Tasks
@app.post("/daily-tasks/generate")
def generate_daily_tasks(request: DailyTaskRequest, service: LifeOSService = Depends(get_service)):
    """Generate AI-powered daily tasks with context"""
    try:
        schedules = service.generate_daily_tasks(request.user_id, request.target_date)
        
        return {
            "date": request.target_date.isoformat(),
            "tasks_count": len(schedules),
            "message": f"Generated {len(schedules)} tasks for {request.target_date}"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/daily-tasks/{user_id}/{target_date}")
def get_daily_tasks(user_id: int, target_date: date, service: LifeOSService = Depends(get_service)):
    """Get tasks for a specific day"""
    try:
        tasks = service.get_daily_tasks(user_id, target_date)
        return {
            "date": target_date.isoformat(),
            "tasks": tasks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/daily-tasks/{schedule_id}")
def update_task_status(schedule_id: int, update: TaskStatusUpdate, service: LifeOSService = Depends(get_service)):
    """Update task completion status"""
    try:
        schedule = service.update_task_status(schedule_id, update.status, update.notes)
        return {
            "schedule_id": schedule.id,
            "status": schedule.status,
            "message": "Task updated successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Context and Analytics
@app.get("/users/{user_id}/context")
def get_user_context(user_id: int, service: LifeOSService = Depends(get_service)):
    """Get full user context for AI planning"""
    try:
        context = service.get_user_context(user_id)
        return context
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}/stats")
def get_user_stats(user_id: int, db: Session = Depends(get_db)):
    """Get user statistics"""
    from .models import Goal, Task, DailySchedule, Milestone
    from datetime import timedelta
    
    # Get counts
    goals_count = db.query(Goal).filter(Goal.user_id == user_id).count()
    
    # Get tasks from user's goals
    tasks = db.query(Task).join(Task.milestone).join(Milestone.goal).filter(
        Goal.user_id == user_id
    ).all()
    
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.status == "completed")
    
    # Get recent completion rate
    last_7_days = date.today() - timedelta(days=7)
    recent_schedules = db.query(DailySchedule).filter(
        DailySchedule.user_id == user_id,
        DailySchedule.schedule_date >= last_7_days
    ).all()
    
    completed_recent = sum(1 for s in recent_schedules if s.status == "completed")
    total_recent = len(recent_schedules)
    completion_rate = (completed_recent / total_recent * 100) if total_recent > 0 else 0
    
    return {
        "goals_count": goals_count,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "completion_rate_7days": round(completion_rate, 1),
        "tasks_this_week": total_recent
    }

# Automation Endpoints
@app.post("/automation/daily/{user_id}")
def run_daily_automation(user_id: int, db: Session = Depends(get_db)):
    """Run daily automation: check progress and generate tasks"""
    from .automation import DailyAutomation
    
    try:
        automation = DailyAutomation(db, get_planner())
        result = automation.run_daily_automation(user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/automation/check-and-generate/{user_id}")
def check_and_generate_tasks(user_id: int, db: Session = Depends(get_db)):
    """Check if today's tasks exist, generate if not"""
    from .automation import DailyAutomation
    
    try:
        automation = DailyAutomation(db, get_planner())
        result = automation.check_and_generate_if_needed(user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/automation/generate-week/{user_id}")
def generate_week_tasks(user_id: int, days: int = 7, db: Session = Depends(get_db)):
    """Generate tasks for the next N days"""
    from .automation import DailyAutomation
    
    try:
        automation = DailyAutomation(db, get_planner())
        result = automation.generate_next_n_days(user_id, days)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/automation/cron-daily")
def cron_daily_automation(db: Session = Depends(get_db)):
    """Cron endpoint to run automation for all users"""
    from .automation import run_automation_for_all_users
    
    try:
        results = run_automation_for_all_users(db)
        return {
            "status": "success",
            "users_processed": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
