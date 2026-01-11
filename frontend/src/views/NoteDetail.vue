<template>
  <div class="note-detail">
    <div v-if="note">
      <h1>{{ note.title }}</h1>
      <div class="note-meta">
        <span>Создано: {{ formatDate(note.created_at) }}</span>
        <span v-if="note.category" class="category">Категория: {{ note.category }}</span>
      </div>
      <div class="note-content" v-html="renderedContent"></div>
      <div class="note-tags">
        <span class="tag" v-for="tag in note.tags" :key="tag">{{ tag }}</span>
      </div>
      <div class="note-actions">
        <button @click="editNote" class="btn btn-secondary">Редактировать</button>
        <button @click="deleteNote" class="btn btn-danger">Удалить</button>
        <button @click="goBack" class="btn btn-outline">Назад</button>
      </div>
    </div>
    <div v-else>
      <p>Заметка не найдена</p>
    </div>
    
    <!-- Модальное окно для редактирования заметки -->
    <div v-if="showEditModal" class="modal-overlay">
      <div class="modal-content">
        <NoteEditor 
          :note="note" 
          @save="updateNote"
          @cancel="closeModal"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import NoteEditor from '@/components/NoteEditor.vue';
import DOMPurify from 'dompurify';

export default {
  name: 'NoteDetailView',
  components: {
    NoteEditor
  },
  data() {
    return {
      showEditModal: false
    };
  },
  computed: {
    ...mapState('notes', ['note']),
    renderedContent() {
      // Очищаем HTML от потенциально опасных элементов
      return DOMPurify.sanitize(this.note.content || '');
    }
  },
  methods: {
    ...mapActions('notes', ['fetchNote', 'deleteNoteById', 'updateNote']),
    
    async loadNote() {
      const noteId = parseInt(this.$route.params.id);
      await this.fetchNote(noteId);
    },
    
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    },
    
    editNote() {
      this.showEditModal = true;
    },
    
    async deleteNote() {
      if (confirm('Вы уверены, что хотите удалить эту заметку?')) {
        await this.deleteNoteById(this.note.id);
        this.$router.push('/notes');
      }
    },
    
    async updateNote(noteData) {
      try {
        await this.updateNote(noteData);
        this.closeModal();
      } catch (error) {
        console.error('Ошибка обновления заметки:', error);
      }
    },
    
    closeModal() {
      this.showEditModal = false;
    },
    
    goBack() {
      this.$router.go(-1);
    }
  },
  mounted() {
    this.loadNote();
  },
  watch: {
    '$route.params.id'() {
      this.loadNote();
    }
  }
};
</script>

<style scoped>
.note-detail {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.note-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
  color: #666;
  font-size: 0.9rem;
}

.category {
  background: #e3f2fd;
  color: #1976d2;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.note-content {
  margin: 2rem 0;
  line-height: 1.6;
  color: #333;
}

.note-tags {
  margin: 1rem 0;
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.tag {
 background: #f5f5f5;
  color: #555;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
}

.note-actions {
  margin-top: 2rem;
  display: flex;
  gap: 1rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  text-decoration: none;
  display: inline-block;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
}

.btn-outline {
  background-color: transparent;
  color: #007bff;
  border: 1px solid #007bff;
}

.btn:hover {
  opacity: 0.9;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}
</style>