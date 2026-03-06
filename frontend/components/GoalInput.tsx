'use client'

import { useState, useEffect } from 'react'
import { userAPI, goalAPI } from '@/lib/api'

interface GoalInputProps {
  onUserCreated?: (userId: number) => void
  onGoalCreated?: () => void
}

export default function GoalInput({ onUserCreated, onGoalCreated }: GoalInputProps) {
  const [userId, setUserId] = useState<number | null>(null)
  const [email, setEmail] = useState('')
  const [name, setName] = useState('')
  const [goalText, setGoalText] = useState('')
  const [hours, setHours] = useState(8)
  const [skills, setSkills] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [step, setStep] = useState<'user' | 'goal'>('user')

  useEffect(() => {
    // Check if user exists in localStorage
    const storedUserId = localStorage.getItem('userId')
    if (storedUserId) {
      setUserId(parseInt(storedUserId))
      setStep('goal')
    }
  }, [])

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      const response = await userAPI.create({
        email,
        name,
        daily_hours_available: hours,
        current_skills: skills
      })
      
      const newUserId = response.data.id
      setUserId(newUserId)
      localStorage.setItem('userId', newUserId.toString())
      setStep('goal')
      onUserCreated?.(newUserId)
    } catch (error) {
      console.error('Error creating user:', error)
      alert('Error creating user. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!userId) return
    
    setLoading(true)
    
    try {
      const response = await goalAPI.create({
        user_id: userId,
        goal_text: goalText
      })
      
      // Fetch full goal details
      const goalDetails = await goalAPI.get(response.data.goal_id)
      setResult(goalDetails.data)
      onGoalCreated?.()
    } catch (error) {
      console.error('Error creating goal:', error)
      alert('Error creating goal. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  if (step === 'user') {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Welcome to AI Life OS</h2>
        <p className="text-sm text-gray-600 mb-6">First, let's set up your profile</p>
        
        <form onSubmit={handleCreateUser} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              placeholder="your@email.com"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              placeholder="Your name"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Available hours per day
            </label>
            <input
              type="number"
              value={hours}
              onChange={(e) => setHours(parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              min={1}
              max={16}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Current skills
            </label>
            <input
              type="text"
              value={skills}
              onChange={(e) => setSkills(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              placeholder="e.g., Python, basic ML"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400"
          >
            {loading ? 'Creating Profile...' : 'Continue'}
          </button>
        </form>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-4">Set Your Life Goal</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            What do you want to achieve?
          </label>
          <textarea
            value={goalText}
            onChange={(e) => setGoalText(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
            rows={3}
            placeholder="e.g., Become a top ML engineer in 3 years"
            required
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400"
        >
          {loading ? 'Planning...' : 'Generate Plan'}
        </button>
      </form>

      {result && (
        <div className="mt-6 border-t pt-6">
          <h3 className="font-semibold mb-3">Your Plan</h3>
          <p className="text-sm text-gray-600 mb-4">{result.goal_summary}</p>
          
          <div className="space-y-4">
            {result.milestones?.map((milestone: any, idx: number) => (
              <div key={idx} className="bg-gray-50 p-4 rounded">
                <h4 className="font-medium">{milestone.title}</h4>
                <p className="text-sm text-gray-600">{milestone.description}</p>
                <div className="mt-2 flex items-center gap-4">
                  <span className="text-xs text-gray-500">
                    Progress: {milestone.progress?.toFixed(0) || 0}%
                  </span>
                  <span className="text-xs text-gray-500">
                    {milestone.tasks?.length} tasks
                  </span>
                </div>
                
                {milestone.tasks && milestone.tasks.length > 0 && (
                  <div className="mt-3 space-y-2">
                    {milestone.tasks.slice(0, 3).map((task: any, tidx: number) => (
                      <div key={tidx} className="text-xs bg-white p-2 rounded">
                        <span className="font-medium">{task.title}</span>
                        <span className="text-gray-500 ml-2">({task.estimated_time_minutes} min)</span>
                      </div>
                    ))}
                    {milestone.tasks.length > 3 && (
                      <p className="text-xs text-gray-500">
                        +{milestone.tasks.length - 3} more tasks
                      </p>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
