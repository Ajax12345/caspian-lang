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
    def exec_StaticAbstractFunctionBlock(self, _ast:'BlockTokenGroup', scope:'state_objects.Scopes', scope_vars:'state_objects.VariableScopes') -> 'state_objects.ExecStatus':
        '''loads a static abstract function into memory'''

    @abc.abstractmethod
    def exec_StaticAsyncAbstractFunctionBlock(self, _ast:'BlockTokenGroup', scope:'state_objects.Scopes', scope_vars:'state_objects.VariableScopes') -> 'state_objects.ExecStatus':
        '''loads a static async abstract function into memory'''

    @abc.abstractmethod
    def exec_StaticAsyncFunctionBlock(self, _ast:'BlockTokenGroup', scope:'state_objects.Scopes', scope_vars:'state_objects.VariableScopes') -> 'state_objects.ExecStatus':
        '''loads a static async function into memory'''

    @abc.abstractmethod
    def exec_AsyncAbstractFunctionBlock(self, _ast:'BlockTokenGroup', scope:'state_objects.Scopes', scope_vars:'state_objects.VariableScopes') -> 'state_objects.ExecStatus':
        '''loads a async abstract function into memory'''

    @abc.abstractmethod
    def exec_StaticFunctionBlock(self, _ast:'BlockTokenGroup', scope:'state_objects.Scopes', scope_vars:'state_objects.VariableScopes') -> 'state_objects.ExecStatus':
        '''loads a static function into memory'''

    @abc.abstractmethod
    def exec_AbstractFunctionBlock(self, _ast:'BlockTokenGroup', scope:'state_objects.Scopes', scope_vars:'state_objects.VariableScopes') -> 'state_objects.ExecStatus':
        '''loads a abstract function into memory'''

    @abc.abstractmethod
    def exec_AsyncFunctionBlock(self, _ast:'BlockTokenGroup', scope:'state_objects.Scopes', scope_vars:'state_objects.VariableScopes') -> 'state_objects.ExecStatus':
        '''loads a async function into memory'''

    @abc.abstractmethod
    def exec_FunctionBlock(self, _ast:'BlockTokenGroup', scope:'state_objects.Scopes', scope_vars:'state_objects.VariableScopes') -> 'state_objects.ExecStatus':
        '''loads a function into memory'''

    @abc.abstractmethod
    def exec_ValueLabel(self, _ast:'BlockTokenGroup', scope:'state_objects.Scopes', scope_vars:'state_objects.VariableScopes') -> 'state_objects.ExecStatus':
        '''runs a lookup in scope vars for a specific label name and if found, returns the memory pointer'''

    @abc.abstractmethod
    def exec_PrimativeSignature(self, _ast:'BlockTokenGroup', scope:'state_objects.Scopes', scope_vars:'state_objects.VariableScopes') -> 'state_objects.ExecStatus':
        '''instantiates an Py2Caspian Primative object and returns the memory pointer'''

    @abc.abstractmethod
    def exec_String(self, _ast:'BlockTokenGroup', scope:'state_objects.Scopes', scope_vars:'state_objects.VariableScopes') -> 'state_objects.ExecStatus':
        '''instantiates an Py2Caspian String object and returns the memory pointer'''

    @abc.abstractmethod
    def exec_Null(self, _ast:'BlockTokenGroup', scope:'state_objects.Scopes', scope_vars:'state_objects.VariableScopes') -> 'state_objects.ExecStatus':
        '''instantiates an Py2Caspian Null object and returns the memory pointer'''

    @abc.abstractmethod
    def exec_Bool(self, _ast:'BlockTokenGroup', scope:'state_objects.Scopes', scope_vars:'state_objects.VariableScopes') -> 'state_objects.ExecStatus':
        '''instantiates an Py2Caspian Bool object and returns the memory pointer'''

    @abc.abstractmethod
    def exec_Float(self, _ast:'BlockTokenGroup', scope:'state_objects.Scopes', scope_vars:'state_objects.VariableScopes') -> 'state_objects.ExecStatus':
        '''instantiates an Py2Caspian Float object and returns the memory pointer'''

    @abc.abstractmethod
    def exec_Integer(self, _ast:'BlockTokenGroup', scope:'state_objects.Scopes', scope_vars:'state_objects.VariableScopes') -> 'state_objects.ExecStatus':
        '''instantiates an Py2Caspian Integer object and returns the memory pointer'''

    @abc.abstractmethod
    def exec_Expr(self, _ast:'BlockTokenGroup', scope:'state_objects.Scopes', scope_vars:'state_objects.VariableScopes') -> 'state_objects.ExecStatus':
        '''runs the contents of an expression block'''

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