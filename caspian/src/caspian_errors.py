import typing

class CaspianException:
    def __init__(self, _line:int, _char:int, details:typing.Optional=None) -> None:
        self.line, self.char = _line, _char
        self.details = details

class InvalidSyntax(CaspianException):
    def __str__(self) -> str:
        return f"Caspian Error:\n{self.__class__.__name__}: {self.details}"

    def __repr__(self) -> str:
        return str(self)

class InvalidIndentation(CaspianException):
    def __str__(self) -> str:
        return f"Caspian Error:\n{self.__class__.__name__}: {self.details}"

    def __repr__(self) -> str:
        return str(self)

class ValueError(CaspianException):
    def __str__(self) -> str:
        return f"Caspian Error:\n{self.__class__.__name__}: {self.details}"

class ErrorPacket:
    def __init__(self, _line:int, _char:int, _error:typing.Union[InvalidSyntax, InvalidIndentation], details:typing.Optional=None) -> None:
        self.line, self.char, self.error = _line, _char, _error
        self.details = details

    @classmethod
    def char_error_marker(cls, _chr_num:int, _line:str, _error:typing.Union[InvalidSyntax, InvalidIndentation]) -> str:
        return f'{_line}\n{" "*(len(_error.__name__)+2)}{"-"*(_chr_num)}{"^"}'

    @property
    def gen_error(self) -> typing.Union[InvalidSyntax, InvalidIndentation]:
        return self.error(self.line, self.char, self.details)
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} '{self.error.__name__}'>"