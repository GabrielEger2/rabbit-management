from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from routes import users_router, auth_router, admin_router
from dotenv import load_dotenv

load_dotenv()

tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users.",
    },
    {
        "name": "auth",
        "description": "Authentication operations. **Access token** is generated here.",
    },
    {
        "name": "admin",
        "description": "Admin operations. **Level** is managed here.",
    },
]

app = FastAPI(
    title="FastRetail API - Users Section",
    description="This is the Users Section of the FastRetail API. It includes operations with users, auth, and admin.",
    version="1.0.0",
    openapi_tags=tags_metadata,
    license_info={
        "name": "Apache 2.0",
        "identifier": "MIT",
    },
)

# Include routers
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])

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


@app.get("/api-users/openapi.json", include_in_schema=False)
async def get_openapi_schema():
    return custom_openapi()


@app.get("/users-docs", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(openapi_url="/api-users/openapi.json", title=app.title)


@app.get("/users-swagger", include_in_schema=False)
async def swagger_html():
    return get_swagger_ui_html(openapi_url="/api-users/openapi.json", title=app.title)
