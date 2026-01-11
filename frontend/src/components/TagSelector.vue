<template>
  <div class="tag-selector">
    <input 
      type="text" 
      v-model="inputValue" 
      @keyup.enter="addTag"
      placeholder="Введите тег и нажмите Enter"
    >
    <div class="tags-container">
      <span 
        class="tag" 
        v-for="(tag, index) in tags" 
        :key="index"
      >
        {{ tag }}
        <button @click="removeTag(index)">×</button>
      </span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TagSelector',
  props: {
    initialTags: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      inputValue: '',
      tags: [...this.initialTags]
    };
  },
  watch: {
    tags: {
      handler(newTags) {
        this.$emit('update-tags', newTags);
      },
      deep: true
    }
  },
  methods: {
    addTag() {
      if (this.inputValue.trim()) {
        if (!this.tags.includes(this.inputValue.trim())) {
          this.tags.push(this.inputValue.trim());
        }
        this.inputValue = '';
      }
    },
    removeTag(index) {
      this.tags.splice(index, 1);
    }
  }
};
</script>

<style scoped>
.tag-selector input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
}

.tags-container {
  margin-top: 0.5rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag {
  background: #e3f2fd;
  color: #1976d2;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.tag button {
  background: none;
  border: none;
  color: #1976d2;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>