from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .schemas import ScenarioRequest
from .config import settings
import httpx

app = FastAPI()

# Increase timeout duration significantly
TIMEOUT_SECONDS = 480  # 8 minutes

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/generate-test-cases")
async def generate_test_cases_endpoint(request: ScenarioRequest):
    try:
        print(f"Received request: {request.scenario}")  # Debug print
        
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            print(f"Sending request to Colab: {settings.COLAB_URL}")  # Debug print
            
            response = await client.post(
                f"{settings.COLAB_URL}/generate",
                json={"scenario": request.scenario},
                timeout=TIMEOUT_SECONDS
            )
            
            print(f"Response status: {response.status_code}")  # Debug print
            
            if response.status_code == 200:
                print(f"Successful response: {response.text[:100]}...")  # Debug print
                return response.json()
            else:
                print(f"Error response: {response.text}")  # Debug print
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Colab server error: {response.text}"
                )
                
    except httpx.TimeoutException as e:
        print(f"Timeout error: {str(e)}")  # Debug print
        raise HTTPException(
            status_code=504,
            detail="The request to the model timed out. This could be due to high server load or a complex request. Please try again or simplify your scenario."
        )
    except httpx.ConnectError as e:
        print(f"Connection error: {str(e)}")  # Debug print
        raise HTTPException(
            status_code=503,
            detail="Could not connect to the model server. Please ensure the Colab notebook is running and try again."
        )
    except Exception as e:
        print(f"Unexpected error: {str(e)}")  # Debug print
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )
