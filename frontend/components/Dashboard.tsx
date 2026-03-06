'use client'

import { useState, useEffect } from 'react'
import { userAPI, goalAPI } from '@/lib/api'

interface DashboardProps {
  userId: number
}

export default function Dashboard({ userId }: DashboardProps) {
  const [stats, setStats] = useState<any>(null)
  const [goals, setGoals] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboard()
  }, [userId])

  const loadDashboard = async () => {
    setLoading(true)
    try {
      const [statsRes, goalsRes] = await Promise.all([
        userAPI.getStats(userId),
        goalAPI.getUserGoals(userId)
      ])
      
      setStats(statsRes.data)
      setGoals(goalsRes.data)
    } catch (error) {
      console.error('Error loading dashboard:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-gray-600">Loading dashboard...</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-gray-600">Active Goals</p>
          <p className="text-3xl font-bold text-blue-600">{stats?.goals_count || 0}</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-gray-600">Total Tasks</p>
          <p className="text-3xl font-bold text-green-600">{stats?.total_tasks || 0}</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-gray-600">Completed</p>
          <p className="text-3xl font-bold text-purple-600">{stats?.completed_tasks || 0}</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-gray-600">7-Day Rate</p>
          <p className="text-3xl font-bold text-orange-600">{stats?.completion_rate_7days || 0}%</p>
        </div>
      </div>

      {/* Goals List */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Your Goals</h2>
        
        {goals.length === 0 ? (
          <p className="text-gray-600">No goals yet. Create your first goal to get started!</p>
        ) : (
          <div className="space-y-4">
            {goals.map(goal => (
              <div key={goal.id} className="border rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="font-medium">{goal.goal_text}</h3>
                    {goal.goal_summary && (
                      <p className="text-sm text-gray-600 mt-1">{goal.goal_summary}</p>
                    )}
                    <div className="flex gap-3 mt-2">
                      <span className="text-xs px-2 py-1 rounded bg-blue-100 text-blue-800">
                        {goal.milestones_count} milestones
                      </span>
                      <span className={`text-xs px-2 py-1 rounded ${
                        goal.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                      }`}>
                        {goal.status}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="bg-blue-50 rounded-lg p-6 border border-blue-200">
        <h3 className="font-semibold text-blue-900 mb-2">💡 Daily Automation Active</h3>
        <p className="text-sm text-blue-800">
          Your tasks are automatically generated each morning based on your progress and goals. 
          Check the Daily Tasks tab to see today's plan!
        </p>
      </div>
    </div>
  )
}
