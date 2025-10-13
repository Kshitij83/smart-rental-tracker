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
  blue: 'text-blue-600 bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200',
  green: 'text-green-600 bg-gradient-to-br from-green-50 to-green-100 border-green-200',
  red: 'text-red-600 bg-gradient-to-br from-red-50 to-red-100 border-red-200',
  yellow: 'text-yellow-600 bg-gradient-to-br from-yellow-50 to-yellow-100 border-yellow-200',
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
    <div className="group relative bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg hover:shadow-xl border border-gray-200/50 p-6 transition-all duration-300 hover:-translate-y-1 overflow-hidden">
      {/* Background gradient overlay */}
      <div className={`absolute inset-0 opacity-0 group-hover:opacity-5 transition-opacity duration-300 ${colorClasses[color].split(' ')[1]}`}></div>
      
      <div className="relative flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-semibold text-gray-600 uppercase tracking-wide">{title}</p>
          <p className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent mt-2">{value}</p>
          {trend && (
            <div className="flex items-center mt-3">
              <div className={`flex items-center px-2 py-1 rounded-full text-xs font-semibold ${
                trendDirection === 'up' 
                  ? 'bg-green-100 text-green-700 border border-green-200' 
                  : 'bg-red-100 text-red-700 border border-red-200'
              }`}>
                {trendDirection === 'up' ? (
                  <span className="mr-1 text-sm">↗</span>
                ) : (
                  <span className="mr-1 text-sm">↘</span>
                )}
                {trend}
              </div>
            </div>
          )}
        </div>
        <div className={`p-4 rounded-2xl ${colorClasses[color]} shadow-lg group-hover:scale-110 transition-transform duration-300`}>
          {renderIcon()}
        </div>
      </div>
      
      {/* Decorative elements */}
      <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-gray-100/50 to-transparent rounded-full -translate-y-10 translate-x-10"></div>
      <div className="absolute bottom-0 left-0 w-16 h-16 bg-gradient-to-tr from-gray-100/30 to-transparent rounded-full translate-y-8 -translate-x-8"></div>
    </div>
  )
}
