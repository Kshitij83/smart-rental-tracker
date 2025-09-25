'use client'

import { useState, useEffect } from 'react'
import { equipmentApi } from '../lib/api'
import AddEquipmentModal from './AddEquipmentModal'

interface Equipment {
  id: number
  equipment_id: string
  type: string
  site_id?: string
  check_out_date?: string
  check_in_date?: string
  engine_hours_per_day?: number
  idle_hours_per_day?: number
  operating_days?: number
  last_operator_id?: string
  model?: string
  manufacturer?: string
  year?: number
  status: string
  created_at: string
  updated_at: string
}

export default function EquipmentTable() {
  const [equipment, setEquipment] = useState<Equipment[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState('all')
  const [filterStatus, setFilterStatus] = useState('all')
  const [isModalOpen, setIsModalOpen] = useState(false)

  const fetchEquipment = async () => {
    try {
      const response = await equipmentApi.getAll()
      setEquipment(response.data)
    } catch (error) {
      console.error('Error fetching equipment:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchEquipment()
  }, [])

  const handleEquipmentAdded = () => {
    fetchEquipment() // Refresh the equipment list
  }

  // Filter equipment based on search and filters
  const filteredEquipment = equipment.filter(item => {
    const matchesSearch = item.equipment_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (item.model && item.model.toLowerCase().includes(searchTerm.toLowerCase()))
    
    const matchesType = filterType === 'all' || item.type === filterType
    const matchesStatus = filterStatus === 'all' || item.status === filterStatus
    
    return matchesSearch && matchesType && matchesStatus
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'available':
        return 'bg-green-100 text-green-800'
      case 'rented':
        return 'bg-blue-100 text-blue-800'
      case 'maintenance':
        return 'bg-yellow-100 text-yellow-800'
      case 'retired':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Filters and Search */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <input
            type="text"
            placeholder="Search equipment ID, type, or model..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input-field"
          />
        </div>
        <div className="flex gap-2">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="input-field max-w-xs"
          >
            <option value="all">All Types</option>
            <option value="Excavator">Excavator</option>
            <option value="Bulldozer">Bulldozer</option>
            <option value="Crane">Crane</option>
            <option value="Grader">Grader</option>
          </select>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="input-field max-w-xs"
          >
            <option value="all">All Status</option>
            <option value="available">Available</option>
            <option value="rented">Rented</option>
            <option value="maintenance">Maintenance</option>
            <option value="retired">Retired</option>
          </select>
        </div>
      </div>

      {/* Equipment Count */}
      <div className="bg-gray-50 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-600">
            Showing {filteredEquipment.length} of {equipment.length} equipment items
          </p>
          <button 
            onClick={() => setIsModalOpen(true)}
            className="btn-primary"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Add New Equipment
          </button>
        </div>
      </div>

      {/* Equipment Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Equipment ID
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Type
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Site ID
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Model
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Engine Hrs/Day
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredEquipment.map((item) => (
              <tr key={item.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{item.equipment_id}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">{item.type}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-500">{item.site_id || 'N/A'}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-500">{item.model || 'N/A'}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-500">{item.engine_hours_per_day || 0}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(item.status)}`}>
                    {item.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <div className="flex space-x-2">
                    <button className="text-primary-600 hover:text-primary-900">
                      Edit
                    </button>
                    <button className="text-gray-600 hover:text-gray-900">
                      View
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Empty State */}
      {filteredEquipment.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          </div>
          <h3 className="text-sm font-medium text-gray-900 mb-2">No equipment found</h3>
          <p className="text-sm text-gray-500">
            {searchTerm || filterType !== 'all' || filterStatus !== 'all'
              ? 'Try adjusting your search or filters'
              : 'No equipment has been added yet'
            }
          </p>
        </div>
      )}

      {/* Pagination */}
      {filteredEquipment.length > 0 && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-700">
            Showing <span className="font-medium">1</span> to{' '}
            <span className="font-medium">{filteredEquipment.length}</span> of{' '}
            <span className="font-medium">{equipment.length}</span> results
          </div>
          <div className="flex space-x-2">
            <button className="btn-secondary disabled:opacity-50" disabled>
              Previous
            </button>
            <button className="btn-secondary disabled:opacity-50" disabled>
              Next
            </button>
          </div>
        </div>
      )}
      
      {/* Add Equipment Modal */}
      <AddEquipmentModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={handleEquipmentAdded}
      />
    </div>
  )
}
