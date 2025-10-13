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

interface EditEquipmentModalProps {
    isOpen: boolean
    onClose: () => void
    equipmentId: number | null
    onSuccess: () => void
}

export default function EditEquipmentModal({ isOpen, onClose, equipmentId, onSuccess }: EditEquipmentModalProps) {
    const [equipment, setEquipment] = useState<Equipment | null>(null)
    const [formData, setFormData] = useState({
        status: '',
        site_id: '',
        check_out_date: '',
        check_in_date: '',
        engine_hours_per_day: 0,
        idle_hours_per_day: 0,
        operating_days: 0,
        last_operator_id: '',
        model: '',
        manufacturer: '',
        year: '',
        serial_number: ''
    })
    const [loading, setLoading] = useState(false)
    const [saving, setSaving] = useState(false)
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

            // Populate form with current data
            setFormData({
                status: data.status || '',
                site_id: data.site_id || '',
                check_out_date: data.check_out_date ? data.check_out_date.split('T')[0] : '',
                check_in_date: data.check_in_date ? data.check_in_date.split('T')[0] : '',
                engine_hours_per_day: data.engine_hours_per_day || 0,
                idle_hours_per_day: data.idle_hours_per_day || 0,
                operating_days: data.operating_days || 0,
                last_operator_id: data.last_operator_id || '',
                model: data.model || '',
                manufacturer: data.manufacturer || '',
                year: data.year ? data.year.toString() : '',
                serial_number: data.serial_number || ''
            })
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred')
        } finally {
            setLoading(false)
        }
    }

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value } = e.target
        setFormData(prev => ({
            ...prev,
            [name]: value
        }))
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!equipmentId) return

        setSaving(true)
        setError(null)

        try {
            // Prepare the update data - include site_id and check_out_date as editable fields
            const updateData: any = {}

            // Include all editable fields
            if (formData.status) updateData.status = formData.status
            if (formData.check_in_date) updateData.check_in_date = formData.check_in_date
            if (formData.site_id) updateData.site_id = formData.site_id
            if (formData.check_out_date) updateData.check_out_date = formData.check_out_date

            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'https://cat-v7yf.onrender.com'}/equipment/${equipmentId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(updateData),
            })

            if (!response.ok) {
                const errorData = await response.json()
                throw new Error(errorData.detail || 'Failed to update equipment')
            }

            onSuccess()
            onClose()
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred')
        } finally {
            setSaving(false)
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
                            <Dialog.Panel className="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-2xl sm:p-6">
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
                                            Edit Equipment Details
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
                                            <form onSubmit={handleSubmit} className="space-y-4">
                                                {/* Equipment ID - Read only */}
                                                <div>
                                                    <label className="block text-sm font-medium text-gray-700">Equipment ID</label>
                                                    <input
                                                        type="text"
                                                        value={equipment.equipment_id}
                                                        disabled
                                                        className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-500"
                                                    />
                                                </div>

                                                {/* Type - Read only */}
                                                <div>
                                                    <label className="block text-sm font-medium text-gray-700">Type</label>
                                                    <input
                                                        type="text"
                                                        value={equipment.type}
                                                        disabled
                                                        className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-500"
                                                    />
                                                </div>

                                                <div className="grid grid-cols-2 gap-4">
                                                    {/* Status - Editable */}
                                                    <div>
                                                        <label className="block text-sm font-medium text-gray-700">Status</label>
                                                        <select
                                                            name="status"
                                                            value={formData.status}
                                                            onChange={handleInputChange}
                                                            className="mt-1 block w-full rounded-md border-blue-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-blue-500 bg-white"
                                                        >
                                                            <option value="available">Available</option>
                                                            <option value="rented">Rented</option>
                                                            <option value="maintenance">Maintenance</option>
                                                            <option value="retired">Retired</option>
                                                        </select>
                                                    </div>

                                                    {/* Site ID - Now Editable */}
                                                    <div>
                                                        <label className="block text-sm font-medium text-gray-700">Site ID</label>
                                                        <input
                                                            type="text"
                                                            name="site_id"
                                                            value={formData.site_id}
                                                            onChange={handleInputChange}
                                                            className="mt-1 block w-full rounded-md border-blue-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-blue-500 bg-white"
                                                        />
                                                    </div>
                                                </div>

                                                <div className="grid grid-cols-2 gap-4">
                                                    {/* Check Out Date - Now Editable */}
                                                    <div>
                                                        <label className="block text-sm font-medium text-gray-700">Check Out Date</label>
                                                        <input
                                                            type="date"
                                                            name="check_out_date"
                                                            value={formData.check_out_date}
                                                            onChange={handleInputChange}
                                                            className="mt-1 block w-full rounded-md border-blue-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-blue-500 bg-white"
                                                        />
                                                    </div>

                                                    {/* Check In Date - Editable */}
                                                    <div>
                                                        <label className="block text-sm font-medium text-gray-700">Check In Date</label>
                                                        <input
                                                            type="date"
                                                            name="check_in_date"
                                                            value={formData.check_in_date}
                                                            onChange={handleInputChange}
                                                            className="mt-1 block w-full rounded-md border-blue-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-blue-500 bg-white"
                                                        />
                                                    </div>
                                                </div>

                                                <div className="grid grid-cols-2 gap-4">
                                                    {/* Model - Read only */}
                                                    <div>
                                                        <label className="block text-sm font-medium text-gray-700">Model</label>
                                                        <input
                                                            type="text"
                                                            value={formData.model}
                                                            disabled
                                                            className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-500"
                                                        />
                                                    </div>

                                                    {/* Manufacturer - Read only */}
                                                    <div>
                                                        <label className="block text-sm font-medium text-gray-700">Manufacturer</label>
                                                        <input
                                                            type="text"
                                                            value={formData.manufacturer}
                                                            disabled
                                                            className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-500"
                                                        />
                                                    </div>
                                                </div>

                                                <div className="grid grid-cols-3 gap-4">
                                                    {/* Engine Hours Per Day - Read only */}
                                                    <div>
                                                        <label className="block text-sm font-medium text-gray-700">Engine Hrs/Day</label>
                                                        <input
                                                            type="number"
                                                            value={formData.engine_hours_per_day}
                                                            disabled
                                                            className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-500"
                                                        />
                                                    </div>

                                                    {/* Idle Hours Per Day - Read only */}
                                                    <div>
                                                        <label className="block text-sm font-medium text-gray-700">Idle Hrs/Day</label>
                                                        <input
                                                            type="number"
                                                            value={formData.idle_hours_per_day}
                                                            disabled
                                                            className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-500"
                                                        />
                                                    </div>

                                                    {/* Operating Days - Read only */}
                                                    <div>
                                                        <label className="block text-sm font-medium text-gray-700">Operating Days</label>
                                                        <input
                                                            type="number"
                                                            value={formData.operating_days}
                                                            disabled
                                                            className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-500"
                                                        />
                                                    </div>
                                                </div>

                                                <div className="grid grid-cols-2 gap-4">
                                                    {/* Last Operator ID - Read only */}
                                                    <div>
                                                        <label className="block text-sm font-medium text-gray-700">Last Operator ID</label>
                                                        <input
                                                            type="text"
                                                            value={formData.last_operator_id}
                                                            disabled
                                                            className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-500"
                                                        />
                                                    </div>

                                                    {/* Year - Read only */}
                                                    <div>
                                                        <label className="block text-sm font-medium text-gray-700">Year</label>
                                                        <input
                                                            type="number"
                                                            value={formData.year}
                                                            disabled
                                                            className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-500"
                                                        />
                                                    </div>
                                                </div>

                                                {/* Serial Number - Read only */}
                                                <div>
                                                    <label className="block text-sm font-medium text-gray-700">Serial Number</label>
                                                    <input
                                                        type="text"
                                                        value={formData.serial_number}
                                                        disabled
                                                        className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-500"
                                                    />
                                                </div>

                                                <div className="mt-6 flex justify-end space-x-3">
                                                    <button
                                                        type="button"
                                                        className="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
                                                        onClick={onClose}
                                                        disabled={saving}
                                                    >
                                                        Cancel
                                                    </button>
                                                    <button
                                                        type="submit"
                                                        className="rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 disabled:opacity-50"
                                                        disabled={saving}
                                                    >
                                                        {saving ? (
                                                            <>
                                                                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline" fill="none" viewBox="0 0 24 24">
                                                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                                                </svg>
                                                                Saving...
                                                            </>
                                                        ) : (
                                                            'Save Changes'
                                                        )}
                                                    </button>
                                                </div>
                                            </form>
                                        )}
                                    </div>
                                </div>
                            </Dialog.Panel>
                        </Transition.Child>
                    </div>
                </div>
            </Dialog>
        </Transition.Root>
    )
}
