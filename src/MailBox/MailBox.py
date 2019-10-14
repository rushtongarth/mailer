import abc


class AbstractMailBox(abc.ABC):

    @abc.abstractmethod
    def __init__(self, user, pswd, location):
        pass

    @abc.abstractmethod
    def __enter__(self):
        pass

    @abc.abstractmethod
    def __exit__(self, *args):
        pass
