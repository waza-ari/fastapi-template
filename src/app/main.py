from app.api import router
from app.core import create_application, settings

app = create_application(router=router, settings=settings)
