'use client'

import { Fragment, useState, useEffect } from 'react'
import { Dialog, Transition } from '@headlessui/react'

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
    serial_number?: string
    created_at: string
    updated_at: string
}

interface ViewEquipmentModalProps {
    isOpen: boolean
    onClose: () => void
    equipmentId: number | null
}

export default function ViewEquipmentModal({ isOpen, onClose, equipmentId }: ViewEquipmentModalProps) {
    const [equipment, setEquipment] = useState<Equipment | null>(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        if (isOpen && equipmentId) {
            fetchEquipment()
        }
    }, [isOpen, equipmentId])

    const fetchEquipment = async () => {
        if (!equipmentId) return

        setLoading(true)
        setError(null)

        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'https://cat-v7yf.onrender.com'}/equipment/${equipmentId}`)
            if (!response.ok) {
                throw new Error('Failed to fetch equipment details')
            }
            const data = await response.json()
            setEquipment(data)
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred')
        } finally {
            setLoading(false)
        }
    }

    const formatDate = (dateString?: string) => {
        if (!dateString) return 'N/A'
        return new Date(dateString).toLocaleDateString()
    }

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

    return (
        <Transition.Root show={isOpen} as={Fragment}>
            <Dialog as="div" className="relative z-50" onClose={onClose}>
                <Transition.Child
                    as={Fragment}
                    enter="ease-out duration-300"
                    enterFrom="opacity-0"
                    enterTo="opacity-100"
                    leave="ease-in duration-200"
                    leaveFrom="opacity-100"
                    leaveTo="opacity-0"
                >
                    <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
                </Transition.Child>

                <div className="fixed inset-0 z-10 overflow-y-auto">
                    <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
                        <Transition.Child
                            as={Fragment}
                            enter="ease-out duration-300"
                            enterFrom="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
                            enterTo="opacity-100 translate-y-0 sm:scale-100"
                            leave="ease-in duration-200"
                            leaveFrom="opacity-100 translate-y-0 sm:scale-100"
                            leaveTo="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
                        >
                            <Dialog.Panel className="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
                                <div className="absolute right-0 top-0 pr-4 pt-4">
                                    <button
                                        type="button"
                                        className="rounded-md bg-white text-gray-400 hover:text-gray-500"
                                        onClick={onClose}
                                    >
                                        <span className="sr-only">Close</span>
                                        <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                        </svg>
                                    </button>
                                </div>

                                <div className="sm:flex sm:items-start">
                                    <div className="mt-3 text-center sm:ml-4 sm:mt-0 sm:text-left w-full">
                                        <Dialog.Title as="h3" className="text-lg font-semibold leading-6 text-gray-900 mb-4">
                                            Equipment Details
                                        </Dialog.Title>

                                        {loading && (
                                            <div className="flex items-center justify-center py-8">
                                                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                                            </div>
                                        )}

                                        {error && (
                                            <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-4">
                                                <p className="text-red-600 text-sm">{error}</p>
                                            </div>
                                        )}

                                        {equipment && !loading && (
                                            <div className="space-y-4">
                                                <div className="grid grid-cols-2 gap-4">
                                                    <div>
                                                        <label className="block text-sm font-medium text-gray-500">Equipment ID</label>
                                                        <p className="text-sm text-gray-900">{equipment.equipment_id}</p>
                                                    </div>
                                                    <div>
                                                        <label className="block text-sm font-medium text-gray-500">Type</label>
                                                        <p className="text-sm text-gray-900">{equipment.type}</p>
                                                    </div>
                                                </div>

                                                <div className="grid grid-cols-2 gap-4">
                                                    <div>
                                                        <label className="block text-sm font-medium text-gray-500">Model</label>
                                                        <p className="text-sm text-gray-900">{equipment.model || 'N/A'}</p>
                                                    </div>
                                                    <div>
                                                        <label className="block text-sm font-medium text-gray-500">Manufacturer</label>
                                                        <p className="text-sm text-gray-900">{equipment.manufacturer || 'N/A'}</p>
                                                    </div>
                                                </div>

                                                <div className="grid grid-cols-2 gap-4">
                                                    <div>
                                                        <label className="block text-sm font-medium text-gray-500">Year</label>
                                                        <p className="text-sm text-gray-900">{equipment.year || 'N/A'}</p>
                                                    </div>
                                                    <div>
                                                        <label className="block text-sm font-medium text-gray-500">Serial Number</label>
                                                        <p className="text-sm text-gray-900">{equipment.serial_number || 'N/A'}</p>
                                                    </div>
                                                </div>

                                                <div className="grid grid-cols-2 gap-4">
                                                    <div>
                                                        <label className="block text-sm font-medium text-gray-500">Status</label>
                                                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(equipment.status)}`}>
                                                            {equipment.status}
                                                        </span>
                                                    </div>
                                                    <div>
                                                        <label className="block text-sm font-medium text-gray-500">Site ID</label>
                                                        <p className="text-sm text-gray-900">{equipment.site_id || 'Not assigned'}</p>
                                                    </div>
                                                </div>

                                                <div className="grid grid-cols-2 gap-4">
                                                    <div>
                                                        <label className="block text-sm font-medium text-gray-500">Check Out Date</label>
                                                        <p className="text-sm text-gray-900">{formatDate(equipment.check_out_date)}</p>
                                                    </div>
                                                    <div>
                                                        <label className="block text-sm font-medium text-gray-500">Check In Date</label>
                                                        <p className="text-sm text-gray-900">{formatDate(equipment.check_in_date)}</p>
                                                    </div>
                                                </div>

                                                <div className="grid grid-cols-2 gap-4">
                                                    <div>
                                                        <label className="block text-sm font-medium text-gray-500">Engine Hours/Day</label>
                                                        <p className="text-sm text-gray-900">{equipment.engine_hours_per_day || 0}</p>
                                                    </div>
                                                    <div>
                                                        <label className="block text-sm font-medium text-gray-500">Idle Hours/Day</label>
                                                        <p className="text-sm text-gray-900">{equipment.idle_hours_per_day || 0}</p>
                                                    </div>
                                                </div>

                                                <div className="grid grid-cols-2 gap-4">
                                                    <div>
                                                        <label className="block text-sm font-medium text-gray-500">Operating Days</label>
                                                        <p className="text-sm text-gray-900">{equipment.operating_days || 0}</p>
                                                    </div>
                                                    <div>
                                                        <label className="block text-sm font-medium text-gray-500">Last Operator</label>
                                                        <p className="text-sm text-gray-900">{equipment.last_operator_id || 'N/A'}</p>
                                                    </div>
                                                </div>

                                                <div className="grid grid-cols-2 gap-4">
                                                    <div>
                                                        <label className="block text-sm font-medium text-gray-500">Created</label>
                                                        <p className="text-sm text-gray-900">{formatDate(equipment.created_at)}</p>
                                                    </div>
                                                    <div>
                                                        <label className="block text-sm font-medium text-gray-500">Last Updated</label>
                                                        <p className="text-sm text-gray-900">{formatDate(equipment.updated_at)}</p>
                                                    </div>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>

                                <div className="mt-6 flex justify-end">
                                    <button
                                        type="button"
                                        className="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
                                        onClick={onClose}
                                    >
                                        Close
                                    </button>
                                </div>
                            </Dialog.Panel>
                        </Transition.Child>
                    </div>
                </div>
            </Dialog>
        </Transition.Root>
    )
}
