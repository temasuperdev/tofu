<template>
  <div id="app">
    <nav class="bg-gray-800 text-white p-4">
      <div class="container mx-auto flex justify-between items-center">
        <h1 class="text-xl font-bold">Notes App</h1>
        <div>
          <router-link to="/" class="mr-4">Home</router-link>
          <router-link to="/notes" class="mr-4">My Notes</router-link>
          <router-link to="/login" v-if="!isLoggedIn" class="mr-4">Login</router-link>
          <router-link to="/register" v-if="!isLoggedIn" class="mr-4">Register</router-link>
          <button @click="logout" v-if="isLoggedIn" class="bg-red-600 hover:bg-red-700 px-4 py-2 rounded">Logout</button>
        </div>
      </div>
    </nav>
    
    <main class="container mx-auto mt-8 p-4">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from './store/auth';

const router = useRouter();
const authStore = useAuthStore();

const isLoggedIn = computed(() => authStore.isLoggedIn);

const logout = () => {
  authStore.logout();
  router.push('/login');
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>