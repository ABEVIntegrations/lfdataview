"""Pydantic schemas for table operations."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TableInfo(BaseModel):
    """Information about a single table."""

    name: str = Field(..., description="Table name")
    displayName: Optional[str] = Field(None, description="Display name of the table")
    description: Optional[str] = Field(None, description="Table description")


class TableListResponse(BaseModel):
    """Response for listing tables."""

    tables: List[TableInfo] = Field(..., description="List of available tables")


class TableRowsResponse(BaseModel):
    """Response for getting table rows with pagination."""

    rows: List[Dict[str, Any]] = Field(..., description="List of row data")
    total: int = Field(..., description="Total number of rows in table", ge=0)
    limit: int = Field(..., description="Number of rows per page", ge=1, le=1000)
    offset: int = Field(..., description="Number of rows skipped", ge=0)


class CreateRowRequest(BaseModel):
    """Request body for creating a table row."""

    data: Dict[str, Any] = Field(..., description="Row data as key-value pairs")

    class Config:
        json_schema_extra = {
            "example": {
                "data": {
                    "CustomerID": "001",
                    "Name": "Acme Corp",
                    "Email": "contact@acme.com",
                }
            }
        }


class UpdateRowRequest(BaseModel):
    """Request body for updating a table row."""

    data: Dict[str, Any] = Field(..., description="Partial row data to update")

    class Config:
        json_schema_extra = {
            "example": {
                "data": {
                    "Email": "new-email@acme.com",
                }
            }
        }


class RowResponse(BaseModel):
    """Response for single row operations (create, update, get)."""

    data: Dict[str, Any] = Field(..., description="Row data")

    class Config:
        json_schema_extra = {
            "example": {
                "data": {
                    "CustomerID": "001",
                    "Name": "Acme Corp",
                    "Email": "contact@acme.com",
                }
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Machine-readable error code")

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Table 'Customers' not found",
                "error_code": "TABLE_NOT_FOUND",
            }
        }
