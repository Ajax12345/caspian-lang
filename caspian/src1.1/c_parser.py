import typing, c_ast
from c_grammar import * 

def _(ast:typing.Union[None, c_ast.Ast], message:typing.Optional[typing.Union[None, str]]=None) -> c_ast.Ast:
    if ast is None:
        raise Exception('syntax error' if message is None else message)
    
    return ast

class Parser:
    def __init__(self, tokenizer:Tokenizer) -> None:
        self.tokenizer = tokenizer

    def peek(self) -> typing.Union[None, 'TOKEN']:
        return self.tokenizer.peek()

    def consume(self) -> typing.Union[None, 'TOKEN']:
        return self.tokenizer.consume()
    
    def check_if_custom_true(self, m_fun:typing.Callable) -> typing.Union[None, 'TOKEN']:
        return m_fun(self.peek())

    def check_if_custom_true_or_exception(self, m_fun:typing.Callable) -> typing.Union[None, 'TOKEN']:
        if m_fun(self.peek()):
            return True
        
        raise Exception('Syntax error')

    def check_if_true(self, token:'TOKEN') -> bool:
        return (t:=self.peek()) is not None and (t.matches(token) if not isinstance(token, tuple) else any(t.matches(i) for i in token))

    def consume_if_custom_true(self, m_fun:typing.Callable) -> typing.Union[None, 'TOKEN']:
        if m_fun(self.peek()):
            return self.consume()

    def consume_if_custom_true_or_exception(self, m_fun:typing.Callable) -> typing.Union[None, 'TOKEN']:
        if m_fun(self.peek()):
            return self.consume()

        raise Exception('Invalid Syntax')

    def consume_if_eq(self, token:TOKEN) -> typing.Union[None, 'TOKEN']:
        pass
    
    def consume_if_true_or_exception(self, token:TOKEN) -> TOKEN:
        if (t:=self.consume()) is not None and t.matches(token):
            return t

        raise Exception(f'Invalid Syntax (expecting {token})')

    def check_if_true_or_exception(self, token:TOKEN) -> TOKEN:
        if (t:=self.peek()) is not None and t.matches(token):
            return t

        raise Exception(f'Invalid Syntax (expecting {token})')

    def release_token(self, token:TOKEN) -> None:
        self.tokenizer.release_token(token)

    def consume_if_true(self, token:typing.Union['TOKEN', typing.Tuple['TOKEN']]) -> typing.Union['TOKEN', None]:
        if isinstance(token, tuple):
            if (t:=self.peek()) is not None and any(t.matches(i) for i in token):
                return self.consume()

            return

        if (t:=self.peek()) is not None and t.matches(token):
            return self.consume()

    def parse_import(self) -> c_ast.Import:
        path, alias = [], None
        while True:
            path.append(self.consume_if_true_or_exception(TOKEN.NAME))
            if self.consume_if_true(TOKEN.DOT) is None:
                break
        
        if self.consume_if_true(TOKEN.AS) is not None:
            alias = self.consume_if_true_or_exception(TOKEN.NAME)
        
        return c_ast.Import(path=path, alias=alias.value if alias is not None else None, line=path[0].line)

    def parse_comma_separated_items(self, end:typing.Union[None, 'TOKEN']=None) -> c_ast.CommaSeparatedItems:
        items = []
        while True:
            if (i:=self.parse_expr(TOKEN.INDENT)) is None:
                break
            items.append(i)
            if self.check_if_custom_true(lambda x:x.matches(TOKEN.FOR) or x.matches(TOKEN.ASYNC)):
                if len(items) != 1:
                    raise Exception('invalid syntax in comprehension')
                loop_bodies = []
                while True:
                    aio = False
                    if (t:=self.consume()).matches(TOKEN.ASYNC):
                        aio=True
                        self.consume_if_true_or_exception(TOKEN.FOR)
                    if (loop_param:=self.parse_expr(None)) is None:
                        raise Exception('expecting loop param in comprehension')
                    self.consume_if_true_or_exception(TOKEN.IN)
                    if (iter_obj:=self.parse_expr(None, terminate=TOKEN.IF)) is None:
                        raise Exception('expecting iter object in comprehension')
                    loop_bodies.append((c_ast.ComprehensionBlock if not aio else c_ast.AsyncComprehensionBlock)(loop_param = loop_param, iter_obj = iter_obj))
                    if self.check_if_true(end):
                        self.consume()
                        return c_ast.Comprehension(value=items[0], body=loop_bodies, condition=None)
                    if self.consume_if_true(TOKEN.IF):
                        if (condition:=self.parse_expr(None)) is None:
                            raise Exception("Expecting conditional in comprehension")
                        self.consume_if_true_or_exception(end)
                        return c_ast.Comprehension(value=items[0], body=loop_bodies, condition=condition)
                
            if self.consume_if_true(TOKEN.COMMA) is None:
                break
            elif self.consume_if_true(TOKEN.EOL):
                self.consume_if_true(TOKEN.INDENT)

            self.consume_if_true(TOKEN.EOL)
        if end is not None:
            self.consume_if_true_or_exception(end)
        return c_ast.CommaSeparatedItems(items = items)

    def parse_expr(self, indent:'TOKEN', t_priority=None, stmnt:typing.Optional[bool] = False, terminate:typing.Optional['TOKEN']=None) -> c_ast.Expr:
        value = None
        while not self.check_if_true(TOKEN.EOL):
            if terminate is not None and self.check_if_true(terminate):
                return value
            if self.consume_if_true(TOKEN.O_PAREN):
                v = c_ast.ParenItems(items=self.parse_comma_separated_items(TOKEN.C_PAREN))
                if value is None:
                    value = v
                else:
                    value = c_ast.Call(obj = value, signature = v)

                print('after o paren', value, terminate)

            elif self.consume_if_true(TOKEN.O_BRACE):
                v = c_ast.BraceItems(items=self.parse_comma_separated_items(TOKEN.C_BRACE))
                if value is None:
                    value = v
                else:
                    value = c_ast.GetItem(obj = value, signature = v)

            elif self.consume_if_true(TOKEN.O_BRACKET):
                if value is not None:
                    raise Exception('got bracket object with value already set')

                value = c_ast.BracketItems(items=self.parse_comma_separated_items(TOKEN.C_BRACKET))

            elif self.consume_if_true(TOKEN.POUND):
                if value is not None:
                    raise Exception('got pound object with value already set')
                if self.consume_if_true(TOKEN.O_BRACE):
                    value = c_ast.ImmutableContainer(container=self.parse_comma_separated_items(TOKEN.C_BRACE))
                elif self.consume_if_true(TOKEN.O_BRACKET):
                    value = c_ast.ImmutableContainer(container=self.parse_comma_separated_items(TOKEN.C_BRACKET))
                else:
                    raise Exception('Immutability syntax error')

            elif (t:=self.consume_if_true(TOKEN.VALUE)):
                value = t

            elif self.consume_if_true(TOKEN.DOT):
                if value is None:
                    self.consume_if_true_or_exception(TOKEN.DOT)
                    unpack=c_ast.ArrayUnpack if not self.consume_if_true(TOKEN.DOT) else c_ast.MapUnpack
                    value = unpack(container=self.parse_expr(indent, t_priority=priorities[TOKEN.DOT.name], stmnt=stmnt, terminate=terminate))
                else:
                    value = c_ast.GetAttr(obj=value, attr=self.consume_if_true_or_exception(TOKEN.NAME))

            
            elif (t:=self.consume_if_custom_true(lambda x:x.name in operators)):
                if t.matches(TOKEN.MINUS) and value is None:
                    value = c_ast.NegVal(obj=self.parse_expr(indent, t_priority=5, stmnt = stmnt, terminate=terminate))
                    continue

                if t_priority is not None and priorities[t.name] < t_priority:
                    self.release_token(t)
                    return value

                if (v:=self.parse_expr(indent, t_priority=priorities[t.name], stmnt=stmnt, terminate=terminate)) is None:
                    raise Exception('syntax error')

                if t.matches(TOKEN.IMP_OP): 
                    if t.matches(TOKEN.ASSIGN):
                        return (c_ast.Assign if stmnt else c_ast.AssignParam)(obj = value, value = v)
                    
                    return c_ast.ImpOp(obj=value, operator = t, value = v)

                value = c_ast.Operation(operand1=value, operator=t, operand2 = v)
            
            elif (t:=self.consume_if_true(TOKEN.COLON)):
                if value is None:
                    raise Exception('Syntax error, got colon without previous value')

                if self.consume_if_true(TOKEN.COLON):
                    if not value.matches(TOKEN.PRIMATIVE):
                        raise Exception('invalid primative identifier')

                    print('got in here!', value)
                    value = c_ast.Primative(name=self.consume_if_true_or_exception(TOKEN.NAME))
                else:
                    value = c_ast.KeyValue(key=value, value=self.parse_expr(indent, t_priority = priorities[t.name], stmnt=stmnt, terminate=terminate))

            elif (t:=self.consume_if_true(TOKEN.IMP)):
                if value is None:
                    raise Exception('Syntax error, got in-place op without value')
                
                self.check_if_custom_true_or_exception(lambda x:x.matches(TOKEN.EOL) or x.matches(TOKEN.SEMICOLON))
                return c_ast.InPlace(obj=value, operator=t)

            elif (t:=self.consume_if_true(TOKEN.AWAIT)):
                if value is not None:
                    raise Exception('invalid syntax (got await with value not none)')
                
                value = c_ast.AsyncAwait(obj = self.parse_expr(indent, t_priority=priorities[t.name], stmnt = stmnt, terminate=terminate))

            elif (t:=self.consume_if_true(TOKEN.NOT)):
                if value is not None:
                    raise Exception('invalid syntax (got not with value not none)')
                
                value = c_ast.NotOp(obj = self.parse_expr(indent, t_priority=priorities[t.name], stmnt = stmnt, terminate=terminate))

            elif (t:=self.consume_if_true(TOKEN.LAMBDA)):
                if value is None:
                    raise Exception('Invalid Syntax')

                if self.consume_if_true(TOKEN.POUND):
                    self.consume_if_true_or_exception(TOKEN.EOL)
                    body = self.body(TOKEN.INDENT(self.peek().value))
                    self.release_token(TOKEN.EOL)
                    value = c_ast.MultiLineLambda(params = value, body = body)
                    continue 

                if (f:=self.parse_expr(indent)) is None:
                    raise Exception('Invalid syntax')
                
                value = c_ast.Lambda(params = value, body=f)

            elif (t:=self.consume_if_true(TOKEN.CURLYQ)):
                if value is None:
                    raise Exception('Invalid syntax')

                value = c_ast.AssignExpr(obj=value, value=self.parse_expr(indent, t_priority=5))

            elif (t:=self.consume_if_true(TOKEN.IF)):
                if (condition:=self.parse_expr(indent)) is None:
                    raise Exception('inline conditional cannot be none')

                self.consume_if_true_or_exception(TOKEN.ELSE)
                if (else_val:=self.parse_expr(indent)) is None:
                    raise Exception('inline conditional else cannot be none')
                
                return c_ast.Conditional(value=value, condition=condition, default=else_val)

            else:
                return value

        return value
            

    def parse_fun(self, indent:'TOKEN.INDENT', **kwargs:dict) -> c_ast.Fun:
        kwargs = {'async':False, 'abstract':False, 'static':False, **kwargs}
        primative = False
        name = None
        settings, signature, return_type = None, None, None
        body = None
        if self.consume_if_true(TOKEN.PRIMATIVE):
            primative = True
            self.consume_if_true_or_exception(TOKEN.COLON)
            self.consume_if_true_or_exception(TOKEN.COLON)

        name = self.consume_if_true_or_exception(TOKEN.NAME)
        if self.consume_if_true(TOKEN.O_BRACE):
            settings = self.parse_comma_separated_items(end=TOKEN.C_BRACE)
        
        self.consume_if_true_or_exception(TOKEN.O_PAREN)
        signature = self.parse_comma_separated_items(end=TOKEN.C_PAREN)
        if self.consume_if_true(TOKEN.COLON):
            return_type = self.parse_expr(indent)

        self.consume_if_true_or_exception(TOKEN.EOL)
        body = self.body(TOKEN.INDENT(indent.value+4))
        self.release_token(TOKEN.EOL)
        return c_ast.Fun(name=name.value,
                        primative=primative, 
                        settings=settings, 
                        signature=signature, 
                        return_type=return_type, 
                        body=body, 
                        **kwargs)

    def parse_for(self, indent:TOKEN) -> c_ast.For:
        if (loop_param:=self.parse_expr(indent)) is None:
            raise Exception('Invalid syntax (for loop expecting iter result target)')

        self.consume_if_true_or_exception(TOKEN.IN)
        if (iter_obj:=self.parse_expr(indent)) is None:
            raise Exception('Invalid syntax (expecting iter object)')

        self.consume_if_true_or_exception(TOKEN.EOL)
        body = self.body(TOKEN.INDENT(indent.value+4))
        self.release_token(TOKEN.EOL)
        return c_ast.For(loop_param = loop_param, iter_obj = iter_obj, body=body)

    def parse_syntactic_sugar_callables(self, indent, _callable:bool=False) -> c_ast.Ast:
        d = [self.consume().name.lower()]
        while (t1:=self.consume_if_true((TOKEN.ASYNC, TOKEN.STATIC, TOKEN.ABSTRACT))):
            if t1.name.lower() in d:
                raise Exception('Invalid syntax')
            d.append(t1.name.lower())
        
        if not all(d.index(a) < d.index(b) for _a, _b in fun_flags if (a:=_a.name.lower()) in d and (b:=_b.name.lower()) in d):
            raise Exception('Invalid syntax (misplaced function identifiers)')
        
        if self.consume_if_true(TOKEN.FUN):
            f = self.parse_fun(indent, **{i:True for i in d})
            if 'async' in d:
                return c_ast.AsyncFun(fun=f)
            return f

        if self.consume_if_true(TOKEN.CLASS):
            if (invalid_fields:=[j for j in ['static', 'async'] if j in d]):
                raise Exception('Invalid syntax')
            
            return self.parse_class(indent, abstract = True)

        if not _callable:
            if self.consume_if_true(TOKEN.FOR):
                if 'async' not in d or len(d) > 1:
                    raise Exception('invalid syntax')

                return c_ast.AsyncFor(for_loop = self.parse_for(indent))

    def parse_callable(self, indent) -> c_ast.Ast:
        if self.consume_if_true(TOKEN.FUN):
            return self.parse_fun(indent)

        if self.consume_if_true(TOKEN.CLASS):
            return self.parse_class(indent)

        if (t:=self.check_if_true((TOKEN.ASYNC, TOKEN.STATIC, TOKEN.ABSTRACT))):
            if (t:=self.parse_syntactic_sugar_callables(indent, True)):
                return t

    def parse_class(self, indent, abstract:bool = False) -> c_ast.Ast:
        name = self.consume_if_true_or_exception(TOKEN.NAME)
        inherits = []
        if self.consume_if_true(TOKEN.INHERITS):
            while True:
                inherits.append(self.consume_if_true_or_exception(TOKEN.NAME))
                if self.check_if_true(TOKEN.EOL):
                    break
                self.consume_if_true_or_exception(TOKEN.COMMA)
        
        self.consume_if_true(TOKEN.EOL)
        if not (c_body:=self.body(TOKEN.INDENT(indent.value+4))).body:
            raise Exception('Missing body of class statement')
        
        self.release_token(TOKEN.EOL)
        return c_ast.Class(name = name, 
                            inherits = inherits, 
                            abstract = abstract, 
                            body = c_body)
        
    def statement(self, indent:'TOKEN.INDENT') -> c_ast.Ast:
        if (t:=self.consume_if_true(TOKEN.IMPORT)) is not None:
            return self.parse_import()
        
        if (t:=self.consume_if_true(TOKEN.PASS)) is not None:
            return c_ast.Pass(line=t.line)

        if (t:=self.consume_if_true(TOKEN.BREAK)) is not None:
            return c_ast.Break()

        if (t:=self.consume_if_true(TOKEN.CONTINUE)) is not None:
            return c_ast.Break()
        
        if (t:=self.consume_if_true(TOKEN.FUN)) is not None:
            return self.parse_fun(indent)

        if (t:=self.consume_if_true(TOKEN.FOR)) is not None:
            return self.parse_for(indent)

        if (t:=self.consume_if_true(TOKEN.RETURN)) is not None:
            return c_ast.Return(expr=self.parse_expr(indent))
        
        if (t:=self.consume_if_true(TOKEN.YIELD)) is not None:
            return (c_ast.YieldFrom if self.consume_if_true(TOKEN.FROM) else c_ast.Yield)(expr=self.parse_expr(indent))

        if (t:=self.consume_if_true(TOKEN.RAISE)) is not None:
            return c_ast.RaiseException(exception=self.parse_expr(indent))

        if (t:=self.check_if_true((TOKEN.ASYNC, TOKEN.STATIC, TOKEN.ABSTRACT))):
            if (t:=self.parse_syntactic_sugar_callables(indent)):
                return t

            raise Exception('invalid syntax')

        if (t:=self.check_if_true(TOKEN.AT)):
            wrappers = []
            while True:
                if not self.consume_if_true(TOKEN.AT):
                    break
                wrappers.append(self.parse_expr(indent,stmnt=True))
                self.consume_if_true_or_exception(TOKEN.EOL)
                if self.check_if_custom_true(lambda t:t.matches(TOKEN.INDENT) and t.value > indent.value):
                    raise Exception('invalid indent')
            
                self.consume_if_true_or_exception(TOKEN.INDENT)

            if (wrapped:=self.parse_callable(indent)) is None:
                raise Exception("'@' requires a callable")
            
            return c_ast.DecoratedCallable(wrappers=wrappers, wrapped=wrapped)

        if (t:=self.consume_if_true(TOKEN.WHILE)):
            condition = self.parse_expr(indent, stmnt=True)
            self.consume_if_true_or_exception(TOKEN.EOL)
            if not (body:=self.body(TOKEN.INDENT(indent.value+4))).body:
                raise Exception('Missing body of while loop')

            self.release_token(TOKEN.EOL)
            return c_ast.WhileLoop(condition=condition, body=body)

        if (t:=self.consume_if_true(TOKEN.DO)):
            self.consume_if_true_or_exception(TOKEN.EOL)
            if not (body:=self.body(TOKEN.INDENT(indent.value+4))).body:
                raise Exception('Missing body of do-while loop')

            self.consume_if_true_or_exception(TOKEN.INDENT)
            self.consume_if_true_or_exception(TOKEN.WHILE)
            return c_ast.DoWhileLoop(condition=self.parse_expr(indent, stmnt=True), body=body)

        if (t:=self.consume_if_true(TOKEN.IF)):
            if_condition = _(self.parse_expr(indent, stmnt=True))
            self.consume_if_true_or_exception(TOKEN.EOL)
            if not (if_body:=self.body(TOKEN.INDENT(indent.value+4))).body:
                raise Exception('Missing body of if statement')
            
            elif_statements, else_body = [], None
            while True:
                ind = self.consume_if_true(TOKEN.INDENT)
                if self.consume_if_true(TOKEN.ELSE):
                    self.consume_if_true_or_exception(TOKEN.EOL)
                    if not (e_body:=self.body(TOKEN.INDENT(indent.value+4))).body:
                        raise Exception('Missing body of else statement')
                    else_body = e_body
                    break
                
                if self.consume_if_true(TOKEN.ELIF):
                    elif_condition = _(self.parse_expr(indent, stmnt=True))
                    self.consume_if_true_or_exception(TOKEN.EOL)
                    if not (e_body:=self.body(TOKEN.INDENT(indent.value+4))).body:
                        raise Exception('Missing body of else statement')

                    elif_statements.append(c_ast.ElifCondition(condition = elif_condition, body = e_body))
                    continue

                self.release_token(ind)
                break
            self.release_token(TOKEN.EOL)
            return c_ast.IfStatement(condition = if_condition, body=if_body, elif_statements = elif_statements, else_body = else_body)

        if (t:=self.consume_if_true(TOKEN.SWITCH)):
            s_parameter = _(self.parse_expr(indent, stmnt=True))
            cases, default = [], None
            self.consume_if_true_or_exception(TOKEN.EOL)
            while True:
                if self.peek() is not None and not (ind:=self.consume_if_custom_true(lambda x:x.matches(TOKEN.INDENT) and x.value==indent.value+4)):
                    break

                if self.consume_if_true(TOKEN.CASE):
                    c_parameter = _(self.parse_expr(ind, stmnt=True))
                    self.consume_if_true_or_exception(TOKEN.EOL)
                    if not (c_body:=self.body(TOKEN.INDENT(indent.value+8))).body:
                        raise Exception('Missing body of case statement')

                    cases.append(c_ast.CaseStatement(parameter = c_parameter, body = c_body))
                    continue
                
                if self.consume_if_true(TOKEN.DEFAULT):
                    self.consume_if_true_or_exception(TOKEN.EOL)
                    if not (d_body:=self.body(TOKEN.INDENT(indent.value+8))).body:
                        raise Exception('Missing body of default statement')

                    default = d_body
                    break
                    
                break

            self.release_token(TOKEN.EOL)
            return c_ast.SwitchCase(parameter = s_parameter, cases = cases, default = default)

        if (t:=self.consume_if_true(TOKEN.SUPPRESS)):
            params, then_params = self.parse_expr(indent, stmnt=True), None
            then_body = None
            self.consume_if_true_or_exception(TOKEN.EOL)
            if not (s_body:=self.body(TOKEN.INDENT(indent.value+4))).body:
                raise Exception('Missing body of suppress statement')

            if self.peek() is not None and (ind:=self.consume_if_custom_true(lambda x:x.matches(TOKEN.INDENT) and x.value == indent.value)):
                if self.consume_if_true(TOKEN.THEN):
                    then_params = self.parse_expr(ind, stmnt=True)
                    self.consume_if_true_or_exception(TOKEN.EOL)
                    if not (then_body:=self.body(TOKEN.INDENT(indent.value+4))).body:
                        raise Exception('Missing body of then statement')

                else:
                    self.release_token(ind)

            self.release_token(TOKEN.EOL)
            return c_ast.Suppress(params = params, body = s_body, then_params = then_params, then_body = then_body)        
            
        if (t:=self.consume_if_true(TOKEN.CLASS)):
            return self.parse_class(indent)

        return self.parse_expr(indent, stmnt = True)

    def body(self, indent=TOKEN.INDENT(0)) -> c_ast.Body:
        body = []
        while True:
            if self.peek() is None or self.check_if_custom_true(lambda t:t.matches(TOKEN.INDENT) and t.value < indent.value):
                return c_ast.Body(body=body)
            if self.check_if_custom_true(lambda t:t.matches(TOKEN.INDENT) and t.value > indent.value):
                raise Exception('invalid indent')
            
            self.consume_if_true_or_exception(TOKEN.INDENT)
            while True:
                body.append(self.statement(indent))
                if self.consume_if_true(TOKEN.EOL) is not None:
                    break
                self.consume_if_true_or_exception(TOKEN.SEMICOLON)
        
        raise Exception('Invalid syntax (got to end of body while without return)')
            
            

