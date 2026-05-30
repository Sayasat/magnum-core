from fastapi import FastAPI
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exception_handlers import app_exception_handler
from app.core.sentry import init_sentry
from app.shared.exceptions import AppException

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        debug=settings.DEBUG,
    )
    init_sentry(app)
    app.add_exception_handler(AppException, app_exception_handler)
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)
    return app

app = create_app()