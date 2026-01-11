import apiClient from './api';

export const authAPI = {
  async login(credentials) {
    const response = await apiClient.post('/auth/login', credentials);
    const { access_token } = response.data;
    
    // Сохраняем токен в localStorage
    localStorage.setItem('access_token', access_token);
    
    return response.data;
  },
  
  async register(userData) {
    const response = await apiClient.post('/auth/register', userData);
    return response.data;
  },
  
  async getCurrentUser() {
    const response = await apiClient.get('/users/me');
    return response.data;
  },
  
  logout() {
    // Удаляем токен из localStorage
    localStorage.removeItem('access_token');
  },
  
  isAuthenticated() {
    // Проверяем наличие токена
    return !!localStorage.getItem('access_token');
  }
};