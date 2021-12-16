import typing, c_ast
from c_grammar import * 

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
        return (t:=self.peek()) is not None and t.matches(token)

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

    def consume_if_true(self, token:TOKEN) -> typing.Union['TOKEN', None]:
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
        
        return c_ast.Import(path=[i.value for i in path], alias=alias.value if alias is not None else None, line=path[0].line)

    def parse_comma_separated_items(self, end:typing.Union[None, 'TOKEN']=None) -> c_ast.CommaSeparatedItems:
        items = []
        while True:
            if (i:=self.parse_expr(TOKEN.INDENT)) is None:
                break
            items.append(i)
            if self.consume_if_true(TOKEN.COMMA) is None:
                break
            elif self.consume_if_true(TOKEN.EOL):
                self.consume_if_true(TOKEN.INDENT)

            self.consume_if_true(TOKEN.EOL)
        if end is not None:
            self.consume_if_true_or_exception(end)
        return c_ast.CommaSeparatedItems(items = items)

    def parse_expr(self, indent:'TOKEN', t_priority=None, stmnt:typing.Optional[bool] = False) -> c_ast.Expr:
        value = None
        while not self.check_if_true(TOKEN.EOL):
            if self.consume_if_true(TOKEN.O_PAREN):
                v = c_ast.ParenItems(items=self.parse_comma_separated_items(TOKEN.C_PAREN))
                if value is None:
                    value = v
                else:
                    value = c_ast.Call(obj = value, signature = v)

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
                print('got t in here', t.value)
                value = t

            elif self.consume_if_true(TOKEN.DOT):
                if value is None:
                    self.consume_if_true_or_exception(TOKEN.DOT)
                    unpack=c_ast.ArrayUnpack if not self.consume_if_true(TOKEN.DOT) else c_ast.MapUnpack
                    value = unpack(container=self.parse_expr(indent, t_priority=priorities[TOKEN.DOT.name], stmnt=stmnt))
                value = c_ast.GetAttr(obj=value, attr=self.consume_if_true_or_exception(TOKEN.NAME))

            
            elif (t:=self.consume_if_custom_true(lambda x:x.name in operators)):
                if t_priority is not None and priorities[t.name] < t_priority:
                    self.release_token(t)
                    return value

                if (v:=self.parse_expr(indent, t_priority=priorities[t.name], stmnt=stmnt)) is None:
                    raise Exception('syntax error')

                if t.matches(TOKEN.IMP_OP): 
                    if t.matches(TOKEN.ASSIGN):
                        return (c_ast.Assign if stmnt else c_ast.AssignParam)(obj = value, value = v)
                    
                    return c_ast.ImpOp(obj=value, operator = t, value = v)

                value = c_ast.Operation(operand1=value, operator=t, operand2 = v)
            
            elif (t:=self.consume_if_true(TOKEN.COLON)):
                if value is None:
                    raise Exception('Syntax error, got colon without previous value')

                value = c_ast.KeyValue(key=value, value=self.parse_expr(indent, t_priority = priorities[t.name], stmnt=stmnt))

            elif (t:=self.consume_if_true(TOKEN.IMP)):
                if value is None:
                    raise Exception('Syntax error, got in-place op without value')
                
                self.check_if_custom_true_or_exception(lambda x:x.matches(TOKEN.EOL) or x.matches(TOKEN.SEMICOLON))
                return c_ast.InPlace(obj=value, operator=t)

            elif (t:=self.consume_if_true(TOKEN.AWAIT)):
                if value is not None:
                    raise Exception('invalid syntax (got await with value not none)')
                
                value = c_ast.AsyncAwait(obj = self.parse_expr(indent, t_priority=priorities[t.name], stmnt = stmnt))

            else:
                return value

        return value
            

    def parse_fun(self, indent:'TOKEN.INDENT', **kwargs:dict) -> c_ast.Fun:
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
            return_type = self.parse_expr()

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


    def statement(self, indent:'TOKEN.INDENT') -> c_ast.Ast:
        if (t:=self.consume_if_true(TOKEN.IMPORT)) is not None:
            return self.parse_import()
        
        if (t:=self.consume_if_true(TOKEN.PASS)) is not None:
            return c_ast.Pass(line=t.line)
        
        if (t:=self.consume_if_true(TOKEN.FUN)) is not None:
            return self.parse_fun(indent)

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
                    yield (n2:=next(n_c), str(b.value))
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
