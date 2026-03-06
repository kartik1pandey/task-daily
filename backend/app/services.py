"""Business logic services for AI Life OS"""

from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional
from .models import User, Goal, Milestone, Task, DailySchedule, PerformanceLog, WeeklyReflection
from .planner import AIPlanner

class LifeOSService:
    def __init__(self, db: Session, planner: AIPlanner):
        self.db = db
        self.planner = planner
    
    def create_or_get_user(self, email: str, name: str = "User") -> User:
        """Get existing user or create new one"""
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            user = User(email=email, name=name)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        return user
    
    def create_goal_with_plan(self, user_id: int, goal_text: str, deadline: Optional[date] = None) -> Goal:
        """Create goal and generate full plan using AI"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Get AI decomposition
        user_data = {
            "name": user.name,
            "daily_hours_available": user.daily_hours_available,
            "current_skills": user.current_skills or "Not specified",
            "constraints": user.constraints or "None"
        }
        
        plan = self.planner.decompose_goal(
            user_data=user_data,
            goal_text=goal_text,
            deadline=str(deadline) if deadline else None
        )
        
        # Create goal
        goal = Goal(
            user_id=user_id,
            goal_text=goal_text,
            goal_summary=plan.get("goal_summary", ""),
            deadline=deadline,
            status="active"
        )
        self.db.add(goal)
        self.db.flush()
        
        # Create milestones and tasks
        for milestone_data in plan.get("milestones", []):
            milestone = Milestone(
                goal_id=goal.id,
                title=milestone_data["title"],
                description=milestone_data.get("description", ""),
                estimated_duration_weeks=milestone_data.get("estimated_duration_weeks", 4),
                status="active"
            )
            self.db.add(milestone)
            self.db.flush()
            
            # Create tasks for this milestone
            for task_data in milestone_data.get("tasks", []):
                task = Task(
                    milestone_id=milestone.id,
                    title=task_data["title"],
                    description=task_data.get("description", ""),
                    estimated_time_minutes=task_data.get("estimated_time_minutes", 60),
                    difficulty=task_data.get("difficulty", "medium"),
                    priority=task_data.get("priority", "medium"),
                    category=task_data.get("category", "learning"),
                    status="pending"
                )
                self.db.add(task)
        
        self.db.commit()
        self.db.refresh(goal)
        return goal
    
    def generate_daily_tasks(self, user_id: int, target_date: date) -> List[DailySchedule]:
        """Generate AI-powered daily schedule with context"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Get active goals and pending tasks
        active_goals = self.db.query(Goal).filter(
            Goal.user_id == user_id,
            Goal.status == "active"
        ).all()
        
        if not active_goals:
            return []
        
        # Get all pending tasks from active milestones
        pending_tasks = []
        for goal in active_goals:
            for milestone in goal.milestones:
                if milestone.status == "active":
                    for task in milestone.tasks:
                        if task.status == "pending":
                            pending_tasks.append({
                                "id": task.id,
                                "title": task.title,
                                "description": task.description,
                                "estimated_time_minutes": task.estimated_time_minutes,
                                "priority": task.priority,
                                "category": task.category,
                                "difficulty": task.difficulty
                            })
        
        if not pending_tasks:
            return []
        
        # Get recent performance context
        last_7_days = target_date - timedelta(days=7)
        recent_schedules = self.db.query(DailySchedule).filter(
            DailySchedule.user_id == user_id,
            DailySchedule.schedule_date >= last_7_days,
            DailySchedule.schedule_date < target_date
        ).all()
        
        completed_count = sum(1 for s in recent_schedules if s.status == "completed")
        total_count = len(recent_schedules)
        completion_rate = completed_count / total_count if total_count > 0 else 0.75
        
        # Adjust task load based on performance
        if completion_rate < 0.5:
            # Reduce load
            max_tasks = 3
            pending_tasks = sorted(pending_tasks, key=lambda x: x["priority"] == "high", reverse=True)[:max_tasks]
        elif completion_rate > 0.85:
            # Can handle more
            max_tasks = 6
        else:
            max_tasks = 4
        
        pending_tasks = pending_tasks[:max_tasks]
        
        # Generate time-blocked schedule
        user_data = {
            "wake_time": user.wake_time,
            "sleep_time": user.sleep_time,
            "daily_hours_available": user.daily_hours_available
        }
        
        schedule_plan = self.planner.generate_daily_schedule(user_data, pending_tasks)
        
        # Create schedule entries
        schedules = []
        for item in schedule_plan.get("daily_schedule", []):
            # Find matching task
            task_id = None
            for task in pending_tasks:
                if task["title"] in item.get("task_title", ""):
                    task_id = task["id"]
                    break
            
            if task_id:
                schedule = DailySchedule(
                    user_id=user_id,
                    task_id=task_id,
                    schedule_date=target_date,
                    start_time=item.get("start_time"),
                    end_time=item.get("end_time"),
                    status="pending"
                )
                self.db.add(schedule)
                schedules.append(schedule)
        
        self.db.commit()
        return schedules
    
    def update_task_status(self, schedule_id: int, status: str, notes: str = "") -> DailySchedule:
        """Update task completion status and log performance"""
        schedule = self.db.query(DailySchedule).filter(DailySchedule.id == schedule_id).first()
        if not schedule:
            raise ValueError("Schedule not found")
        
        schedule.status = status
        schedule.completion_notes = notes
        
        # Update task status
        task = schedule.task
        if status == "completed":
            task.status = "completed"
            task.completed_at = datetime.utcnow()
            
            # Log performance
            log = PerformanceLog(
                task_id=task.id,
                completion_rate=1.0,
                delay_minutes=0,
                feedback=notes
            )
            self.db.add(log)
        elif status == "skipped":
            log = PerformanceLog(
                task_id=task.id,
                completion_rate=0.0,
                delay_minutes=0,
                feedback=notes or "Skipped"
            )
            self.db.add(log)
        elif status == "partial":
            log = PerformanceLog(
                task_id=task.id,
                completion_rate=0.5,
                delay_minutes=0,
                feedback=notes or "Partially completed"
            )
            self.db.add(log)
        
        # Update milestone progress
        milestone = task.milestone
        total_tasks = len(milestone.tasks)
        completed_tasks = sum(1 for t in milestone.tasks if t.status == "completed")
        milestone.progress = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
        
        if milestone.progress >= 100:
            milestone.status = "completed"
        
        self.db.commit()
        self.db.refresh(schedule)
        return schedule
    
    def get_daily_tasks(self, user_id: int, target_date: date) -> List[Dict]:
        """Get tasks for a specific day"""
        schedules = self.db.query(DailySchedule).filter(
            DailySchedule.user_id == user_id,
            DailySchedule.schedule_date == target_date
        ).all()
        
        result = []
        for schedule in schedules:
            task = schedule.task
            result.append({
                "schedule_id": schedule.id,
                "task_id": task.id,
                "title": task.title,
                "description": task.description,
                "estimated_time_minutes": task.estimated_time_minutes,
                "category": task.category,
                "priority": task.priority,
                "start_time": schedule.start_time,
                "end_time": schedule.end_time,
                "status": schedule.status
            })
        
        return result
    
    def get_user_context(self, user_id: int) -> Dict:
        """Get full user context for AI planning"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {}
        
        # Get goals and progress
        goals = self.db.query(Goal).filter(Goal.user_id == user_id).all()
        
        # Get recent performance
        last_30_days = date.today() - timedelta(days=30)
        recent_logs = self.db.query(PerformanceLog).join(Task).join(Milestone).join(Goal).filter(
            Goal.user_id == user_id,
            PerformanceLog.logged_at >= last_30_days
        ).all()
        
        total_logs = len(recent_logs)
        avg_completion = sum(log.completion_rate for log in recent_logs) / total_logs if total_logs > 0 else 0.75
        
        return {
            "user": {
                "name": user.name,
                "email": user.email,
                "daily_hours": user.daily_hours_available,
                "skills": user.current_skills
            },
            "goals": [{"id": g.id, "text": g.goal_text, "status": g.status} for g in goals],
            "performance": {
                "completion_rate": avg_completion,
                "total_tasks_logged": total_logs
            }
        }
