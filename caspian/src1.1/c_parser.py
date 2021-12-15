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

    def consume_if_custom_true(self, m_fun:typing.Callable) -> typing.Union[None, 'TOKEN']:
        if m_fun(self.peek()):
            return self.consume()

    def consume_if_eq(self, token:TOKEN) -> typing.Union[None, 'TOKEN']:
        pass
    
    def consume_if_true_or_exception(self, token:TOKEN) -> TOKEN:
        if (t:=self.consume()) is not None and t.matches(token):
            return t

        raise Exception(f'Invalid Syntax (expecting {token})')

    def consume_if_true(self, token:TOKEN) -> typing.Union['TOKEN', None]:
        if (t:=self.peek()) is not None and t.matches(token):
            return self.consume()


    def body(self, indent=TOKEN.INDENT(0)) -> c_ast.Body:
        body = []
        while True:
            if self.peek() is None or self.check_if_custom_true(lambda t:t.matches(TOKEN.INDENT) and t.value < indent.value):
                return c_ast.Body(body=body)
            if self.check_if_custom_true(lambda t:t.matches(TOKEN.INDENT) and t.value > indent.value):
                raise Exception('invalid indent')
            
            self.consume_if_true_or_exception(TOKEN.INDENT)
            while True:
                body.append(self.statement())
                if self.consume_if_true(TOKEN.EOL) is not None:
                    break
                self.consume_if_true_or_exception(TOKEN.SEMICOLON)
        
        raise Exception('Invalid syntax (got to end of body while without return)')
            
            

if __name__ == "__main__":
    with open('test_file.txt') as f:
        p = Parser(Tokenizer(f.read()))
        print(p.body())