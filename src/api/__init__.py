from .dependencies import (
    get_unit_of_work,
    get_users_service,
    get_groups_service,
    get_tasks_service
)
from .groups import router as groups_router
from .tasks import router as tasks_router
from .users import router as users_router
