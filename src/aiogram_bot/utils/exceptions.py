
class ValidationError(Exception):
    def __init__(self, message: str):
        self.__message = message

    def get_message(self):
        return self.__message
