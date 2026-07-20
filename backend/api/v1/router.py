from fastapi import APIRouter

from api.v1.endpoints import analytics, auth, content, prompts, publishing

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(content.router, prefix="/content", tags=["content"])
api_router.include_router(publishing.router, prefix="/publishing", tags=["publishing"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(prompts.router, prefix="/prompts", tags=["prompts"])
