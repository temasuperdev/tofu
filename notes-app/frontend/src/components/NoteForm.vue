<template>
  <form @submit.prevent="handleSubmit" class="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4">
    <div class="mb-4">
      <label class="block text-gray-700 text-sm font-bold mb-2" for="title">
        Title
      </label>
      <input
        id="title"
        v-model="formData.title"
        class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
        type="text"
        placeholder="Note title"
        required
      />
    </div>
    <div class="mb-6">
      <label class="block text-gray-700 text-sm font-bold mb-2" for="content">
        Content
      </label>
      <textarea
        id="content"
        v-model="formData.content"
        class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline h-32"
        placeholder="Note content"
        required
      ></textarea>
    </div>
    <div class="mb-6">
      <label class="flex items-center">
        <input
          v-model="formData.is_public"
          type="checkbox"
          class="rounded text-blue-600 focus:ring-blue-500"
        />
        <span class="ml-2 text-gray-700">Make public</span>
      </label>
    </div>
    <div class="flex items-center justify-between">
      <button
        class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
        type="submit"
      >
        {{ isEditing ? 'Update Note' : 'Create Note' }}
      </button>
      <button
        v-if="isEditing"
        @click="$emit('cancel')"
        class="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
        type="button"
      >
        Cancel
      </button>
    </div>
  </form>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  note: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['save', 'cancel']);

const isEditing = ref(false);
const formData = ref({
  title: '',
  content: '',
  is_public: false
});

// Watch for changes in the note prop to handle editing
watch(() => props.note, (newNote) => {
  if (newNote) {
    formData.value = {
      title: newNote.title || '',
      content: newNote.content || '',
      is_public: newNote.is_public || false
    };
    isEditing.value = true;
  } else {
    resetForm();
    isEditing.value = false;
  }
}, { immediate: true });

const handleSubmit = () => {
  emit('save', { ...formData.value });
};

const resetForm = () => {
  formData.value = {
    title: '',
    content: '',
    is_public: false
  };
};
</script>