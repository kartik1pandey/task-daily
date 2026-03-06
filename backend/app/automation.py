"""Automated daily task generation and progress tracking"""

from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from .models import User, Goal, DailySchedule, Task, Milestone
from .services import LifeOSService
from .planner import AIPlanner
from .email_service import send_daily_mission_email
import logging

logger = logging.getLogger(__name__)

class DailyAutomation:
    def __init__(self, db: Session, planner: AIPlanner):
        self.db = db
        self.service = LifeOSService(db, planner)
        self.planner = planner
    
    def run_daily_automation(self, user_id: int, target_date: date = None) -> dict:
        """
        Main automation function that runs every morning:
        1. Check yesterday's progress
        2. Update milestone progress
        3. Generate today's tasks based on context
        4. Send email notification
        """
        if target_date is None:
            target_date = date.today()
        
        yesterday = target_date - timedelta(days=1)
        
        try:
            # Step 1: Analyze yesterday's performance
            yesterday_analysis = self._analyze_yesterday(user_id, yesterday)
            
            # Step 2: Update milestone progress
            self._update_milestone_progress(user_id)
            
            # Step 3: Check if tasks already exist for today
            existing_tasks = self.service.get_daily_tasks(user_id, target_date)
            if existing_tasks:
                logger.info(f"Tasks already exist for {target_date}")
                return {
                    "status": "already_exists",
                    "date": target_date.isoformat(),
                    "tasks_count": len(existing_tasks)
                }
            
            # Step 4: Generate today's tasks with full context
            schedules = self.service.generate_daily_tasks(user_id, target_date)
            
            # Step 5: Send email notification (optional)
            user = self.db.query(User).filter(User.id == user_id).first()
            if user and schedules:
                tasks_for_email = [
                    {
                        "title": s.task.title,
                        "estimated_time_minutes": s.task.estimated_time_minutes,
                        "date": target_date.isoformat()
                    }
                    for s in schedules
                ]
                
                try:
                    send_daily_mission_email(
                        user.email,
                        user.name,
                        tasks_for_email,
                        []
                    )
                except Exception as e:
                    logger.error(f"Failed to send email: {e}")
            
            return {
                "status": "success",
                "date": target_date.isoformat(),
                "tasks_generated": len(schedules),
                "yesterday_completion_rate": yesterday_analysis["completion_rate"],
                "adjustment": yesterday_analysis["adjustment"]
            }
            
        except Exception as e:
            logger.error(f"Daily automation failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _analyze_yesterday(self, user_id: int, yesterday: date) -> dict:
        """Analyze yesterday's task completion"""
        schedules = self.db.query(DailySchedule).filter(
            DailySchedule.user_id == user_id,
            DailySchedule.schedule_date == yesterday
        ).all()
        
        if not schedules:
            return {
                "completion_rate": 0.75,  # Default
                "adjustment": "No data from yesterday"
            }
        
        completed = sum(1 for s in schedules if s.status == "completed")
        total = len(schedules)
        completion_rate = completed / total if total > 0 else 0.75
        
        # Determine adjustment message
        if completion_rate < 0.5:
            adjustment = "Reducing workload - you struggled yesterday"
        elif completion_rate > 0.85:
            adjustment = "Increasing challenge - you're doing great!"
        else:
            adjustment = "Maintaining current pace"
        
        return {
            "completion_rate": completion_rate,
            "completed": completed,
            "total": total,
            "adjustment": adjustment
        }
    
    def _update_milestone_progress(self, user_id: int):
        """Update progress for all active milestones"""
        goals = self.db.query(Goal).filter(
            Goal.user_id == user_id,
            Goal.status == "active"
        ).all()
        
        for goal in goals:
            for milestone in goal.milestones:
                if milestone.status == "active":
                    total_tasks = len(milestone.tasks)
                    if total_tasks > 0:
                        completed_tasks = sum(1 for t in milestone.tasks if t.status == "completed")
                        milestone.progress = (completed_tasks / total_tasks) * 100
                        
                        if milestone.progress >= 100:
                            milestone.status = "completed"
        
        self.db.commit()
    
    def generate_next_n_days(self, user_id: int, days: int = 7) -> dict:
        """Generate tasks for the next N days"""
        results = []
        start_date = date.today()
        
        for i in range(days):
            target_date = start_date + timedelta(days=i)
            result = self.run_daily_automation(user_id, target_date)
            results.append(result)
        
        return {
            "status": "success",
            "days_generated": days,
            "results": results
        }
    
    def check_and_generate_if_needed(self, user_id: int) -> dict:
        """Check if today's tasks exist, generate if not"""
        today = date.today()
        existing_tasks = self.service.get_daily_tasks(user_id, today)
        
        if existing_tasks:
            return {
                "status": "exists",
                "message": "Tasks already exist for today",
                "tasks_count": len(existing_tasks)
            }
        
        return self.run_daily_automation(user_id, today)

def run_automation_for_all_users(db: Session):
    """Run automation for all active users (for cron job)"""
    planner = AIPlanner()
    automation = DailyAutomation(db, planner)
    
    users = db.query(User).all()
    results = []
    
    for user in users:
        # Check if user has active goals
        active_goals = db.query(Goal).filter(
            Goal.user_id == user.id,
            Goal.status == "active"
        ).count()
        
        if active_goals > 0:
            result = automation.run_daily_automation(user.id)
            results.append({
                "user_id": user.id,
                "email": user.email,
                "result": result
            })
    
    return results
