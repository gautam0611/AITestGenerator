<template>
  <div class="scenario-input">
    <!-- Warning message -->
    <div class="warning-message" v-if="!loading">
      Note: Test case generation may take up to 7 minutes. Please be patient.
    </div>

    <!-- Input textarea -->
    <textarea 
      v-model="scenario" 
      placeholder="Enter a scenario for test case generation... (Response may take up to 7 minutes)" 
      :disabled="loading"
      class="scenario-textarea"
    ></textarea>
    
    <!-- Generate button -->
    <button 
      @click="generateTestCases" 
      :disabled="loading || !scenario.trim()"
      class="generate-button"
    >
      {{ loading ? 'Generating...' : 'Generate Test Cases' }}
    </button>

    <!-- Loading bar -->
    <div v-if="loading" class="loading-container">
      <div class="progress-bar-container">
        <div class="progress-bar">
          <div 
            class="progress-bar-fill"
            :style="{ width: `${loadingProgress}%` }"
          ></div>
        </div>
        <div class="loading-text">
          {{ loadingMessage }}
          <div class="timer-container">
            <div class="elapsed-time">
              Time elapsed: {{ formatTime(elapsedTime) }}
            </div>
            <div class="estimated-time" v-if="elapsedTime < 420">
              Estimated time remaining: {{ formatTime(420 - elapsedTime) }}
            </div>
          </div>
        </div>
      </div>
      
      <!-- Cancel button -->
      <button 
        @click="cancelGeneration" 
        class="cancel-button"
      >
        Cancel Generation
      </button>
    </div>

    <!-- Error message -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <!-- Test cases table -->
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
    const elapsedTime = ref(0)
    const loadingProgress = ref(0)
    const loadingMessage = ref('Initializing...')
    const controller = ref<AbortController | null>(null)
    let timer: number | undefined

    const formatTime = (seconds: number): string => {
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
    }

    const startTimer = () => {
      elapsedTime.value = 0
      timer = setInterval(() => {
        elapsedTime.value++
      }, 1000)
    }

    const stopTimer = () => {
      if (timer) {
        clearInterval(timer)
        timer = undefined
      }
    }

    const simulateProgress = () => {
      loadingProgress.value = 0
      const messages = [
        'Initializing model...',
        'Loading language model...',
        'Processing scenario...',
        'Analyzing requirements...',
        'Generating test cases...',
        'Validating test cases...',
        'Formatting results...',
        'Finalizing output...'
      ]
      
      let currentStep = 0
      const totalDuration = 420000 // 7 minutes in milliseconds
      const intervalDuration = 5000 // Update every 5 seconds
      const progressPerStep = 90 / (totalDuration / intervalDuration)
      
      const progressInterval = setInterval(() => {
        if (loadingProgress.value < 90) {
          loadingProgress.value += progressPerStep
          if (loadingProgress.value > (currentStep + 1) * (90 / messages.length) && currentStep < messages.length - 1) {
            currentStep++
            loadingMessage.value = messages[currentStep]
          }
        }
      }, intervalDuration)

      return () => {
        clearInterval(progressInterval)
        loadingProgress.value = 100
        loadingMessage.value = 'Complete!'
      }
    }

    const cancelGeneration = async () => {
      if (controller.value) {
        controller.value.abort()
        loading.value = false
        stopTimer()
        error.value = 'Generation cancelled by user'
      }
    }

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
            preconditions.push(line.trim().replace(/^\*\s*/, '').trim())
          } else if (line.trim().startsWith('*') && inExpectedResults) {
            expectedResults.push(line.trim().replace(/^\*\s*/, '').trim())
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
      startTimer()
      controller.value = new AbortController()

      const stopProgress = simulateProgress()

      try {
        const response = await fetch('http://localhost:8000/generate-test-cases', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            scenario: scenario.value
          }),
          signal: controller.value.signal
        })

        const data = await response.json()
        
        if (!response.ok) {
          throw new Error(data.detail || 'Failed to generate test cases')
        }

        testCases.value = parseTestCases(data.test_cases)
        
      } catch (e) {
        if (e instanceof Error && e.name === 'AbortError') {
          error.value = 'Generation cancelled by user'
        } else {
          error.value = e instanceof Error ? e.message : 'An error occurred'
        }
      } finally {
        stopProgress()
        stopTimer()
        loading.value = false
        controller.value = null
      }
    }

    return {
      scenario,
      loading,
      error,
      testCases,
      generateTestCases,
      elapsedTime,
      loadingProgress,
      loadingMessage,
      formatTime,
      cancelGeneration
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

.warning-message {
  background-color: #fff3cd;
  border: 1px solid #ffeeba;
  color: #856404;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 20px;
  font-size: 14px;
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

.loading-container {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin: 20px 0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.progress-bar-container {
  margin-bottom: 15px;
}

.progress-bar {
  width: 100%;
  height: 20px;
  background-color: #e9ecef;
  border-radius: 10px;
  overflow: hidden;
  position: relative;
}

.progress-bar-fill {
  height: 100%;
  background-color: #4CAF50;
  transition: width 0.5s ease-in-out;
  border-radius: 10px;
  position: relative;
  overflow: hidden;
}

.progress-bar-fill::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    45deg,
    rgba(255, 255, 255, 0.2) 25%,
    transparent 25%,
    transparent 50%,
    rgba(255, 255, 255, 0.2) 50%,
    rgba(255, 255, 255, 0.2) 75%,
    transparent 75%,
    transparent
  );
  background-size: 50px 50px;
  animation: move 2s linear infinite;
  overflow: hidden;
}

@keyframes move {
  0% {
    background-position: 0 0;
  }
  100% {
    background-position: 50px 50px;
  }
}

.loading-text {
  text-align: center;
  margin-top: 10px;
  color: #666;
  font-size: 14px;
}

.timer-container {
  margin-top: 10px;
  text-align: center;
}

.elapsed-time,
.estimated-time {
  font-size: 14px;
  color: #666;
  margin: 5px 0;
}

.cancel-button {
  margin-top: 15px;
  padding: 8px 16px;
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  width: auto;
  display: block;
  margin-left: auto;
  margin-right: auto;
}

.cancel-button:hover {
  background-color: #c82333;
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
