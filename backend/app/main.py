from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .schemas import ScenarioRequest
from .config import settings
import httpx
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        logger.info(f"Received request: {request.scenario}")
        
        if not request.scenario.strip():
            raise HTTPException(status_code=400, detail="Scenario cannot be empty")
        
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            logger.info(f"Sending request to Colab: {settings.COLAB_URL}")
            
            try:
                response = await client.post(
                    f"{settings.COLAB_URL}/generate",
                    json={"scenario": request.scenario},
                    timeout=TIMEOUT_SECONDS
                )
                
                logger.info(f"Response status: {response.status_code}")
                logger.info(f"Response content: {response.text[:200]}...")  # Log first 200 chars
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if not isinstance(data, dict) or 'test_cases' not in data:
                            raise ValueError("Invalid response format from Colab")
                        return data
                    except ValueError as e:
                        logger.error(f"JSON parsing error: {str(e)}")
                        logger.error(f"Raw response: {response.text}")
                        raise HTTPException(
                            status_code=500,
                            detail=f"Invalid response format from Colab: {str(e)}"
                        )
                else:
                    logger.error(f"Error response from Colab: {response.text}")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Colab server error: {response.text}"
                    )
                    
            except httpx.TimeoutException as e:
                logger.error(f"Timeout error: {str(e)}")
                raise HTTPException(
                    status_code=504,
                    detail="The request to the model timed out. Please try again or simplify your scenario."
                )
            except httpx.ConnectError as e:
                logger.error(f"Connection error: {str(e)}")
                raise HTTPException(
                    status_code=503,
                    detail="Could not connect to the model server. Please ensure the Colab notebook is running and try again."
                )
            except httpx.RequestError as e:
                logger.error(f"Request error: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Error making request to Colab: {str(e)}"
                )
                
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error in generate_test_cases_endpoint")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )
