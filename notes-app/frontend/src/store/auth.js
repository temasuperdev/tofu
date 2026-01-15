import { defineStore } from 'pinia';
import axios from 'axios';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
  }),
  
  getters: {
    isLoggedIn: (state) => !!state.token,
    getUser: (state) => state.user,
  },
  
  actions: {
    async login(credentials) {
      try {
        const response = await axios.post('/api/v1/login', credentials, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });
        
        const { access_token } = response.data;
        this.token = access_token;
        localStorage.setItem('token', access_token);
        
        // Set default header for all subsequent requests
        axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
        
        return response.data;
      } catch (error) {
        throw error;
      }
    },
    
    async register(userData) {
      try {
        const response = await axios.post('/api/v1/register', userData);
        return response.data;
      } catch (error) {
        throw error;
      }
    },
    
    logout() {
      this.token = null;
      this.user = null;
      localStorage.removeItem('token');
      delete axios.defaults.headers.common['Authorization'];
    },
    
    async fetchUser() {
      if (!this.token) return;
      
      try {
        const response = await axios.get('/api/v1/users/me');
        this.user = response.data;
        return response.data;
      } catch (error) {
        console.error('Failed to fetch user:', error);
        this.logout();
        throw error;
      }
    }
  }
});