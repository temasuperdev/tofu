import { notesAPI } from '@/services/notes';

const state = {
  notes: [],
  note: null
};

const getters = {
  allNotes: state => state.notes,
  currentNote: state => state.note
};

const mutations = {
  SET_NOTES(state, notes) {
    state.notes = notes;
  },
  ADD_NOTE(state, note) {
    state.notes.unshift(note);
  },
  UPDATE_NOTE(state, updatedNote) {
    const index = state.notes.findIndex(note => note.id === updatedNote.id);
    if (index !== -1) {
      state.notes.splice(index, 1, updatedNote);
    }
    if (state.note && state.note.id === updatedNote.id) {
      state.note = updatedNote;
    }
  },
  DELETE_NOTE(state, noteId) {
    state.notes = state.notes.filter(note => note.id !== noteId);
    if (state.note && state.note.id === noteId) {
      state.note = null;
    }
  },
  SET_CURRENT_NOTE(state, note) {
    state.note = note;
  }
};

const actions = {
  async fetchNotes({ commit }) {
    try {
      const notes = await notesAPI.getNotes();
      commit('SET_NOTES', notes);
    } catch (error) {
      console.error('Error fetching notes:', error);
      throw error;
    }
  },
  
  async fetchNote({ commit }, noteId) {
    try {
      const note = await notesAPI.getNote(noteId);
      commit('SET_CURRENT_NOTE', note);
    } catch (error) {
      console.error('Error fetching note:', error);
      throw error;
    }
  },
  
  async createNote({ commit }, noteData) {
    try {
      const newNote = await notesAPI.createNote(noteData);
      commit('ADD_NOTE', newNote);
      return newNote;
    } catch (error) {
      console.error('Error creating note:', error);
      throw error;
    }
  },
  
  async updateNote({ commit }, noteData) {
    try {
      const updatedNote = await notesAPI.updateNote(noteData.id, noteData);
      commit('UPDATE_NOTE', updatedNote);
      return updatedNote;
    } catch (error) {
      console.error('Error updating note:', error);
      throw error;
    }
  },
  
  async deleteNote({ commit }, noteId) {
    try {
      await notesAPI.deleteNote(noteId);
      commit('DELETE_NOTE', noteId);
    } catch (error) {
      console.error('Error deleting note:', error);
      throw error;
    }
  },
  
  async deleteNoteById({ commit }, noteId) {
    try {
      await notesAPI.deleteNote(noteId);
      commit('DELETE_NOTE', noteId);
    } catch (error) {
      console.error('Error deleting note:', error);
      throw error;
    }
  }
};

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions,
};