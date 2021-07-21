import typing, state_objects as so, internal_errors
import caspian_errors, csp_types.caspian_types

class Compiler(csp_types.caspian_types.CompilerTypes):
    def __init__(self, stack_heap:'CaspianCompile') -> None:
        self.stack_heap = stack_heap

    @so.log_errors
    def exec_Continue(self, _ast:'TokenGroup', scope:so.Scopes, scope_vars:so.VariableScopes) -> so.ExecStatus:
        if not isinstance(scope, (so.Scopes.WhileBlock, so.Scopes.ForBlock)):
            return so.ExecStatus(error=True, error_packet = caspian_errors.ErrorPacket(_ast.ast_blocks[0].line_num, _ast.ast_blocks[0].char_num, caspian_errors.InvalidSyntax, "'continue' must be inside loop"))

        return so.ExecStatus(exit_block = True, exit_stmn = so.BlockExits.Continue)        


    @so.log_errors
    def exec_Break(self, _ast:'TokenGroup', scope:so.Scopes, scope_vars:so.VariableScopes) -> so.ExecStatus:
        if not isinstance(scope, (so.Scopes.WhileBlock, so.Scopes.ForBlock)):
            return so.ExecStatus(error=True, error_packet = caspian_errors.ErrorPacket(_ast.ast_blocks[0].line_num, _ast.ast_blocks[0].char_num, caspian_errors.InvalidSyntax, "'break' must be inside loop"))

        return so.ExecStatus(exit_block = True, exit_stmn = so.BlockExits.Break)        

    @so.log_errors
    def exec_Stmn(self, _ast:'TokenGroup', scope:so.Scopes, scope_vars:so.VariableScopes) -> so.ExecStatus:
        return getattr(self, f'exec_{_ast.pointer_next.state_exec_name}')(_ast.pointer_next, scope, scope_vars)

    @so.log_errors
    def exec_BlockTokenGroup(self, _ast:'BlockTokenGroup', scope:so.Scopes, scope_vars:so.VariableScopes) -> so.ExecStatus:
        for l_ast in _ast.tokenized_statements:
            if (l_len:=len(l_ast)) != 1:
                raise internal_errors.LRQueueLengthError(f"found queue ({l_ast}) with length != 1 ({l_len})")

            exec_response = getattr(self, f'exec_{l_ast[0].state_exec_name}')(l_ast[0], scope, scope_vars)
            if exec_response.exit_block:
                return exec_response

        return so.ExecStatus(finished = True)

    @classmethod
    def head_compile(cls, _stack_heap:'CaspianCompile', _ast:'BlockTokenGroup') -> None:
        c, var_scopes = cls(_stack_heap), so.VariableScopes()
        _ = c.exec_BlockTokenGroup(_ast, so.Scopes.MainBlock(), var_scopes)


        