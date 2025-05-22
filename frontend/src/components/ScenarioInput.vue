<template>
  <div class="scenario-input">
    <textarea 
      v-model="scenario" 
      placeholder="Enter a scenario for test case generation... (Response may take 1-2 minutes)" 
      :disabled="loading"
      class="scenario-textarea"
    ></textarea>
    
    <button 
      @click="generateTestCases" 
      :disabled="loading || !scenario.trim()"
      class="generate-button"
    >
      {{ loading ? 'Generating...' : 'Generate Test Cases' }}
    </button>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <div v-if="testCases.length > 0" class="test-cases-container">
      <h3>Generated Test Cases</h3>
      <table class="test-cases-table">
        <thead>
          <tr>
            <th>Test Case ID</th>
            <th>Description</th>
            <th>Preconditions</th>
            <th>Expected Result</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="testCase in testCases" :key="testCase.id">
            <td>{{ testCase.id }}</td>
            <td>{{ testCase.description }}</td>
            <td>
              <ul>
                <li v-for="(condition, index) in testCase.preconditions" 
                    :key="index">{{ condition }}</li>
              </ul>
            </td>
            <td>
              <ul>
                <li v-for="(result, index) in testCase.expectedResults" 
                    :key="index">{{ result }}</li>
              </ul>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'

interface TestCase {
  id: string;
  description: string;
  preconditions: string[];
  expectedResults: string[];
}

export default defineComponent({
  name: 'ScenarioInput',
  setup() {
    const scenario = ref('')
    const loading = ref(false)
    const error = ref('')
    const testCases = ref<TestCase[]>([])

    const parseTestCases = (rawText: string): TestCase[] => {
      const testCases: TestCase[] = []
      const sections = rawText.split('### Test Case')
      
      sections.slice(1).forEach(section => {
        const idMatch = section.match(/(\d+):/)
        const descMatch = section.match(/\*\*Description:\*\* ([^\n]+)/)
        
        const preconditions: string[] = []
        const expectedResults: string[] = []
        
        let inPreconditions = false
        let inExpectedResults = false
        
        section.split('\n').forEach(line => {
          if (line.includes('**Preconditions:**')) {
            inPreconditions = true
            inExpectedResults = false
          } else if (line.includes('**Expected Result:**')) {
            inPreconditions = false
            inExpectedResults = true
          } else if (line.trim().startsWith('*') && inPreconditions) {
            preconditions.push(line.trim().replace('*', '').trim())
          } else if (line.trim().startsWith('*') && inExpectedResults) {
            expectedResults.push(line.trim().replace('*', '').trim())
          }
        })

        if (idMatch && descMatch) {
          testCases.push({
            id: `TC-${idMatch[1].padStart(3, '0')}`,
            description: descMatch[1],
            preconditions,
            expectedResults
          })
        }
      })

      return testCases
    }

    const generateTestCases = async () => {
      if (!scenario.value.trim()) return
      
      loading.value = true
      error.value = ''
      testCases.value = []

      try {
        const response = await fetch('http://localhost:8000/generate-test-cases', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            scenario: scenario.value
          })
        })

        if (!response.ok) {
          throw new Error('Failed to generate test cases')
        }

        const data = await response.json()
        testCases.value = parseTestCases(data.test_cases)
      } catch (e) {
        error.value = e instanceof Error ? e.message : 'An error occurred'
      } finally {
        loading.value = false
      }
    }

    return {
      scenario,
      loading,
      error,
      testCases,
      generateTestCases
    }
  }
})
</script>

<style scoped>
.scenario-input {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.scenario-textarea {
  width: 100%;
  min-height: 150px;
  padding: 12px;
  margin-bottom: 16px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-family: inherit;
  resize: vertical;
}

.generate-button {
  width: 100%;
  padding: 12px 20px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  margin-bottom: 20px;
}

.generate-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.error-message {
  color: #dc3545;
  padding: 10px;
  margin-bottom: 20px;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
  background-color: #f8d7da;
}

.test-cases-container {
  margin-top: 20px;
}

.test-cases-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
  background-color: white;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}

.test-cases-table th,
.test-cases-table td {
  padding: 12px;
  border: 1px solid #ddd;
  text-align: left;
}

.test-cases-table th {
  background-color: #f5f5f5;
  font-weight: 600;
}

.test-cases-table tr:nth-child(even) {
  background-color: #f9f9f9;
}

.test-cases-table ul {
  margin: 0;
  padding-left: 20px;
}

.test-cases-table li {
  margin-bottom: 4px;
}

h3 {
  color: #333;
  margin-bottom: 15px;
}
</style>
