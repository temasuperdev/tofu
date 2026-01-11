<template>
  <div class="profile">
    <h1>Профиль пользователя</h1>
    
    <div v-if="user">
      <p><strong>Имя пользователя:</strong> {{ user.username }}</p>
      <p><strong>Email:</strong> {{ user.email }}</p>
      <p><strong>Дата регистрации:</strong> {{ formatDate(user.created_at) }}</p>
    </div>
    <div v-else>
      <p>Загрузка данных пользователя...</p>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';

export default {
  name: 'ProfileView',
  computed: {
    ...mapState('auth', ['user'])
  },
  methods: {
    ...mapActions('auth', ['fetchCurrentUser']),
    
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    }
 },
  mounted() {
    this.fetchCurrentUser();
  }
};
</script>

<style scoped>
.profile {
  max-width: 600px;
  margin: 0 auto;
  padding: 2rem;
}

.profile h1 {
  color: #333;
  margin-bottom: 2rem;
}

.profile p {
  margin: 0.5rem 0;
  padding: 0.5rem 0;
  border-bottom: 1px solid #eee;
}
</style>