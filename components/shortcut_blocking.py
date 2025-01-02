class ShortcutBlockable:
    def __init__(self):
        self.__is_blocking = False

    def block(self):
        self.__is_blocking = True

    def unblock(self):
        self.__is_blocking = False

    def is_blocking(self):
        return self.__is_blocking
