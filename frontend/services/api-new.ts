import axios from 'axios';

// API base configuration
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types based on backend schemas
export interface Equipment {
  id: number;
  equipment_id: string;
  type: string;
  model: string;
  site_id: number;
  status: string;
  last_maintenance: string;
  next_maintenance: string;
  created_at: string;
  updated_at: string;
}

export interface EquipmentCreate {
  equipment_id: string;
  type: string;
  model: string;
  site_id: number;
  status: string;
  last_maintenance: string;
  next_maintenance: string;
}

export interface EquipmentUpdate {
  type?: string;
  model?: string;
  site_id?: number;
  status?: string;
  last_maintenance?: string;
  next_maintenance?: string;
}

export interface Site {
  id: number;
  site_id: string;
  name: string;
  location: string;
  contact_person: string;
  contact_phone: string;
  created_at: string;
  updated_at: string;
}

export interface SiteCreate {
  site_id: string;
  name: string;
  location: string;
  contact_person: string;
  contact_phone: string;
}

export interface Operator {
  id: number;
  operator_id: string;
  name: string;
  phone: string;
  email: string;
  license_number: string;
  created_at: string;
  updated_at: string;
}

export interface OperatorCreate {
  operator_id: string;
  name: string;
  phone: string;
  email: string;
  license_number: string;
}

export interface Rental {
  id: number;
  equipment_id: number;
  operator_id: number;
  site_id: number;
  start_date: string;
  end_date: string;
  status: string;
  daily_rate: number;
  total_cost: number;
  created_at: string;
  updated_at: string;
}

export interface RentalCreate {
  equipment_id: number;
  operator_id: number;
  site_id: number;
  start_date: string;
  end_date: string;
  daily_rate: number;
}

export interface RentalUpdate {
  end_date?: string;
  status?: string;
  daily_rate?: number;
  total_cost?: number;
}

export interface UsageLog {
  id: number;
  rental_id: number;
  equipment_id: number;
  operator_id: number;
  site_id: number;
  usage_hours: number;
  fuel_consumption: number;
  maintenance_notes: string;
  created_at: string;
}

export interface UsageLogCreate {
  rental_id: number;
  equipment_id: number;
  operator_id: number;
  site_id: number;
  usage_hours: number;
  fuel_consumption: number;
  maintenance_notes: string;
}

export interface Alert {
  id: number;
  equipment_id: number;
  alert_type: string;
  message: string;
  severity: string;
  is_resolved: boolean;
  resolved_by?: string;
  resolved_at?: string;
  created_at: string;
}

export interface AlertCreate {
  equipment_id: number;
  alert_type: string;
  message: string;
  severity: string;
}

export interface DashboardSummary {
  equipment_summary: {
    total: number;
    available: number;
    rented: number;
    maintenance: number;
  };
  rental_summary: {
    active: number;
    overdue: number;
    completed: number;
  };
  recent_alerts: Alert[];
}

// ML Integration types
export interface MLStatus {
  models_loaded: boolean;
  demand_forecasting: string;
  anomaly_detection: string;
}

export interface DemandForecast {
  site_id: string;
  equipment_type: string;
  forecast_days: number;
  predicted_demand: number;
  confidence_score: number;
  generated_at: string;
}

export interface AnomalyDetectionResult {
  message: string;
  records_analyzed: number;
  anomalies_detected: number;
  alerts_created: number;
  completed_at: string;
}

export interface ForecastHistory {
  forecasts: Array<{
    id: number;
    site_id: string;
    equipment_type: string;
    forecast_date: string;
    predicted_demand: number;
    confidence_score: number;
    actual_demand?: number;
    created_at: string;
  }>;
  total_forecasts: number;
}

// Equipment API calls
const equipmentAPI = {
  create: (data: EquipmentCreate) => api.post<Equipment>('/equipment/', data),
  getAll: (skip = 0, limit = 100) => api.get<Equipment[]>(`/equipment/?skip=${skip}&limit=${limit}`),
  getById: (id: number) => api.get<Equipment>(`/equipment/${id}`),
  update: (id: number, data: EquipmentUpdate) => api.put<Equipment>(`/equipment/${id}`, data),
  getWithStatus: (skip = 0, limit = 100) => api.get(`/equipment/status/detailed?skip=${skip}&limit=${limit}`),
};

