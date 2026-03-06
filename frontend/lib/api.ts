import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// User API
export const userAPI = {
  create: (data: { email: string; name: string; daily_hours_available?: number; current_skills?: string }) =>
    api.post('/users', data),
  
  get: (userId: number) =>
    api.get(`/users/${userId}`),
  
  update: (userId: number, data: any) =>
    api.put(`/users/${userId}`, data),
  
  getContext: (userId: number) =>
    api.get(`/users/${userId}/context`),
  
  getStats: (userId: number) =>
    api.get(`/users/${userId}/stats`),
}

// Goal API
export const goalAPI = {
  create: (data: { user_id: number; goal_text: string; deadline?: string }) =>
    api.post('/goals', data),
  
  get: (goalId: number) =>
    api.get(`/goals/${goalId}`),
  
  getUserGoals: (userId: number) =>
    api.get(`/users/${userId}/goals`),
}

// Daily Tasks API
export const taskAPI = {
  generate: (data: { user_id: number; target_date: string }) =>
    api.post('/daily-tasks/generate', data),
  
  getDaily: (userId: number, targetDate: string) =>
    api.get(`/daily-tasks/${userId}/${targetDate}`),
  
  updateStatus: (scheduleId: number, data: { status: string; notes?: string }) =>
    api.put(`/daily-tasks/${scheduleId}`, data),
}

// Automation API
export const automationAPI = {
  runDaily: (userId: number) =>
    api.post(`/automation/daily/${userId}`),
  
  checkAndGenerate: (userId: number) =>
    api.post(`/automation/check-and-generate/${userId}`),
  
  generateWeek: (userId: number, days: number = 7) =>
    api.post(`/automation/generate-week/${userId}?days=${days}`),
}

