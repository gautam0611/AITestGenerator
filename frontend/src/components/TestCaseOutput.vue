<template>
  <div>
    <h2>Generated Test Cases</h2>
    <ul>
      <li v-for="(testCase, index) in testCases" :key="index">{{ testCase }}</li>
    </ul>
  </div>
</template>

<script lang="ts">
import { defineComponent, PropType } from 'vue';

export default defineComponent({
  props: {
    testCases: {
      type: Array as PropType<string[]>,
      required: true
    }
  }
});
</script>
