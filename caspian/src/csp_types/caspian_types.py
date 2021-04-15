import typing, abc

class TokenRoot(abc.ABC):
    @abc.abstractmethod
    def _(self, _label:str) -> 'TokenGroup':
        '''converts basic token to group, asigns an op name'''

    @abc.abstractmethod
    def match(self, _m_str:str) -> 'TokenRoot':
        '''sets raw parsed value to be matched'''

    @abc.abstractmethod
    def neg_lookahead(self, _t_obj:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> 'TokenGroup':
        '''set negative lookahead for token match'''

    @abc.abstractmethod 
    def lookahead(self, _t_obj:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> 'TokenGroup':
        '''set (positive) lookahead for token match'''

class TokenGroup(abc.ABC):
    @abc.abstractmethod
    def t_add_front(self, _t:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> 'TokenGroup':
        '''add token subgroup to front of token group'''

    @abc.abstractmethod
    def t_add_back(self, _t:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> 'TokenGroup':
        '''add token subgroup to back of token group'''

    @abc.abstractmethod
    def _(self, _label:str) -> 'TokenGroup':
        '''assign op name to group'''

    @abc.abstractmethod
    def neg_lookahead(self, _t_obj:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> 'TokenGroup':
        '''set negative lookahead for token match'''

    @abc.abstractmethod 
    def lookahead(self, _t_obj:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> 'TokenGroup':
        '''set (positive) lookahead for token match'''

class TokenOr(abc.ABC):
    @abc.abstractmethod
    def t_add_front(self, _t:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> 'TokenGroup':
        '''add token subgroup to front of token group'''

    @abc.abstractmethod
    def t_add_back(self, _t:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> 'TokenGroup':
        '''add token subgroup to back of token group'''

    @abc.abstractmethod
    def _(self, _label:str) -> 'TokenGroup':
        '''assign op name to group'''

    @abc.abstractmethod
    def neg_lookahead(self, _t_obj:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> 'TokenOr':
        '''set negative lookahead for token match'''

    @abc.abstractmethod 
    def lookahead(self, _t_obj:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> 'TokenOr':
        '''set (positive) lookahead for token match'''