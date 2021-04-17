import typing, collections, csp_types.caspian_types

__all__ = ('TokenMain',)

class TokenMain:
    class BlockTokenGroup(csp_types.caspian_types.BlockTokenGroup):
        def __init__(self) -> None:
            self.indent, self.indent_level = None, None
            self.lines = collections.deque()
        
        def __call__(self, indent:typing.Optional[bool]=False, indent_level:typing.Optional[int]=0) -> 'BlockTokenGroup':
            self.indent, self.indent_level = indent, indent_level
            return self

        def __repr__(self) -> str:
            return f'{self.__class__.__name__}(indent={self.indent}, ind_level = {self.indent_level})'

    class TokenEOF(csp_types.caspian_types.TokenEOF):
        def __repr__(self) -> str:
            return f'<{self.__class__.__name__}>'
        
    class TokenRoot(csp_types.caspian_types.TokenRoot):
        def __init__(self, _name:str) -> None:
            self.name, self.direct_match = _name, None
            self.non_matches = []

        def match(self, _m_str:str) -> 'TokenRoot':
            self.direct_match = _m_str
            return self

        def nonmatch(self, *args:typing.List[str]) -> 'TokenRoot':
            self.non_matches.extend(list(args))
            return self
        
        def _(self, _label:str) -> 'TokenGroup':
            t = TokenMain.TokenGroup(self)
            t.token_group_name = _label
            return t

        def neg_lookahead(self, _t_obj:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> 'TokenGroup':
            return TokenMain.TokenGroup(self).neg_lookahead(_t_obj)
        
        def lookahead(self, _t_obj:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> 'TokenGroup':
           return TokenMain.TokenGroup(self).lookahead(_t_obj)

        @property
        def raw_token_name(self) -> str:
            return self.name
            
        def __eq__(self, _token:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> bool:
            return self.name == _token.raw_token_name

        def __and__(self, _t_group:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> 'TokenGroup':
            if isinstance(_t_group, TokenMain.TokenRoot) or not isinstance(_t_group, TokenMain.TokenGroup):
                return TokenMain.TokenGroup(self, _t_group)
            
            return _t_group.t_add_front(self)
            
        def __or__(self, _t_or:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> 'TokenOr':
            if isinstance(_t_or, TokenMain.TokenRoot) or not isinstance(_t_or, TokenMain.TokenOr):
                return TokenMain.TokenOr(self, _t_or)
            
            return _t_or.t_add_front(self)


        def __repr__(self) -> str:
            return f'Token({self.name})'

    class TokenGroup(csp_types.caspian_types.TokenGroup):
        '''Token&Token'''
        def __init__(self, *tokens:typing.List[typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']]) -> None:
            self.token_groups, self.token_head = collections.deque(tokens), None
            self.token_group_name = None
            self._neg_lookahead, self._lookahead = None, None
            self.token_search_ml = False
        
        def t_add_front(self, _t:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> 'TokenGroup':
            self.token_groups.appendleft(_t)
            return self

        def t_add_back(self, _t:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> 'TokenGroup':
            self.token_groups.append(_t)
            return self

        def _(self, _label:str) -> 'TokenGroup':
            self.token_group_name = _label
            return self

        def neg_lookahead(self, _t_obj:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> 'TokenGroup':
            self._neg_lookahead = _t_obj
            return self
        
        def lookahead(self, _t_obj:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> 'TokenGroup':
            self._lookahead = _t_obj
            return self

        @property
        def ml(self) -> 'TokenGroup':
            self.token_search_ml = True
            return self

        def __and__(self, _t_group:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> 'TokenGroup':
            return self.t_add_back(_t_group)

        def __or__(self, _t_or:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> 'TokenOr':
            return TokenMain.TokenOr(self, _t_or)
        
        @property
        def raw_token_name(self) -> str:
            return self.token_head.raw_token_name

        def __repr__(self) -> str:
            return f'{self.__class__.__name__}(head={self.token_head}, group_name={self.token_group_name}, ml={self.token_search_ml}, tokens={[*self.token_groups]})'

        

    class TokenOr(csp_types.caspian_types.TokenOr):
        '''Token|Token'''
        def __init__(self, *tokens:typing.List[typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']]) -> None:
            self.token_groups, self.token_head = collections.deque(tokens), None
            self.token_group_name = None
            self._neg_lookahead, self._lookahead = None, None
            self.token_search_ml = False

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

        def neg_lookahead(self, _t_obj:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> 'TokenOr':
            self._neg_lookahead = _t_obj
            return self
        
        def lookahead(self, _t_obj:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> 'TokenOr':
            self._lookahead = _t_obj
            return self

        @property
        def ml(self) -> 'TokenOr':
            self.token_search_ml = True
            return self
            

        def __and__(self, _t_group:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> 'TokenGroup':
            return TokenMain.TokenGroup(self, _t_group)

        def __or__(self, _t_or:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> 'TokenOr':
            return self.t_add_back(_t_or)

        def __repr__(self) -> str:
            return f'{self.__class__.__name__}(head={self.token_head}, group_name={self.token_group_name}, ml={self.token_search_ml}, tokens={[*self.token_groups]})'


    class TokenBase:
        def __init__(self) -> None:
            pass

        def __getattr__(self, _t_name:str) -> 'TokenRoot':
            return TokenMain.TokenRoot(_t_name)