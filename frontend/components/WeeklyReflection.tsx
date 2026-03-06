'use client'

import { useState } from 'react'
import axios from 'axios'

export default function WeeklyReflection() {
  const [wentWell, setWentWell] = useState('')
  const [challenges, setChallenges] = useState('')
  const [changes, setChanges] = useState('')
  const [aiAnalysis, setAiAnalysis] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      const response = await axios.post('http://localhost:8000/reflection/weekly', {
        went_well: wentWell,
        challenges: challenges,
        changes_needed: changes
      }, {
        params: { user_id: 1 }
      })
      setAiAnalysis(response.data.reflection)
    } catch (error) {
      console.error('Error generating reflection:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-4">Weekly Reflection</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            What went well this week?
          </label>
          <textarea
            value={wentWell}
            onChange={(e) => setWentWell(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
            rows={3}
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            What challenges did you face?
          </label>
          <textarea
            value={challenges}
            onChange={(e) => setChallenges(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
            rows={3}
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            What should change next week?
          </label>
          <textarea
            value={changes}
            onChange={(e) => setChanges(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
            rows={3}
            required
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400"
        >
          {loading ? 'Analyzing...' : 'Get AI Analysis'}
        </button>
      </form>

      {aiAnalysis && (
        <div className="mt-6 border-t pt-6">
          <h3 className="font-semibold mb-3">AI Coach Analysis</h3>
          <div className="bg-blue-50 p-4 rounded-md">
            <p className="text-sm text-gray-700 whitespace-pre-wrap">{aiAnalysis}</p>
          </div>
        </div>
      )}
    </div>
  )
}
