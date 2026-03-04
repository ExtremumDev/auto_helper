import datetime

from sqlalchemy import Integer, BigInteger, String, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .enums import TelegramAccountStatus, SubscribeTariffEnum


class User(Base):

    telegram_user_id: Mapped[int] = mapped_column(BigInteger, unique=True)

    is_admin: Mapped[bool] = mapped_column(default=False)

    # account info

    order_keywords: Mapped[str] = mapped_column(String(1000), nullable=True)
    except_words: Mapped[str] = mapped_column(String(600), nullable=True)

    # Subscription

    sub_tariff: Mapped[SubscribeTariffEnum] = mapped_column(Enum(SubscribeTariffEnum), nullable=True)
    is_subscribed: Mapped[bool] = mapped_column(default=False)
    expiration_date: Mapped[datetime.datetime] = mapped_column(default=None, nullable=True)

    # telegram_account: Mapped["TelegramAccount"] = relationship(
    #     "TelegramAccount",
    # )



class TelegramAccount(Base):

    status: Mapped[TelegramAccountStatus] = mapped_column(String(10))

    phone_number: Mapped[str] = mapped_column(String(20))

