"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from app.config import settings

# Create FastAPI app
app = FastAPI(
    title="Laserfiche Data View API",
    description="API for viewing and managing Laserfiche lookup table data",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for Docker."""
    return {"status": "healthy", "environment": settings.ENVIRONMENT}


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Laserfiche Data View API",
        "version": "1.0.0",
        "docs": "/docs" if settings.DEBUG else "disabled in production",
    }


# Include routers
from app.routers import auth, tables

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(tables.router, prefix="/tables", tags=["Tables"])


# Test page endpoint
@app.get("/test", response_class=HTMLResponse)
async def test_page():
    """Serve OAuth test page."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Laserfiche OAuth Test</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                margin-bottom: 10px;
            }
            .status {
                padding: 15px;
                border-radius: 4px;
                margin: 20px 0;
            }
            .status.loading {
                background: #fff3cd;
                border-left: 4px solid #ffc107;
            }
            .status.success {
                background: #d4edda;
                border-left: 4px solid #28a745;
            }
            .status.error {
                background: #f8d7da;
                border-left: 4px solid #dc3545;
            }
            .status.info {
                background: #d1ecf1;
                border-left: 4px solid #17a2b8;
            }
            button {
                background: #007bff;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
                margin: 10px 5px;
            }
            button:hover {
                background: #0056b3;
            }
            button.danger {
                background: #dc3545;
            }
            button.danger:hover {
                background: #c82333;
            }
            pre {
                background: #f4f4f4;
                padding: 15px;
                border-radius: 4px;
                overflow-x: auto;
            }
            .user-info {
                margin: 20px 0;
                padding: 15px;
                background: #e7f3ff;
                border-radius: 4px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔐 Laserfiche OAuth Test</h1>
            <p>Test the OAuth authentication flow</p>

            <div id="status"></div>

            <div id="auth-section">
                <button onclick="checkAuthStatus()">Check Auth Status</button>
                <button onclick="login()">Login with Laserfiche</button>
                <button onclick="logout()" class="danger">Logout</button>
            </div>

            <div id="user-info"></div>
            <div id="response"></div>
        </div>

        <script>
            const API_BASE = window.location.origin;

            function showStatus(message, type = 'info') {
                const statusDiv = document.getElementById('status');
                statusDiv.className = `status ${type}`;
                statusDiv.innerHTML = message;
            }

            function showResponse(title, data) {
                const responseDiv = document.getElementById('response');
                responseDiv.innerHTML = `
                    <h3>${title}</h3>
                    <pre>${JSON.stringify(data, null, 2)}</pre>
                `;
            }

            async function checkAuthStatus() {
                showStatus('Checking authentication status...', 'loading');
                try {
                    const response = await fetch(`${API_BASE}/auth/status`, {
                        credentials: 'include'
                    });

                    const data = await response.json();

                    if (data.authenticated) {
                        showStatus('✅ You are authenticated!', 'success');
                        document.getElementById('user-info').innerHTML = `
                            <div class="user-info">
                                <strong>Status:</strong> Logged in with valid token
                            </div>
                        `;
                    } else {
                        showStatus('❌ Not authenticated. Please login.', 'info');
                        document.getElementById('user-info').innerHTML = '';
                    }

                    showResponse('Auth Status Response', data);
                } catch (error) {
                    showStatus(`Error: ${error.message}`, 'error');
                }
            }

            async function login() {
                showStatus('Initiating OAuth login...', 'loading');
                try {
                    const response = await fetch(`${API_BASE}/auth/login`, {
                        credentials: 'include'
                    });

                    const data = await response.json();
                    showResponse('Login Response', data);

                    if (data.redirect_url) {
                        showStatus('Redirecting to Laserfiche...', 'loading');
                        window.location.href = data.redirect_url;
                    }
                } catch (error) {
                    showStatus(`Error: ${error.message}`, 'error');
                }
            }

            async function logout() {
                showStatus('Logging out...', 'loading');
                try {
                    const response = await fetch(`${API_BASE}/auth/logout`, {
                        method: 'POST',
                        credentials: 'include'
                    });

                    const data = await response.json();
                    showStatus('✅ Logged out successfully!', 'success');
                    showResponse('Logout Response', data);
                    document.getElementById('user-info').innerHTML = '';
                } catch (error) {
                    showStatus(`Error: ${error.message}`, 'error');
                }
            }

            // Check if we just came back from OAuth callback
            window.addEventListener('DOMContentLoaded', () => {
                const urlParams = new URLSearchParams(window.location.search);
                if (urlParams.has('code') || window.location.pathname.includes('callback')) {
                    showStatus('✅ OAuth callback successful! Checking authentication...', 'success');
                    setTimeout(checkAuthStatus, 1000);
                } else {
                    checkAuthStatus();
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
