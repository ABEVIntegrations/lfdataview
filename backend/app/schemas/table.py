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


class RowResponse(BaseModel):
    """Response for single row operations (get)."""

    data: Dict[str, Any] = Field(..., description="Row data")


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


class TableCountResponse(BaseModel):
    """Response for getting table row count."""

    table_name: str = Field(..., description="Name of the table")
    row_count: int = Field(..., description="Number of rows in the table")
