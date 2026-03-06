"""Email Service using Resend (Free tier: 100 emails/day)"""

import os
import resend
from typing import List, Dict

resend.api_key = os.getenv("RESEND_API_KEY")

def send_daily_mission_email(
    to_email: str,
    user_name: str,
    tasks: List[Dict],
    deadlines: List[Dict]
) -> bool:
    """Send daily mission email to user"""
    
    # Format tasks
    task_list = "\n".join([
        f"{i+1}. {task['title']} ({task['estimated_time_minutes']} min)"
        for i, task in enumerate(tasks[:5])  # Top 5 tasks
    ])
    
    # Format deadlines
    deadline_list = "\n".join([
        f"- {d['title']} (Due: {d['deadline']})"
        for d in deadlines
    ]) if deadlines else "No urgent deadlines"
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #2563eb;">Your Daily Mission 🎯</h2>
        <p>Hi {user_name},</p>
        
        <h3>Today's Focus</h3>
        <pre style="background: #f3f4f6; padding: 15px; border-radius: 5px;">{task_list}</pre>
        
        <h3>Deadlines</h3>
        <pre style="background: #fef3c7; padding: 15px; border-radius: 5px;">{deadline_list}</pre>
        
        <p style="color: #6b7280; margin-top: 30px;">
            Remember: Progress over perfection. You've got this! 💪
        </p>
        
        <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;">
        <p style="font-size: 12px; color: #9ca3af;">
            AI Life OS - Your AI Chief of Staff
        </p>
    </body>
    </html>
    """
    
    try:
        params = {
            "from": "AI Life OS <onboarding@resend.dev>",  # Use your verified domain
            "to": [to_email],
            "subject": f"Your Mission for {tasks[0].get('date', 'Today')}",
            "html": html_content,
        }
        
        resend.Emails.send(params)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_weekly_reflection_email(
    to_email: str,
    user_name: str,
    reflection: str,
    completion_rate: float
) -> bool:
    """Send weekly reflection summary"""
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #2563eb;">Weekly Reflection 📊</h2>
        <p>Hi {user_name},</p>
        
        <div style="background: #f3f4f6; padding: 20px; border-radius: 5px; margin: 20px 0;">
            <h3>Completion Rate: {completion_rate:.0%}</h3>
            <div style="background: #e5e7eb; height: 20px; border-radius: 10px; overflow: hidden;">
                <div style="background: #2563eb; height: 100%; width: {completion_rate:.0%};"></div>
            </div>
        </div>
        
        <h3>AI Coach Analysis</h3>
        <div style="background: #eff6ff; padding: 15px; border-radius: 5px; border-left: 4px solid #2563eb;">
            {reflection}
        </div>
        
        <p style="color: #6b7280; margin-top: 30px;">
            Keep pushing forward! 🚀
        </p>
    </body>
    </html>
    """
    
    try:
        params = {
            "from": "AI Life OS <onboarding@resend.dev>",
            "to": [to_email],
            "subject": "Your Weekly Progress Report",
            "html": html_content,
        }
        
        resend.Emails.send(params)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
