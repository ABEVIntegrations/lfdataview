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

    async def get_table_rows(
        self,
        access_token: str,
        table_name: str,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict:
        """Get rows from a table with pagination using OData Table API.

        Args:
            access_token: Valid access token with project scope
            table_name: Name of the table
            limit: Number of rows to return (default: 50, max: 1000)
            offset: Number of rows to skip (default: 0)

        Returns:
            Dict with rows, total count, limit, and offset

        Raises:
            httpx.HTTPError: If request fails
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }

        params = {
            "$top": min(limit, 1000),  # Cap at 1000
            "$skip": offset,
            "$count": "true",  # Include total count (OData uses string "true")
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.API_BASE}/table/{table_name}",
                headers=headers,
                params=params,
            )
            response.raise_for_status()
            data = response.json()

            rows = data.get("value", [])

            # Laserfiche OData API doesn't support $count
            # Use -1 to indicate unknown total (frontend will handle this)
            total = data.get("@odata.count")
            if total is None:
                total = -1  # Unknown total

            return {
                "rows": rows,
                "total": int(total),
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
        """Get the schema/columns of a table.

        Args:
            access_token: Valid access token with project scope
            table_name: Name of the table

        Returns:
            List of column definitions with name and type

        Raises:
            httpx.HTTPError: If request fails
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }

        # Get one row to infer schema from the data
        # OData Table API doesn't have a dedicated schema endpoint
        async with httpx.AsyncClient() as client:
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
                col_type = "string"
                if isinstance(value, bool):
                    col_type = "boolean"
                elif isinstance(value, int):
                    col_type = "integer"
                elif isinstance(value, float):
                    col_type = "number"
                elif value is None:
                    col_type = "string"

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
        timeout: int = 300,
    ) -> Dict:
        """Replace all rows in a table with new data.

        This deletes all existing rows and inserts the provided rows.
        Note: This is NOT atomic - if creation fails partway through,
        some data may be lost.

        Args:
            access_token: Valid access token with project scope
            table_name: Name of the table
            rows: List of row data dictionaries (without _key)
            timeout: Maximum seconds to wait for operation (default: 300)

        Returns:
            Dict with operation result

        Raises:
            httpx.HTTPError: If request fails
        """
        import asyncio
        import logging
        logger = logging.getLogger(__name__)

        # Step 1: Get all existing rows to find their keys
        logger.info(f"Fetching existing rows from {table_name}")
        existing_rows = []
        offset = 0
        limit = 1000

        while True:
            data = await self.get_table_rows(
                access_token=access_token,
                table_name=table_name,
                limit=limit,
                offset=offset,
            )
            batch = data.get("rows", [])
            existing_rows.extend(batch)

            if len(batch) < limit:
                break
            offset += limit

        logger.info(f"Found {len(existing_rows)} existing rows to delete")

        # Step 2: Delete all existing rows
        if existing_rows:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                semaphore = asyncio.Semaphore(10)  # Limit concurrent deletes

                async def delete_row(key: str):
                    async with semaphore:
                        try:
                            response = await client.delete(
                                f"{self.API_BASE}/table/{table_name}('{key}')",
                                headers=headers,
                            )
                            response.raise_for_status()
                            return True
                        except Exception as e:
                            logger.error(f"Failed to delete row {key}: {e}")
                            return False

                # Delete all rows concurrently
                keys = [row.get("_key") for row in existing_rows if row.get("_key")]
                delete_tasks = [delete_row(key) for key in keys]
                delete_results = await asyncio.gather(*delete_tasks)

                deleted_count = sum(1 for r in delete_results if r)
                logger.info(f"Deleted {deleted_count}/{len(keys)} rows")

        # Step 3: Create all new rows using batch_create_rows
        if rows:
            logger.info(f"Creating {len(rows)} new rows")
            results = await self.batch_create_rows(
                access_token=access_token,
                table_name=table_name,
                rows=rows,
            )

            succeeded = sum(1 for r in results if r.get("success"))
            failed = len(results) - succeeded

            if failed > 0:
                return {
                    "success": False,
                    "rows_replaced": succeeded,
                    "error": f"{failed} rows failed to create",
                }

            return {
                "success": True,
                "rows_replaced": succeeded,
            }

        return {
            "success": True,
            "rows_replaced": 0,
        }


# Global instance
laserfiche_client = LaserficheClient()
