from fastapi import FastAPI
from app.routes.weather import router as weather_router
from app.routes.activities import router as activities_router
from app.routes.vote import router as vote_router
from app.routes.users import router as users_router
from app.routes.admin import router as admin_router
from app.routes.user import router as user_router
from app.routes.air_quality import router as air_quality_router

app = FastAPI(title="Weather Activity Recommendation API")

app.include_router(weather_router)
app.include_router(activities_router)
app.include_router(vote_router)
app.include_router(users_router)
app.include_router(admin_router)
app.include_router(user_router)
app.include_router(air_quality_router)
