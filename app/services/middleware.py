# APIHub/app/services/middleware.py
import logging
from fastapi import Request
from starlette.responses import Response
from app.services.logs import mask_sensitive_data, logger

# Middleware to log requests and responses
async def log_requests(request: Request, call_next):
    # Log the incoming request
    logger.info(f"Incoming request: {request.method} {request.url}")
    
    # Log the headers
    headers = dict(request.headers)
    logger.info(f"Headers: {headers}")
    
    logger.info(f"Query params: {request.query_params}")
    logger.info(f"Path params: {request.path_params}")
    
    try:
        body = await request.json()
        # Mask sensitive data (password is masked)
        masked_body = mask_sensitive_data(body)
        logger.info(f"Request body: {masked_body}")
    except Exception:
        logger.info("Request body: <not JSON>")

    # Call the next middleware or route handler
    response = await call_next(request)

    # Log the outgoing response
    logger.info(f"Outgoing response: Status code {response.status_code}")
    
    # Log the response headers
    response_headers = dict(response.headers)
    logger.info(f"Response headers: {response_headers}")
    
    try:
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk
        response_body_str = response_body.decode()
        
        # Log the response body
        logger.info(f"Response body: {response_body_str}")
        
        # Reconstruct the response with the body iterator
        response = Response(
            content=response_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type
        )
    except Exception:
        logger.info("Response body: <not JSON>")

    return response
