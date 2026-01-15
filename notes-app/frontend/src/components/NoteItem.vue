<template>
  <div class="border rounded-lg p-4 mb-4 shadow-sm hover:shadow-md transition-shadow">
    <div class="flex justify-between items-start">
      <h3 class="text-lg font-semibold text-gray-800">{{ note.title }}</h3>
      <div class="flex space-x-2">
        <button 
          @click="$emit('edit', note)" 
          class="text-blue-600 hover:text-blue-800"
        >
          Edit
        </button>
        <button 
          @click="$emit('delete', note.id)" 
          class="text-red-600 hover:text-red-800"
        >
          Delete
        </button>
      </div>
    </div>
    <p class="mt-2 text-gray-600">{{ note.content.substring(0, 100) }}{{ note.content.length > 100 ? '...' : '' }}</p>
    <div class="mt-3 flex justify-between items-center">
      <span class="text-xs text-gray-500">
        {{ new Date(note.created_at).toLocaleDateString() }}
      </span>
      <span 
        class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
        :class="note.is_public ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'"
      >
        {{ note.is_public ? 'Public' : 'Private' }}
      </span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  note: {
    type: Object,
    required: true
  }
});

defineEmits(['edit', 'delete']);
</script>