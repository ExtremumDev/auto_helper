from src.common.databsae.dao.base import BaseDAO
from src.common.databsae.models.user import User


class UserDAO(BaseDAO):
    model = User
