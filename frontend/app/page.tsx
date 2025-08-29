'use client'

import { useState, useEffect } from 'react'
import DashboardCard from './components/DashboardCard'
import EquipmentTable from './components/EquipmentTable'
import AnomalyAlerts from './components/AnomalyAlerts'
import DemandForecast from './components/DemandForecast'
import EquipmentStats from './components/EquipmentStats'

export default function Dashboard() {
  const [dashboardData, setDashboardData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('overview')
  const [backendStatus, setBackendStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking')
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)
  const [autoRefresh, setAutoRefresh] = useState(true)

  useEffect(() => {
    const checkBackendStatus = async () => {
      try {
        const response = await fetch('http://localhost:8000/')
        if (response.ok) {
          setBackendStatus('connected')
          // If backend just came online, refresh dashboard data
          if (dashboardData?.overview?.total_equipment === 0) {
            loadDashboardData()
          }
        } else {
          setBackendStatus('disconnected')
        }
      } catch (error) {
        setBackendStatus('disconnected')
      }
    }

    checkBackendStatus()

    // Poll backend status every 10 seconds
    const interval = setInterval(checkBackendStatus, 10000)
    return () => clearInterval(interval)
  }, [dashboardData?.overview?.total_equipment])

  // Initial data loading and auto-refresh
  useEffect(() => {
    loadDashboardData()

    // Set up auto-refresh every 30 seconds if enabled
    let refreshInterval: NodeJS.Timeout | null = null

    if (autoRefresh) {
      refreshInterval = setInterval(() => {
        // Only refresh if backend is connected and we're not currently loading
        if (backendStatus === 'connected' && !loading) {
          loadDashboardData()
        }
      }, 30000)
    }

    return () => {
      if (refreshInterval) {
        clearInterval(refreshInterval)
      }
    }
  }, [autoRefresh, backendStatus, loading])

  const checkBackendStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/')
      if (response.ok) {
        setBackendStatus('connected')
        // If backend just came online, refresh dashboard data
        if (dashboardData?.overview?.total_equipment === 0) {
          loadDashboardData()
        }
      } else {
        setBackendStatus('disconnected')
      }
    } catch (error) {
      setBackendStatus('disconnected')
    }
  }

  const loadDashboardData = async () => {
    try {
      // Always try to fetch real data from backend first
      const response = await fetch('http://localhost:8000/dashboard')
      if (response.ok) {
        const data = await response.json()
        setDashboardData(data)
        setLastUpdated(new Date())
        setBackendStatus('connected')
      } else {
        throw new Error('Backend not accessible')
      }
    } catch (error) {
      console.error('Error loading dashboard data:', error)
      setBackendStatus('disconnected')
      // Show empty state when backend is offline
      setDashboardData({
        overview: {
          total_equipment: 0,
          active_rentals: 0,
          anomalies: 0,
          utilization_rate: 0
        },
        equipment_stats: null,
        anomalies: null,
        recommendations: []
      })
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading Smart Rental Tracker...</p>
        </div>
      </div>
    )
  }

  const tabs = [
    { id: 'overview', name: 'Overview', icon: '📊' },
    { id: 'equipment', name: 'Equipment', icon: '⚙️' },
    { id: 'anomalies', name: 'Anomalies', icon: '⚠️' },
    { id: 'forecasting', name: 'Demand Forecast', icon: '📈' },
    { id: 'analytics', name: 'Analytics', icon: '📊' },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Smart Rental Tracking System
              </h1>
              <p className="mt-1 text-sm text-gray-500">
                AI-powered equipment rental management with real-time monitoring
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">
                  {new Date().toLocaleDateString()}
                </p>
                <p className="text-xs text-gray-500">
                  {new Date().toLocaleTimeString()}
                </p>
                {lastUpdated && (
                  <p className="text-xs text-gray-400">
                    Last updated: {lastUpdated.toLocaleTimeString()}
                  </p>
                )}
              </div>
              <div className="flex items-center space-x-2">
                <label className="flex items-center space-x-1 text-xs text-gray-600">
                  <input
                    type="checkbox"
                    checked={autoRefresh}
                    onChange={(e) => setAutoRefresh(e.target.checked)}
                    className="w-3 h-3 text-blue-600 rounded"
                  />
                  <span>Auto-refresh (30s)</span>
                </label>
              </div>
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${backendStatus === 'connected' ? 'bg-green-500' :
                    backendStatus === 'disconnected' ? 'bg-red-500' : 'bg-yellow-500'
                  }`}></div>
                <span className={`text-xs font-medium ${backendStatus === 'connected' ? 'text-green-600' :
                    backendStatus === 'disconnected' ? 'text-red-600' : 'text-yellow-600'
                  }`}>
                  {backendStatus === 'connected' ? 'Backend Connected' :
                    backendStatus === 'disconnected' ? 'Backend Offline' : 'Checking...'}
                </span>
                <button
                  onClick={() => {
                    setBackendStatus('checking')
                    checkBackendStatus()
                  }}
                  className="ml-2 p-1 text-gray-400 hover:text-gray-600 transition-colors"
                  title="Refresh backend status"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </button>
                <button
                  onClick={() => {
                    setLoading(true)
                    loadDashboardData()
                  }}
                  className="ml-2 p-1 text-gray-400 hover:text-gray-600 transition-colors"
                  title="Refresh dashboard data"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.121A1 1 0 013 6.414V4z" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
              >
                <span className="inline-block w-5 h-5 mr-2">{tab.icon}</span>
                {tab.name}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Backend Status Message */}
        {backendStatus === 'disconnected' && (
          <div className="mb-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-yellow-800">
                  Backend Server Offline
                </h3>
                <div className="mt-2 text-sm text-yellow-700">
                  <p>
                    The backend server is currently offline. You're viewing cached data.
                    To see real-time data, please start the backend server:
                  </p>
                  <div className="mt-2 font-mono text-xs bg-yellow-100 p-2 rounded">
                    cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Dashboard Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <DashboardCard
                title="Total Equipment"
                value={dashboardData?.overview?.total_equipment || 0}
                icon="⚙️"
                trend="+12%"
                trendDirection="up"
                color="blue"
              />
              <DashboardCard
                title="Active Rentals"
                value={dashboardData?.overview?.active_rentals || 0}
                icon="⏰"
                trend="+5%"
                trendDirection="up"
                color="green"
              />
              <DashboardCard
                title="Anomalies Detected"
                value={dashboardData?.overview?.anomalies || 0}
                icon="⚠️"
                trend="-8%"
                trendDirection="down"
                color="red"
              />
              <DashboardCard
                title="Utilization Rate"
                value={`${dashboardData?.overview?.utilization_rate || 0}%`}
                icon="📊"
                trend="+3%"
                trendDirection="up"
                color="yellow"
              />
            </div>

            {/* Charts and Tables */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="card">
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  Equipment Performance
                </h3>
                <EquipmentStats />
              </div>
              <div className="card">
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  Recent Anomalies
                </h3>
                <AnomalyAlerts />
              </div>
            </div>

            {/* Demand Forecast Preview */}
            <div className="card">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Demand Forecast (Next 7 Days)
              </h3>
              <DemandForecast daysAhead={7} />
            </div>
          </div>
        )}

        {activeTab === 'equipment' && (
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">
              Equipment Management
            </h2>
            <EquipmentTable />
          </div>
        )}

        {activeTab === 'anomalies' && (
          <div className="space-y-6">
            <div className="card">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">
                Anomaly Detection & Alerts
              </h2>
              <AnomalyAlerts />
            </div>
          </div>
        )}

        {activeTab === 'forecasting' && (
          <div className="space-y-6">
            <div className="card">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">
                Demand Forecasting
              </h2>
              <DemandForecast daysAhead={30} />
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="space-y-6">
            <div className="card">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">
                Equipment Analytics
              </h2>
              <EquipmentStats />
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
