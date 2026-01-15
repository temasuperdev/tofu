import { defineStore } from 'pinia';
import axios from 'axios';

export const useNotesStore = defineStore('notes', {
  state: () => ({
    notes: [],
    loading: false,
  }),
  
  getters: {
    getAllNotes: (state) => state.notes,
    getNoteById: (state) => (id) => {
      return state.notes.find(note => note.id === id);
    }
  },
  
  actions: {
    async fetchNotes() {
      this.loading = true;
      try {
        const response = await axios.get('/api/v1/notes');
        this.notes = response.data;
        return response.data;
      } catch (error) {
        console.error('Failed to fetch notes:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    async createNote(noteData) {
      try {
        const response = await axios.post('/api/v1/notes', noteData);
        this.notes.push(response.data);
        return response.data;
      } catch (error) {
        console.error('Failed to create note:', error);
        throw error;
      }
    },
    
    async updateNote(id, noteData) {
      try {
        const response = await axios.put(`/api/v1/notes/${id}`, noteData);
        const index = this.notes.findIndex(note => note.id === id);
        if (index !== -1) {
          this.notes[index] = response.data;
        }
        return response.data;
      } catch (error) {
        console.error('Failed to update note:', error);
        throw error;
      }
    },
    
    async deleteNote(id) {
      try {
        await axios.delete(`/api/v1/notes/${id}`);
        this.notes = this.notes.filter(note => note.id !== id);
      } catch (error) {
        console.error('Failed to delete note:', error);
        throw error;
      }
    }
  }
});