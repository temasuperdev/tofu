<template>
  <div class="notes-list">
    <div class="notes-header">
      <h1>Мои заметки</h1>
      <button @click="showCreateModal = true" class="btn btn-primary">Создать заметку</button>
    </div>
    
    <div class="notes-grid">
      <NoteCard 
        v-for="note in notes" 
        :key="note.id" 
        :note="note"
        @edit="editNote"
        @delete="deleteNote"
      />
    </div>
    
    <!-- Модальное окно для создания/редактирования заметки -->
    <div v-if="showCreateModal" class="modal-overlay">
      <div class="modal-content">
        <NoteEditor 
          :note="currentNote" 
          @save="saveNote"
          @cancel="closeModal"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import NoteCard from '@/components/NoteCard.vue';
import NoteEditor from '@/components/NoteEditor.vue';

export default {
  name: 'NoteList',
  components: {
    NoteCard,
    NoteEditor
  },
  data() {
    return {
      showCreateModal: false,
      currentNote: null,
    };
  },
  computed: {
    ...mapState('notes', ['notes'])
  },
  methods: {
    ...mapActions('notes', ['fetchNotes', 'createNote', 'updateNote', 'deleteNote']),
    
    async loadNotes() {
      await this.fetchNotes();
    },
    
    editNote(note) {
      this.currentNote = { ...note };
      this.showCreateModal = true;
    },
    
    async deleteNote(noteId) {
      if (confirm('Вы уверены, что хотите удалить эту заметку?')) {
        await this.deleteNote(noteId);
      }
    },
    
    async saveNote(noteData) {
      try {
        if (noteData.id) {
          await this.updateNote(noteData);
        } else {
          await this.createNote(noteData);
        }
        this.closeModal();
      } catch (error) {
        console.error('Ошибка сохранения заметки:', error);
      }
    },
    
    closeModal() {
      this.showCreateModal = false;
      this.currentNote = null;
    }
  },
  mounted() {
    this.loadNotes();
  }
};
</script>

<style scoped>
.notes-list {
  padding: 20px 0;
}

.notes-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.notes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
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