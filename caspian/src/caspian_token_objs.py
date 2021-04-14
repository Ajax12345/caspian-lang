import typing, collections

__all__ = ('TokenMain',)

class TokenMain:
    class TokenRoot:
        def __init__(self, _name:str) -> None:
            self.name = _name
        
        def _(self, _label:str) -> 'TokenGroup':
            t = TokenMain.TokenGroup(self)
            t.token_group_name = _label
            return t

        @property
        def raw_token_name(self) -> str:
            return self.name
            
        def __eq__(self, _token:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> bool:
            return self.name == _token.raw_token_name

        def __add__(self, _t_group:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> 'TokenGroup':
            if isinstance(_t_group, TokenMain.TokenRoot):
                return TokenMain.TokenGroup(self, _t_group)

            return _t_group.t_add_front(self)
            

        def __repr__(self) -> str:
            return f'Token({self.name})'

    class TokenGroup:
        '''Token&Token'''
        def __init__(self, *tokens:typing.List[typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']]) -> None:
            self.token_groups, self.token_head = collections.deque(tokens), None
            self.token_group_name = None

        def t_add_front(self, _t:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> 'TokenGroup':
            self.token_groups.appendleft(_t)
            return self

        def t_add_back(self, _t:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> 'TokenGroup':
            self.token_groups.append(_t)
            return self

        def _(self, _label:str) -> 'TokenGroup':
            self.token_group_name = _label
            return self

        def __add__(self, _t_group:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> 'TokenGroup':
            return self.t_add_back(_t_group)
        
        @property
        def raw_token_name(self) -> str:
            return self.token_head.raw_token_name

        def __repr__(self) -> str:
            return f'{self.__class__.__name__}(head={self.token_head}, group_name={self.token_group_name}, tokens={self.token_groups})'

        

    class TokenOr:
        '''Token|Token'''
        def __init__(self, *tokens:typing.List[typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']]) -> None:
            self.token_groups, self.token_head = collections.deque(tokens), None
            self.token_group_name = None

        @property
        def raw_token_name(self) -> str:
            return self.token_head.raw_token_name

        def t_add_front(self, _t:typing.List[typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']]) -> 'TokenOr':
            self.token_groups.appendleft(_t)
            return self

        def t_add_back(self, _t:typing.List[typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']]) -> 'TokenOr':
            self.token_groups.append(_t)
            return self
        
        def _(self, _label:str) -> 'TokenOr':
            self.token_group_name = _label
            return self


        def __add__(self, _t_group:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> 'TokenGroup':
            return self.t_add_back(_t_group)

        def __repr__(self) -> str:
            return f'{self.__class__.__name__}(head={self.token_head}, group_name={self.token_group_name}, tokens={self.token_groups})'


    class TokenBase:
        def __init__(self) -> None:
            pass

        def __getattr__(self, _t_name:str) -> 'TokenRoot':
            return TokenMain.TokenRoot(_t_name)