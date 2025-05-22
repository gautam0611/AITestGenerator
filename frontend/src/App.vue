<template>
  <div class="app">
    <h1>Test Case Generator</h1>
    <ScenarioInput />
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import ScenarioInput from './components/ScenarioInput.vue';

export default defineComponent({
  name: 'App',
  components: {
    ScenarioInput
  }
});
</script>

<style>
.app {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
}
</style>
