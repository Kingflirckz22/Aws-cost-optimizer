import axios from 'axios';
import { API_ENDPOINTS } from '../config';

// API Service Layer
class ApiService {
  constructor() {
    this.client = axios.create({
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    });
  }

  async getLatestScan() {
    try {
      const response = await this.client.get(API_ENDPOINTS.latest);
      if (response.data.success) {
        return response.data.data;
      }
      throw new Error(response.data.error || 'Failed to fetch latest scan');
    } catch (error) {
      console.error('Error fetching latest scan:', error);
      throw error;
    }
  }

  async getScans(limit = 10, sort = 'desc') {
    try {
      const response = await this.client.get(API_ENDPOINTS.scans, {
        params: { limit, sort }
      });
      if (response.data.success) {
        return response.data.data;
      }
      throw new Error(response.data.error || 'Failed to fetch scans');
    } catch (error) {
      console.error('Error fetching scans:', error);
      throw error;
    }
  }

  async getSummary() {
    try {
      const response = await this.client.get(API_ENDPOINTS.summary);
      if (response.data.success) {
        return response.data.data;
      }
      throw new Error(response.data.error || 'Failed to fetch summary');
    } catch (error) {
      console.error('Error fetching summary:', error);
      throw error;
    }
  }

  async triggerScan() {
    try {
      const response = await this.client.post(API_ENDPOINTS.triggerScan);
      if (response.data.success) {
        return response.data.data;
      }
      throw new Error(response.data.error || 'Failed to trigger scan');
    } catch (error) {
      console.error('Error triggering scan:', error);
      throw error;
    }
  }
}

export default new ApiService();