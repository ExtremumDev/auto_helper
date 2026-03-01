import datetime

from sqlalchemy import Integer, BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(Base):

    telegram_user_id: Mapped[int] = mapped_column(BigInteger, )

    # account info

    order_keywords: Mapped[str] = mapped_column(String(1000))

    # Subscription

    is_subscribed: Mapped[bool] = mapped_column(default=False)
    expiration_date: Mapped[datetime.datetime] = mapped_column(default=None, nullable=True)

