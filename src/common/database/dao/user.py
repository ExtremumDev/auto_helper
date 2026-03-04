from src.common.database.dao.base import BaseDAO
from src.common.database.models.user import User


class UserDAO(BaseDAO):
    model = User
