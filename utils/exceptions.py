"""Exceptions for the retail platform."""


class InventoryException(Exception):
    """Base exception for inventory operations."""
    pass


class InsufficientStockException(InventoryException):
    """Raised when insufficient stock is available."""
    pass


class InvalidTransactionException(InventoryException):
    """Raised when transaction parameters are invalid."""
    pass


class ForecastingException(Exception):
    """Base exception for forecasting operations."""
    pass


class ModelNotTrainedException(ForecastingException):
    """Raised when trying to use untrained model."""
    pass


class DataIngestionException(Exception):
    """Base exception for data ingestion."""
    pass


class ValidationException(DataIngestionException):
    """Raised when data validation fails."""
    pass


class TransformationException(DataIngestionException):
    """Raised when data transformation fails."""
    pass


class ComputerVisionException(Exception):
    """Base exception for CV operations."""
    pass


class ModelInferenceException(ComputerVisionException):
    """Raised when model inference fails."""
    pass
