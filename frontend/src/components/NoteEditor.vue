<template>
  <div class="note-editor">
    <h2>{{ note ? 'Редактировать заметку' : 'Создать новую заметку' }}</h2>
    
    <form @submit.prevent="submitNote">
      <div class="form-group">
        <label for="title">Заголовок:</label>
        <input 
          type="text" 
          id="title" 
          v-model="formData.title" 
          required
          placeholder="Введите заголовок заметки"
        >
      </div>
      
      <div class="form-group">
        <label for="category">Категория:</label>
        <select id="category" v-model="formData.category">
          <option value="">Без категории</option>
          <option value="work">Работа</option>
          <option value="personal">Личное</option>
          <option value="ideas">Идеи</option>
          <option value="todo">Список дел</option>
        </select>
      </div>
      
      <div class="form-group">
        <label for="tags">Теги:</label>
        <input 
          type="text" 
          id="tags" 
          v-model="tagsInput" 
          placeholder="Введите теги через запятую"
        >
        <div class="tags-preview">
          <span 
            class="tag" 
            v-for="(tag, index) in formData.tags" 
            :key="index"
          >
            {{ tag }}
            <button @click="removeTag(index)" type="button">×</button>
          </span>
        </div>
      </div>
      
      <div class="form-group">
        <label for="content">Содержание:</label>
        <textarea 
          id="content" 
          v-model="formData.content" 
          rows="10"
          placeholder="Введите содержание заметки"
        ></textarea>
      </div>
      
      <div class="form-group">
        <label>
          <input 
            type="checkbox" 
            v-model="formData.is_public"
          > 
          Опубликовать для других
        </label>
      </div>
      
      <div class="form-actions">
        <button type="submit" class="btn btn-primary">
          {{ note ? 'Сохранить изменения' : 'Создать заметку' }}
        </button>
        <button type="button" @click="$emit('cancel')" class="btn btn-secondary">
          Отмена
        </button>
      </div>
    </form>
  </div>
</template>

<script>
export default {
  name: 'NoteEditor',
  props: {
    note: {
      type: Object,
      default: null
    }
  },
  emits: ['save', 'cancel'],
  data() {
    return {
      formData: {
        title: '',
        content: '',
        category: '',
        tags: [],
        is_public: false
      },
      tagsInput: ''
    };
  },
  watch: {
    note: {
      immediate: true,
      handler(newNote) {
        if (newNote) {
          this.formData = {
            ...newNote
          };
          this.tagsInput = newNote.tags.join(', ');
        } else {
          this.resetForm();
        }
      }
    },
    tagsInput: {
      handler(newTags) {
        // Обновляем теги при изменении строки ввода
        this.formData.tags = newTags
          .split(',')
          .map(tag => tag.trim())
          .filter(tag => tag.length > 0);
      }
    }
  },
  methods: {
    resetForm() {
      this.formData = {
        title: '',
        content: '',
        category: '',
        tags: [],
        is_public: false
      };
      this.tagsInput = '';
    },
    
    submitNote() {
      this.$emit('save', { ...this.formData });
    },
    
    removeTag(index) {
      this.formData.tags.splice(index, 1);
      this.tagsInput = this.formData.tags.join(', ');
    }
  }
};
</script>

<style scoped>
.note-editor {
  width: 100%;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 4px;
  font-weight: bold;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1em;
}

.form-group textarea {
  resize: vertical;
  min-height: 150px;
}

.tags-preview {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.tag {
  background: #e3f2fd;
  color: #1976d2;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8em;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.tag button {
  background: none;
  border: none;
  color: #1976d2;
  cursor: pointer;
  font-size: 1.2em;
  padding: 0;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}
</style>