import typing

class Ast:
    def __init__(self, **kwargs) -> None:
        self.vals = kwargs

    def __getattr__(self, attr:str) -> typing.Any:
        return self.vals[attr]

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.vals})'

class Import(Ast):
    pass

class Body(Ast):
    pass