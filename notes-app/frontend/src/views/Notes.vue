<template>
  <div>
    <h1 class="text-2xl font-bold text-gray-800 mb-6">My Notes</h1>
    
    <!-- Create Note Form -->
    <div v-if="!editingNote" class="mb-8">
      <NoteForm @save="createNote" />
    </div>
    
    <!-- Edit Note Form -->
    <div v-else class="mb-8">
      <NoteForm :note="editingNote" @save="updateNote" @cancel="cancelEdit" />
    </div>
    
    <!-- Loading indicator -->
    <div v-if="loading" class="text-center py-4">
      <p>Loading notes...</p>
    </div>
    
    <!-- Notes list -->
    <div v-else>
      <div v-if="notes.length === 0" class="text-center py-8">
        <p class="text-gray-600">You don't have any notes yet.</p>
        <p class="text-gray-600 mt-2">Create your first note above!</p>
      </div>
      
      <div v-else>
        <h2 class="text-xl font-semibold text-gray-700 mb-4">Your Notes ({{ notes.length }})</h2>
        <NoteItem 
          v-for="note in notes" 
          :key="note.id" 
          :note="note"
          @edit="startEdit"
          @delete="deleteNote"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useNotesStore } from '../store/notes';
import NoteForm from '../components/NoteForm.vue';
import NoteItem from '../components/NoteItem.vue';

const notesStore = useNotesStore();

onMounted(async () => {
  await notesStore.fetchNotes();
});

const { notes, loading, createNote: createNoteAction, updateNote: updateNoteAction, deleteNote: deleteNoteAction } = notesStore;

// Editing state
let editingNote = $ref(null);

const createNote = async (noteData) => {
  try {
    await createNoteAction(noteData);
    // Reset form after successful creation
  } catch (error) {
    console.error('Failed to create note:', error);
  }
};

const startEdit = (note) => {
  editingNote = { ...note }; // Create a copy to avoid direct mutation
};

const updateNote = async (noteData) => {
  try {
    await updateNoteAction(editingNote.id, noteData);
    editingNote = null;
  } catch (error) {
    console.error('Failed to update note:', error);
  }
};

const cancelEdit = () => {
  editingNote = null;
};

const deleteNote = async (id) => {
  if (confirm('Are you sure you want to delete this note?')) {
    try {
      await deleteNoteAction(id);
    } catch (error) {
      console.error('Failed to delete note:', error);
    }
  }
};
</script>