<template>
  <div class="home">
    <div class="max-w-3xl mx-auto text-center">
      <h1 class="text-3xl font-bold text-gray-800 mb-4">Welcome to Notes App</h1>
      <p class="text-lg text-gray-600 mb-8">
        A secure and easy way to manage your notes online.
      </p>
      
      <div v-if="!isLoggedIn" class="space-y-4">
        <router-link 
          to="/login" 
          class="inline-block bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded focus:outline-none focus:shadow-outline"
        >
          Login
        </router-link>
        <router-link 
          to="/register" 
          class="inline-block bg-gray-800 hover:bg-gray-900 text-white font-bold py-2 px-6 rounded focus:outline-none focus:shadow-outline ml-4"
        >
          Register
        </router-link>
      </div>
      
      <div v-else class="space-y-4">
        <router-link 
          to="/notes" 
          class="inline-block bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded focus:outline-none focus:shadow-outline"
        >
          View My Notes
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useAuthStore } from '../store/auth';

const authStore = useAuthStore();
const isLoggedIn = computed(() => authStore.isLoggedIn);
</script>