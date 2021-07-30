import typing, state_objects as so, internal_errors
import caspian_errors, csp_types.caspian_types
import default_objects

class Compiler(csp_types.caspian_types.CompilerTypes):
    def __init__(self, stack_heap:'CaspianCompile') -> None:
        self.stack_heap = stack_heap

    @so.log_errors
    def exec_Integer(self, _ast:'TokenGroup', scope:so.Scopes, scope_vars:so.VariableScopes) -> so.ExecStatus:
        return so.ExecStatus(mem_pointer=scope_vars['Integer', True].instantiate(_ast.matched_str))

    @so.log_errors
    def exec_Expr(self, _ast:'TokenGroup', scope:so.Scopes, scope_vars:so.VariableScopes) -> so.ExecStatus:
        return getattr(self, f'exec_{_ast.pointer_next.state_exec_name}')(_ast.pointer_next, scope, scope_vars)

    @so.log_errors
    def exec_PassStmn(self, _ast:'TokenGroup', scope:so.Scopes, scope_vars:so.VariableScopes) -> so.ExecStatus:
        return so.ExecStatus(pass_stmn = True)        

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

            if not hasattr(self, f'exec_{l_ast[0].state_exec_name}'):
                return so.ExecStatus(error=True, error_packet = caspian_errors.ErrorPacket((rm_term:=self.__class__.rightmost_nonterminal(l_ast[0])).line_num, rm_term.char_num, caspian_errors.InvalidSyntax, caspian_errors.ErrorPacket.char_error_marker(rm_term.char_num, self.stack_heap.lines.get(rm_term.line_num, ''), caspian_errors.InvalidSyntax)))
            
            exec_response = getattr(self, f'exec_{l_ast[0].state_exec_name}')(l_ast[0], scope, scope_vars)
            print('exec_response in block', exec_response)
            if exec_response.exit_block:
                return exec_response

        return so.ExecStatus(finished = True)

    @classmethod
    def rightmost_nonterminal(cls, _ast:typing.Union['TokenRoot', 'TokenGroup']) -> 'TokenRoot':
        if hasattr(_ast, 'pointer_next'):
            if _ast.pointer_next is None:
                return _ast

            return cls.rightmost_nonterminal(_ast.pointer_next)
        
        return cls.rightmost_nonterminal(_ast.ast_blocks[-1])
        

    @classmethod
    def head_compile(cls, _stack_heap:'CaspianCompile', _ast:'BlockTokenGroup') -> None:
        c = cls(_stack_heap)
        status_result = c.exec_BlockTokenGroup(_ast, so.Scopes.MainBlock(), _stack_heap.var_scopes)
        #print('returned ExecStatus after compile', status_result)

        