<template>
  <div class="home">
    <h1>Добро пожаловать в Notes App!</h1>
    <p>Приложение для управления вашими заметками.</p>
    
    <div class="home-actions" v-if="!isLoggedIn">
      <router-link to="/login" class="btn btn-primary">Войти</router-link>
      <router-link to="/register" class="btn btn-secondary">Регистрация</router-link>
    </div>
    
    <div class="home-actions" v-else>
      <router-link to="/notes" class="btn btn-primary">Перейти к заметкам</router-link>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  name: 'HomeView',
  computed: {
    ...mapGetters('auth', ['isLoggedIn'])
  }
};
</script>

<style scoped>
.home {
  text-align: center;
  padding: 2rem;
}

.home h1 {
  color: #333;
  margin-bottom: 1rem;
}

.home p {
  color: #666;
  margin-bottom: 2rem;
}

.home-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
  font-size: 1rem;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn:hover {
  opacity: 0.9;
}
</style>