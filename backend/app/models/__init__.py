# 作用：alembic autogenerate 要靠 Base.metadata 发现新表
from app.models.water_log import WaterLog # noqa: F401
from app.models.user import User # noqa: F401
from app.models.agent_traces import AgentTrace # noqa: F401
from app.models.diet_log import DietLog # noqa: F401 s
from app.models.weight_log import WeightLog # noqa: F401
from app.models.workout_log import WorkoutLog # noqa: F401
from app.models.knowledge import Knowledge # noqa: F401
from app.models.profile import Profile # noqa: F401

