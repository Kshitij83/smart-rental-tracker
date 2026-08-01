'use client'

import { useState, useEffect } from 'react'
import {
  Boxes,
  CalendarClock,
  AlertTriangle,
  Gauge,
  RefreshCw,
  LayoutDashboard,
  Cog,
  ShieldAlert,
  TrendingUp,
  BarChart3,
  Wrench,
  CloudOff,
  Clock,
  Server,
} from 'lucide-react'
import DashboardCard from './components/DashboardCard'
import EquipmentTable from './components/EquipmentTable'
import AnomalyAlerts from './components/AnomalyAlerts'
import DemandForecast from './components/DemandForecast'
import EquipmentStats from './components/EquipmentStats'
import { API_BASE_URL } from './lib/config'

export default function Dashboard() {
  const [dashboardData, setDashboardData] = useState<any>(null)
  const [mlStatus, setMlStatus] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('overview')
  const [backendStatus, setBackendStatus] = useState<
    'connected' | 'disconnected' | 'checking'
  >('checking')

  const checkBackendStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/`)
      if (response.ok) {
        setBackendStatus('connected')
      } else {
        setBackendStatus('disconnected')
      }
    } catch (error) {
      setBackendStatus('disconnected')
    }
  }

  const loadMlStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/ml/status`)
      if (response.ok) {
        const data = await response.json()
        setMlStatus(data)
      }
    } catch (error) {
      setMlStatus(null)
    }
  }

  const loadDashboardData = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/dashboard`)
      if (response.ok) {
        const data = await response.json()
        setDashboardData(data)
      } else {
        throw new Error('Backend not accessible')
      }
    } catch (error) {
      console.error('Error loading dashboard data:', error)
      setDashboardData({
        overview: {
          total_equipment: 0,
          active_rentals: 0,
          anomalies: 0,
          utilization_rate: 0,
        },
        equipment_stats: null,
        anomalies: null,
        recommendations: [],
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    checkBackendStatus()
    loadDashboardData()
    loadMlStatus()
    const interval = setInterval(checkBackendStatus, 10000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-amber-400 mx-auto"></div>
          <p className="mt-4 text-slate-600 font-medium">
            Loading Smart Rental Tracker...
          </p>
        </div>
      </div>
    )
  }

  const tabs = [
    { id: 'overview', name: 'Overview', icon: LayoutDashboard },
    { id: 'equipment', name: 'Equipment', icon: Cog },
    { id: 'anomalies', name: 'Anomalies', icon: ShieldAlert },
    { id: 'forecasting', name: 'Demand Forecast', icon: TrendingUp },
    { id: 'analytics', name: 'Analytics', icon: BarChart3 },
  ]

  const overview = dashboardData?.overview || {}

  const statusColor =
    backendStatus === 'connected'
      ? 'bg-emerald-500'
      : backendStatus === 'disconnected'
        ? 'bg-red-500'
        : 'bg-amber-500'
  const statusText =
    backendStatus === 'connected'
      ? 'API Connected'
      : backendStatus === 'disconnected'
        ? 'API Offline'
        : 'Checking...'
  const statusTextColor =
    backendStatus === 'connected'
      ? 'text-emerald-300'
      : backendStatus === 'disconnected'
        ? 'text-red-300'
        : 'text-amber-300'

  return (
    <div className="min-h-screen bg-slate-100">
      {/* Header */}
      <header className="bg-slate-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center py-6 gap-4">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-2xl bg-amber-400 flex items-center justify-center shadow-lg shadow-amber-400/20">
                <Wrench className="w-6 h-6 text-slate-900" />
              </div>
              <div>
                <h1 className="text-2xl font-bold tracking-tight">
                  Smart Rental Tracker
                </h1>
                <p className="text-sm text-slate-400">
                  AI-powered equipment rental management &amp; real-time
                  monitoring
                </p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right hidden sm:block">
                <p className="text-sm font-medium">
                  {new Date().toLocaleDateString(undefined, {
                    weekday: 'short',
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric',
                  })}
                </p>
                <p className="text-xs text-slate-400">
                  {new Date().toLocaleTimeString()}
                </p>
              </div>
              <div
                className={`flex items-center gap-2 rounded-full px-3 py-1.5 ring-1 ${
                  backendStatus === 'connected'
                    ? 'bg-emerald-500/10 ring-emerald-400/30'
                    : backendStatus === 'disconnected'
                      ? 'bg-red-500/10 ring-red-400/30'
                      : 'bg-amber-500/10 ring-amber-400/30'
                }`}
              >
                <span className={`w-2.5 h-2.5 rounded-full ${statusColor} animate-pulse`}></span>
                <span className={`text-xs font-semibold ${statusTextColor}`}>
                  {statusText}
                </span>
              </div>
              <button
                onClick={() => {
                  setBackendStatus('checking')
                  checkBackendStatus()
                  loadDashboardData()
                  loadMlStatus()
                }}
                className="p-2 rounded-xl bg-white/10 hover:bg-white/20 transition-colors"
                title="Refresh data"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-white border-b border-slate-200 sticky top-0 z-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex overflow-x-auto gap-1 py-2">
            {tabs.map((tab) => {
              const Icon = tab.icon
              const active = activeTab === tab.id
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium whitespace-nowrap transition-colors ${
                    active
                      ? 'bg-slate-900 text-white shadow'
                      : 'text-slate-500 hover:text-slate-900 hover:bg-slate-100'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.name}
                </button>
              )
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {backendStatus === 'disconnected' && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-2xl p-5 flex items-start gap-3">
            <CloudOff className="w-5 h-5 text-red-500 mt-0.5 shrink-0" />
            <div>
              <h3 className="text-sm font-semibold text-red-800">
                API server unreachable
              </h3>
              <p className="mt-1 text-sm text-red-700">
                The backend at{' '}
                <code className="font-mono text-xs bg-red-100 px-1.5 py-0.5 rounded">
                  {API_BASE_URL}
                </code>{' '}
                is offline. Start it locally or check the deployment.
              </p>
            </div>
          </div>
        )}

        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
              <DashboardCard
                title="Total Equipment"
                value={overview.total_equipment ?? 0}
                icon={<Boxes className="w-5 h-5" />}
                trend="Fleet"
                trendDirection="up"
                accent="blue"
                subtitle="units in fleet"
              />
              <DashboardCard
                title="Active Rentals"
                value={overview.active_rentals ?? 0}
                icon={<CalendarClock className="w-5 h-5" />}
                trend="Deployed"
                trendDirection="up"
                accent="green"
                subtitle="currently on-site"
              />
              <DashboardCard
                title="Anomalies Detected"
                value={overview.anomalies ?? 0}
                icon={<AlertTriangle className="w-5 h-5" />}
                trend="Flagged"
                trendDirection="down"
                accent="red"
                subtitle="need attention"
              />
              <DashboardCard
                title="Utilization Rate"
                value={`${overview.utilization_rate ?? 0}%`}
                icon={<Gauge className="w-5 h-5" />}
                trend="Fleet avg"
                trendDirection="up"
                accent="amber"
                subtitle="engine vs idle"
              />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="card">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-slate-900">
                    Equipment Performance
                  </h3>
                  <span className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-500">
                    <Clock className="w-3.5 h-3.5" /> by type
                  </span>
                </div>
                <EquipmentStats />
              </div>
              <div className="card">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-slate-900">
                    Recent Anomalies
                  </h3>
                  <span className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-500">
                    <ShieldAlert className="w-3.5 h-3.5" /> realtime
                  </span>
                </div>
                <AnomalyAlerts />
              </div>
            </div>

            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-slate-900">
                    Demand Forecast
                  </h3>
                  <p className="text-sm text-slate-500">
                    ML-powered demand predictions for the next 7 days
                  </p>
                </div>
                <span
                  className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold ${
                    mlStatus?.models_loaded
                      ? 'bg-emerald-50 text-emerald-700'
                      : 'bg-slate-100 text-slate-500'
                  }`}
                >
                  <Server className="w-3.5 h-3.5" />
                  {mlStatus?.models_loaded ? 'ML Online' : 'ML Standby'}
                </span>
              </div>
              <DemandForecast daysAhead={7} />
            </div>
          </div>
        )}

        {activeTab === 'equipment' && (
          <div className="card">
            <h2 className="text-xl font-semibold text-slate-900 mb-6">
              Equipment Management
            </h2>
            <EquipmentTable />
          </div>
        )}

        {activeTab === 'anomalies' && (
          <div className="space-y-6">
            <div className="card">
              <div className="flex items-center gap-3 mb-6">
                <ShieldAlert className="w-6 h-6 text-red-500" />
                <h2 className="text-xl font-semibold text-slate-900">
                  Anomaly Detection &amp; Alerts
                </h2>
              </div>
              <AnomalyAlerts showAll={true} />
            </div>
          </div>
        )}

        {activeTab === 'forecasting' && (
          <div className="space-y-6">
            <div className="card">
              <h2 className="text-xl font-semibold text-slate-900 mb-6">
                Demand Forecasting
              </h2>
              <DemandForecast daysAhead={30} />
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="space-y-6">
            <div className="card">
              <h2 className="text-xl font-semibold text-slate-900 mb-6">
                Equipment Analytics
              </h2>
              <EquipmentStats showDetailed={true} />
            </div>
          </div>
        )}

        <footer className="mt-10 pb-6 text-center">
          <p className="text-xs text-slate-400">
            Smart Rental Tracker · Caterpillar Hackathon · FastAPI + Next.js +
            scikit-learn
          </p>
        </footer>
      </main>
    </div>
  )
}
