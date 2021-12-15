import typing

class TOKEN:
    def __init__(self, name:str, parent:'TOKEN'=None, value:typing.Union[int, str]=None, line:int = None, ch:int=None) -> None:
        self.name = name
        self.parent = parent
        self.value = value
        self.line, self.ch = line, ch

    def __getattr__(self, name:str) -> 'TOKEN':
        if self.parent is None:
            self.parent = TOKEN(name)
            return self

        getattr(self.parent, name)
        return self
    
    def match(self, token:'TOKEN', strict:bool=True) -> bool:
        if self.name == token.name:
            return True
        
        if not strict:
            p = self.parent
            while p is not None:
                if p.name == token.name:
                    return True
                p = p.parent

        return False

    def __call__(self, value:typing.Any, line:typing.Optional[int]=None, ch:typing.Optional[int]=None) -> 'TOKEN':
        return TOKEN(self.name, value, line, ch)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.name}, parent={self.parent})'

class TOKEN_BASE:
    def __init__(self) -> None:
        pass
    
    def __getattr__(self, t_name:str) -> TOKEN:
        return TOKEN(t_name)

if __name__ == '__main__':
    print(TOKEN('TRUE').BOOL.VALUE)