import apiClient from './api';

export const notesAPI = {
  async getNotes(params = {}) {
    const response = await apiClient.get('/notes', params);
    return response.data;
  },
  
  async getNote(noteId) {
    const response = await apiClient.get(`/notes/${noteId}`);
    return response.data;
  },
  
  async createNote(noteData) {
    const response = await apiClient.post('/notes', noteData);
    return response.data;
  },
  
  async updateNote(noteId, noteData) {
    const response = await apiClient.put(`/notes/${noteId}`, noteData);
    return response.data;
  },
  
  async deleteNote(noteId) {
    const response = await apiClient.delete(`/notes/${noteId}`);
    return response.data;
  }
};