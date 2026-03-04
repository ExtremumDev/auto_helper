from aiogram.fsm.state import State, StatesGroup


class AccountAuthorizationFSM(StatesGroup):
    phone_number_sate = State()
