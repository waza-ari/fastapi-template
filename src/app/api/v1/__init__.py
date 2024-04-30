"""
API version 1 module.
"""

from fastapi import APIRouter

from .ability import router as ability_router
from .hero import router as hero_router

router = APIRouter(prefix="/v1")
router.include_router(ability_router)
router.include_router(hero_router)
