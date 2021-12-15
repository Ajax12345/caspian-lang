import typing

class Body:
    def __init__(self, **kwargs) -> None:
        self.vals = kwargs
        
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.vals})'