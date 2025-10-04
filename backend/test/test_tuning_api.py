"""
API Integration Tests for Phase 4, Sub-phase 4.3
Tests the Tuning Loop endpoints (Automated Tuning Loop)
"""

import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import status
from unittest.mock import AsyncMock, patch, MagicMock
from bson import ObjectId

from main import app
from models.tuning_loop import TuningStatus


# Test data fixtures
@pytest.fixture
def valid_prompt_id():
    """Valid prompt ID for testing"""
    return str(ObjectId())


@pytest.fixture
def valid_scenario_ids():
    """Valid scenario IDs for testing"""
    return [str(ObjectId()), str(ObjectId()), str(ObjectId())]


@pytest.fixture
def tuning_loop_request(valid_prompt_id, valid_scenario_ids):
    """Valid tuning loop creation request"""
    return {
        "initial_prompt_id": valid_prompt_id,
        "target_score": 85.0,
        "max_iterations": 3,
        "scenarios": [
            {"scenario_id": valid_scenario_ids[0], "weight": 5},
            {"scenario_id": valid_scenario_ids[1], "weight": 3},
            {"scenario_id": valid_scenario_ids[2], "weight": 4}
        ]
    }


@pytest.fixture
def mock_tuning_loop_document(valid_prompt_id, valid_scenario_ids):
    """Mock tuning loop document from database"""
    tuning_loop_id = str(ObjectId())
    return {
        "_id": tuning_loop_id,
        "initial_prompt_id": valid_prompt_id,
        "status": TuningStatus.PENDING.value,
        "config": {
            "target_score": 85.0,
            "max_iterations": 3,
            "scenario_weights": [
                {"scenario_id": valid_scenario_ids[0], "weight": 5},
                {"scenario_id": valid_scenario_ids[1], "weight": 3},
                {"scenario_id": valid_scenario_ids[2], "weight": 4}
            ]
        },
        "iterations": [],
        "final_prompt_id": None,
        "created_at": "2025-10-04T10:00:00",
        "updated_at": "2025-10-04T10:00:00"
    }


