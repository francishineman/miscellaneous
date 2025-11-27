# main.py
from fastapi import FastAPI, HTTPException, status
from typing import Dict, List
import json

# Import Pydantic models from the previous section (assuming they are in the same file or module)
# from .models import TestSuite, TestSuiteUpdate

# --- In-Memory Database (for demonstration) ---
# Stores TestSuite objects indexed by their suite_id
testbed_db: Dict[str, TestSuite] = {}

# --- FastAPI Initialization ---
app = FastAPI(
    title="QA Testbed API",
    description="REST API for managing and querying QA Test Suite Runs and Results.",
    version="1.0.0"
)

# --- Endpoints ---

@app.get("/", status_code=status.HTTP_200_OK, tags=["Root"])
async def root():
    """Simple root endpoint to confirm the API is running."""
    return {"message": "QA Testbed API is running!"}

## 📝 CREATE Endpoint (Upload a new test suite)
@app.post("/suites", response_model=TestSuite, status_code=status.HTTP_201_CREATED, tags=["Test Suites"])
async def create_test_suite(suite: TestSuite):
    """Upload a new complete test suite run result."""
    if suite.suite_id in testbed_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Suite with ID {suite.suite_id} already exists."
        )
    testbed_db[suite.suite_id] = suite
    return suite

## 🔍 READ Endpoints
@app.get("/suites", response_model=List[TestSuite], tags=["Test Suites"])
async def get_all_suites():
    """Retrieve a list of all recorded test suite runs."""
    return list(testbed_db.values())

@app.get("/suites/{suite_id}", response_model=TestSuite, tags=["Test Suites"])
async def get_suite_by_id(suite_id: str):
    """Retrieve a specific test suite run by its ID."""
    if suite_id not in testbed_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Suite with ID {suite_id} not found."
        )
    return testbed_db[suite_id]

## 🔄 UPDATE Endpoint
@app.patch("/suites/{suite_id}", response_model=TestSuite, tags=["Test Suites"])
async def update_suite_notes(suite_id: str, update_data: TestSuiteUpdate):
    """Update metadata (e.g., notes) for an existing test suite run."""
    if suite_id not in testbed_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Suite with ID {suite_id} not found."
        )

    existing_suite = testbed_db[suite_id]
    
    # Update fields that are provided in the update_data model
    update_data_dict = update_data.model_dump(exclude_unset=True)
    
    # Create a new suite instance with updated values
    updated_suite_data = existing_suite.model_copy(update=update_data_dict)
    testbed_db[suite_id] = updated_suite_data
    
    return updated_suite_data

## 🗑️ DELETE Endpoint
@app.delete("/suites/{suite_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Test Suites"])
async def delete_suite(suite_id: str):
    """Delete a specific test suite run by its ID."""
    if suite_id not in testbed_db:
        # FastAPI's HTTPException still works well here even if we return 204
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Suite with ID {suite_id} not found."
        )
    del testbed_db[suite_id]
    return
