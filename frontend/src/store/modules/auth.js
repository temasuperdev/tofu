import { authAPI } from '@/services/auth';

const state = {
  user: null,
  token: localStorage.getItem('access_token') || null,
};

const getters = {
 isLoggedIn: state => !!state.token,
  currentUser: state => state.user,
};

const mutations = {
  SET_USER(state, user) {
    state.user = user;
  },
  SET_TOKEN(state, token) {
    state.token = token;
    if (token) {
      localStorage.setItem('access_token', token);
    } else {
      localStorage.removeItem('access_token');
    }
 },
  CLEAR_AUTH(state) {
    state.user = null;
    state.token = null;
    localStorage.removeItem('access_token');
  },
};

const actions = {
  async login({ commit }, credentials) {
    try {
      const response = await authAPI.login(credentials);
      const { access_token } = response;
      
      commit('SET_TOKEN', access_token);
      
      // Получаем информацию о пользователе
      const userResponse = await authAPI.getCurrentUser();
      commit('SET_USER', userResponse);
      
      return true;
    } catch (error) {
      throw error;
    }
  },
  
  async register({ commit }, userData) {
    try {
      const response = await authAPI.register(userData);
      return response;
    } catch (error) {
      throw error;
    }
  },
  
  logout({ commit }) {
    authAPI.logout();
    commit('CLEAR_AUTH');
  },
  
  async fetchCurrentUser({ commit }) {
    try {
      const response = await authAPI.getCurrentUser();
      commit('SET_USER', response);
    } catch (error) {
      console.error('Failed to fetch user:', error);
      // Если запрос не удался, очищаем аутентификацию
      commit('CLEAR_AUTH');
      throw error;
    }
  },
};

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions,
};