import typing, state_objects, internal_errors
import caspian_errors, csp_types.caspian_types

class Compiler(csp_types.caspian_types.CompilerTypes):
    def __init__(self, stack_heap:'CaspianCompile') -> None:
        self.stack_heap = stack_heap

    @state_objects.log_errors
    def exec_BlockTokenGroup(self, _ast:'BlockTokenGroup', scope:state_objects.Scopes, scope_vars:state_objects.VariableScopes) -> state_objects.ExecStatus:
        for l_ast in _ast.tokenized_statements:
            if (l_len:=len(l_ast)) != 1:
                raise internal_errors.LRQueueLengthError(f"found queue ({l_ast}) with length != 1 ({l_len})")
            print(l_ast[0])
            print('token_group_name here', l_ast[0].pointer_next.state_exec_name)
        
        return state_objects.ExecStatus(finished = True)

    @classmethod
    def head_compile(cls, _stack_heap:'CaspianCompile', _ast:'BlockTokenGroup') -> None:
        c = cls(_stack_heap)
        _ = c.exec_BlockTokenGroup(_ast, state_objects.Scopes.MainBlock(), state_objects.VariableScopes())

        