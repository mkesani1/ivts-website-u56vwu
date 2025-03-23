import os
import sys

from fastapi import FastAPI  # fastapi ^0.95.0
import uvicorn  # uvicorn ^0.22.0

from app.core.config import settings  # Import application configuration settings
from app.core.logging import get_logger  # Import logger factory function
from app import initialize_app  # Import application initialization function
from app.extensions import cleanup_extensions  # Import function to clean up application extensions
from app.middlewares.cors_middleware import setup_cors  # Import function to configure CORS middleware
from app.middlewares.error_handler import setup_error_handlers  # Import function to configure error handlers
from app.middlewares.request_logger import RequestLoggerMiddleware  # Import request logging middleware
from app.middlewares.rate_limiter import setup_rate_limiting  # Import function to configure rate limiting
from app.middlewares.security_middleware import setup_security_middleware  # Import function to configure security middleware
from app.api.routes import get_api_router  # Import function to get configured API router

# Initialize logger
logger = get_logger(__name__)

# Define FastAPI application instance
app = FastAPI(title=settings.PROJECT_NAME, debug=settings.DEBUG, docs_url='/docs', redoc_url='/redoc')

def create_app() -> FastAPI:
    """
    Creates and configures the FastAPI application

    Returns:
        fastapi.FastAPI: Configured FastAPI application instance
    """
    # Create FastAPI application with project name and debug settings
    app = FastAPI(title=settings.PROJECT_NAME, debug=settings.DEBUG, docs_url='/docs', redoc_url='/redoc')

    # Configure CORS middleware using setup_cors()
    setup_cors(app)

    # Configure error handlers using setup_error_handlers()
    setup_error_handlers(app)

    # Add request logging middleware
    app.add_middleware(RequestLoggerMiddleware)

    # Configure rate limiting using setup_rate_limiting()
    setup_rate_limiting(app)

    # Configure security middleware using setup_security_middleware()
    setup_security_middleware(app)

    # Include API router using get_api_router()
    api_router = get_api_router()
    app.include_router(api_router)

    @app.on_event("startup")
    async def startup_event():
        """Event handler that runs when the application starts"""
        logger.info("Application startup event triggered")
        # Log application startup
        logger.info("Starting up application...")

        # Initialize application components using initialize_app()
        success = initialize_app(app)
        if success:
            logger.info("Application initialization completed successfully")
        else:
            logger.warning("Application initialization completed with some issues")

    @app.on_event("shutdown")
    async def shutdown_event():
        """Event handler that runs when the application shuts down"""
        logger.info("Application shutdown event triggered")
        # Log application shutdown
        logger.info("Shutting down application...")

        # Clean up application extensions using cleanup_extensions()
        cleanup_extensions()

        # Log successful cleanup
        logger.info("Application cleanup completed successfully")

    # Return the configured application
    return app

if __name__ == "__main__":
    """Main entry point for running the application"""
    # Create and configure the application using create_app()
    app = create_app()

    # Run the application using uvicorn if script is executed directly
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
    # Configure uvicorn with host, port, and reload settings