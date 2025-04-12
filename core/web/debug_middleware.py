#!/usr/bin/env python3
"""
Debug middleware for the Dawn Framework web server.

This middleware adds debug features to the web server when debug mode is enabled.
"""  # noqa: D202

import time
import json
import logging
from typing import Callable, Dict, Any

from core.utils.debug import is_debug_mode

# Configure logger
logger = logging.getLogger("dawn.web.debug")

class DebugMiddleware:
    """
    Middleware that adds debug features to the web server.
    
    Features include:
    - Request/response logging
    - Performance timing
    - Debug headers
    """  # noqa: D202
    
    def __init__(self, app):
        """
        Initialize the debug middleware.
        
        Args:
            app: The ASGI application
        """
        self.app = app
        self.debug_enabled = is_debug_mode()
        if self.debug_enabled:
            logger.info("Debug middleware initialized")
    
    async def __call__(self, scope, receive, send):
        """
        ASGI application entry point.
        
        Args:
            scope: The ASGI connection scope
            receive: The ASGI receive function
            send: The ASGI send function
        """
        if not self.debug_enabled:
            # Debug mode is disabled, just pass through
            await self.app(scope, receive, send)
            return
        
        # Only process HTTP requests
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Start timer
        start_time = time.time()
        
        # Log request
        method = scope.get("method", "UNKNOWN")
        path = scope.get("path", "UNKNOWN")
        query_string = scope.get("query_string", b"").decode("utf-8", errors="replace")
        client = scope.get("client", ("Unknown", 0))
        
        request_id = f"{int(time.time() * 1000)}-{id(scope)}"
        
        # Extract headers
        headers = {}
        for name, value in scope.get("headers", []):
            headers[name.decode("utf-8")] = value.decode("utf-8")
        
        logger.debug(f"[{request_id}] Request: {method} {path}?{query_string} from {client[0]}:{client[1]}")
        logger.debug(f"[{request_id}] Headers: {json.dumps(headers, indent=2)}")
        
        # Intercept the send function to capture and modify responses
        async def send_with_debug(message):
            if message["type"] == "http.response.start":
                # Calculate and log response time
                response_time = time.time() - start_time
                
                # Get response status
                status = message.get("status", 0)
                
                # Log response info
                logger.debug(f"[{request_id}] Response: {status} in {response_time:.4f}s")
                
                # Extract headers
                response_headers = {}
                for name, value in message.get("headers", []):
                    response_headers[name.decode("utf-8")] = value.decode("utf-8")
                
                logger.debug(f"[{request_id}] Response Headers: {json.dumps(response_headers, indent=2)}")
                
                # Add debug headers
                debug_headers = [
                    (b"X-Debug-Time", f"{response_time:.4f}".encode()),
                    (b"X-Debug-Request-ID", request_id.encode()),
                ]
                
                # Append debug headers to the response
                message["headers"] = message.get("headers", []) + debug_headers
            
            # Pass the message to the original send function
            await send(message)
        
        # Call the application with our modified send function
        try:
            await self.app(scope, receive, send_with_debug)
        except Exception as e:
            # Log exception
            logger.exception(f"[{request_id}] Unhandled exception in request: {str(e)}")
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Send a generic 500 response with debug info
            headers = [
                (b"content-type", b"application/json"),
                (b"X-Debug-Time", f"{response_time:.4f}".encode()),
                (b"X-Debug-Request-ID", request_id.encode()),
            ]
            
            # Send response headers
            await send({
                "type": "http.response.start",
                "status": 500,
                "headers": headers,
            })
            
            # Send response body
            error_body = {
                "error": "Internal Server Error",
                "detail": str(e),
                "request_id": request_id,
                "debug_info": {
                    "exception_type": type(e).__name__,
                    "request_path": path,
                    "request_method": method,
                }
            }
            
            await send({
                "type": "http.response.body",
                "body": json.dumps(error_body).encode("utf-8"),
            })

def apply_debug_middleware(app_factory: Callable[[], Any]) -> Callable[[], Any]:
    """
    Factory function to apply the debug middleware to an ASGI application.
    Only applies the middleware when debug mode is enabled.
    
    Args:
        app_factory: Factory function that creates the ASGI application
        
    Returns:
        Factory function that creates the ASGI application with debug middleware applied
    """
    def create_app_with_debug():
        app = app_factory()
        if is_debug_mode():
            logger.info("Applying debug middleware to web application")
            return DebugMiddleware(app)
        return app
    
    return create_app_with_debug 