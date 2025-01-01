from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from routes import reimbursements_router
from dotenv import load_dotenv

load_dotenv()

tags_metadata = [
    {
        "name": "reimbursements",
        "description": "Operations with reimbursements.",
    },
]

app = FastAPI(
    title="FastRetail API - Reimbursements",
    description="This is a FastRetail API service for reimbursements.",
    version="1.0.0",
    openapi_tags=tags_metadata,
    license_info={
        "name": "Apache 2.0",
        "identifier": "MIT",
    },
)

app.include_router(
    reimbursements_router, prefix="/reimbursements", tags=["reimbursements"]
)

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


@app.get("/api-reimbursements/openapi.json", include_in_schema=False)
async def get_openapi_schema():
    return custom_openapi()


@app.get("/reimbursements-docs", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url="/api-reimbursements/openapi.json", title=app.title
    )


@app.get("/reimbursements-swagger", include_in_schema=False)
async def swagger_html():
    return get_swagger_ui_html(
        openapi_url="/api-reimbursements/openapi.json", title=app.title
    )
