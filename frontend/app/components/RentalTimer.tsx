'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Badge } from './ui/badge'
import { Clock, AlertTriangle, CheckCircle, Calendar, Timer } from 'lucide-react'

interface RentalTimerProps {
  rentalId: number
  equipmentId: string
  equipmentType: string
  checkOutDate: string
  expectedReturnDate: string
  status: string
  onExtendRental?: (days: number) => void
  onCheckIn?: () => void
  onSendReminder?: () => void
}

interface TimerData {
  elapsed_days: number
  elapsed_hours: number
  days_remaining: number | null
  hours_remaining: number | null
  is_overdue: boolean
  overdue_days: number
  status: string
}

export default function RentalTimer({
  rentalId,
  equipmentId,
  equipmentType,
  checkOutDate,
  expectedReturnDate,
  status,
  onExtendRental,
  onCheckIn,
  onSendReminder
}: RentalTimerProps) {
  const [timerData, setTimerData] = useState<TimerData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showExtendModal, setShowExtendModal] = useState(false)
  const [extensionDays, setExtensionDays] = useState(7)

  // Fetch timer data
  const fetchTimerData = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'https://cat-v7yf.onrender.com'}/rentals/${rentalId}/timer`)
      if (response.ok) {
        const data = await response.json()
        setTimerData(data)
        setError(null)
      } else {
        setError('Failed to fetch timer data')
      }
    } catch (err) {
      setError('Error connecting to server')
    } finally {
      setLoading(false)
    }
  }

  // Update timer every minute
  useEffect(() => {
    fetchTimerData()
    const interval = setInterval(fetchTimerData, 60000) // Update every minute
    return () => clearInterval(interval)
  }, [rentalId])

  // Auto-refresh timer display every second for countdown
  useEffect(() => {
    if (!timerData || status !== 'active') return
    
    const interval = setInterval(() => {
      setTimerData(prev => {
        if (!prev) return prev
        
        // Update elapsed time
        const now = new Date()
        const start = new Date(checkOutDate)
        const elapsed = now.getTime() - start.getTime()
        const elapsed_days = Math.floor(elapsed / (1000 * 60 * 60 * 24))
        const elapsed_hours = elapsed / (1000 * 60 * 60)
        
        // Update remaining time
        let days_remaining = prev.days_remaining
        let hours_remaining = prev.hours_remaining
        let is_overdue = prev.is_overdue
        let overdue_days = prev.overdue_days
        
        if (expectedReturnDate) {
          const expected = new Date(expectedReturnDate)
          const remaining = expected.getTime() - now.getTime()
          
          if (remaining > 0) {
            days_remaining = Math.floor(remaining / (1000 * 60 * 60 * 24))
            hours_remaining = remaining / (1000 * 60 * 60)
            is_overdue = false
            overdue_days = 0
          } else {
            days_remaining = 0
            hours_remaining = 0
            is_overdue = true
            overdue_days = Math.abs(Math.floor(remaining / (1000 * 60 * 60 * 24)))
          }
        }
        
        return {
          ...prev,
          elapsed_days,
          elapsed_hours,
          days_remaining,
          hours_remaining,
          is_overdue,
          overdue_days
        }
      })
    }, 1000)
    
    return () => clearInterval(interval)
  }, [timerData, checkOutDate, expectedReturnDate, status])

  const handleExtendRental = async () => {
    if (!onExtendRental) return
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'https://cat-v7yf.onrender.com'}/rentals/${rentalId}/extend`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ extension_days: extensionDays }),
      })
      
      if (response.ok) {
        onExtendRental(extensionDays)
        setShowExtendModal(false)
        fetchTimerData() // Refresh timer data
      }
    } catch (err) {
      console.error('Failed to extend rental:', err)
    }
  }

  const handleSendReminder = async () => {
    if (!onSendReminder) return
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'https://cat-v7yf.onrender.com'}/rentals/${rentalId}/send-reminder`, {
        method: 'POST',
      })
      
      if (response.ok) {
        onSendReminder()
      }
    } catch (err) {
      console.error('Failed to send reminder:', err)
    }
  }

  if (loading) {
    return (
      <Card className="w-full">
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-2">Loading timer...</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className="w-full">
        <CardContent className="p-6">
          <div className="text-red-600 text-center">
            <AlertTriangle className="h-6 w-6 mx-auto mb-2" />
            {error}
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!timerData) {
    return (
      <Card className="w-full">
        <CardContent className="p-6">
          <div className="text-gray-500 text-center">No timer data available</div>
        </CardContent>
      </Card>
    )
  }

  const getStatusColor = () => {
    if (timerData.is_overdue) return 'bg-red-100 text-red-800 border-red-200'
    if (timerData.days_remaining !== null && timerData.days_remaining <= 3) return 'bg-yellow-100 text-yellow-800 border-yellow-200'
    return 'bg-green-100 text-green-800 border-green-200'
  }

  const getStatusIcon = () => {
    if (timerData.is_overdue) return <AlertTriangle className="h-4 w-4" />
    if (timerData.days_remaining !== null && timerData.days_remaining <= 3) return <Clock className="h-4 w-4" />
    return <CheckCircle className="h-4 w-4" />
  }

  return (
    <Card className="w-full">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-2">
          <Timer className="h-5 w-5" />
          Rental Timer - {equipmentId}
        </CardTitle>
        <div className="flex items-center gap-2">
          <Badge className={getStatusColor()}>
            {getStatusIcon()}
            <span className="ml-1">
              {timerData.is_overdue ? 'OVERDUE' : 
               timerData.days_remaining !== null && timerData.days_remaining <= 3 ? 'DUE SOON' : 'ACTIVE'}
            </span>
          </Badge>
          <span className="text-sm text-gray-600">{equipmentType}</span>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Timer Display */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{timerData.elapsed_days}</div>
            <div className="text-sm text-gray-600">Days Elapsed</div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{Math.round(timerData.elapsed_hours)}</div>
            <div className="text-sm text-gray-600">Hours Elapsed</div>
          </div>
          
          {timerData.days_remaining !== null && (
            <>
              <div className="text-center">
                <div className={`text-2xl font-bold ${timerData.is_overdue ? 'text-red-600' : 'text-green-600'}`}>
                  {timerData.is_overdue ? timerData.overdue_days : timerData.days_remaining}
                </div>
                <div className="text-sm text-gray-600">
                  {timerData.is_overdue ? 'Days Overdue' : 'Days Remaining'}
                </div>
              </div>
              
              <div className="text-center">
                <div className={`text-2xl font-bold ${timerData.is_overdue ? 'text-red-600' : 'text-green-600'}`}>
                  {timerData.is_overdue ? 
                    Math.round((timerData.overdue_days * 24)) : 
                    Math.round(timerData.hours_remaining || 0)
                  }
                </div>
                <div className="text-sm text-gray-600">
                  {timerData.is_overdue ? 'Hours Overdue' : 'Hours Remaining'}
                </div>
              </div>
            </>
          )}
        </div>

        {/* Dates */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4 text-gray-500" />
            <span className="text-gray-600">Check-out:</span>
            <span className="font-medium">{new Date(checkOutDate).toLocaleDateString()}</span>
          </div>
          
          {expectedReturnDate && (
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-gray-500" />
              <span className="text-gray-600">Expected Return:</span>
              <span className="font-medium">{new Date(expectedReturnDate).toLocaleDateString()}</span>
            </div>
          )}
        </div>

        {/* Overdue Warning */}
        {timerData.is_overdue && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center gap-2 text-red-800">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-medium">Equipment is overdue by {timerData.overdue_days} days!</span>
            </div>
            <p className="text-red-700 text-sm mt-1">
              Please return the equipment immediately to avoid additional charges.
            </p>
          </div>
        )}

        {/* Due Soon Warning */}
        {!timerData.is_overdue && timerData.days_remaining !== null && timerData.days_remaining <= 3 && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-center gap-2 text-yellow-800">
              <Clock className="h-5 w-5" />
              <span className="font-medium">Equipment due in {timerData.days_remaining} days</span>
            </div>
            <p className="text-yellow-700 text-sm mt-1">
              Consider extending the rental or preparing for return.
            </p>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-wrap gap-2">
          {onExtendRental && (
            <Button
              variant="outline"
              onClick={() => setShowExtendModal(true)}
              className="flex items-center gap-2"
            >
              <Calendar className="h-4 w-4" />
              Extend Rental
            </Button>
          )}
          
          {onSendReminder && (
            <Button
              variant="outline"
              onClick={handleSendReminder}
              className="flex items-center gap-2"
            >
              <Clock className="h-4 w-4" />
              Send Reminder
            </Button>
          )}
          
          {onCheckIn && (
            <Button
              onClick={onCheckIn}
              className="flex items-center gap-2 bg-green-600 hover:bg-green-700"
            >
              <CheckCircle className="h-4 w-4" />
              Check In
            </Button>
          )}
        </div>

        {/* Extension Modal */}
        {showExtendModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
              <h3 className="text-lg font-semibold mb-4">Extend Rental</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Extension Period (days)
                  </label>
                  <select
                    value={extensionDays}
                    onChange={(e) => setExtensionDays(Number(e.target.value))}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  >
                    <option value={1}>1 day</option>
                    <option value={3}>3 days</option>
                    <option value={7}>1 week</option>
                    <option value={14}>2 weeks</option>
                    <option value={30}>1 month</option>
                  </select>
                </div>
                
                <div className="flex gap-2">
                  <Button
                    onClick={handleExtendRental}
                    className="flex-1"
                  >
                    Extend Rental
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => setShowExtendModal(false)}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