if __name__ == "__main__":
    import itertools as it
    import matplotlib.pyplot as plt
    import networkx as nx, gen_ast_tree
    a_g, n_c = nx.Graph(), it.count(1)
    
    def display_ast(g, ast, p = None):
        if isinstance(ast, list):
            for i in ast:
                if isinstance(i, c_ast.Ast):
                    yield from display_ast(g, i, p)
                else:
                    yield (n1:=next(n_c), i.value)
                    g.add_node(n1)
                    g.add_edge(p, n1)
        else:
            yield (n:=next(n_c), ast.__class__.__name__)
            g.add_node(n)
            if p is not None:
                g.add_edge(p, n)
            p = n
            for a, b in ast.vals.items():
                yield (n1:=next(n_c), a)
                g.add_node(n1)
                g.add_edge(p, n1)
                if isinstance(b, (c_ast.Ast, list)):
                    if b is not None:
                        yield from display_ast(g, b, n1)
                else:
                    yield (n2:=next(n_c), str(b if b is None or isinstance(b, (str, int)) else b.value))
                    g.add_node(n2)
                    g.add_edge(n1, n2)

    with open('test_file.txt') as f:
        p = Parser(Tokenizer(f.read()))
        body = p.body()
        print(body)
        labels = dict(display_ast(a_g, body))
        pos = gen_ast_tree.hierarchy_pos(a_g,1)    
        nx.draw(a_g, pos, labels=labels, with_labels = True)
        plt.show()
