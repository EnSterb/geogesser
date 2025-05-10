from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from sqlalchemy.orm import Session

from app.routers.game import router as game_router
from app.database import get_db
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi import Request, Depends
from app.routers.auth import router as auth_router
from app.routers.pages import router as pages_router, redirect_if_not_authenticated

app = FastAPI(
    title='Geogesser',
    version='0.1.1',
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Your API",
        version="1.0.0",
        routes=app.routes,
    )

    # Добавляем поддержку OAuth2 в Swagger
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/auth/login",
                    "scopes": {},
                }
            }
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
app.include_router(auth_router)
app.include_router(game_router)
app.include_router(pages_router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    user = await redirect_if_not_authenticated(request, db)
    if isinstance(user, RedirectResponse):
        return templates.TemplateResponse("menu.html", {
        "request": request
    })
    return templates.TemplateResponse("menu.html", {
        "request": request,
        "user": user
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)