class TestPostTuningEndpoint:
    """Tests for POST /api/tuning endpoint"""
    
    @pytest.mark.asyncio
    async def test_create_tuning_loop_success(
        self, 
        tuning_loop_request,
        valid_prompt_id,
        valid_scenario_ids
    ):
        """Test successful tuning loop creation"""
        
        # Mock database functions AND background task
        with patch("api.tuning.database.get_prompt_by_id") as mock_get_prompt, \
             patch("api.tuning.database.get_scenario_by_id") as mock_get_scenario, \
             patch("api.tuning.database.insert_tuning_loop") as mock_insert, \
             patch("api.tuning.perform_tuning_loop") as mock_bg_task:
            
            # Setup mocks
            mock_get_prompt.return_value = {
                "_id": valid_prompt_id,
                "name": "Test Prompt v1.0",
                "prompt_text": "Test prompt"
            }
            
            mock_get_scenario.return_value = {
                "_id": valid_scenario_ids[0],
                "title": "Test Scenario"
            }
            
            tuning_loop_id = str(ObjectId())
            mock_insert.return_value = tuning_loop_id
            
            # Mock background task to do nothing
            mock_bg_task.return_value = None
            
            # Make request
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.post("/tuning", json=tuning_loop_request)
            
            # Assert response
            assert response.status_code == status.HTTP_202_ACCEPTED
            data = response.json()
            assert data["tuning_loop_id"] == tuning_loop_id
            assert data["status"] == TuningStatus.PENDING.value
            assert data["current_iteration"] is None
            assert data["latest_score"] is None
            
            # Verify database calls
            mock_get_prompt.assert_awaited_once_with(valid_prompt_id)
            assert mock_get_scenario.await_count == 3  # Called for each scenario
            mock_insert.assert_awaited_once()
    
    @pytest.mark.asyncio
    async def test_create_tuning_loop_prompt_not_found(
        self,
        tuning_loop_request,
        valid_prompt_id
    ):
        """Test tuning loop creation with non-existent prompt"""
        
        with patch("api.tuning.database.get_prompt_by_id") as mock_get_prompt:
            # Prompt does not exist
            mock_get_prompt.return_value = None
            
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post("/tuning", json=tuning_loop_request)
            
            # Assert 404 error
            assert response.status_code == status.HTTP_404_NOT_FOUND
            data = response.json()
            assert "not found" in data["detail"].lower()
            assert valid_prompt_id in data["detail"]
    
    @pytest.mark.asyncio
    async def test_create_tuning_loop_scenario_not_found(
        self,
        tuning_loop_request,
        valid_prompt_id,
        valid_scenario_ids
    ):
        """Test tuning loop creation with non-existent scenario"""
        
        with patch("api.tuning.database.get_prompt_by_id") as mock_get_prompt, \
             patch("api.tuning.database.get_scenario_by_id") as mock_get_scenario:
            
            # Prompt exists
            mock_get_prompt.return_value = {
                "_id": valid_prompt_id,
                "name": "Test Prompt"
            }
            
            # First scenario does not exist
            mock_get_scenario.return_value = None
            
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post("/tuning", json=tuning_loop_request)
            
            # Assert 404 error
            assert response.status_code == status.HTTP_404_NOT_FOUND
            data = response.json()
            assert "scenario" in data["detail"].lower()
            assert "not found" in data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_create_tuning_loop_invalid_target_score(
        self,
        tuning_loop_request
    ):
        """Test validation for target_score out of range"""
        
        # Target score too high
        invalid_request = tuning_loop_request.copy()
        invalid_request["target_score"] = 150.0
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/tuning", json=invalid_request)
        
        # Assert validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_create_tuning_loop_invalid_max_iterations(
        self,
        tuning_loop_request
    ):
        """Test validation for max_iterations out of range"""
        
        # Max iterations too high
        invalid_request = tuning_loop_request.copy()
        invalid_request["max_iterations"] = 15
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/tuning", json=invalid_request)
        
        # Assert validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_create_tuning_loop_invalid_weight(
        self,
        tuning_loop_request
    ):
        """Test validation for scenario weight out of range"""
        
        # Weight too high
        invalid_request = tuning_loop_request.copy()
        invalid_request["scenarios"][0]["weight"] = 10
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/tuning", json=invalid_request)
        
        # Assert validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_create_tuning_loop_missing_required_fields(self):
        """Test validation for missing required fields"""
        
        # Missing initial_prompt_id
        invalid_request = {
            "target_score": 85.0,
            "max_iterations": 3,
            "scenarios": []
        }
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/tuning", json=invalid_request)
        
        # Assert validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_create_tuning_loop_empty_scenarios(
        self,
        tuning_loop_request
    ):
        """Test validation for empty scenarios list"""
        
        invalid_request = tuning_loop_request.copy()
        invalid_request["scenarios"] = []
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/tuning", json=invalid_request)
        
        # Assert validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestGetTuningLoopEndpoint:
    """Tests for GET /api/tuning/{tuning_loop_id} endpoint"""
    
    @pytest.mark.asyncio
    async def test_get_tuning_loop_pending_status(
        self,
        mock_tuning_loop_document
    ):
        """Test retrieving a PENDING tuning loop"""
        
        tuning_loop_id = mock_tuning_loop_document["_id"]
        
        with patch("api.tuning.database.get_tuning_loop_by_id") as mock_get:
            mock_get.return_value = mock_tuning_loop_document
            
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(f"/tuning/{tuning_loop_id}")
            
            # Assert response
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["_id"] == tuning_loop_id
            assert data["status"] == TuningStatus.PENDING.value
            assert data["config"]["target_score"] == 85.0
            assert data["config"]["max_iterations"] == 3
            assert len(data["iterations"]) == 0
            assert data["final_prompt_id"] is None
            
            mock_get.assert_awaited_once_with(tuning_loop_id)
    
    @pytest.mark.asyncio
    async def test_get_tuning_loop_running_status(
        self,
        mock_tuning_loop_document,
        valid_prompt_id
    ):
        """Test retrieving a RUNNING tuning loop with iterations"""
        
        tuning_loop_id = mock_tuning_loop_document["_id"]
        
        # Modify mock to show RUNNING status with iterations
        mock_tuning_loop_document["status"] = TuningStatus.RUNNING.value
        mock_tuning_loop_document["iterations"] = [
            {
                "iteration_number": 1,
                "prompt_id": valid_prompt_id,
                "evaluation_ids": [str(ObjectId()), str(ObjectId())],
                "weighted_score": 75.5,
                "started_at": "2025-10-04T10:01:00",
                "completed_at": "2025-10-04T10:05:00"
            }
        ]
        
        with patch("api.tuning.database.get_tuning_loop_by_id") as mock_get:
            mock_get.return_value = mock_tuning_loop_document
            
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(f"/tuning/{tuning_loop_id}")
            
            # Assert response
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["status"] == TuningStatus.RUNNING.value
            assert len(data["iterations"]) == 1
            assert data["iterations"][0]["iteration_number"] == 1
            assert data["iterations"][0]["weighted_score"] == 75.5
    
    @pytest.mark.asyncio
    async def test_get_tuning_loop_completed_status(
        self,
        mock_tuning_loop_document,
        valid_prompt_id
    ):
        """Test retrieving a COMPLETED tuning loop"""
        
        tuning_loop_id = mock_tuning_loop_document["_id"]
        final_prompt_id = str(ObjectId())
        
        # Modify mock to show COMPLETED status
        mock_tuning_loop_document["status"] = TuningStatus.COMPLETED.value
        mock_tuning_loop_document["final_prompt_id"] = final_prompt_id
        mock_tuning_loop_document["iterations"] = [
            {
                "iteration_number": 1,
                "prompt_id": valid_prompt_id,
                "evaluation_ids": [str(ObjectId())],
                "weighted_score": 75.5,
                "started_at": "2025-10-04T10:01:00",
                "completed_at": "2025-10-04T10:05:00"
            },
            {
                "iteration_number": 2,
                "prompt_id": final_prompt_id,
                "evaluation_ids": [str(ObjectId())],
                "weighted_score": 87.3,
                "started_at": "2025-10-04T10:06:00",
                "completed_at": "2025-10-04T10:10:00"
            }
        ]
        
        with patch("api.tuning.database.get_tuning_loop_by_id") as mock_get:
            mock_get.return_value = mock_tuning_loop_document
            
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(f"/tuning/{tuning_loop_id}")
            
            # Assert response
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["status"] == TuningStatus.COMPLETED.value
            assert data["final_prompt_id"] == final_prompt_id
            assert len(data["iterations"]) == 2
            assert data["iterations"][1]["weighted_score"] > data["iterations"][0]["weighted_score"]
    
    @pytest.mark.asyncio
    async def test_get_tuning_loop_not_found(self):
        """Test retrieving non-existent tuning loop"""
        
        fake_id = str(ObjectId())
        
        with patch("api.tuning.database.get_tuning_loop_by_id") as mock_get:
            mock_get.return_value = None
            
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(f"/tuning/{fake_id}")
            
            # Assert 404 error
            assert response.status_code == status.HTTP_404_NOT_FOUND
            data = response.json()
            assert "not found" in data["detail"].lower()
            assert fake_id in data["detail"]
    
    @pytest.mark.asyncio
    async def test_get_tuning_loop_invalid_id_format(self):
        """Test retrieving with invalid ObjectId format"""
        
        invalid_id = "not-a-valid-objectid"
        
        with patch("api.tuning.database.get_tuning_loop_by_id") as mock_get:
            # Simulate the error that would occur with invalid ObjectId
            mock_get.side_effect = Exception("Invalid ObjectId")
            
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(f"/tuning/{invalid_id}")
            
            # Assert 500 error (handled by exception handler)
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


