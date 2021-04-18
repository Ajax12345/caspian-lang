import typing

class CaspianException:
    def __init__(self, _line:int, _char:int, _stack:typing.List, details:typing.Optional=None) -> None:
        self.line, self.char = _line, _char
        self.stack = _stack
        self.details = details

class InvalidSyntax(CaspianException):
    pass

class ErrorPacket:
    def __init__(self, _line:int, _char:int, _error:typing.Union[InvalidSyntax], _stack:typing.List, details:typing.Optional=None) -> None:
        self.line, self.char, self.error = _line, _char, _error
        self.stack = _stack
        self.details = details

    @property
    def gen_error(self) -> typing.Union[InvalidSyntax]:
        return self.error(_line, _char, _stack, details)
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} '{self.error.__name__}'>"