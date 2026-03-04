import datetime

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.aiogram_bot.utils.exceptions import ValidationError
from src.common.database.dao.user import UserDAO
from src.common.database.models.enums import SubscribeTariffEnum
from src.common.database.models.user import User


class UserService:

    async def subscribe(self, days: int, tariff: SubscribeTariffEnum, user: User, db_session: AsyncSession):
        today = datetime.datetime.now()
        expire_date = today + datetime.timedelta(days=days)

        user.expiration_date = expire_date
        user.sub_tariff = tariff
        user.is_subscribed = True

        await db_session.commit()

    async def register_user(self, telegram_user_id: int, db_session: AsyncSession):
        user = await UserDAO.add(
            session=db_session,
            telegram_user_id=telegram_user_id,
            is_admin=False
        )

        # free 10 days full sub

        await self.subscribe(days=10, tariff=SubscribeTariffEnum.HARD, user=user, db_session=db_session)


    async def update_keywords(self, keywords: str, db_session: AsyncSession, user: User, editing: str):
        """

        :param keywords:
        :param db_session:
        :param user:
        :param editing: What is editing: keywords - if keywords, exceptions - if words-exceptions
        :return:
        """

        max_length = 1000
        if editing == "keywords":
            max_length = 1000
        elif editing == "exceptions":
            max_length = 600

        if len(keywords) > max_length:
            raise ValidationError("Длина списка должна быть не более 1000 символов!, попробуйте ещё раз")
        else:

            if editing == "keywords":
                user.order_keywords = keywords
            elif editing == "exceptions":
                user.except_words = keywords
            try:
                await db_session.commit()
            except SQLAlchemyError:
                raise ValidationError("Произошла неизвестная ошибка, обратитесь с этой проблемой к администратору")