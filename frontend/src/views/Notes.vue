<template>
  <div class="notes">
    <NoteList />
  </div>
</template>

<script>
import NoteList from '@/components/NoteList.vue';

export default {
  name: 'NotesView',
  components: {
    NoteList
  }
};
</script>