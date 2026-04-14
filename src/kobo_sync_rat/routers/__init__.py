from .auth import router as auth_router
from .configuration import router as configuration_router
from .documentation import router as documentation_router
from .library import router as library_router
from .store import router as store_router

__all__ = (
    "auth_router",
    "configuration_router",
    "documentation_router",
    "library_router",
    "store_router",
)
