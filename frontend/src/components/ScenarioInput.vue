<script lang="ts">
import { defineComponent, ref } from 'vue'

interface TestCase {
  id: string;
  name: string;
  description: string;
  steps: {
    step: string;
    expectedResult: string;
  }[];
  preconditions: string[];
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
    const rawResponse = ref('')
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

    const parseTestCases = (rawText: string): TestCase[] => {
      const testCases: TestCase[] = [];
      
      try {
        // Extract overall description and preconditions
        const descMatch = rawText.match(/\*\*Description:\*\*(.*?)(?=\*\*Preconditions)/s);
        const preMatch = rawText.match(/\*\*Preconditions:\*\*(.*?)(?=\*\*Steps)/s);
        
        const generalDescription = descMatch ? descMatch[1].trim() : '';
        const preconditions = preMatch 
          ? preMatch[1]
            .split('*')
            .map(item => item.trim())
            .filter(item => item.length > 0) 
          : [];

        // Split into individual test cases
        const testCaseBlocks = rawText.split(/\*\*Test Case \d+:\*\*/);
        
        testCaseBlocks.slice(1).forEach((block, index) => {
          const steps: { step: string; expectedResult: string; }[] = [];
          
          // Extract steps and expected results
          const stepMatches = block.matchAll(/\*\*Step \d+:\*\* (.*?)(?=\*\*|$)/g);
          const expectedMatch = block.match(/\*\*Expected Result:\*\* (.*?)(?=\d\.|$)/s);
          
          for (const match of stepMatches) {
            steps.push({
              step: match[1].trim(),
              expectedResult: ''
            });
          }

          if (expectedMatch) {
            // Add expected result to last step
            if (steps.length > 0) {
              steps[steps.length - 1].expectedResult = expectedMatch[1].trim();
            }
          }

          testCases.push({
            id: `TC-${(index + 1).toString().padStart(3, '0')}`,
            name: block.split('\n')[0].trim(),
            description: generalDescription,
            steps: steps,
            preconditions: preconditions
          });
        });
      } catch (e) {
        console.error('Error parsing test cases:', e);
      }

      return testCases;
    };

    const generateTestCases = async () => {
      if (!scenario.value.trim()) return;
      
      loading.value = true;
      error.value = '';
      testCases.value = [];
      rawResponse.value = '';
      startTimer();
      controller.value = new AbortController();
      loadingProgress.value = 0;
      loadingMessage.value = 'Generating test cases...';

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
        });

        const data = await response.json();
        
        // Immediately stop loading when we get the response
        loading.value = false;
        loadingProgress.value = 100;
        stopTimer();
        
        if (!response.ok) {
          throw new Error(data.detail || 'Failed to generate test cases');
        }

        // Store and display raw response
        if (data.test_cases) {
          rawResponse.value = data.test_cases;
          console.log('Raw response:', data.test_cases);
          testCases.value = parseTestCases(data.test_cases);
        } else {
          throw new Error('No test cases in response');
        }
        
      } catch (e) {
        console.error('Error:', e);
        error.value = e instanceof Error ? e.message : 'An error occurred';
        loading.value = false;
        stopTimer();
      }
    };

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
      rawResponse
    }
  }
})
</script>

<template>
  <div class="scenario-input">
    <!-- Warning message -->
    <div class="warning-message" v-if="!loading">
      Note: Test case generation may take up to 7 minutes. Please be patient.
    </div>

    <!-- Input textarea -->
    <textarea 
      v-model="scenario" 
      placeholder="Enter a scenario for test case generation..." 
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
          </div>
        </div>
      </div>
    </div>

    <!-- Error message -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <!-- Results Container -->
    <div v-if="rawResponse" class="results-container">
      <!-- Raw Response Display -->
      <div class="raw-response">
        <h3>Generated Test Cases:</h3>
        <pre>{{ rawResponse }}</pre>
      </div>

      <!-- Test cases table -->
      <div class="test-cases-container">
        <table class="test-cases-table">
          <thead>
            <tr>
              <th>Test Case ID</th>
              <th>Description</th>
              <th>Raw Response</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="testCase in testCases" :key="testCase.id">
              <td>{{ testCase.id }}</td>
              <td>{{ testCase.description }}</td>
              <td class="raw-response-cell">
                <pre>{{ testCase.preconditions[0] }}</pre>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<style scoped>
