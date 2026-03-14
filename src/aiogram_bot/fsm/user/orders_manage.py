from aiogram.fsm.state import State, StatesGroup


class KeywordsInputFSM(StatesGroup):
    words_state = State()

class AddHandlingGroupFSM(StatesGroup):
    chat_state = State()
