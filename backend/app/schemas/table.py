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
    total: int = Field(..., description="Total number of rows in table (-1 if unknown)", ge=-1)
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


class ColumnInfo(BaseModel):
    """Information about a table column."""

    name: str = Field(..., description="Column name")
    type: str = Field(..., description="Column data type")
    required: bool = Field(False, description="Whether the column is required")


class TableSchemaResponse(BaseModel):
    """Response for getting table schema/columns."""

    table_name: str = Field(..., description="Name of the table")
    columns: List[ColumnInfo] = Field(..., description="List of column definitions")


class BatchCreateRequest(BaseModel):
    """Request body for batch creating table rows."""

    rows: List[Dict[str, Any]] = Field(..., description="List of row data to create")

    class Config:
        json_schema_extra = {
            "example": {
                "rows": [
                    {"Name": "Item 1", "Value": 100},
                    {"Name": "Item 2", "Value": 200},
                ]
            }
        }


class RowResult(BaseModel):
    """Result of a single row operation in batch."""

    index: int = Field(..., description="Index of the row in the request")
    success: bool = Field(..., description="Whether the operation succeeded")
    data: Optional[Dict[str, Any]] = Field(None, description="Created row data if successful")
    error: Optional[str] = Field(None, description="Error message if failed")


class BatchCreateResponse(BaseModel):
    """Response for batch create operations."""

    total: int = Field(..., description="Total number of rows in request")
    succeeded: int = Field(..., description="Number of rows successfully created")
    failed: int = Field(..., description="Number of rows that failed")
    results: List[RowResult] = Field(..., description="Individual results for each row")


class ReplaceAllRequest(BaseModel):
    """Request body for replacing all table rows."""

    rows: List[Dict[str, Any]] = Field(..., description="List of row data to replace table with")

    class Config:
        json_schema_extra = {
            "example": {
                "rows": [
                    {"Name": "Item 1", "Value": 100},
                    {"Name": "Item 2", "Value": 200},
                ]
            }
        }


class ReplaceAllResponse(BaseModel):
    """Response for replace all operation."""

    success: bool = Field(..., description="Whether the operation succeeded")
    rows_replaced: int = Field(..., description="Number of rows in the new table")
    error: Optional[str] = Field(None, description="Error message if failed")


class TableCountResponse(BaseModel):
    """Response for getting table row count."""

    table_name: str = Field(..., description="Name of the table")
    row_count: int = Field(..., description="Number of rows in the table")
