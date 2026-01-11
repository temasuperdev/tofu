import axios from 'axios';

const apiClient = axios.create({
 baseURL: process.env.VUE_APP_API_BASE_URL || 'https://serv.temasuug.ru/api/v1',
  timeout: 10000,
});

// Перехватчик запросов для добавления токена
apiClient.interceptors.request.use(
 (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Перехватчик ответов для обработки ошибок
apiClient.interceptors.response.use(
 (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Токен истек, перенаправляем на страницу входа
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;