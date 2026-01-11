<template>
  <div id="app">
    <Navigation v-if="isLoggedIn" />
    <main class="container">
      <router-view />
    </main>
  </div>
</template>

<script>
import Navigation from '@/components/Navigation.vue'
import { mapGetters } from 'vuex'

export default {
  name: 'App',
  components: {
    Navigation
  },
  computed: {
    ...mapGetters(['isLoggedIn'])
  }
}
</script>

<style>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}
</style>