// Site API calls
const siteAPI = {
  create: (data: SiteCreate) => api.post<Site>('/sites/', data),
  getAll: (skip = 0, limit = 100) => api.get<Site[]>(`/sites/?skip=${skip}&limit=${limit}`),
  getById: (id: number) => api.get<Site>(`/sites/${id}`),
  update: (id: number, data: Partial<SiteCreate>) => api.put<Site>(`/sites/${id}`, data),
};

// Operator API calls
const operatorAPI = {
  create: (data: OperatorCreate) => api.post<Operator>('/operators/', data),
  getAll: (skip = 0, limit = 100) => api.get<Operator[]>(`/operators/?skip=${skip}&limit=${limit}`),
  getById: (id: number) => api.get<Operator>(`/operators/${id}`),
  update: (id: number, data: Partial<OperatorCreate>) => api.put<Operator>(`/operators/${id}`, data),
};

// Rental API calls
const rentalAPI = {
  create: (data: RentalCreate) => api.post<Rental>('/rentals/', data),
  createManual: (data: RentalCreate) => api.post<Rental>('/rentals/manual', data),
  getAll: (skip = 0, limit = 100, status?: string) => {
    const params = new URLSearchParams();
    if (skip) params.append('skip', skip.toString());
    if (limit) params.append('limit', limit.toString());
    if (status) params.append('status', status);
    return api.get<Rental[]>(`/rentals/?${params.toString()}`);
  },
  getActive: () => api.get<Rental[]>('/rentals/active'),
  getOverdue: () => api.get<Rental[]>('/rentals/overdue'),
  getById: (id: number) => api.get<Rental>(`/rentals/${id}`),
  update: (id: number, data: RentalUpdate) => api.put<Rental>(`/rentals/${id}`, data),
  checkIn: (id: number) => api.post<Rental>(`/rentals/${id}/checkin`),
};

// Usage Log API calls
const usageLogAPI = {
  create: (data: UsageLogCreate) => api.post<UsageLog>('/usage-logs/', data),
  getByRental: (rentalId: number) => api.get<UsageLog[]>(`/usage-logs/rental/${rentalId}`),
  getByEquipment: (equipmentId: number) => api.get<UsageLog[]>(`/usage-logs/equipment/${equipmentId}`),
};

// Alert API calls
const alertAPI = {
  create: (data: AlertCreate) => api.post<Alert>('/alerts/', data),
  getAll: (skip = 0, limit = 100, isResolved?: boolean) => {
    const params = new URLSearchParams();
    if (skip) params.append('skip', skip.toString());
    if (limit) params.append('limit', limit.toString());
    if (isResolved !== undefined) params.append('is_resolved', isResolved.toString());
    return api.get<Alert[]>(`/alerts/?${params.toString()}`);
  },
  resolve: (id: number, resolvedBy: string) => api.put(`/alerts/${id}/resolve`, { resolved_by: resolvedBy }),
};

// Dashboard API calls
const dashboardAPI = {
  getSummary: () => api.get<DashboardSummary>('/dashboard/summary'),
  detectAnomalies: () => api.post('/analytics/detect-anomalies'),
};

// ML Integration API calls
const mlAPI = {
  // Get ML status
  getMLStatus: () => api.get<MLStatus>('/ml/status'),
  
  // Demand forecasting
  generateDemandForecast: (data: {
    site_id: string;
    equipment_type: string;
    days_ahead?: number;
  }) => api.post<DemandForecast>('/ml/demand-forecast', null, { 
    params: data 
  }),
  
  generateBulkDemandForecast: (days_ahead: number = 7) => 
    api.post('/ml/demand-forecast/bulk', null, { 
      params: { days_ahead } 
    }),
  
  getDemandForecastHistory: (params?: {
    site_id?: string;
    equipment_type?: string;
    days_back?: number;
  }) => api.get<ForecastHistory>('/ml/demand-forecast/history', { 
    params 
  }),
  
  // Anomaly detection
  detectAnomalies: () => api.post<AnomalyDetectionResult>('/ml/anomaly-detection'),
  
  getAnomalyDetectionStatus: () => api.get('/ml/anomaly-detection/status'),
  
  // Model management
  retrainMLModels: () => api.post('/ml/retrain'),
};

// Error handling interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Export all APIs
export {
  equipmentAPI,
  siteAPI,
  operatorAPI,
  rentalAPI,
  usageLogAPI,
  alertAPI,
  dashboardAPI,
  mlAPI
};

export default api;
