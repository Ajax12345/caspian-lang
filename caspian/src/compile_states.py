import typing, state_objects, internal_errors
import caspian_errors, csp_types.caspian_types

class Compiler(csp_types.caspian_types.CompilerTypes):
    def __init__(self, stack_heap:'CaspianCompile') -> None:
        self.stack_heap = stack_heap

    @state_objects.log_errors
    def exec_BlockTokenGroup(self, _ast:'BlockTokenGroup', scope:state_objects.Scopes, scope_vars:state_objects.VariableScopes) -> state_objects.ExecStatus:
        print('in exec_BlockTokenGroup')
        print(scope)
        print(scope_vars)

    @classmethod
    def head_compile(cls, _stack_heap:'CaspianCompile', _ast:'BlockTokenGroup') -> None:
        c = cls(_stack_heap)
        _ = c.exec_BlockTokenGroup(_ast, state_objects.Scopes.MainBlock(), state_objects.VariableScopes())

        