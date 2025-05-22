<template>
  <div>
    <textarea v-model="scenario" placeholder="Enter a scenario"></textarea>
    <button @click="generate">Generate Test Cases</button>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  emits: ['generate'],
  setup(_, { emit }) {
    const scenario = ref('');

    const generate = () => {
      emit('generate', scenario.value);
    };

    return { scenario, generate };
  }
});
</script>
