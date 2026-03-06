"""LLM Prompt Templates for AI Life OS"""

SYSTEM_PROMPT = """You are an AI life strategist and planning engine.
Your job is to convert user goals into actionable structured plans.

Rules:
- Always break goals into milestones, tasks, and timelines
- Tasks must be realistic given the user's available hours
- Prioritize high-impact work
- Balance learning, health, and productivity
- Avoid vague tasks
- Ensure tasks are measurable and completable in one session
- Always output structured JSON

Planning hierarchy: Goal → Milestones → Weekly Objectives → Daily Tasks

Each task must include:
- title
- description
- estimated_time_minutes
- difficulty
- priority
- deadline
- category

Categories: learning, building, health, relationship, reflection, administrative
"""

GOAL_DECOMPOSITION_PROMPT = """User Profile:
Name: {name}
Available Hours Per Day: {hours}
Current Skills: {skills}
Constraints: {constraints}

Goal: {goal_text}
Deadline: {goal_deadline}

Break this goal into milestones and tasks.

Constraints:
- Tasks must be realistic
- Each task should be 30-120 minutes
- Prioritize foundational knowledge first
- Include both learning and project tasks

Output JSON format:
{{
  "goal_summary": "",
  "milestones": [
    {{
      "title": "",
      "description": "",
      "estimated_duration_weeks": 0,
      "tasks": [
        {{
          "title": "",
          "description": "",
          "estimated_time_minutes": 0,
          "priority": "high|medium|low",
          "difficulty": "easy|medium|hard",
          "category": "learning|building|health|relationship|reflection|administrative"
        }}
      ]
    }}
  ]
}}
"""

WEEKLY_PLANNING_PROMPT = """User Info:
Available hours per day: {hours}
Active Milestones: {milestones}
Pending Tasks: {tasks}

Generate a weekly plan.

Constraints:
- Balance workload across days
- Avoid overload
- Include rest or light tasks
- Prioritize highest-impact tasks

Output JSON format:
{{
  "week_plan": [
    {{
      "day": "Monday",
      "tasks": [
        {{
          "title": "",
          "description": "",
          "estimated_time_minutes": 0,
          "priority": "",
          "category": ""
        }}
      ]
    }}
  ]
}}
"""

DAILY_SCHEDULE_PROMPT = """User Schedule Constraints:
Wake time: {wake_time}
Sleep time: {sleep_time}
Available work hours: {available_hours}

Tasks to complete today: {tasks}

Generate a time-blocked schedule.

Rules:
- Each task must have start_time and end_time
- Insert breaks after 90 minutes
- Place hardest task in first productivity block

Output JSON format:
{{
  "daily_schedule": [
    {{
      "start_time": "HH:MM",
      "end_time": "HH:MM",
      "task_title": "",
      "category": "",
      "priority": ""
    }}
  ]
}}
"""

PERFORMANCE_EVALUATION_PROMPT = """User Performance Data:
Completed Tasks: {completed}
Skipped Tasks: {skipped}
Partial Tasks: {partial}

Analyze:
- Productivity patterns
- Possible causes of skipped tasks
- Recommended adjustments

Output JSON format:
{{
  "completion_rate": 0.0,
  "analysis": "",
  "recommendations": []
}}
"""

ADAPTIVE_PLANNING_PROMPT = """User Weekly Performance:
Completion rate: {rate}
Common skipped tasks: {skipped_tasks}
User available hours: {hours}

Adjust next week's plan.

Rules:
- Reduce complexity if completion rate < 50%
- Increase challenge if completion rate > 85%
- Maintain learning consistency

Output JSON format:
{{
  "plan_adjustment": "",
  "new_task_difficulty": "",
  "recommended_focus": []
}}
"""

WEEKLY_REFLECTION_PROMPT = """User weekly data:
Tasks completed: {completed}
Tasks skipped: {skipped}
Goals progress: {progress}

Write:
- Summary of the week
- Key achievements
- Areas to improve
- Advice for next week

Tone: constructive and motivational.
"""

DAILY_EMAIL_PROMPT = """Today's Tasks: {tasks}
Deadlines: {deadlines}

Write a concise email containing:
- Today's focus
- Top priority tasks
- Deadlines
- Motivational closing

Keep it under 200 words.
"""

BURNOUT_DETECTION_PROMPT = """User data:
Last 10 days completion rate: {rate}
Skipped tasks: {skipped}
User mood feedback: {mood}

Detect possible burnout.

If burnout likely:
- reduce workload
- recommend recovery tasks
- suggest schedule changes

Output JSON format:
{{
  "burnout_risk": "low|medium|high",
  "recommended_changes": []
}}
"""

SKILL_PROGRESS_PROMPT = """User completed learning tasks: {tasks}

Determine skill progress.

Output JSON format:
{{
  "skills": [
    {{
      "name": "",
      "progress_percent": 0,
      "recommended_next_topics": []
    }}
  ]
}}
"""
