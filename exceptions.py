
# cannot find element in database

class BaseCustomException(Exception):
    def __init__(self, message=''):
        self.message = message

    def __str__(self):
        return self.message


class NotFoundInDatabaseException(BaseCustomException):
    pass


class SubscriptionNotFoundException(BaseCustomException):
    pass


class UserNotFoundException(BaseCustomException):
    pass


class DataUpdaterException(BaseCustomException):
    pass