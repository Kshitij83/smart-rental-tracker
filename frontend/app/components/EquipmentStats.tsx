'use client'

import { useState, useEffect } from 'react'
import { RefreshCw, Boxes, CalendarClock, Gauge, Zap } from 'lucide-react'
import { API_BASE_URL } from '../lib/config'

interface EquipmentStatsData {
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

interface EquipmentStatsProps {
  showDetailed?: boolean
}

const typeIcons: Record<string, string> = {
  excavator: '🚜',
  bulldozer: '🚜',
  crane: '🏗️',
  grader: '🛞',
  loader: '🛠️',
}

export default function EquipmentStats({
  showDetailed = false,
}: EquipmentStatsProps) {
  const [stats, setStats] = useState<EquipmentStatsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadEquipmentStats = async () => {
    try {
      setLoading(true)
      setError(null)

      const response = await fetch(`${API_BASE_URL}/dashboard`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      setStats(data.equipment_stats)
    } catch (err) {
      console.error('Error loading equipment stats:', err)
      setError(err instanceof Error ? err.message : 'Failed to load statistics')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadEquipmentStats()
  }, [])

  if (loading) {
    return (
      <div className="space-y-3">
        <div className="animate-pulse h-5 bg-slate-200 rounded w-3/4"></div>
        <div className="animate-pulse h-5 bg-slate-200 rounded w-1/2"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-red-600 bg-red-50 p-4 rounded-xl">
        <p className="font-medium">Error loading statistics</p>
        <p className="text-sm mt-1">{error}</p>
        <button
          onClick={loadEquipmentStats}
          className="mt-2 btn-secondary text-sm"
        >
          Try Again
        </button>
      </div>
    )
  }

  if (!stats || !stats.overview) {
    return (
      <div className="text-slate-600 bg-slate-50 p-4 rounded-xl">
        <p className="font-medium">No equipment data available</p>
        <button
          onClick={loadEquipmentStats}
          className="mt-2 btn-secondary text-sm"
        >
          Refresh Data
        </button>
      </div>
    )
  }

  const types = Object.entries(stats.by_equipment_type || {})
  const utilColor = (v: number) =>
    v >= 70
      ? 'bg-emerald-500'
      : v >= 50
        ? 'bg-amber-400'
        : 'bg-red-400'

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 flex-1">
          <div className="bg-blue-50 rounded-xl p-3">
            <p className="text-xs text-blue-600 font-medium flex items-center gap-1">
              <Boxes className="w-3 h-3" /> Total
            </p>
            <p className="text-xl font-bold text-blue-800">
              {stats.overview.total_equipment}
            </p>
          </div>
          <div className="bg-emerald-50 rounded-xl p-3">
            <p className="text-xs text-emerald-600 font-medium flex items-center gap-1">
              <CalendarClock className="w-3 h-3" /> Rentals
            </p>
            <p className="text-xl font-bold text-emerald-800">
              {stats.overview.total_rentals}
            </p>
          </div>
          <div className="bg-violet-50 rounded-xl p-3">
            <p className="text-xs text-violet-600 font-medium flex items-center gap-1">
              <Gauge className="w-3 h-3" /> Utilization
            </p>
            <p className="text-xl font-bold text-violet-800">
              {stats.overview.average_utilization}%
            </p>
          </div>
          <div className="bg-orange-50 rounded-xl p-3">
            <p className="text-xs text-orange-600 font-medium flex items-center gap-1">
              <Zap className="w-3 h-3" /> Engine Hrs
            </p>
            <p className="text-xl font-bold text-orange-800">
              {Math.round(stats.overview.total_engine_hours)}
            </p>
          </div>
        </div>
        <button
          onClick={loadEquipmentStats}
          className="ml-3 p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-600 transition-colors"
          title="Refresh"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      <div className="space-y-4">
        <h4 className="font-medium text-slate-700">
          Performance by Equipment Type
        </h4>
        {types.map(([type, data]) => (
          <div
            key={type}
            className="bg-slate-50 rounded-xl p-4"
          >
            <div className="flex items-center justify-between mb-2">
              <h5 className="font-medium text-slate-800 capitalize">
                <span className="mr-2">{typeIcons[type.toLowerCase()] || '⚙️'}</span>
                {type}
              </h5>
              <span className="text-sm text-slate-500">
                {data.count} units · {data.utilization}%
              </span>
            </div>
            <div className="h-2.5 w-full bg-slate-200 rounded-full overflow-hidden">
              <div
                className={`h-full ${utilColor(data.utilization)} rounded-full transition-all duration-700`}
                style={{ width: `${Math.min(100, data.utilization)}%` }}
              ></div>
            </div>
            {showDetailed && (
              <div className="mt-3 grid grid-cols-3 gap-3 text-sm">
                <div>
                  <p className="text-xs text-slate-500">Utilization</p>
                  <p className="font-semibold text-slate-800">
                    {data.avg_utilization}%
                  </p>
                </div>
                <div>
                  <p className="text-xs text-slate-500">Efficiency</p>
                  <p className="font-semibold text-slate-800">
                    {(data.avg_efficiency * 100).toFixed(1)}%
                  </p>
                </div>
                <div>
                  <p className="text-xs text-slate-500">Fleet Share</p>
                  <p className="font-semibold text-slate-800">
                    {stats.overview.total_equipment > 0
                      ? Math.round((data.count / stats.overview.total_equipment) * 100)
                      : 0}
                    %
                  </p>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
