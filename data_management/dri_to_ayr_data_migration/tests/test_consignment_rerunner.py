import pytest

from data_management.dri_to_ayr_data_migration.consignment_rerunner.handler import (
    lambda_handler,
)


class TestConsignmentRerunner:
    def test_handler_does_as_expected(self):
        # Arrange
        event = {
            "runId": "test-run-id",
            "series": "test-series",
            "consignmentReference": "test-consignment-reference",
        }

        context = {}

        # Act
        result = lambda_handler(event, context)

        # Assert
        assert result == {
            "consignmentReference": "test-consignment-reference",
            "filesQueued": 0,
            "deletedStagingObjects": [],
            "deletedOutputObjects": [],
        }

    def test_handler_raises_for_missing_run_id(self):
        # Arrange
        event = {
            "series": "test-series",
            "consignmentReference": "test-consignment-reference",
        }

        context = {}

        # Act & Assert
        with pytest.raises(ValueError) as e:
            lambda_handler(event, context)
        assert str(e.value) == "Missing required field: runId"

    def test_handler_raises_for_missing_series(self):
        # Arrange
        event = {
            "runId": "test-run-id",
            "consignmentReference": "test-consignment-reference",
        }

        context = {}

        # Act & Assert
        with pytest.raises(ValueError) as e:
            lambda_handler(event, context)
        assert str(e.value) == "Missing required field: series"

    def test_handler_raises_for_missing_consignment_reference(self):
        # Arrange
        event = {
            "runId": "test-run-id",
            "series": "test-series",
        }

        context = {}

        # Act & Assert
        with pytest.raises(ValueError) as e:
            lambda_handler(event, context)
        assert str(e.value) == "Missing required field: consignmentReference"

    def test_handler_raises_for_all_missing_fields(self):
        # Arrange
        event = {}

        context = {}

        # Act & Assert
        with pytest.raises(ValueError) as e:
            lambda_handler(event, context)
        assert str(e.value) == "Missing required field: runId"
