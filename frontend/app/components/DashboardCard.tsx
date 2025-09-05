import { ReactElement, ComponentType } from 'react'

interface DashboardCardProps {
  title: string
  value: string | number
  icon: ComponentType<{ className?: string }> | string
  trend?: string
  trendDirection?: 'up' | 'down'
  color?: 'blue' | 'green' | 'red' | 'yellow'
}

const colorClasses = {
  blue: 'text-blue-600 bg-blue-100',
  green: 'text-green-600 bg-green-100',
  red: 'text-red-600 bg-red-100',
  yellow: 'text-yellow-600 bg-yellow-100',
}

export default function DashboardCard({
  title,
  value,
  icon,
  trend,
  trendDirection,
  color = 'blue',
}: DashboardCardProps) {
  const renderIcon = () => {
    if (typeof icon === 'string') {
      // Handle emoji string
      return <span className="text-2xl">{icon}</span>
    } else {
      // Handle React component
      const IconComponent = icon as ComponentType<{ className?: string }>
      return <IconComponent className="w-6 h-6" />
    }
  }

  return (
    <div className="card hover:shadow-lg transition-shadow duration-200">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
          {trend && (
            <div className="flex items-center mt-2">
              {trendDirection === 'up' ? (
                <span className="text-green-500 mr-1 text-lg">↑</span>
              ) : (
                <span className="text-red-500 mr-1 text-lg">↓</span>
              )}
              <span
                className={`text-sm font-medium ${
                  trendDirection === 'up' ? 'text-green-600' : 'text-red-600'
                }`}
              >
                {trend}
              </span>
            </div>
          )}
        </div>
        <div className={`p-3 rounded-full ${colorClasses[color]}`}>
          {renderIcon()}
        </div>
      </div>
    </div>
  )
}
