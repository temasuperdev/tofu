<template>
  <div class="register-form">
    <h2>Регистрация</h2>
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="username">Имя пользователя:</label>
        <input 
          type="text" 
          id="username" 
          v-model="form.username" 
          required
          placeholder="Введите имя пользователя"
        >
      </div>
      
      <div class="form-group">
        <label for="email">Email:</label>
        <input 
          type="email" 
          id="email" 
          v-model="form.email" 
          required
          placeholder="Введите email"
        >
      </div>
      
      <div class="form-group">
        <label for="password">Пароль:</label>
        <input 
          type="password" 
          id="password" 
          v-model="form.password" 
          required
          placeholder="Введите пароль"
        >
      </div>
      
      <div class="form-group">
        <label for="confirmPassword">Подтверждение пароля:</label>
        <input 
          type="password" 
          id="confirmPassword" 
          v-model="form.confirmPassword" 
          required
          placeholder="Подтвердите пароль"
        >
      </div>
      
      <button type="submit" class="btn btn-primary" :disabled="loading">
        {{ loading ? 'Регистрация...' : 'Зарегистрироваться' }}
      </button>
    </form>
    
    <p class="login-link">
      Уже есть аккаунт? 
      <router-link to="/login">Войти</router-link>
    </p>
  </div>
</template>

<script>
import { mapActions } from 'vuex';

export default {
  name: 'RegisterForm',
  data() {
    return {
      form: {
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
      },
      loading: false
    };
  },
  methods: {
    ...mapActions('auth', ['register']),
    
    async handleSubmit() {
      if (this.form.password !== this.form.confirmPassword) {
        alert('Пароли не совпадают');
        return;
      }
      
      this.loading = true;
      try {
        await this.register(this.form);
        this.$router.push('/login');
      } catch (error) {
        alert('Ошибка регистрации: ' + error.message);
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.register-form {
  max-width: 400px;
  margin: 0 auto;
  padding: 2rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: white;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
}

.form-group input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
}

.btn {
  width: 100%;
  padding: 0.75rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

.btn-primary {
  background-color: #28a745;
  color: white;
}

.btn:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.login-link {
  margin-top: 1rem;
  text-align: center;
}

.login-link a {
  color: #007bff;
  text-decoration: none;
}

.login-link a:hover {
  text-decoration: underline;
}
</style>