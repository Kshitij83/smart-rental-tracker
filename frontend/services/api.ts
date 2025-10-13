import axios from 'axios';

// API base configuration
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'https://cat-v7yf.onrender.com',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types based on backend schemas
export interface Equipment {
  id: number;
  equipment_id: string;
  type: string;
  site_id: string;
  check_out_date: string;
  check_in_date: string;
  engine_hours_per_day: number;
  idle_hours_per_day: number;
  operating_days: number;
  last_operator_id: string;
  model: string;
  manufacturer: string;
  year: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface CreateEquipmentData {
  equipment_id: string;
  type: string;
  site_id?: string;
  check_out_date?: string;
  check_in_date?: string;
  engine_hours_per_day?: number;
  idle_hours_per_day?: number;
  operating_days?: number;
  last_operator_id?: string;
  model?: string;
  manufacturer?: string;
  year?: number;
  status?: string;
}

// Equipment API
export const equipmentApi = {
  getAll: async (skip = 0, limit = 100): Promise<Equipment[]> => {
    const response = await api.get(`/equipment/?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  getById: async (id: number): Promise<Equipment> => {
    const response = await api.get(`/equipment/${id}`);
    return response.data;
  },

  create: async (data: CreateEquipmentData): Promise<Equipment> => {
    const response = await api.post('/equipment/', data);
    return response.data;
  },

  update: async (id: number, data: Partial<CreateEquipmentData>): Promise<Equipment> => {
    const response = await api.put(`/equipment/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/equipment/${id}`);
  },
};

// Dashboard API
export const dashboardApi = {
  getDashboardData: async () => {
    const response = await api.get('/dashboard');
    return response.data;
  },

  getEquipmentStats: async () => {
    const response = await api.get('/equipment-stats');
    return response.data;
  },
};

// ML API
export const mlApi = {
  getDemandForecast: async (equipmentType: string, days: number = 30) => {
    const response = await api.get(`/ml/demand-forecast`, {
      params: { equipment_type: equipmentType, days }
    });
    return response.data;
  },

  getAnomalyDetection: async () => {
    const response = await api.get('/ml/anomaly-detection');
    return response.data;
  },

  runAnomalyDetection: async () => {
    const response = await api.post('/ml/run-anomaly-detection');
    return response.data;
  },
};

export default api;