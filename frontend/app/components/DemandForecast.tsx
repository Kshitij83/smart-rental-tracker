'use client'

import { useState, useEffect, useCallback } from 'react'
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { RefreshCw, Server, WifiOff } from 'lucide-react'
import { API_BASE_URL } from '../lib/config'

interface DemandForecastProps {
  daysAhead: number
}

export default function DemandForecast({ daysAhead }: DemandForecastProps) {
  const [forecast, setForecast] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [source, setSource] = useState<'ml' | 'fallback'>('ml')
  const [selectedEquipment, setSelectedEquipment] = useState<string>('all')

  const generateMockForecast = useCallback(() => {
    const mockForecast =
      selectedEquipment === 'all'
        ? {
            forecasts: [
              { equipment_type: 'Excavator', predicted_demand: 14.7, average_daily_demand: 2.1, trend: 'stable' },
              { equipment_type: 'Bulldozer', predicted_demand: 11.6, average_daily_demand: 1.66, trend: 'decreasing' },
              { equipment_type: 'Crane', predicted_demand: 13.7, average_daily_demand: 1.96, trend: 'increasing' },
              { equipment_type: 'Grader', predicted_demand: 11.5, average_daily_demand: 1.64, trend: 'increasing' },
            ],
          }
        : {
            forecasts: Array.from({ length: daysAhead }, (_, i) => ({
              date: new Date(Date.now() + i * 24 * 60 * 60 * 1000).toLocaleDateString(),
              predicted_demand: Math.floor(Math.random() * 4) + 1,
              confidence: (Math.random() * 0.15 + 0.85).toFixed(2),
              day_of_week: new Date(Date.now() + i * 24 * 60 * 60 * 1000).toLocaleDateString('en-US', { weekday: 'short' }),
            })),
            total_predicted_demand: undefined,
            average_daily_demand: undefined,
            trend: 'stable',
          }
    setForecast(mockForecast)
    setLoading(false)
  }, [selectedEquipment, daysAhead])

  const loadForecast = useCallback(async () => {
    setLoading(true)
    try {
      const base = `${API_BASE_URL}/ml/demand-forecast`
      let url: string
      let payload: any

      if (selectedEquipment === 'all') {
        url = `${base}/bulk?days_ahead=${daysAhead}`
        payload = null
      } else {
        url = `${base}?equipment_type=${encodeURIComponent(selectedEquipment)}&days_ahead=${daysAhead}`
        payload = null
      }

      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: payload,
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      const data = await response.json()
      if (data && (data.forecasts || data.error)) {
        setForecast(data)
        setSource('ml')
      } else {
        throw new Error('Empty forecast')
      }
    } catch (err) {
      console.warn('ML forecast unavailable, using fallback:', err)
      setSource('fallback')
      generateMockForecast()
    }
  }, [selectedEquipment, daysAhead, generateMockForecast])

  useEffect(() => {
    loadForecast()
  }, [loadForecast])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-400"></div>
      </div>
    )
  }

  if (!forecast) {
    return (
      <div className="text-center text-slate-500 py-8">
        No demand forecast available
      </div>
    )
  }

  const prepareChartData = () => {
    if (selectedEquipment === 'all' && forecast.forecasts) {
      return forecast.forecasts.map((item: any) => ({
        name: item.equipment_type,
        demand: item.predicted_demand,
        avgDaily: item.average_daily_demand,
        trend: item.trend,
      }))
    } else if (forecast.forecasts) {
      return forecast.forecasts.map((day: any) => ({
        name: day.date,
        demand: day.predicted_demand,
        confidence: day.confidence,
        dayOfWeek: day.day_of_week,
      }))
    }
    return []
  }

  const chartData = prepareChartData()
  const totalDemand =
    selectedEquipment === 'all'
      ? forecast.forecasts?.reduce(
          (sum: number, item: any) => sum + (item.predicted_demand || 0),
          0
        ) || 0
      : forecast.total_predicted_demand || 0
  const avgDemand =
    selectedEquipment === 'all'
      ? forecast.forecasts?.length
        ? (
            forecast.forecasts.reduce(
              (sum: number, item: any) => sum + (item.predicted_demand || 0),
              0
            ) / forecast.forecasts.length
          ).toFixed(1)
        : '0.0'
      : forecast.average_daily_demand || 0

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center gap-4 justify-between">
        <div className="flex items-center gap-3">
          <label className="text-sm font-medium text-slate-700">
            Equipment Type:
          </label>
          <select
            value={selectedEquipment}
            onChange={(e) => setSelectedEquipment(e.target.value)}
            className="input-field max-w-xs"
          >
            <option value="all">All Equipment Types</option>
            <option value="Excavator">Excavator</option>
            <option value="Bulldozer">Bulldozer</option>
            <option value="Crane">Crane</option>
            <option value="Grader">Grader</option>
          </select>
        </div>
        <div className="flex items-center gap-3">
          <span
            className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold ${
              source === 'ml'
                ? 'bg-emerald-50 text-emerald-700'
                : 'bg-slate-100 text-slate-500'
            }`}
          >
            {source === 'ml' ? (
              <Server className="w-3.5 h-3.5" />
            ) : (
              <WifiOff className="w-3.5 h-3.5" />
            )}
            {source === 'ml' ? 'ML Forecast' : 'Fallback Estimate'}
          </span>
          <button
            onClick={loadForecast}
            className="p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-600 transition-colors"
            title="Refresh forecast"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-2xl p-6 text-white">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
          <div>
            <p className="text-3xl font-bold text-amber-400">
              {Number(totalDemand).toFixed(1)}
            </p>
            <p className="text-sm text-slate-300">Total Predicted Demand</p>
          </div>
          <div>
            <p className="text-3xl font-bold text-emerald-400">
              {avgDemand}
            </p>
            <p className="text-sm text-slate-300">Average Daily Demand</p>
          </div>
          <div>
            <p className="text-3xl font-bold capitalize text-violet-300">
              {forecast.trend || 'stable'}
            </p>
            <p className="text-sm text-slate-300">Demand Trend</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {selectedEquipment === 'all' ? (
          <div>
            <h4 className="text-lg font-medium text-slate-900 mb-4">
              Demand by Equipment Type
            </h4>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip
                  contentStyle={{ borderRadius: 12, border: '1px solid #e2e8f0' }}
                />
                <Bar dataKey="demand" fill="#f59e0b" radius={[8, 8, 0, 0]} name="Predicted Demand" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div>
            <h4 className="text-lg font-medium text-slate-900 mb-4">
              Daily Demand Forecast
            </h4>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="demandFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip
                  contentStyle={{ borderRadius: 12, border: '1px solid #e2e8f0' }}
                />
                <Area
                  type="monotone"
                  dataKey="demand"
                  stroke="#d97706"
                  strokeWidth={2.5}
                  fill="url(#demandFill)"
                  name="Predicted Demand"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}

        <div>
          <h4 className="text-lg font-medium text-slate-900 mb-4">
            {selectedEquipment === 'all'
              ? 'Equipment Performance'
              : 'Forecast Confidence'}
          </h4>
          {selectedEquipment === 'all' ? (
            <div className="space-y-3">
              {chartData.map((item: any) => (
                <div
                  key={item.name}
                  className="bg-slate-50 rounded-xl p-4 flex items-center justify-between"
                >
                  <span className="font-medium text-slate-900">
                    {item.name}
                  </span>
                  <div className="flex items-center gap-3">
                    <span className="text-sm text-slate-500">
                      {item.avgDaily?.toFixed(1) || 0} /day
                    </span>
                    <span
                      className={`text-sm px-2.5 py-1 rounded-full font-semibold ${
                        item.trend === 'increasing'
                          ? 'bg-emerald-100 text-emerald-700'
                          : item.trend === 'decreasing'
                            ? 'bg-red-100 text-red-700'
                            : 'bg-slate-200 text-slate-700'
                      }`}
                    >
                      {item.trend === 'increasing'
                        ? '↗ Increasing'
                        : item.trend === 'decreasing'
                          ? '↘ Decreasing'
                          : '→ Stable'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-3">
              {chartData.slice(0, 10).map((day: any, i: number) => (
                <div
                  key={i}
                  className="bg-slate-50 rounded-xl p-3 flex items-center justify-between"
                >
                  <div>
                    <span className="font-medium text-slate-900">
                      {day.name}
                    </span>
                    <p className="text-xs text-slate-500">{day.dayOfWeek}</p>
                  </div>
                  <div className="text-right">
                    <span className="text-lg font-bold text-amber-600">
                      {day.demand}
                    </span>
                    <p className="text-xs text-slate-500">
                      {(day.confidence * 100).toFixed(0)}% conf.
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {selectedEquipment !== 'all' && forecast.forecasts && (
        <div>
          <h4 className="text-lg font-medium text-slate-900 mb-4">
            Detailed Forecast
          </h4>
          <div className="overflow-x-auto rounded-xl ring-1 ring-slate-200">
            <table className="min-w-full divide-y divide-slate-200">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    Day
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    Predicted Demand
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    Confidence
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-200">
                {forecast.forecasts.map((day: any, index: number) => (
                  <tr key={index} className="hover:bg-slate-50">
                    <td className="px-6 py-3 whitespace-nowrap text-sm font-medium text-slate-900">
                      {day.date}
                    </td>
                    <td className="px-6 py-3 whitespace-nowrap text-sm text-slate-500">
                      {day.day_of_week}
                    </td>
                    <td className="px-6 py-3 whitespace-nowrap text-sm text-slate-500">
                      {day.predicted_demand}
                    </td>
                    <td className="px-6 py-3 whitespace-nowrap text-sm text-slate-500">
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-1.5 bg-slate-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-amber-400 rounded-full"
                            style={{ width: `${(day.confidence * 100).toFixed(0)}%` }}
                          ></div>
                        </div>
                        {(day.confidence * 100).toFixed(0)}%
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
