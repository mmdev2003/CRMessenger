class ErrUnauthorized(Exception):
    def __str__(self):
        return "Unauthorized"


class ErrServiceUnavailable(Exception):
    def __str__(self):
        return "Before 3 retry service don`t answer"
