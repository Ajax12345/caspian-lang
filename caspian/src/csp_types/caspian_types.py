import typing, abc

class TokenEOF(abc.ABC):
    pass

class BlockTokenGroup(abc.ABC):
    pass

class TokenRoot(abc.ABC):
    @abc.abstractmethod
    def _(self, _label:str) -> 'TokenGroup':
        '''converts basic token to group, asigns an op name'''

    @abc.abstractmethod
    def match(self, _m_str:str) -> 'TokenRoot':
        '''sets raw parsed value to be matched'''

    @abc.abstractmethod
    def nonmatch(self, *args:typing.List[str]) -> 'TokenRoot':
        '''sets values to be matched against'''

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


class CompilerTypes(abc.ABC):
    @abc.abstractmethod
    def exec_PassStmn(self, _ast:'BlockTokenGroup', scope:'state_objects.Scopes', scope_vars:'state_objects.VariableScopes') -> 'state_objects.ExecStatus':
        '''executes a `continue` statement'''

    @abc.abstractmethod
    def exec_Continue(self, _ast:'BlockTokenGroup', scope:'state_objects.Scopes', scope_vars:'state_objects.VariableScopes') -> 'state_objects.ExecStatus':
        '''executes a `continue` statement'''

    @abc.abstractmethod
    def exec_Break(self, _ast:'BlockTokenGroup', scope:'state_objects.Scopes', scope_vars:'state_objects.VariableScopes') -> 'state_objects.ExecStatus':
        '''executes a `break` statement'''

    @abc.abstractmethod
    def exec_Stmn(self, _ast:'BlockTokenGroup', scope:'state_objects.Scopes', scope_vars:'state_objects.VariableScopes') -> 'state_objects.ExecStatus':
        '''takes in a Stmn @_ast and delegates to sub statement exec'''

    @abc.abstractmethod
    def exec_BlockTokenGroup(self, _ast:'BlockTokenGroup', scope:'state_objects.Scopes', scope_vars:'state_objects.VariableScopes') -> 'state_objects.ExecStatus':
        '''takes in an @_ast set to a BlockTokenGroup and traverses _ast.tokenized_statements'''