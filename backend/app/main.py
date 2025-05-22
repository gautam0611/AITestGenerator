from fastapi import FastAPI, HTTPException
from schemas import ScenarioRequest

app = FastAPI()


@app.post("/generate-test-cases/")
async def generate_test_cases_endpoint(request: ScenarioRequest):
    try:
        test_cases = generate_test_cases(request.scenario)
        return {"test_cases": test_cases}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
