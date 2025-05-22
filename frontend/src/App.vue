<template>
  <div id="app">
    <h1>AI Test Case Generator</h1>
    <ScenarioInput @generate="handleGenerate" />
    <TestCaseOutput :testCases="testCases" />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import ScenarioInput from './components/ScenarioInput.vue';
import TestCaseOutput from './components/TestCaseOutput.vue';

export default defineComponent({
  components: { ScenarioInput, TestCaseOutput },
  setup() {
    const testCases = ref<string[]>([]);

    const handleGenerate = async (scenario: string) => {
      const response = await fetch('/api/generate-test-cases/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario })
      });
      const data = await response.json();
      testCases.value = data.test_cases.split('\n');
    };

    return { testCases, handleGenerate };
  }
});
</script>
