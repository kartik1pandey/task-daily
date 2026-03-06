'use client'

import { useState, useEffect } from 'react'
import GoalInput from '@/components/GoalInput'
import DailyTasks from '@/components/DailyTasks'
import Dashboard from '@/components/Dashboard'

export default function Home() {
  const [activeView, setActiveView] = useState<'dashboard' | 'goals' | 'daily'>('dashboard')
  const [userId, setUserId] = useState<number | null>(null)
  const [hasGoal, setHasGoal] = useState(false)

  useEffect(() => {
    // Check localStorage for user
    const storedUserId = localStorage.getItem('userId')
    const storedHasGoal = localStorage.getItem('hasGoal')
    
    if (storedUserId) {
      setUserId(parseInt(storedUserId))
    }
    
    if (storedHasGoal === 'true') {
      setHasGoal(true)
    }
  }, [])

  const handleGoalCreated = () => {
    setHasGoal(true)
    localStorage.setItem('hasGoal', 'true')
    setActiveView('daily')
  }

  const handleUserCreated = (newUserId: number) => {
    setUserId(newUserId)
    localStorage.setItem('userId', newUserId.toString())
  }

  return (
    <main className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">AI Life OS</h1>
              <p className="text-sm text-gray-600">Your AI Chief of Staff</p>
            </div>
            {userId && (
              <div className="text-sm text-gray-600">
                User ID: {userId}
              </div>
            )}
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {!userId ? (
          <GoalInput onUserCreated={handleUserCreated} onGoalCreated={handleGoalCreated} />
        ) : !hasGoal ? (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Welcome Back!</h2>
            <p className="text-gray-600 mb-4">Let's set up your first goal to get started.</p>
            <GoalInput onUserCreated={handleUserCreated} onGoalCreated={handleGoalCreated} />
          </div>
        ) : (
          <>
            <div className="flex gap-4 mb-6">
              <button
                onClick={() => setActiveView('dashboard')}
                className={`px-4 py-2 rounded ${activeView === 'dashboard' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700'}`}
              >
                Dashboard
              </button>
              <button
                onClick={() => setActiveView('daily')}
                className={`px-4 py-2 rounded ${activeView === 'daily' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700'}`}
              >
                Daily Tasks
              </button>
              <button
                onClick={() => setActiveView('goals')}
                className={`px-4 py-2 rounded ${activeView === 'goals' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700'}`}
              >
                Add Goal
              </button>
            </div>

            {activeView === 'dashboard' && <Dashboard userId={userId} />}
            {activeView === 'daily' && <DailyTasks userId={userId} />}
            {activeView === 'goals' && <GoalInput onUserCreated={handleUserCreated} onGoalCreated={handleGoalCreated} />}
          </>
        )}
      </div>
    </main>
  )
}
