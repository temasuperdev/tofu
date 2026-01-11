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
    const response = await authAPI.login(credentials);
    const { access_token } = response;
    
    commit('SET_TOKEN', access_token);
    
    // Получаем информацию о пользователе
    const userResponse = await authAPI.getCurrentUser();
    commit('SET_USER', userResponse);
    
    return true;
  },
  
   async register({ commit }, userData) { // eslint-disable-line no-unused-vars
     const response = await authAPI.register(userData);
     return response;
   },
  
   logout({ commit }) { // eslint-disable-line no-unused-vars
     authAPI.logout();
     commit('CLEAR_AUTH');
   },
  
   async fetchCurrentUser({ commit }) {
     const response = await authAPI.getCurrentUser();
     commit('SET_USER', response);
   },
};

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions,
};