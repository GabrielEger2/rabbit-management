from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from routes import trips_router
from dotenv import load_dotenv

load_dotenv()

tags_metadata = [
    {
        "name": "trips",
        "description": "Operations with trips.",
    },
]

app = FastAPI(
    title="FastRetail API - Trips Section",
    description="Manage expenses, including flexible schema for different expense types.",
    version="1.0.0",
    openapi_tags=tags_metadata,
    license_info={
        "name": "Apache 2.0",
        "identifier": "MIT",
    },
)

app.include_router(trips_router, prefix="/trips", tags=["trips"])

security_scheme = {
    "bearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }
}


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
        openapi_version=app.openapi_version,
        description=app.description,
        license_info=app.license_info,
        tags=app.openapi_tags,
    )
    openapi_schema["components"]["securitySchemes"] = security_scheme
    openapi_schema["security"] = [{"bearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/api-trips/openapi.json", include_in_schema=False)
async def get_openapi_schema():
    return custom_openapi()


@app.get("/trips-docs", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(openapi_url="/api-trips/openapi.json", title=app.title)


@app.get("/trips-swagger", include_in_schema=False)
async def swagger_html():
    return get_swagger_ui_html(openapi_url="/api-trips/openapi.json", title=app.title)
