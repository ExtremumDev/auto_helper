from aiogram import types, F, Dispatcher
from aiogram.enums import ContentType
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButtonRequestChat, KeyboardButton

from sqlalchemy.ext.asyncio import AsyncSession

from src.aiogram_bot.config import MAX_GROUPS
from src.aiogram_bot.database.utils import provide_user
from src.aiogram_bot.fsm.user.orders_manage import AddHandlingGroupFSM
from src.aiogram_bot.keyboards.user.main import main_user_reply_markup
from src.aiogram_bot.services.app_messaging import PyrogramAppProcedureCall
from src.aiogram_bot.utils.paging.groups import GroupListPaging
from src.common.database.core.database import connection
from src.common.database.dao.user import GroupDAO
from src.common.database.models.user import User
from src.common.utils.auth import GroupAddResponseStatus


@provide_user(load_groups=True)
async def send_current_group_list(c: types.CallbackQuery, user: User, db_session: AsyncSession, *args):
    paging = GroupListPaging()
    await paging.get_queryset(user=user)
    await paging.get_current_page()

    await c.message.answer(
        "Список ваших групп:",
        reply_markup=paging.get_reply_markup()
    )

    await c.answer()


@provide_user(load_groups=True)
async def ask_group(c: types.CallbackQuery, state: FSMContext, user: User, *args, **kwargs):
    if len(user.handling_groups) < MAX_GROUPS:
        await state.set_state(AddHandlingGroupFSM.chat_state)
        await c.message.answer(
            "Поделитесь чатом, заказы из которого хотите отслеживать. Нажмите кнопку внизу",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(
                            text="⤴️ Поделиться чатом",
                            request_chat=KeyboardButtonRequestChat(
                                request_id=c.from_user.id,
                                chat_is_channel=False
                            )
                        )
                    ],
                    [
                        KeyboardButton(text="⬅️ Назад")
                    ]
                ],
                resize_keyboard=True
            )
        )


    else:
        await c.answer("Вы достигли лимита отслеживаемых групп!", show_alert=True)


@provide_user(load_tg_account=True)
async def handle_group(m: types.Message, state: FSMContext, user: User, *args, **kwargs):
    if m.chat_shared:
        await state.clear()
        chat_id = m.chat_shared.chat_id

        group_add_result = await PyrogramAppProcedureCall.get_instance().check_group(
            tg_account_id=user.telegram_account.id,
            group_chat_id=chat_id
        )

        text = "Произошла неизвестная ошибка, попробуйте позже"
        match group_add_result:
            case GroupAddResponseStatus.SUCCESS:
                text = "✅ Группа успешно добавлена и теперь отслеживается на наличие новых заказов"
            case GroupAddResponseStatus.INVALID_CHAT:
                text = "❌ Аккаунт, в которым вы авторизовались, не состоит в этом чате или не имеет доступа к сообщениям"
            case GroupAddResponseStatus.INVALID_CHAT_TYPE:
                text = "Чат должен являться группой(а не каналом или ЛС)"
            case GroupAddResponseStatus.UNEXPECTED:
                text = "❌ Не удалось добавить этот чат, попробуйте позже"
        await m.answer(
            text=text,
            reply_markup=main_user_reply_markup
        )

@provide_user(load_groups=True)
async def delete_group(c: types.CallbackQuery, user: User, db_session: AsyncSession, *args, **kwargs):
    c_data = c.data.split('_')
    group_id, page = int(c_data[1]), int(c_data[2])

    await GroupDAO.delete_obj(session=db_session, obj_id=group_id)
    await c.answer("Группа успешно удалена и больше не будет отслеживаться")

    paging = GroupListPaging(page=page)
    await paging.get_queryset(user=user)
    await paging.get_current_page()

    await c.message.edit_reply_markup(
        reply_markup=paging.get_reply_markup()
    )




def register_groups_list_edit_markup(dp: Dispatcher):
    dp.callback_query.register(send_current_group_list, F.data == "edit_groups")
    GroupListPaging.register_paging_handlers(dp)
    dp.callback_query.register(ask_group, F.data == "add_group")
    dp.message.register(handle_group, StateFilter(AddHandlingGroupFSM.chat_state), F.content_type==ContentType.CHAT_SHARED)
    dp.callback_query.register(delete_group, F.data.startswith("delgroup_"))
