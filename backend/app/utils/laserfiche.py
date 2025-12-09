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
            # Response format: { "value": [{ "rowCount": 123 }] }
            value = data.get("value", [])
            if value and len(value) > 0:
                return value[0].get("rowCount", 0)
            return 0

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


# Global instance
laserfiche_client = LaserficheClient()
