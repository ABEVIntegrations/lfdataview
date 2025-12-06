"""Laserfiche API client for OAuth and OData operations."""

import base64
import httpx
from typing import Dict, List, Optional
from app.config import settings


class LaserficheClient:
    """Client for interacting with Laserfiche OAuth and OData APIs."""

    OAUTH_BASE = "https://signin.laserfiche.com/oauth"
    API_BASE_V2 = "https://api.laserfiche.com/repository/v2"
    API_BASE = "https://api.laserfiche.com/odata4"  # Legacy, may not be used

    def get_authorization_url(self, state: str, scopes: List[str]) -> str:
        """Build OAuth authorization URL for user redirect.

        Args:
            state: Random state parameter for CSRF protection
            scopes: List of OAuth scopes to request

        Returns:
            Full authorization URL
        """
        scope_str = " ".join(scopes)
        params = {
            "client_id": settings.LASERFICHE_CLIENT_ID,
            "redirect_uri": settings.LASERFICHE_REDIRECT_URI,
            "response_type": "code",
            "scope": scope_str,
            "state": state,
        }

        # Build query string
        query = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.OAUTH_BASE}/Authorize?{query}"

    async def exchange_code_for_token(self, code: str) -> Dict:
        """Exchange authorization code for access and refresh tokens.

        Args:
            code: Authorization code from OAuth callback

        Returns:
            Token response dict with access_token, refresh_token, expires_in, etc.

        Raises:
            httpx.HTTPError: If token exchange fails
        """
        # Create Basic auth header with client_id:client_secret
        credentials = f"{settings.LASERFICHE_CLIENT_ID}:{settings.LASERFICHE_CLIENT_SECRET}"
        b64_credentials = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Authorization": f"Basic {b64_credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.LASERFICHE_REDIRECT_URI,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.OAUTH_BASE}/Token",
                headers=headers,
                data=data,
            )
            response.raise_for_status()
            return response.json()

    async def refresh_access_token(self, refresh_token: str) -> Dict:
        """Refresh an expired access token using refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            New token response dict

        Raises:
            httpx.HTTPError: If token refresh fails
        """
        credentials = f"{settings.LASERFICHE_CLIENT_ID}:{settings.LASERFICHE_CLIENT_SECRET}"
        b64_credentials = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Authorization": f"Basic {b64_credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.OAUTH_BASE}/Token",
                headers=headers,
                data=data,
            )
            response.raise_for_status()
            return response.json()

    async def get_user_info(self, access_token: str) -> Optional[Dict]:
        """Get user information from Laserfiche (if endpoint available).

        Args:
            access_token: Valid access token

        Returns:
            User info dict or None if not available

        Note:
            This is a placeholder. Update with actual Laserfiche user info endpoint.
        """
        # TODO: Check Laserfiche API docs for user info endpoint
        # For now, return None and we'll use placeholder data
        return None

    # ========== Repository API Methods ==========

    async def get_repositories(self, access_token: str) -> List[Dict]:
        """Get list of accessible repositories.

        Args:
            access_token: Valid access token

        Returns:
            List of repository dictionaries

        Raises:
            httpx.HTTPError: If request fails
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.API_BASE_V2}/Repositories",
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("value", [])

    # ========== Table API Methods ==========

    async def get_table_row_count(self, access_token: str, table_name: str) -> int:
        """Get the row count for a table using OData aggregate.

        Args:
            access_token: Valid access token with project scope
            table_name: Name of the table

        Returns:
            Number of rows in the table

        Raises:
            httpx.HTTPError: If request fails
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }

        params = {
            "$apply": "aggregate($count as rowCount)",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.API_BASE}/table/{table_name}",
                headers=headers,
                params=params,
            )
            response.raise_for_status()
            data = response.json()
            # Response format: { "rowCount": 123 }
            return data.get("rowCount", 0)

    async def list_tables(self, access_token: str) -> List[Dict]:
        """List all accessible tables using OData Table API.

        Args:
            access_token: Valid access token with project scope

        Returns:
            List of table dictionaries with name and metadata

        Raises:
            httpx.HTTPError: If request fails
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.API_BASE}/table",
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            # OData returns data in "value" array
            return data.get("value", [])

    def _build_odata_filter(
        self, filters: Dict[str, str], filter_mode: str = "and"
    ) -> Optional[str]:
        """Build OData $filter string from column filters.

        Laserfiche OData Table API only supports:
        - Comparison operators: eq, ne, gt, ge, lt, le, in
        - Logical operators: and, or, not
        - Function: toupper
        - Literal: null

        NOTE: contains, startswith, endswith are NOT supported by Laserfiche.
        This filter only supports exact match (case-insensitive).

        Args:
            filters: Dict of column names to filter values
            filter_mode: 'and' (all must match) or 'or' (any must match)

        Returns:
            OData $filter string or None if no filters
        """
        if not filters:
            return None

        filter_parts = []
        for column, value in filters.items():
            if not value:
                continue

            # Skip _key column in filters
            if column == "_key":
                continue

            # Strip wildcards - Laserfiche doesn't support contains/startswith/endswith
            # Just do exact match (case-insensitive)
            clean_value = value.strip("*").strip()
            if not clean_value:
                continue

            # Escape single quotes in value
            escaped_value = clean_value.replace("'", "''")

            # Case-insensitive exact match using toupper
            filter_parts.append(
                f"toupper({column}) eq toupper('{escaped_value}')"
            )

        if not filter_parts:
            return None

        # Join with 'and' or 'or' based on filter_mode
        joiner = f" {filter_mode} "
        return joiner.join(filter_parts)

    async def get_table_rows(
        self,
        access_token: str,
        table_name: str,
        limit: int = 50,
        offset: int = 0,
        filters: Optional[Dict[str, str]] = None,
        filter_mode: str = "and",
    ) -> Dict:
        """Get rows from a table with pagination and filtering using OData Table API.

        Args:
            access_token: Valid access token with project scope
            table_name: Name of the table
            limit: Number of rows to return (default: 50, max: 1000)
            offset: Number of rows to skip (default: 0)
            filters: Optional dict of column names to filter values (exact match)
            filter_mode: 'and' (all must match) or 'or' (any must match)

        Returns:
            Dict with rows, total count, limit, and offset

        Raises:
            httpx.HTTPError: If request fails
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }

        params: Dict[str, any] = {
            "$top": min(limit, 1000),  # Cap at 1000
            "$skip": offset,
        }

        # Add filter if provided
        odata_filter = self._build_odata_filter(filters, filter_mode)
        if odata_filter:
            params["$filter"] = odata_filter

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.API_BASE}/table/{table_name}",
                headers=headers,
                params=params,
            )
            response.raise_for_status()
            data = response.json()

            rows = data.get("value", [])

            # Try to get total count from X-APIServer-ResultCount header
            total = -1
            result_count = response.headers.get("X-APIServer-ResultCount")
            if result_count:
                try:
                    total = int(result_count)
                except ValueError:
                    pass

            return {
                "rows": rows,
                "total": total,
                "limit": limit,
                "offset": offset,
            }

    async def get_table_row(
        self,
        access_token: str,
        table_name: str,
        key: str,
    ) -> Dict:
        """Get a single row from a table by key using OData Table API.

        Args:
            access_token: Valid access token with project scope
            table_name: Name of the table
            key: Primary key value

        Returns:
            Row data dictionary

        Raises:
            httpx.HTTPError: If request fails or row not found (404)
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.API_BASE}/table/{table_name}('{key}')",
                headers=headers,
            )
            response.raise_for_status()
            return response.json()

    async def create_table_row(
        self,
        access_token: str,
        table_name: str,
        data: Dict,
    ) -> Dict:
        """Create a new row in a table using OData Table API.

        Args:
            access_token: Valid access token with project scope
            table_name: Name of the table
            data: Row data dictionary

        Returns:
            Created row data

        Raises:
            httpx.HTTPError: If request fails or validation fails
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.API_BASE}/table/{table_name}",
                headers=headers,
                json=data,
            )
            response.raise_for_status()
            return response.json()

    async def update_table_row(
        self,
        access_token: str,
        table_name: str,
        key: str,
        data: Dict,
    ) -> Dict:
        """Update an existing row in a table using OData Table API.

        Args:
            access_token: Valid access token with project scope
            table_name: Name of the table
            key: Primary key value
            data: Partial row data to update

        Returns:
            Updated row data

        Raises:
            httpx.HTTPError: If request fails or row not found (404)
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.API_BASE}/table/{table_name}('{key}')",
                headers=headers,
                json=data,
            )
            response.raise_for_status()
            # PATCH may return 204 No Content or JSON
            if response.status_code == 204 or not response.content:
                return data  # Return the updated data we sent
            return response.json()

    async def delete_table_row(
        self,
        access_token: str,
        table_name: str,
        key: str,
    ) -> None:
        """Delete a row from a table using OData Table API.

        Args:
            access_token: Valid access token with project scope
            table_name: Name of the table
            key: Primary key value

        Raises:
            httpx.HTTPError: If request fails or row not found (404)
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.API_BASE}/table/{table_name}('{key}')",
                headers=headers,
            )
            response.raise_for_status()
            # DELETE returns 204 No Content on success

    async def get_table_schema(
        self,
        access_token: str,
        table_name: str,
    ) -> List[Dict]:
        """Get the schema/columns of a table from OData $metadata.

        Args:
            access_token: Valid access token with project scope
            table_name: Name of the table

        Returns:
            List of column definitions with name and type

        Raises:
            httpx.HTTPError: If request fails
        """
        import xml.etree.ElementTree as ET
        import logging
        logger = logging.getLogger(__name__)

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/xml",
        }

        async with httpx.AsyncClient() as client:
            # Try to get schema from $metadata endpoint
            try:
                response = await client.get(
                    f"{self.API_BASE}/table/$metadata",
                    headers=headers,
                )
                response.raise_for_status()

                # Parse XML metadata
                root = ET.fromstring(response.text)
                # OData metadata uses namespaces
                ns = {
                    "edmx": "http://docs.oasis-open.org/odata/ns/edmx",
                    "edm": "http://docs.oasis-open.org/odata/ns/edm",
                }

                columns = []
                # Find the EntityType for our table
                for entity_type in root.findall(".//edm:EntityType", ns):
                    entity_name = entity_type.get("Name", "")
                    if entity_name.lower() == table_name.lower():
                        for prop in entity_type.findall("edm:Property", ns):
                            prop_name = prop.get("Name", "")
                            prop_type = prop.get("Type", "Edm.String")
                            nullable = prop.get("Nullable", "true").lower() == "true"

                            columns.append({
                                "name": prop_name,
                                "type": prop_type,
                                "required": not nullable,
                            })
                        break

                if columns:
                    logger.info(f"Got schema from $metadata for {table_name}: {len(columns)} columns")
                    return columns

            except Exception as e:
                logger.warning(f"Failed to get $metadata for {table_name}: {e}, falling back to inference")

            # Fallback: infer schema from first row
            headers["Accept"] = "application/json"
            response = await client.get(
                f"{self.API_BASE}/table/{table_name}",
                headers=headers,
                params={"$top": 1},
            )
            response.raise_for_status()
            data = response.json()

            rows = data.get("value", [])
            if not rows:
                return []

            # Infer column types from first row
            columns = []
            for key, value in rows[0].items():
                col_type = "Edm.String"
                if isinstance(value, bool):
                    col_type = "Edm.Boolean"
                elif isinstance(value, int):
                    col_type = "Edm.Int32"
                elif isinstance(value, float):
                    col_type = "Edm.Double"
                elif value is None:
                    col_type = "Edm.String"

                columns.append({
                    "name": key,
                    "type": col_type,
                    "required": key == "_key",  # Only _key is required (and auto-generated)
                })

            return columns

    async def batch_create_rows(
        self,
        access_token: str,
        table_name: str,
        rows: List[Dict],
        max_concurrent: int = 5,
    ) -> List[Dict]:
        """Create multiple rows concurrently.

        Args:
            access_token: Valid access token with project scope
            table_name: Name of the table
            rows: List of row data dictionaries
            max_concurrent: Maximum concurrent requests

        Returns:
            List of results with index, success, data/error for each row
        """
        import asyncio

        results = []
        semaphore = asyncio.Semaphore(max_concurrent)

        async def create_with_semaphore(index: int, row_data: Dict) -> Dict:
            async with semaphore:
                try:
                    created = await self.create_table_row(
                        access_token=access_token,
                        table_name=table_name,
                        data=row_data,
                    )
                    return {
                        "index": index,
                        "success": True,
                        "data": created,
                        "error": None,
                    }
                except httpx.HTTPStatusError as e:
                    error_msg = str(e)
                    try:
                        error_data = e.response.json()
                        error_msg = error_data.get("error", {}).get("message", str(e))
                    except Exception:
                        pass
                    return {
                        "index": index,
                        "success": False,
                        "data": None,
                        "error": error_msg,
                    }
                except Exception as e:
                    return {
                        "index": index,
                        "success": False,
                        "data": None,
                        "error": str(e),
                    }

        # Create tasks for all rows
        tasks = [
            create_with_semaphore(i, row)
            for i, row in enumerate(rows)
        ]

        # Execute concurrently
        results = await asyncio.gather(*tasks)

        return list(results)

    async def replace_all_rows(
        self,
        access_token: str,
        table_name: str,
        rows: List[Dict],
        poll_interval: float = 2.0,
        max_wait: int = 300,
    ) -> Dict:
        """Replace all rows using Laserfiche ReplaceAllRowsAsync endpoint.

        This uses the atomic ReplaceAllRowsAsync endpoint which:
        1. Initiates an async replace operation via file upload
        2. Returns a task ID to monitor
        3. Completes atomically (all or nothing)

        The API requires multipart/form-data with a file upload (CSV or JSON).
        We send the data as a JSON file.

        Args:
            access_token: Valid access token with project scope
            table_name: Name of the table
            rows: List of row data dictionaries (without _key)
            poll_interval: Seconds between task status checks (default: 2.0)
            max_wait: Maximum seconds to wait for operation (default: 300)

        Returns:
            Dict with operation result

        Raises:
            httpx.HTTPError: If request fails
            TimeoutError: If operation exceeds max_wait
        """
        import asyncio
        import logging
        import json
        logger = logging.getLogger(__name__)

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }

        # Convert rows to JSON file content (array of objects)
        json_content = json.dumps(rows)

        async with httpx.AsyncClient(timeout=60.0) as client:
            # Step 1: Start async replace operation via file upload
            logger.info(f"Starting ReplaceAllRowsAsync for {table_name} with {len(rows)} rows")

            # Send as multipart/form-data with a file
            files = {
                "file": ("data.json", json_content, "application/json")
            }

            response = await client.post(
                f"{self.API_BASE}/table/{table_name}/ReplaceAllRowsAsync",
                headers=headers,
                files=files,
            )
            response.raise_for_status()

            result = response.json()
            task_id = result.get("taskId")

            if not task_id:
                # Operation completed synchronously (small tables)
                logger.info(f"Replace completed synchronously for {table_name}")
                return {"success": True, "rows_replaced": len(rows)}

            # Step 2: Poll task status until complete
            # Status values are PascalCase: NotStarted, InProgress, Completed, Failed, Cancelled, Unknown
            logger.info(f"Polling task {task_id} for {table_name}")
            elapsed = 0.0
            while elapsed < max_wait:
                await asyncio.sleep(poll_interval)
                elapsed += poll_interval

                task_response = await client.get(
                    f"{self.API_BASE}/general/Tasks({task_id})",
                    headers=headers,
                )
                task_response.raise_for_status()
                task_data = task_response.json()

                # Laserfiche API returns PascalCase field names: Status, Errors, Id, Type
                status = task_data.get("Status", "")
                logger.info(f"Task {task_id} status: {status} (elapsed: {elapsed:.1f}s)")

                if status == "Completed":
                    logger.info(f"Replace completed successfully for {table_name}")
                    return {"success": True, "rows_replaced": len(rows)}
                elif status == "Failed":
                    # Errors array uses PascalCase: "Errors", with "Title" and "Detail" fields
                    errors = task_data.get("Errors", [])
                    if errors and len(errors) > 0:
                        error_msg = errors[0].get("Title", "Unknown error")
                        detail = errors[0].get("Detail", "")
                        if detail:
                            error_msg = f"{error_msg}: {detail}"
                    else:
                        error_msg = "Replace operation failed"
                    logger.error(f"Replace failed for {table_name}: {error_msg}")
                    return {"success": False, "rows_replaced": 0, "error": error_msg}
                elif status == "Cancelled":
                    logger.error(f"Replace cancelled for {table_name}")
                    return {"success": False, "rows_replaced": 0, "error": "Operation was cancelled"}
                # NotStarted, InProgress, Unknown - continue polling

            # Timeout reached
            logger.error(f"Replace timed out for {table_name} after {max_wait}s")
            raise TimeoutError(f"Replace operation timed out after {max_wait}s")


# Global instance
laserfiche_client = LaserficheClient()
