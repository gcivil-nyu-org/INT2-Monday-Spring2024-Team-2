class EmailValidationError(Exception):
    "Raised when the input is not a valid email."
    pass


class PasswordValidationError(Exception):
    "Raised when the input does not meet password requirements."
    pass


class NameValidationError(Exception):
    "Raised when the input is not a valid name."
    pass