class TestGetAllTuningLoopsEndpoint:
    """Tests for GET /api/tuning endpoint"""
    
    @pytest.mark.asyncio
    async def test_get_all_tuning_loops_success(
        self,
        mock_tuning_loop_document
    ):
        """Test retrieving all tuning loops"""
        
        # Create multiple mock documents
        mock_loops = [
            mock_tuning_loop_document,
            {
                **mock_tuning_loop_document,
                "_id": str(ObjectId()),
                "status": TuningStatus.COMPLETED.value
            },
            {
                **mock_tuning_loop_document,
                "_id": str(ObjectId()),
                "status": TuningStatus.FAILED.value
            }
        ]
        
        with patch("api.tuning.database.get_all_tuning_loops") as mock_get_all:
            mock_get_all.return_value = mock_loops
            
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/tuning")
            
            # Assert response
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 3
            
            # Check statuses
            statuses = [loop["status"] for loop in data]
            assert TuningStatus.PENDING.value in statuses
            assert TuningStatus.COMPLETED.value in statuses
            assert TuningStatus.FAILED.value in statuses
            
            mock_get_all.assert_awaited_once()
    
    @pytest.mark.asyncio
    async def test_get_all_tuning_loops_empty(self):
        """Test retrieving all tuning loops when none exist"""
        
        with patch("api.tuning.database.get_all_tuning_loops") as mock_get_all:
            mock_get_all.return_value = []
            
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/tuning")
            
            # Assert response
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 0


