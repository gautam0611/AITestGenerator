<template>
  <div>
    <h2>Generated Test Cases</h2>
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>Test Case</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(testCase, index) in testCases" :key="index">
          <td>{{ index + 1 }}</td>
          <td>{{ testCase }}</td>
        </tr>
      </tbody>
    </table>
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

<style scoped>
table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

th {
  background-color: #f2f2f2;
}
</style>
