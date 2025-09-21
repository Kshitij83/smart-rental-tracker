'use client'

import { useState, useEffect } from 'react'
import DashboardCard from './components/DashboardCard'
import EquipmentTable from './components/EquipmentTable'
import AnomalyAlerts from './components/AnomalyAlerts'
import DemandForecast from './components/DemandForecast'
import EquipmentStats from './components/EquipmentStats'
import RentalDashboard from './components/RentalDashboard'

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
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'https://cat-v7yf.onrender.com'}/`)
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

  // Listen for refresh events from child components
  useEffect(() => {
    const handleRefreshDashboard = () => {
      loadDashboardData()
    }

    window.addEventListener('refreshDashboard', handleRefreshDashboard)
    
    return () => {
      window.removeEventListener('refreshDashboard', handleRefreshDashboard)
    }
  }, [])

  const checkBackendStatus = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'https://cat-v7yf.onrender.com'}/`)
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
      // Fetch dashboard data and equipment data in parallel
      const [dashboardResponse, equipmentResponse] = await Promise.all([
        fetch(`${process.env.NEXT_PUBLIC_API_URL || 'https://cat-v7yf.onrender.com'}/dashboard`),
        fetch(`${process.env.NEXT_PUBLIC_API_URL || 'https://cat-v7yf.onrender.com'}/equipment/`)
      ])
      
      if (dashboardResponse.ok && equipmentResponse.ok) {
        const dashboardData = await dashboardResponse.json()
        const equipmentData = await equipmentResponse.json()
        
        // Add equipment data to dashboard data
        dashboardData.equipment_list = equipmentData
        
        setDashboardData(dashboardData)
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
    { id: 'rentals', name: 'Rental Management', icon: '⏰' },
    { id: 'equipment', name: 'Equipment', icon: '⚙️' },
    { id: 'anomalies', name: 'Anomalies', icon: '⚠️' },
    { id: 'forecasting', name: 'Demand Forecast', icon: '📈' },
    { id: 'analytics', name: 'Analytics', icon: '📊' },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md shadow-lg border-b border-gray-200/50 lg:sticky lg:top-0 z-40">
        <div className="max-w-7xl mx-auto px-2 sm:px-4 lg:px-8">
          <div className="flex flex-col lg:flex-row lg:justify-between lg:items-center py-4 sm:py-6 gap-4">
            <div className="flex-1">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                  <span className="text-white font-bold text-lg">SRT</span>
                </div>
                <div>
                  <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
                    Smart Rental Tracking System
                  </h1>
                  <p className="mt-1 text-xs sm:text-sm text-gray-600">
                    AI-powered equipment rental management with real-time monitoring
                  </p>
                </div>
              </div>
            </div>
            
            {/* Mobile Layout */}
            <div className="lg:hidden space-y-3">
              <div className="flex items-center justify-between">
                <div className="text-left">
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
                  <div className={`w-3 h-3 rounded-full ${backendStatus === 'connected' ? 'bg-green-500' :
                      backendStatus === 'disconnected' ? 'bg-red-500' : 'bg-yellow-500'
                    }`}></div>
                  <span className={`text-xs font-medium ${backendStatus === 'connected' ? 'text-green-600' :
                      backendStatus === 'disconnected' ? 'text-red-600' : 'text-yellow-600'
                    }`}>
                    {backendStatus === 'connected' ? 'Connected' :
                      backendStatus === 'disconnected' ? 'Offline' : 'Checking...'}
                  </span>
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <label className="flex items-center space-x-1 text-xs text-gray-600">
                  <input
                    type="checkbox"
                    checked={autoRefresh}
                    onChange={(e) => setAutoRefresh(e.target.checked)}
                    className="w-3 h-3 text-blue-600 rounded"
                  />
                  <span>Auto-refresh (30s)</span>
                </label>
                <div className="flex items-center space-x-1">
                  <button
                    onClick={() => {
                      setBackendStatus('checking')
                      checkBackendStatus()
                    }}
                    className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
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
                    className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                    title="Refresh dashboard data"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.121A1 1 0 013 6.414V4z" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            {/* Desktop Layout */}
            <div className="hidden lg:flex items-center space-x-4">
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
      <nav className="bg-white/60 backdrop-blur-sm border-b border-gray-200/50">
        <div className="max-w-7xl mx-auto px-2 sm:px-4 lg:px-8">
          <div className="overflow-x-auto">
            <div className="flex space-x-1 sm:space-x-2 lg:space-x-4 min-w-max py-2">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`relative py-3 sm:py-4 px-3 sm:px-6 font-medium text-xs sm:text-sm whitespace-nowrap flex items-center rounded-xl transition-all duration-200 group ${
                    activeTab === tab.id
                      ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg transform scale-105'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100/80 hover:shadow-md'
                  }`}
                >
                  <span className={`inline-block w-4 h-4 sm:w-5 sm:h-5 mr-2 text-xs sm:text-sm transition-transform duration-200 ${
                    activeTab === tab.id ? 'scale-110' : 'group-hover:scale-105'
                  }`}>
                    {tab.icon}
                  </span>
                  <span className="hidden sm:inline font-semibold">{tab.name}</span>
                  <span className="sm:hidden font-semibold">{tab.name.split(' ')[0]}</span>
                  
                  {/* Active indicator */}
                  {activeTab === tab.id && (
                    <div className="absolute -bottom-1 left-1/2 transform -translate-x-1/2 w-2 h-2 bg-white rounded-full shadow-lg"></div>
                  )}
                </button>
              ))}
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto pt-8 sm:pt-12 pb-4 sm:pb-6 px-2 sm:px-4 lg:px-8">
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
          <div className="space-y-4 sm:space-y-6">
            {/* Dashboard Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
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
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
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
                Demand Forecast (Next 30 Days)
              </h3>
              <DemandForecast daysAhead={30} />
            </div>
          </div>
        )}

        {activeTab === 'rentals' && (
          <div className="space-y-4 sm:space-y-6">
            <RentalDashboard dashboardData={dashboardData} />
          </div>
        )}

        {activeTab === 'equipment' && (
          <div className="card">
            <h2 className="text-lg sm:text-xl font-semibold text-gray-900 mb-4 sm:mb-6">
              Equipment Management
            </h2>
            <EquipmentTable />
          </div>
        )}

        {activeTab === 'anomalies' && (
          <div className="space-y-4 sm:space-y-6">
            <div className="card">
              <h2 className="text-lg sm:text-xl font-semibold text-gray-900 mb-4 sm:mb-6">
                Anomaly Detection & Alerts
              </h2>
              <AnomalyAlerts />
            </div>
          </div>
        )}

        {activeTab === 'forecasting' && (
          <div className="space-y-4 sm:space-y-6">
            <div className="card">
              <h2 className="text-lg sm:text-xl font-semibold text-gray-900 mb-4 sm:mb-6">
                Demand Forecasting
              </h2>
              <DemandForecast daysAhead={30} />
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="space-y-4 sm:space-y-6">
            <div className="card">
              <h2 className="text-lg sm:text-xl font-semibold text-gray-900 mb-4 sm:mb-6">
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
