"""API endpoints for table CRUD operations."""

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, status
import httpx

from app.dependencies import get_user_access_token
from app.schemas.table import (
    TableListResponse,
    TableRowsResponse,
    CreateRowRequest,
    UpdateRowRequest,
    RowResponse,
    ErrorResponse,
    TableInfo,
    TableSchemaResponse,
    ColumnInfo,
    BatchCreateRequest,
    BatchCreateResponse,
    RowResult,
)
from app.utils.laserfiche import laserfiche_client

router = APIRouter()


@router.get(
    "/debug",
    summary="Debug table API",
    description="Debug endpoint to see raw Laserfiche API response and access token",
)
async def debug_tables(
    access_token: str = Depends(get_user_access_token),
):
    """Debug endpoint to test Laserfiche Table API.

    Returns raw response from Laserfiche and the access token for Postman testing.
    """
    import logging
    logger = logging.getLogger(__name__)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }

    url = "https://api.laserfiche.com/odata4/table"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

            logger.info(f"Debug - URL: {url}")
            logger.info(f"Debug - Status: {response.status_code}")
            logger.info(f"Debug - Response: {response.text[:500]}")

            return {
                "url": url,
                "status_code": response.status_code,
                "response_headers": dict(response.headers),
                "response_body": response.json() if response.status_code == 200 else response.text,
                "access_token_for_postman": access_token,  # Use this in Postman!
            }
    except Exception as e:
        return {
            "url": url,
            "error": str(e),
            "access_token_for_postman": access_token,
        }


def handle_laserfiche_error(e: httpx.HTTPStatusError) -> HTTPException:
    """Transform Laserfiche API errors to FastAPI HTTPExceptions.

    Args:
        e: HTTP error from Laserfiche API

    Returns:
        HTTPException with appropriate status code and message
    """
    status_code = e.response.status_code

    # Try to extract error message from response
    try:
        error_data = e.response.json()
        detail = error_data.get("error", {}).get("message", str(e))
    except Exception:
        detail = str(e)

    # Map common error codes
    error_messages = {
        400: f"Bad request: {detail}",
        401: "Authentication failed. Please log in again.",
        403: "Insufficient permissions. Check your OAuth scopes.",
        404: f"Resource not found: {detail}",
        409: f"Conflict: {detail}",
        500: "Laserfiche API error. Please try again later.",
    }

    message = error_messages.get(status_code, detail)

    raise HTTPException(status_code=status_code, detail=message)


@router.get(
    "",
    response_model=TableListResponse,
    summary="List all tables",
    description="Get a list of all accessible Laserfiche lookup tables",
)
async def list_tables(
    access_token: str = Depends(get_user_access_token),
) -> TableListResponse:
    """List all accessible tables.

    Requires authentication via session cookie.

    Returns:
        List of table information
    """
    try:
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Attempting to list tables with token: {access_token[:20]}...")

        tables_data = await laserfiche_client.list_tables(access_token)
        logger.info(f"Received {len(tables_data)} tables from Laserfiche")

        # Transform to our schema
        tables = [
            TableInfo(
                name=table.get("name", ""),
                displayName=table.get("displayName"),
                description=table.get("description"),
            )
            for table in tables_data
        ]

        return TableListResponse(tables=tables)

    except httpx.HTTPStatusError as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Laserfiche API error: {e.response.status_code} - {e.response.text}")
        handle_laserfiche_error(e)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Unexpected error listing tables: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tables: {str(e)}",
        )


@router.get(
    "/{table_name}",
    response_model=TableRowsResponse,
    summary="Get table rows",
    description="Get rows from a table with pagination support",
)
async def get_table_rows(
    table_name: str,
    limit: int = Query(50, ge=1, le=1000, description="Number of rows per page"),
    offset: int = Query(0, ge=0, description="Number of rows to skip"),
    access_token: str = Depends(get_user_access_token),
) -> TableRowsResponse:
    """Get rows from a table with pagination.

    Args:
        table_name: Name of the table
        limit: Number of rows per page (max: 1000)
        offset: Number of rows to skip
        access_token: User's access token (from dependency)

    Returns:
        Paginated rows with metadata
    """
    try:
        data = await laserfiche_client.get_table_rows(
            access_token=access_token,
            table_name=table_name,
            limit=limit,
            offset=offset,
        )

        return TableRowsResponse(**data)

    except httpx.HTTPStatusError as e:
        handle_laserfiche_error(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get table rows: {str(e)}",
        )


