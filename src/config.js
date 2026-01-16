// API Configuration
// Replace with your actual API Gateway URL
export const API_BASE_URL = 'https://6ht92lu3ib.execute-api.us-east-1.amazonaws.com/prod/api';

export const API_ENDPOINTS = {
  latest: `${API_BASE_URL}/latest`,
  scans: `${API_BASE_URL}/scans`,
  summary: `${API_BASE_URL}/summary`,
  triggerScan: `${API_BASE_URL}/scan`
};

export const SEVERITY_COLORS = {
  HIGH: '#ef4444',
  MEDIUM: '#f59e0b',
  LOW: '#3b82f6'
};

export const SERVICE_COLORS = {
  EC2: '#FF9900',
  EBS: '#527FFF',
  'Elastic IP': '#8C4FFF',
  Snapshots: '#5DADE2'
};