.scenario-input {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

.warning-message {
  background-color: #fff3cd;
  border: 1px solid #ffeeba;
  color: #856404;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 20px;
  font-size: 14px;
  text-align: center;
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
  font-size: 14px;
  line-height: 1.5;
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
  transition: background-color 0.3s ease;
}

.generate-button:hover {
  background-color: #45a049;
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
  margin-bottom: 20px;
}

.progress-bar {
  width: 100%;
  height: 20px;
  background-color: #e9ecef;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: inset 0 1px 2px rgba(0,0,0,0.1);
}

.progress-bar-fill {
  height: 100%;
  background-color: #4CAF50;
  transition: width 0.5s ease-in-out;
  background-image: linear-gradient(
    45deg,
    rgba(255, 255, 255, 0.15) 25%,
    transparent 25%,
    transparent 50%,
    rgba(255, 255, 255, 0.15) 50%,
    rgba(255, 255, 255, 0.15) 75%,
    transparent 75%,
    transparent
  );
  background-size: 1rem 1rem;
  animation: progress-bar-stripes 1s linear infinite;
}

@keyframes progress-bar-stripes {
  from { background-position: 1rem 0; }
  to { background-position: 0 0; }
}

.loading-text {
  margin-top: 10px;
  text-align: center;
  color: #666;
  font-size: 14px;
}

.timer-container {
  margin-top: 10px;
  font-size: 14px;
  display: flex;
  justify-content: center;
  gap: 20px;
}

.elapsed-time {
  color: #666;
}

.error-message {
  color: #dc3545;
  margin: 20px 0;
  padding: 12px;
  border: 1px solid #dc3545;
  border-radius: 4px;
  background-color: #f8d7da;
  font-size: 14px;
}

/* Results Container Styles */
.results-container {
  margin-top: 30px;
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* Test Cases Table Styles */
.test-cases-container {
  margin-top: 20px;
  overflow-x: auto;
}

.test-cases-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border: 1px solid #dee2e6;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  font-size: 14px;
  margin-bottom: 20px;
}

.test-cases-table th,
.test-cases-table td {
  border: 1px solid #dee2e6;
  padding: 12px 16px;
  text-align: left;
  vertical-align: top;
}

.test-cases-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #333;
  position: sticky;
  top: 0;
  z-index: 1;
}

.test-cases-table td {
  line-height: 1.5;
}

/* Column specific styles */
.test-cases-table th:nth-child(1),
.test-cases-table td:nth-child(1) { /* ID */
  width: 80px;
  white-space: nowrap;
}

.test-cases-table th:nth-child(2),
.test-cases-table td:nth-child(2) { /* Name */
  width: 150px;
}

.test-cases-table th:nth-child(3),
.test-cases-table td:nth-child(3) { /* Description */
  width: 200px;
}

.test-cases-table ul {
  margin: 0;
  padding-left: 20px;
  list-style-type: disc;
}

.test-cases-table li {
  margin: 8px 0;
  line-height: 1.4;
}

/* Raw Response Styles */
.raw-response {
  margin-top: 30px;
  padding: 15px;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 4px;
}

.raw-response h3 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
}

.raw-response pre {
  margin: 0;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 4px;
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow-x: auto;
}

/* Responsive Design */
@media (max-width: 768px) {
  .scenario-input {
    padding: 10px;
  }

  .results-container {
    padding: 10px;
  }

  .test-cases-container {
    margin-top: 15px;
  }

  .test-cases-table {
    display: block;
    overflow-x: auto;
  }

  .test-cases-table th,
  .test-cases-table td {
    padding: 8px;
    font-size: 13px;
  }

  .timer-container {
    flex-direction: column;
    align-items: center;
    gap: 10px;
  }
}

/* Dark Mode Support */
@media (prefers-color-scheme: dark) {
  .scenario-input {
    background-color: #1a1a1a;
    color: #e0e0e0;
  }

  .scenario-textarea {
    background-color: #2d2d2d;
    border-color: #404040;
    color: #e0e0e0;
  }

  .results-container {
    background: #2d2d2d;
  }

  .test-cases-table {
    background: #363636;
    border-color: #404040;
  }

  .test-cases-table th {
    background: #2d2d2d;
    color: #e0e0e0;
    border-color: #404040;
  }

  .test-cases-table td {
    border-color: #404040;
    color: #e0e0e0;
  }

  .test-cases-table tr:hover {
    background-color: #404040;
  }

  .raw-response {
    background: #363636;
    border-color: #404040;
  }

  .raw-response h3 {
    color: #e0e0e0;
  }

  .raw-response pre {
    background: #2d2d2d;
    color: #e0e0e0;
  }

  .loading-container {
    background-color: #2d2d2d;
  }

  .loading-text,
  .elapsed-time {
    color: #e0e0e0;
  }

  .progress-bar {
    background-color: #404040;
  }
}

/* Print Styles */
@media print {
  .scenario-textarea,
  .generate-button,
  .loading-container {
    display: none;
  }

  .results-container {
    margin-top: 0;
    padding: 0;
    box-shadow: none;
  }

  .test-cases-table {
    border: 1px solid #000;
    box-shadow: none;
  }

  .test-cases-table th,
  .test-cases-table td {
    border: 1px solid #000;
  }

  .raw-response {
    display: none;
  }
}

/* Scrollbar Styling */
.raw-response pre::-webkit-scrollbar,
.test-cases-container::-webkit-scrollbar {
  height: 8px;
  width: 8px;
}

.raw-response pre::-webkit-scrollbar-track,
.test-cases-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.raw-response pre::-webkit-scrollbar-thumb,
.test-cases-container::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.raw-response pre::-webkit-scrollbar-thumb:hover,
.test-cases-container::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* Firefox Scrollbar */
.raw-response pre,
.test-cases-container {
  scrollbar-width: thin;
  scrollbar-color: #888 #f1f1f1;
}

/* Animations */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.results-container {
  animation: fadeIn 0.3s ease-in-out;
}

/* Accessibility */
.test-cases-table th[scope="col"] {
  font-weight: bold;
}

/* Focus styles */
.scenario-textarea:focus,
.generate-button:focus {
  outline: 2px solid #4CAF50;
  outline-offset: 2px;
}

/* High contrast mode support */
@media screen and (-ms-high-contrast: active) {
  .generate-button {
    border: 2px solid currentColor;
  }
}

</style>
