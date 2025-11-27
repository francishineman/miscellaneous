from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
import uuid

# --- Pydantic Models ---

# Represents a single test result within a suite
class TestResult(BaseModel):
    """Schema for a single test run result."""
    test_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the test run.")
    name: str = Field(..., description="Name of the test (e.g., 'Login with valid credentials').")
    status: str = Field(..., description="The outcome of the test (e.g., 'PASS', 'FAIL', 'SKIP').")
    duration_ms: float = Field(..., description="Duration of the test in milliseconds.")
    error_message: Optional[str] = Field(None, description="Detailed failure message if status is 'FAIL'.")

# Represents a complete test suite run
class TestSuite(BaseModel):
    """Schema for a complete test suite run."""
    suite_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the test suite run.")
    environment: str = Field(..., description="The environment the tests were run on (e.g., 'staging', 'production', 'local').")
    start_time: datetime = Field(default_factory=datetime.now, description="Timestamp when the suite started.")
    end_time: datetime = Field(..., description="Timestamp when the suite finished.")
    total_tests: int = Field(..., description="Total number of tests executed.")
    pass_count: int = Field(..., description="Number of passing tests.")
    fail_count: int = Field(..., description="Number of failing tests.")
    results: List[TestResult] = Field(..., description="List of individual test results.")

# Model for updating a suite (if needed, e.g., to add a note)
class TestSuiteUpdate(BaseModel):
    """Schema for updating a test suite's metadata."""
    notes: Optional[str] = Field(None, description="Optional notes or comments for the suite run.")
