'use client'

import { useState, useEffect } from 'react'

interface EquipmentStats {
  overview: {
    total_equipment: number
    total_rentals: number
    average_utilization: number
    total_engine_hours: number
  }
  by_equipment_type: {
    [key: string]: {
      count: number
      utilization: number
      avg_utilization: number
      avg_efficiency: number
    }
  }
}

export default function EquipmentStats() {
  const [stats, setStats] = useState<EquipmentStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadEquipmentStats()
  }, [])

  const loadEquipmentStats = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'https://cat-v7yf.onrender.com'}/dashboard`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      setStats(data.equipment_stats)
    } catch (err) {
      console.error('Error loading equipment stats:', err)
      setError(err instanceof Error ? err.message : 'Failed to load equipment statistics')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Equipment Performance Statistics</h3>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3"></div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Equipment Performance Statistics</h3>
        <div className="text-red-600 bg-red-50 p-4 rounded-lg">
          <p className="font-medium">Error loading equipment statistics</p>
          <p className="text-sm mt-1">{error}</p>
          <button 
            onClick={loadEquipmentStats}
            className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 text-sm"
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  if (!stats || !stats.overview) {
    return (
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Equipment Performance Statistics</h3>
        <div className="text-gray-600 bg-gray-50 p-4 rounded-lg">
          <p className="font-medium">No Equipment Data Available</p>
          <p className="text-sm mt-1">
            The equipment statistics are currently unavailable. This could be due to:
          </p>
          <ul className="text-sm mt-2 list-disc list-inside space-y-1">
            <li>Backend server not running</li>
            <li>CSV data file not accessible</li>
            <li>Database connection issues</li>
          </ul>
          <button 
            onClick={loadEquipmentStats}
            className="mt-3 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
          >
            Refresh Data
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Equipment Performance Statistics</h3>
        <button 
          onClick={loadEquipmentStats}
          className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
        >
          Refresh
        </button>
      </div>

      {/* Overall Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-blue-50 p-3 rounded-lg">
          <p className="text-sm text-blue-600 font-medium">Total Equipment</p>
          <p className="text-2xl font-bold text-blue-800">{stats.overview.total_equipment}</p>
        </div>
        <div className="bg-green-50 p-3 rounded-lg">
          <p className="text-sm text-green-600 font-medium">Active Rentals</p>
          <p className="text-2xl font-bold text-green-800">{stats.overview.total_rentals}</p>
        </div>
        <div className="bg-purple-50 p-3 rounded-lg">
          <p className="text-sm text-purple-600 font-medium">Avg Utilization</p>
          <p className="text-2xl font-bold text-purple-800">{stats.overview.average_utilization}%</p>
        </div>
        <div className="bg-orange-50 p-3 rounded-lg">
          <p className="text-sm text-orange-600 font-medium">Total Engine Hours</p>
          <p className="text-2xl font-bold text-orange-800">{stats.overview.total_engine_hours}</p>
        </div>
      </div>

      {/* Equipment Type Breakdown */}
      <div className="space-y-4">
        <h4 className="font-medium text-gray-700">Performance by Equipment Type</h4>
        {stats.by_equipment_type && Object.entries(stats.by_equipment_type).map(([type, data]) => (
          <div key={type} className="bg-gray-50 p-4 rounded-lg">
            <div className="flex justify-between items-center mb-2">
              <h5 className="font-medium text-gray-800 capitalize">{type}</h5>
              <span className="text-sm text-gray-500">{data.count} units</span>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Utilization Rate</p>
                <p className="text-lg font-semibold text-blue-600">{data.utilization}%</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Efficiency Score</p>
                <p className="text-lg font-semibold text-green-600">{(data.avg_efficiency * 100).toFixed(1)}%</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
