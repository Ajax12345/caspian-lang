import typing, state_objects, internal_errors
import caspian_errors

class Compiler:
    def __init__(self, stack_heap:'CaspianCompile') -> None:
        self.stack_heap = stack_heap

    @state_objects.log_errors
    def exec_BlockTokenGroup(self, _ast:'BlockTokenGroup', scope:state_objects.Scopes) -> state_objects.ExecStatus:
        pass

    @classmethod
    def head_compile(cls, _stack_heap:'CaspianCompile', _ast:'BlockTokenGroup') -> None:
        c = cls(_stack_heap)
        _ = c.exec_BlockTokenGroup(_ast, state_objects.Scopes.MainBlock)

        