@router.get(
    "/{table_name}/schema",
    response_model=TableSchemaResponse,
    summary="Get table schema",
    description="Get the column definitions for a table",
)
async def get_table_schema(
    table_name: str,
    access_token: str = Depends(get_user_access_token),
) -> TableSchemaResponse:
    """Get table schema/column definitions.

    Args:
        table_name: Name of the table
        access_token: User's access token (from dependency)

    Returns:
        Table schema with column definitions
    """
    try:
        columns_data = await laserfiche_client.get_table_schema(
            access_token=access_token,
            table_name=table_name,
        )

        columns = [
            ColumnInfo(
                name=col["name"],
                type=col["type"],
                required=col.get("required", False),
            )
            for col in columns_data
        ]

        return TableSchemaResponse(table_name=table_name, columns=columns)

    except httpx.HTTPStatusError as e:
        handle_laserfiche_error(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get table schema: {str(e)}",
        )


@router.get(
    "/{table_name}/{key}",
    response_model=RowResponse,
    summary="Get single row",
    description="Get a single row from a table by its primary key",
)
async def get_table_row(
    table_name: str,
    key: str,
    access_token: str = Depends(get_user_access_token),
) -> RowResponse:
    """Get a single row by key.

    Args:
        table_name: Name of the table
        key: Primary key value
        access_token: User's access token (from dependency)

    Returns:
        Row data
    """
    try:
        data = await laserfiche_client.get_table_row(
            access_token=access_token,
            table_name=table_name,
            key=key,
        )

        return RowResponse(data=data)

    except httpx.HTTPStatusError as e:
        handle_laserfiche_error(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get table row: {str(e)}",
        )


@router.post(
    "/{table_name}",
    response_model=RowResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create row",
    description="Create a new row in a table",
)
async def create_table_row(
    table_name: str,
    request: CreateRowRequest,
    access_token: str = Depends(get_user_access_token),
) -> RowResponse:
    """Create a new row in a table.

    Args:
        table_name: Name of the table
        request: Row data to create
        access_token: User's access token (from dependency)

    Returns:
        Created row data
    """
    try:
        data = await laserfiche_client.create_table_row(
            access_token=access_token,
            table_name=table_name,
            data=request.data,
        )

        return RowResponse(data=data)

    except httpx.HTTPStatusError as e:
        handle_laserfiche_error(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create table row: {str(e)}",
        )


@router.post(
    "/{table_name}/batch",
    response_model=BatchCreateResponse,
    summary="Batch create rows",
    description="Create multiple rows in a table concurrently",
)
async def batch_create_rows(
    table_name: str,
    request: BatchCreateRequest,
    access_token: str = Depends(get_user_access_token),
) -> BatchCreateResponse:
    """Create multiple rows in a table.

    Args:
        table_name: Name of the table
        request: Batch of rows to create
        access_token: User's access token (from dependency)

    Returns:
        Results for each row (success/failure)
    """
    try:
        results = await laserfiche_client.batch_create_rows(
            access_token=access_token,
            table_name=table_name,
            rows=request.rows,
        )

        row_results = [
            RowResult(
                index=r["index"],
                success=r["success"],
                data=r["data"],
                error=r["error"],
            )
            for r in results
        ]

        succeeded = sum(1 for r in results if r["success"])
        failed = len(results) - succeeded

        return BatchCreateResponse(
            total=len(results),
            succeeded=succeeded,
            failed=failed,
            results=row_results,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to batch create rows: {str(e)}",
        )


@router.patch(
    "/{table_name}/{key}",
    response_model=RowResponse,
    summary="Update row",
    description="Update an existing row in a table (partial update)",
)
async def update_table_row(
    table_name: str,
    key: str,
    request: UpdateRowRequest,
    access_token: str = Depends(get_user_access_token),
) -> RowResponse:
    """Update an existing row in a table.

    Args:
        table_name: Name of the table
        key: Primary key value
        request: Partial row data to update
        access_token: User's access token (from dependency)

    Returns:
        Updated row data
    """
    try:
        data = await laserfiche_client.update_table_row(
            access_token=access_token,
            table_name=table_name,
            key=key,
            data=request.data,
        )

        return RowResponse(data=data)

    except httpx.HTTPStatusError as e:
        handle_laserfiche_error(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update table row: {str(e)}",
        )


@router.delete(
    "/{table_name}/{key}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete row",
    description="Delete a row from a table",
)
async def delete_table_row(
    table_name: str,
    key: str,
    access_token: str = Depends(get_user_access_token),
) -> None:
    """Delete a row from a table.

    Args:
        table_name: Name of the table
        key: Primary key value
        access_token: User's access token (from dependency)

    Returns:
        No content (204)
    """
    try:
        await laserfiche_client.delete_table_row(
            access_token=access_token,
            table_name=table_name,
            key=key,
        )

        return None

    except httpx.HTTPStatusError as e:
        handle_laserfiche_error(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete table row: {str(e)}",
        )
