from aiogram.fsm.state import State, StatesGroup

class ChangeUserTariffFSM(StatesGroup):
    date_state = State()
    date_input_state = State()
