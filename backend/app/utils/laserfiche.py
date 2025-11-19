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
            "$count": "true",  # Include total count
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.API_BASE}/table/{table_name}",
                headers=headers,
                params=params,
            )
            response.raise_for_status()
            data = response.json()

            return {
                "rows": data.get("value", []),
                "total": data.get("@odata.count", 0),
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


# Global instance
laserfiche_client = LaserficheClient()
