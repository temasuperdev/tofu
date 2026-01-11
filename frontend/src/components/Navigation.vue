<template>
  <nav class="navbar">
    <div class="nav-brand">
      <router-link to="/">Notes App</router-link>
    </div>
    <div class="nav-menu">
      <router-link to="/notes" class="nav-link">Мои заметки</router-link>
      <router-link to="/profile" class="nav-link">Профиль</router-link>
      <button @click="logout" class="btn btn-link">Выйти</button>
    </div>
  </nav>
</template>

<script>
import { mapActions } from 'vuex';

export default {
  name: 'AppNavigation',
  methods: {
    ...mapActions('auth', ['logout'])
  }
}
</script>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: #343a40;
  color: white;
}

.nav-brand a {
  color: white;
  text-decoration: none;
  font-size: 1.5rem;
  font-weight: bold;
}

.nav-menu {
  display: flex;
  gap: 1.5rem;
 align-items: center;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.nav-link:hover, .nav-link.router-link-active {
  background-color: #495057;
}

.btn-link {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.btn-link:hover {
  background-color: #495057;
}
</style>