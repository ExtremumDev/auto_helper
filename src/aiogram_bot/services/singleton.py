

class BaseSingleton:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def create_instance(cls):
        cls()

    @classmethod
    def get_instance(cls):
        return cls._instance
