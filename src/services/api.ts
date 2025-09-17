import { ApiResponse, ProgressData } from '../types';

// Base URL for your Flask API
const BASE_URL = 'http://192.168.1.194:5001'; // Update this to match your Flask app's IP

class ApiService {
  private async makeRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    try {
      const response = await fetch(`${BASE_URL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  async generateRandomPage(): Promise<ApiResponse> {
    return this.makeRequest<ApiResponse>('/generate', {
      method: 'POST',
    });
  }

  async getProgress(): Promise<ProgressData> {
    return this.makeRequest<ProgressData>('/progress');
  }

  async downloadImage(imageUrl: string): Promise<string> {
    // For now, return the full URL
    // In a real app, you might want to download and cache the image
    return `${BASE_URL}${imageUrl}`;
  }
}

export const apiService = new ApiService();
