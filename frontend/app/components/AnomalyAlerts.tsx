'use client'

import { useState, useEffect } from 'react'
import { RefreshCw, AlertTriangle, Clock, MapPin, Activity } from 'lucide-react'
import { API_BASE_URL } from '../lib/config'

interface Anomaly {
  equipment_id: string
  type: string
  anomaly_type: string
  severity: string
  anomaly_score: number
  site_id: string
  engine_hours_per_day: number
  idle_hours_per_day: number
  utilization_ratio: number
  check_out_date: string
  check_in_date: string
}

interface AnomalyData {
  summary: {
    total_anomalies: number
    total_records: number
    anomaly_types: {
      high_idle_time: number
      low_utilization: number
    }
  }
  anomalies: Anomaly[]
}

interface AnomalyAlertsProps {
  showAll?: boolean
}

export default function AnomalyAlerts({ showAll = false }: AnomalyAlertsProps) {
  const [anomalyData, setAnomalyData] = useState<AnomalyData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadAnomalyData = async () => {
    try {
      setLoading(true)
      setError(null)

      const response = await fetch(`${API_BASE_URL}/dashboard`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      setAnomalyData(data.anomalies)
    } catch (err) {
      console.error('Error loading anomaly data:', err)
      setError(err instanceof Error ? err.message : 'Failed to load anomaly data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadAnomalyData()
  }, [])

  const severityClasses: Record<string, string> = {
    high: 'bg-red-50 ring-red-200',
    medium: 'bg-amber-50 ring-amber-200',
    low: 'bg-blue-50 ring-blue-200',
  }

  const severityBadge: Record<string, string> = {
    high: 'bg-red-500 text-white',
    medium: 'bg-amber-500 text-white',
    low: 'bg-blue-500 text-white',
  }

  const typeLabels: Record<string, { label: string; icon: any }> = {
    high_idle_time: { label: 'High Idle Time', icon: Clock },
    low_utilization: { label: 'Low Utilization', icon: Activity },
  }

  if (loading) {
    return (
      <div className="space-y-3">
        <div className="animate-pulse h-5 bg-slate-200 rounded w-2/3"></div>
        <div className="animate-pulse h-5 bg-slate-200 rounded w-1/2"></div>
        <div className="animate-pulse h-5 bg-slate-200 rounded w-3/4"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-red-600 bg-red-50 p-4 rounded-xl">
        <p className="font-medium">Error loading anomaly data</p>
        <p className="text-sm mt-1">{error}</p>
        <button onClick={loadAnomalyData} className="mt-2 btn-danger text-sm">
          Try Again
        </button>
      </div>
    )
  }

  if (!anomalyData) {
    return (
      <div className="text-slate-600 bg-slate-50 p-4 rounded-xl">
        <p className="font-medium">No anomaly data available</p>
        <button onClick={loadAnomalyData} className="mt-2 btn-secondary text-sm">
          Refresh Data
        </button>
      </div>
    )
  }

  const summary = anomalyData.summary
  const visibleAnomalies = showAll
    ? anomalyData.anomalies
    : anomalyData.anomalies.slice(0, 4)

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div className="grid grid-cols-3 gap-3 flex-1">
          <div className="bg-red-50 rounded-xl p-3">
            <p className="text-xs text-red-600 font-medium">Total</p>
            <p className="text-xl font-bold text-red-800">
              {summary.total_anomalies}
            </p>
          </div>
          <div className="bg-amber-50 rounded-xl p-3">
            <p className="text-xs text-amber-600 font-medium">High Idle</p>
            <p className="text-xl font-bold text-amber-800">
              {summary.anomaly_types?.high_idle_time ?? 0}
            </p>
          </div>
          <div className="bg-blue-50 rounded-xl p-3">
            <p className="text-xs text-blue-600 font-medium">Low Util.</p>
            <p className="text-xl font-bold text-blue-800">
              {summary.anomaly_types?.low_utilization ?? 0}
            </p>
          </div>
        </div>
        <button
          onClick={loadAnomalyData}
          className="ml-3 p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-600 transition-colors"
          title="Refresh"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {visibleAnomalies.length === 0 ? (
        <div className="text-center text-slate-500 py-8">
          <AlertTriangle className="mx-auto h-10 w-10 text-emerald-400" />
          <h3 className="text-lg font-medium text-slate-900 mt-2">
            All Clear!
          </h3>
          <p className="text-sm">
            No anomalies detected in your equipment data.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {visibleAnomalies.map((anomaly, index) => {
            const typeInfo = typeLabels[anomaly.anomaly_type] || {
              label: anomaly.anomaly_type.replace(/_/g, ' '),
              icon: AlertTriangle,
            }
            const TypeIcon = typeInfo.icon
            return (
              <div
                key={index}
                className={`rounded-xl ring-1 p-4 ${severityClasses[anomaly.severity] || 'bg-slate-50 ring-slate-200'}`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-3 min-w-0">
                    <span className="w-9 h-9 rounded-lg bg-white/70 flex items-center justify-center shrink-0">
                      <TypeIcon className="w-5 h-5 text-slate-700" />
                    </span>
                    <div className="min-w-0">
                      <p className="font-semibold text-slate-800 truncate">
                        {anomaly.equipment_id}
                      </p>
                      <p className="text-xs text-slate-500 capitalize">
                        {anomaly.type}
                      </p>
                    </div>
                  </div>
                  <span
                    className={`shrink-0 px-2.5 py-1 rounded-full text-xs font-bold ${severityBadge[anomaly.severity] || 'bg-slate-500 text-white'}`}
                  >
                    {anomaly.severity.toUpperCase()}
                  </span>
                </div>

                <p className="mt-3 text-sm font-semibold text-slate-800">
                  {typeInfo.label}
                </p>
                <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
                  <div className="bg-white/70 rounded-lg p-2">
                    <p className="text-slate-500 font-medium">Engine Hrs</p>
                    <p className="font-semibold text-slate-800">
                      {anomaly.engine_hours_per_day}
                    </p>
                  </div>
                  <div className="bg-white/70 rounded-lg p-2">
                    <p className="text-slate-500 font-medium">Idle Hrs</p>
                    <p className="font-semibold text-slate-800">
                      {anomaly.idle_hours_per_day}
                    </p>
                  </div>
                  <div className="bg-white/70 rounded-lg p-2">
                    <p className="text-slate-500 font-medium">Utilization</p>
                    <p className="font-semibold text-slate-800">
                      {(anomaly.utilization_ratio * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div className="bg-white/70 rounded-lg p-2">
                    <p className="text-slate-500 font-medium flex items-center gap-1">
                      <MapPin className="w-3 h-3" /> Site
                    </p>
                    <p className="font-semibold text-slate-800 truncate">
                      {anomaly.site_id}
                    </p>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
