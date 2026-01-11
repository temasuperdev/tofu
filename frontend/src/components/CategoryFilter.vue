<template>
  <div class="category-filter">
    <select @change="onCategoryChange" v-model="selectedCategory">
      <option value="">Все категории</option>
      <option value="work">Работа</option>
      <option value="personal">Личное</option>
      <option value="ideas">Идеи</option>
      <option value="todo">Список дел</option>
    </select>
  </div>
</template>

<script>
export default {
  name: 'CategoryFilter',
  data() {
    return {
      selectedCategory: ''
    };
  },
  methods: {
    onCategoryChange() {
      this.$emit('category-change', this.selectedCategory);
    }
  }
};
</script>

<style scoped>
.category-filter select {
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
}
</style>