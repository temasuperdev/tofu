<template>
  <div class="note-card">
    <div class="note-header">
      <h3>{{ note.title }}</h3>
      <span class="note-category" v-if="note.category">{{ note.category }}</span>
    </div>
    
    <div class="note-content" v-html="renderedContent"></div>
    
    <div class="note-meta">
      <span class="note-date">{{ formatDate(note.created_at) }}</span>
      <div class="note-tags">
        <span class="tag" v-for="tag in note.tags" :key="tag">{{ tag }}</span>
      </div>
    
    <div class="note-actions">
      <button @click="$emit('edit', note)" class="btn btn-secondary">Редактировать</button>
      <button @click="$emit('delete', note.id)" class="btn btn-danger">Удалить</button>
    </div>
  </div>
</template>

<script>
import DOMPurify from 'dompurify';

export default {
  name: 'NoteCard',
  props: {
    note: {
      type: Object,
      required: true
    }
  },
  emits: ['edit', 'delete'],
  computed: {
    renderedContent() {
      // Очищаем HTML от потенциально опасных элементов
      return DOMPurify.sanitize(this.note.content || '');
    }
  },
  methods: {
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    }
  }
};
</script>

<style scoped>
.note-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0.1);
  transition: transform 0.2s;
}

.note-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.note-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.note-header h3 {
  margin: 0;
  font-size: 1.2em;
  color: #333;
}

.note-category {
  background: #e3f2fd;
  color: #1976d2;
 padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8em;
}

.note-content {
  margin-bottom: 16px;
  color: #555;
  line-height: 1.5;
  max-height: 150px;
  overflow: hidden;
}

.note-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-size: 0.85em;
  color: #777;
}

.note-tags {
  display: flex;
  gap: 4px;
}

.tag {
  background: #f5f5f5;
  color: #555;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.8em;
}

.note-actions {
  display: flex;
  gap: 8px;
}

.btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9em;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn:hover {
  opacity: 0.9;
}
</style>