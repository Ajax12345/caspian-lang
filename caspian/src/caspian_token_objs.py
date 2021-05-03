import typing, collections, csp_types.caspian_types
import copy

__all__ = ('TokenMain',)

class TokenGroupAbout:
    def __init__(self, _token_head:typing.Union['TokenRoot', 'TokenGroup'], _group_name:typing.Union[str, None]) -> None:
        self.token, self.group_name = _token_head, _group_name
    
    def __str__(self) -> str:
        return f'{self.__class__.__name__}({self.token.raw_token_name}, {self.group_name})'

    @classmethod
    def form_token_about(cls, _token:typing.Union['TokenRoot', 'TokenGroup']) -> 'TokenGroupAbout':
        if _token.token_head is None:
            return 
        return cls(_token.token_head, _token.token_group_name)

    def __repr__(self) -> str:
        return str(self)

class TokenMain:
    class BlockTokenGroup(csp_types.caspian_types.BlockTokenGroup):
        __slots__ = ('body_lines', 'tokenized_statements')
        def __init__(self, body_lines:typing.List['TokenizedLine']=None) -> None:
            self.body_lines = body_lines
            self.tokenized_statements = None
        
        def __iter__(self) -> typing.Iterator:
            yield from self.body_lines

        def __call__(self, _lines:typing.List['TokenizedLine']) -> 'BlockTokenGroup':
            return self.__class__(_lines)

        def __eq__(self, _token:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> bool:
            return isinstance(_token, self.__class__)
            
        @classmethod
        def form_new_block(cls, _lines:typing.List['TokenizedLine']) -> 'BlockTokenGroup':
            return cls([i.decrement_whitespace() for i in _lines])

        def is_match(self, token_arr:'MatchQueue', multiline:bool=False, l_queue:'LRQueue' = None) -> typing.Tuple[typing.Union[None, 'TokenRoot'], bool]:
            if not token_arr:
                return token_arr, None, False

            if self == (t_p:=token_arr.pop()):
                return token_arr, t_p, True
            
            return token_arr, None, False

        def __repr__(self) -> str:
            if self.tokenized_statements is not None:
                return f'<{self.__class__.__name__} (tokenized_statements = {self.tokenized_statements})>'

            return f'<{self.__class__.__name__}>' if self.body_lines is None else f'<{self.__class__.__name__} ({(_l:=len(self.body_lines))} line{"s" if _l != 1 else ""})>'

    class TokenEOF(csp_types.caspian_types.TokenEOF):
        def __init__(self) -> None:
            raise Exception('Depreciated. Scheduled for removal')

        def __repr__(self) -> str:
            return f'<{self.__class__.__name__}>'

        def is_match(self, token_arr:'MatchQueue', multiline:bool=False, l_queue:'LRQueue' = None) -> typing.Tuple[typing.Union[None, 'TokenRoot'], bool]:
            if l_queue.peek() is None:
                return token_arr, None, True

            return token_arr, None, False
        
    class TokenRoot(csp_types.caspian_types.TokenRoot):
        def __init__(self, _name:str, matched_str:str = None, direct_match:str=None, non_matches:list = [], line_num:int = None, char_num:int = None, eof_flag:bool = False) -> None:
            self.name, self.direct_match = _name, direct_match
            self.non_matches = non_matches
            self.matched_str = matched_str
            self.line_num, self.char_num = line_num, char_num
            self.pointer_next, self.eof_flag = None, eof_flag
            self.head_chain = []

        def copy(self) -> 'TokenRoot':
            _c = self.__class__(self.name)
            _c.__dict__ = {a:b for a, b in self.__dict__.items()}
            return _c

        def set_token_head(self, _head:'TokenRoot') -> 'TokenGroup':
            _head = _head.copy()
            _head.pointer_next = self
            return _head

        @property
        def eof(self) -> 'TokenRoot':
            self.eof_flag = True
            return self

        def is_match(self, token_arr:'MatchQueue', multiline:bool=False, l_queue:'LRQueue' = None) -> typing.Tuple[typing.Union[None, 'TokenRoot'], bool]:
            if self.eof_flag and l_queue is not None and l_queue.peek() is not None:
                return token_arr, None, False
            
            if not token_arr:
                return token_arr, None, False

            if (t_p:=token_arr.pop()) == self:
                return token_arr, t_p, True
            
            return token_arr, None, False


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

        def __call__(self, _line_num:int, _char_num:int, _matched_val:str) -> 'TokenRoot':
            return self.__class__(self.name, matched_str = _matched_val, direct_match = self.direct_match, non_matches = self.non_matches, line_num = _line_num, char_num = _char_num, eof_flag = self.eof_flag)

        def neg_lookahead(self, _t_obj:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> 'TokenGroup':
            return TokenMain.TokenGroup(self).neg_lookahead(_t_obj)
        
        def lookahead(self, _t_obj:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> 'TokenGroup':
           return TokenMain.TokenGroup(self).lookahead(_t_obj)

        @property
        def raw_token_name(self) -> str:
            return self.name
            
        def __eq__(self, _token:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> bool:
            if self.name != _token.raw_token_name:
                return False

            if isinstance(_token, self.__class__):
                if _token.direct_match is not None:
                    return self.matched_str == _token.direct_match
                
                if self.matched_str is not None:
                    return self.matched_str not in _token.non_matches
                    
            return True

        def __ne__(self, _token:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> bool:
            return self.name != _token.raw_token_name

        def __and__(self, _t_group:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> 'TokenGroup':
            if isinstance(_t_group, TokenMain.TokenRoot) or not isinstance(_t_group, TokenMain.TokenGroup):
                return TokenMain.TokenGroup(self, _t_group)
            
            return _t_group.t_add_front(self)
            
        def __or__(self, _t_or:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> 'TokenOr':
            if isinstance(_t_or, TokenMain.TokenRoot) or not isinstance(_t_or, TokenMain.TokenOr):
                return TokenMain.TokenOr(self, _t_or)
            
            return _t_or.t_add_front(self)

        def __str__(self) -> str:
            return repr(self)

        def __repr__(self) -> str:
            if self.matched_str:
                return f"""Token({self.name}, m = '{self.matched_str}')"""

            if self.pointer_next is not None:
                return f"""Token({self.name}, pointer = {self.pointer_next})"""

            return f'Token({self.name})'

    class TokenGroup(csp_types.caspian_types.TokenGroup):
        '''Token&Token'''
        def __init__(self, *tokens:typing.List[typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']]) -> None:
            self.token_groups, self.token_head = collections.deque(tokens), None
            self.token_group_name = None
            self._neg_lookahead, self._lookahead = None, None
            self.token_search_ml = False
            self.head_chain = collections.deque()
        
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

        def __eq__(self, _token:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> bool:
            if self.token_head is None:
                return False

            return self.raw_token_name == _token.raw_token_name
             
        def set_token_head(self, _head:'TokenRoot') -> 'TokenGroup':
            _c = self.__class__()
            _c.__dict__ = {a:b for a, b in self.__dict__.items()}
            #_c.head_chain = collections.deque([TokenGroupAbout.form_token_about(_c), *_c.head_chain]) #possibly unecessary
            #_c.token_head = _head #possibly unecessary
            _h = _head.copy()
            _h.pointer_next = _c
            #return _c
            return _h

        def attach_block_results(self, _block:list) -> 'TokenGroup':
            tg = self.__class__()
            tg.__dict__ = {a:b for a, b in self.__dict__.items()}
            tg.ast_blocks = _block
            return tg

        def is_match(self, token_arr:'MatchQueue', multiline:bool=False, l_queue:'LRQueue' = None) -> typing.Tuple[typing.Union[None, 'TokenRoot'], bool]:
            if not self.token_search_ml and multiline:
                return token_arr, None, False
            
            if not token_arr:
                return token_arr, None, False
            
            if self._neg_lookahead is not None:
                _, _, s = self._neg_lookahead.is_match(l_queue.to_match_queue(reverse=True))
                if s:
                    return token_arr, None, False

            if self._lookahead is not None:
                _, _, s = self._lookahead.is_match(l_queue.to_match_queue(reverse=True))
                if not s:
                    return token_arr, None, False 

            block_t_results = collections.deque()
            for i in list(self.token_groups)[::-1]:
                t_arr, t_packet, m_status = i.is_match(token_arr.copy(), multiline = multiline, l_queue = l_queue)
                if not m_status:
                    return token_arr, None, False

                token_arr = t_arr

                block_t_results.appendleft(t_packet)
            
            return token_arr, self.attach_block_results(block_t_results), True
            
        @property
        def raw_token_name(self) -> str:
            return self.token_head.raw_token_name

        def __repr__(self) -> str:
            if not hasattr(self, 'ast_blocks'):
                return f'{self.__class__.__name__}(head={self.token_head}, group_name={self.token_group_name}, ml={self.token_search_ml}, heads = [{", ".join(map(str, self.head_chain))}], tokens={[*self.token_groups]})'
            
            return f'{self.__class__.__name__}(head={self.token_head}, group_name={self.token_group_name}, ml={self.token_search_ml}, heads = [{", ".join(map(str, self.head_chain))}], ast_blocks={self.ast_blocks})'
        

    class TokenOr(csp_types.caspian_types.TokenOr):
        '''Token|Token'''
        def __init__(self, *tokens:typing.List[typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']]) -> None:
            self.token_groups, self.token_head = collections.deque(tokens), None
            self.token_group_name = None
            self._neg_lookahead, self._lookahead = None, None
            self.token_search_ml = False

        def is_match(self, token_arr:'MatchQueue', multiline:bool=False, l_queue:'LRQueue' = None) -> typing.Tuple[typing.Union[None, 'TokenRoot'], bool]:
            if not self.token_search_ml and multiline:
                return token_arr, None, False
            
            if not token_arr:
                return token_arr, None, False
            
            for group in self.token_groups:
                t_arr, t_packet, m_status = group.is_match(token_arr.copy(), multiline = multiline, l_queue = l_queue)
                if m_status:
                    token_arr = t_arr
                    return token_arr, t_packet, m_status

            
            return token_arr, None, False

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