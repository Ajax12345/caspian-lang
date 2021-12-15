import typing

class TOKEN:
    def __init__(self, name:str) -> None:
        self.name = name
        self.parent = None
    
    def __call__(self, token:'TOKEN') -> 'TOKEN':
        if token.parent is None:
            token.parent = self
            return token

        return self(token.parent)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.name}, parent={self.parent})'

class TOKEN_BASE:
    def __init__(self) -> None:
        pass
    
    def __getattr__(self, t_name:str) -> TOKEN:
        return TOKEN(t_name)