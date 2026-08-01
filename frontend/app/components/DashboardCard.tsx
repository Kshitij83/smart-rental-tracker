import { ReactElement } from 'react'
import { TrendingUp, TrendingDown } from 'lucide-react'

interface DashboardCardProps {
  title: string
  value: string | number
  icon: ReactElement
  trend?: string
  trendDirection?: 'up' | 'down'
  accent?: string
  subtitle?: string
}

const iconChipClasses: Record<string, string> = {
  blue: 'bg-blue-50 text-blue-600',
  green: 'bg-emerald-50 text-emerald-600',
  red: 'bg-red-50 text-red-600',
  amber: 'bg-amber-50 text-amber-600',
  purple: 'bg-violet-50 text-violet-600',
}

export default function DashboardCard({
  title,
  value,
  icon,
  trend,
  trendDirection,
  accent = 'blue',
  subtitle,
}: DashboardCardProps) {
  return (
    <div className="card group hover:shadow-lg hover:ring-slate-300 transition-all duration-200">
      <div className="flex items-start justify-between">
        <div className="min-w-0">
          <p className="text-sm font-medium text-slate-500">{title}</p>
          <p className="text-3xl font-bold text-slate-900 mt-2 tracking-tight">
            {value}
          </p>
          {subtitle && (
            <p className="mt-1 text-xs text-slate-400">{subtitle}</p>
          )}
          {trend && (
            <div className="flex items-center gap-1 mt-3">
              <span
                className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold ${
                  trendDirection === 'up'
                    ? 'bg-emerald-50 text-emerald-700'
                    : 'bg-red-50 text-red-700'
                }`}
              >
                {trendDirection === 'up' ? (
                  <TrendingUp className="w-3.5 h-3.5" />
                ) : (
                  <TrendingDown className="w-3.5 h-3.5" />
                )}
                {trend}
              </span>
            </div>
          )}
        </div>
        <div
          className={`stat-icon shrink-0 ${iconChipClasses[accent] || iconChipClasses.blue}`}
        >
          {icon}
        </div>
      </div>
    </div>
  )
}
