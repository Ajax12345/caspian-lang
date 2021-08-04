import typing, state_objects as so, internal_errors
import caspian_errors, csp_types.caspian_types
import default_objects, collections

class Compiler(csp_types.caspian_types.CompilerTypes):
    def __init__(self, stack_heap:'CaspianCompile') -> None:
        self.stack_heap = stack_heap

    @so.log_errors
    def exec_function_object(self, _ast:'TokenGroup', scope:so.Scopes, scope_vars:so.VariableScopes, _async:bool = False, _abstract:bool = False, _static:bool = False) -> so.ExecStatus:
        fun_block = _ast
        if fun_block.state_exec_name != 'FunctionBlock':
            while getattr((fun_block:=fun_block.ast_blocks[1] if hasattr(fun_block, 'ast_blocks') else fun_block.pointer_next), 'state_exec_name', None) != 'FunctionBlock':
                pass
        
        fun_sig = fun_block
        while (fs:=fun_sig.ast_blocks[0] if hasattr(fun_sig, 'ast_blocks') else fun_sig.pointer_next).state_exec_name in {None, 'FunctionStub'}:
            fun_sig = fs

        f_name_expr = fun_sig.ast_blocks[1].pointer_next.ast_blocks[0].pointer_next
        
        if not isinstance(scope, so.Scopes.ClassBlock):
            if _static:
                return so.ExecStatus(error=True, error_packet = caspian_errors.ErrorPacket(None, None, caspian_errors.ValueError, 'static function must be contained in a class'))
            
            if f_name_expr.state_exec_name == 'PrimativeSignature':
                return so.ExecStatus(error=True, error_packet = caspian_errors.ErrorPacket(None, None, caspian_errors.ValueError, 'primative function must be contained in a class'))
        

    @so.log_errors
    def exec_StaticAbstractFunctionBlock(self, _ast:'TokenGroup', scope:so.Scopes, scope_vars:so.VariableScopes) -> so.ExecStatus:
        return self.exec_function_object(_ast, scope, scope_vars, _abstract = True, _static = True)

    @so.log_errors
    def exec_StaticAsyncAbstractFunctionBlock(self, _ast:'TokenGroup', scope:so.Scopes, scope_vars:so.VariableScopes) -> so.ExecStatus:
        return self.exec_function_object(_ast, scope, scope_vars, _async = True, _abstract = True, _static = True)

    @so.log_errors
    def exec_StaticAsyncFunctionBlock(self, _ast:'TokenGroup', scope:so.Scopes, scope_vars:so.VariableScopes) -> so.ExecStatus:
        return self.exec_function_object(_ast, scope, scope_vars, _async = True, _static = True)

    @so.log_errors
    def exec_AsyncAbstractFunctionBlock(self, _ast:'TokenGroup', scope:so.Scopes, scope_vars:so.VariableScopes) -> so.ExecStatus:
        return self.exec_function_object(_ast, scope, scope_vars, _async = True, _abstract = True)

    @so.log_errors
    def exec_StaticFunctionBlock(self, _ast:'TokenGroup', scope:so.Scopes, scope_vars:so.VariableScopes) -> so.ExecStatus:
        return self.exec_function_object(_ast, scope, scope_vars, _static = True)

    @so.log_errors
    def exec_AbstractFunctionBlock(self, _ast:'TokenGroup', scope:so.Scopes, scope_vars:so.VariableScopes) -> so.ExecStatus:
        return self.exec_function_object(_ast, scope, scope_vars, _abstract = True)

    @so.log_errors
    def exec_AsyncFunctionBlock(self, _ast:'TokenGroup', scope:so.Scopes, scope_vars:so.VariableScopes) -> so.ExecStatus:
        return self.exec_function_object(_ast, scope, scope_vars, _async = True)

    @so.log_errors
    def exec_FunctionBlock(self, _ast:'TokenGroup', scope:so.Scopes, scope_vars:so.VariableScopes) -> so.ExecStatus:
        return self.exec_function_object(_ast, scope, scope_vars)

    @so.log_errors
    def exec_ValueLabel(self, _ast:'TokenGroup', scope:so.Scopes, scope_vars:so.VariableScopes) -> so.ExecStatus:
        if (r:=scope_vars[_ast.pointer_next.matched_str]):
            return so.ExecStatus(mem_pointer = r)

        return so.ExecStatus(error=True, error_packet = caspian_errors.ErrorPacket(None, None, caspian_errors.ValueError, f"'{_ast.pointer_next.matched_str}' is not defined"))

    @so.log_errors
    def exec_PrimativeSignature(self, _ast:'TokenGroup', scope:so.Scopes, scope_vars:so.VariableScopes) -> so.ExecStatus:
        if (p:=_ast.pointer_next.ast_blocks[-1].pointer_next).state_exec_name != 'ValueLabel':
            return so.ExecStatus(error=True, error_packet = caspian_errors.ErrorPacket(None, None, caspian_errors.ValueError, 'Primative signature must be a label'))

        return so.ExecStatus(mem_pointer=scope_vars['Primative', True].instantiate(p.pointer_next.matched_str))
    
    @so.log_errors
    def exec_String(self, _ast:'TokenGroup', scope:so.Scopes, scope_vars:so.VariableScopes) -> so.ExecStatus:
        return so.ExecStatus(mem_pointer=scope_vars['String', True].instantiate(_ast.matched_str[1:-1]))

    @so.log_errors
    def exec_Bool(self, _ast:'TokenGroup', scope:so.Scopes, scope_vars:so.VariableScopes) -> so.ExecStatus:
        return so.ExecStatus(mem_pointer=scope_vars['Bool', True].instantiate(_ast.matched_str == 'true'))

    @so.log_errors
    def exec_Null(self, _ast:'TokenGroup', scope:so.Scopes, scope_vars:so.VariableScopes) -> so.ExecStatus:
        return so.ExecStatus(mem_pointer=scope_vars['null', True].instantiate())

    @so.log_errors
    def exec_Float(self, _ast:'TokenGroup', scope:so.Scopes, scope_vars:so.VariableScopes) -> so.ExecStatus:
        return so.ExecStatus(mem_pointer=scope_vars['Float', True].instantiate(_ast.matched_str))

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
            #print('exec_response in block', self.stack_heap.heap[exec_response.mem_pointer].public)
            print(exec_response)
            if exec_response.exit_block:
                return exec_response

        return so.ExecStatus(finished = True)

    @classmethod
    def rightmost_nonterminal(cls, _ast:typing.Union['TokenRoot', 'TokenGroup']) -> 'TokenRoot':
        if hasattr(_ast, 'pointer_next'):
            if _ast.pointer_next is None:
                return _ast

            return cls.rightmost_nonterminal(_ast.pointer_next)
        
        if hasattr(_ast, 'tokenized_statements'):
            return cls.rightmost_nonterminal(_ast.tokenized_statements[-1])

        if hasattr(_ast, 'q_vals'):
            return cls.rightmost_nonterminal(_ast.q_vals[-1])
        
        return cls.rightmost_nonterminal(_ast.ast_blocks[-1])
        

    @classmethod
    def head_compile(cls, _stack_heap:'CaspianCompile', _ast:'BlockTokenGroup') -> None:
        c = cls(_stack_heap)
        status_result = c.exec_BlockTokenGroup(_ast, so.Scopes.MainBlock(), _stack_heap.var_scopes)
        #print('returned ExecStatus after compile', status_result)

        