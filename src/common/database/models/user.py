import datetime
from typing import List

from sqlalchemy import Integer, BigInteger, String, ForeignKey, Enum, Boolean, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .enums import TelegramAccountStatus, SubscribeTariffEnum


class User(Base):

    telegram_user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    telegram_username: Mapped[str] = mapped_column(String(32), nullable=True)

    is_admin: Mapped[bool] = mapped_column(default=False)

    # account info

    order_keywords: Mapped[str] = mapped_column(String(1000), nullable=True)
    except_words: Mapped[str] = mapped_column(String(600), nullable=True)

    # Subscription

    sub_tariff: Mapped[SubscribeTariffEnum] = mapped_column(Enum(SubscribeTariffEnum), nullable=True)
    is_subscribed: Mapped[bool] = mapped_column(default=False)
    expiration_date: Mapped[datetime.datetime] = mapped_column(default=None, nullable=True)

    telegram_account_id: Mapped[int] = mapped_column(
        ForeignKey("telegram_accounts.id", ondelete="SET NULL"),
        nullable=True
    )
    telegram_account: Mapped["TelegramAccount"] = relationship(
        "TelegramAccount",
        back_populates="user"
    )

    handling_groups: Mapped[List["Group"]] = relationship(
        "Group",
        back_populates="user",
        uselist=True,
        cascade="all, delete-orphan"
    )

    @property
    def register_date(self):
        return self.created_at.strftime("%d.%m.%Y")


class Group(Base):

    display_name: Mapped[str] = mapped_column(String(50))
    chat_id: Mapped[int] = mapped_column(BigInteger)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(
        "User",
        back_populates="handling_groups"
    )



class TelegramAccount(Base):

    status: Mapped[TelegramAccountStatus] = mapped_column(Enum(TelegramAccountStatus), default=TelegramAccountStatus.AUTH_NEEDED)

    phone_number: Mapped[str] = mapped_column(String(20))
    telegram_user_id: Mapped[int] = mapped_column(BigInteger, nullable=True)

    is_message_handling: Mapped[bool] = mapped_column(Boolean, default=True)

    code_hash: Mapped[str] = mapped_column(String(22), nullable=True)
    user: Mapped["User"] = relationship(
        "User",
        back_populates="telegram_account"
    )

    @property
    def client_id(self):
        return f"account-{self.id}"