class TestTuningLoopIntegration:
    """Integration tests for the full tuning loop workflow"""
    
    @pytest.mark.asyncio
    async def test_full_workflow_create_and_poll(
        self,
        tuning_loop_request,
        valid_prompt_id,
        valid_scenario_ids
    ):
        """Test creating a tuning loop and polling for status"""
        
        tuning_loop_id = str(ObjectId())
        
        with patch("api.tuning.database.get_prompt_by_id") as mock_get_prompt, \
             patch("api.tuning.database.get_scenario_by_id") as mock_get_scenario, \
             patch("api.tuning.database.insert_tuning_loop") as mock_insert, \
             patch("api.tuning.database.get_tuning_loop_by_id") as mock_get_loop, \
             patch("api.tuning.perform_tuning_loop") as mock_bg_task:
            
            # Setup mocks for creation
            mock_get_prompt.return_value = {"_id": valid_prompt_id, "name": "Test"}
            mock_get_scenario.return_value = {"_id": valid_scenario_ids[0], "title": "Test"}
            mock_insert.return_value = tuning_loop_id
            
            # Mock background task to do nothing
            mock_bg_task.return_value = None
            
            # Create tuning loop
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                create_response = await client.post("/tuning", json=tuning_loop_request)
            
            assert create_response.status_code == status.HTTP_202_ACCEPTED
            response_data = create_response.json()
            returned_id = response_data["tuning_loop_id"]
            
            # Setup mock for polling
            mock_get_loop.return_value = {
                "_id": returned_id,
                "initial_prompt_id": valid_prompt_id,
                "status": TuningStatus.RUNNING.value,
                "config": {
                    "target_score": 85.0,
                    "max_iterations": 3,
                    "scenario_weights": []
                },
                "iterations": [],
                "final_prompt_id": None,
                "created_at": "2025-10-04T10:00:00",
                "updated_at": "2025-10-04T10:01:00"
            }
            
            # Poll for status
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                poll_response = await client.get(f"/tuning/{returned_id}")
            
            assert poll_response.status_code == status.HTTP_200_OK
            poll_data = poll_response.json()
            assert poll_data["_id"] == returned_id
            assert poll_data["status"] == TuningStatus.RUNNING.value
