"""AI Planning Engine - Core LLM Integration"""

import json
import os
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("Warning: Groq library not installed. Install with: pip install groq")

from .prompts import *

class AIPlanner:
    def __init__(self, provider: str = "groq"):
        self.provider = provider
        
        if not GROQ_AVAILABLE:
            raise ImportError("Groq library not installed. Run: pip install groq==0.11.0")
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key == "your_groq_key_here":
            raise ValueError(
                "GROQ_API_KEY not set. Get your free key from: https://console.groq.com/keys"
            )
        
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"  # Fast and free
    
    def _call_llm(self, prompt: str, system_prompt: str = SYSTEM_PROMPT) -> Dict:
        """Call LLM with structured JSON output"""
        response = self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4096
        )
        return json.loads(response.choices[0].message.content)
    
    def decompose_goal(self, user_data: Dict, goal_text: str, deadline: str = None) -> Dict:
        """Break down a life goal into milestones and tasks"""
        prompt = GOAL_DECOMPOSITION_PROMPT.format(
            name=user_data.get("name", "User"),
            hours=user_data.get("daily_hours_available", 8),
            skills=user_data.get("current_skills", "Not specified"),
            constraints=user_data.get("constraints", "None"),
            goal_text=goal_text,
            goal_deadline=deadline or "Not specified"
        )
        return self._call_llm(prompt)
    
    def generate_weekly_plan(self, user_hours: int, milestones: List[Dict], tasks: List[Dict]) -> Dict:
        """Generate weekly task distribution"""
        prompt = WEEKLY_PLANNING_PROMPT.format(
            hours=user_hours,
            milestones=json.dumps(milestones),
            tasks=json.dumps(tasks)
        )
        return self._call_llm(prompt)
    
    def generate_daily_schedule(self, user_data: Dict, tasks: List[Dict]) -> Dict:
        """Generate time-blocked daily schedule"""
        prompt = DAILY_SCHEDULE_PROMPT.format(
            wake_time=user_data.get("wake_time", "07:00"),
            sleep_time=user_data.get("sleep_time", "23:00"),
            available_hours=user_data.get("daily_hours_available", 8),
            tasks=json.dumps(tasks)
        )
        return self._call_llm(prompt)
    
    def evaluate_performance(self, completed: List[Dict], skipped: List[Dict], partial: List[Dict]) -> Dict:
        """Analyze user performance and provide recommendations"""
        prompt = PERFORMANCE_EVALUATION_PROMPT.format(
            completed=json.dumps(completed),
            skipped=json.dumps(skipped),
            partial=json.dumps(partial)
        )
        return self._call_llm(prompt)
    
    def adapt_plan(self, completion_rate: float, skipped_tasks: List[Dict], user_hours: int) -> Dict:
        """Adjust planning based on performance"""
        prompt = ADAPTIVE_PLANNING_PROMPT.format(
            rate=completion_rate,
            skipped_tasks=json.dumps(skipped_tasks),
            hours=user_hours
        )
        return self._call_llm(prompt)
    
    def generate_reflection(self, completed: List[Dict], skipped: List[Dict], progress: Dict) -> str:
        """Generate weekly reflection summary"""
        prompt = WEEKLY_REFLECTION_PROMPT.format(
            completed=json.dumps(completed),
            skipped=json.dumps(skipped),
            progress=json.dumps(progress)
        )
        result = self._call_llm(prompt)
        return result.get("reflection", "")
    
    def generate_daily_email(self, tasks: List[Dict], deadlines: List[Dict]) -> str:
        """Generate daily mission email"""
        prompt = DAILY_EMAIL_PROMPT.format(
            tasks=json.dumps(tasks),
            deadlines=json.dumps(deadlines)
        )
        result = self._call_llm(prompt)
        return result.get("email_content", "")
    
    def detect_burnout(self, completion_rate: float, skipped: List[Dict], mood: str = None) -> Dict:
        """Detect burnout risk and recommend changes"""
        prompt = BURNOUT_DETECTION_PROMPT.format(
            rate=completion_rate,
            skipped=json.dumps(skipped),
            mood=mood or "Not provided"
        )
        return self._call_llm(prompt)
    
    def analyze_skill_progress(self, completed_tasks: List[Dict]) -> Dict:
        """Track skill development progress"""
        prompt = SKILL_PROGRESS_PROMPT.format(
            tasks=json.dumps(completed_tasks)
        )
        return self._call_llm(prompt)
