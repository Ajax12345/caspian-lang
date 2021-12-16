import c_tokens, re
import collections, typing

__all__ = ('grammar', 'TOKEN', 'Tokenizer')

TOKEN = c_tokens.TOKEN_BASE()

grammar = [
    (TOKEN.WHITESPACE, re.compile(r'\s')),
    (TOKEN.FLOAT.VALUE, re.compile(r'\d+\.\d+\b')),
    (TOKEN.INT.VALUE, re.compile(r'\d+\b')),
    (TOKEN.STRING.VALUE, re.compile(r'".*?"')),
    (TOKEN.STRING.VALUE, re.compile(r"'.*?'")),
    (TOKEN.STRING.VALUE, re.compile(r"`.*?`")),
    (TOKEN.TRUE.BOOL.VALUE, re.compile(r'true\b')),
    (TOKEN.FALSE.BOOL.VALUE, re.compile(r'false\b')),
    (TOKEN.NULL.VALUE, re.compile(r'null\b')),
    (TOKEN.AND.OP, re.compile(r'and\b')),
    (TOKEN.OR.OP, re.compile(r'or\b')),
    (TOKEN.IN.OP, re.compile(r'or\b')),
    (TOKEN.NOT, re.compile(r'not\b')),
    (TOKEN.AS, re.compile(r'as\b')),
    (TOKEN.FUN, re.compile(r'fun\b')),
    (TOKEN.YIELD, re.compile(r'yield\b')),
    (TOKEN.FROM, re.compile(r'from\b')),
    (TOKEN.RETURN, re.compile(r'return\b')),
    (TOKEN.AWAIT, re.compile(r'await\b')),
    (TOKEN.ASYNC, re.compile(r'async\b')),
    (TOKEN.ABSTRACT, re.compile(r'abstract\b')),
    (TOKEN.STATIC, re.compile(r'abstract\b')),
    (TOKEN.IF, re.compile(r'if\b')),
    (TOKEN.ELIF, re.compile(r'elif\b')),
    (TOKEN.ELIF, re.compile(r'else\b')),
    (TOKEN.SWITCH, re.compile(r'switch\b')),
    (TOKEN.CASE, re.compile(r'switch\b')),
    (TOKEN.DEFAULT, re.compile(r'switch\b')),
    (TOKEN.WHILE, re.compile(r'while\b')),
    (TOKEN.DO, re.compile(r'do\b')),
    (TOKEN.FOR, re.compile(r'for\b')),
    (TOKEN.SUPPRESS, re.compile(r'suppress\b')),
    (TOKEN.THEN, re.compile(r'then\b')),
    (TOKEN.FINALLY, re.compile(r'then\b')),
    (TOKEN.RAISE, re.compile(r'raise\b')),
    (TOKEN.IMPORT, re.compile(r'import\b')),
    (TOKEN.CLASS, re.compile(r'class\b')),
    (TOKEN.AT, re.compile(r'@\b')),
    (TOKEN.PRIMATIVE, re.compile(r'primative\b')),
    (TOKEN.INHERITS, re.compile(r'inherits\b')),
    (TOKEN.PASS, re.compile(r'pass\b')),
    (TOKEN.BREAK, re.compile(r'break\b')),
    (TOKEN.CONTINUE, re.compile(r'continue\b')),
    (TOKEN.NAME.VALUE, re.compile(r'[a-zA-Z_](?:\w+)*\b')),
    (TOKEN.DOT, re.compile(r'\.')),
    (TOKEN.COLON, re.compile(r'\:')),
    (TOKEN.EQ.OP, re.compile(r'\=\=')),
    (TOKEN.NOT_EQ.OP, re.compile(r'\!\=')),
    (TOKEN.AMP.OP, re.compile(r'\&')),
    (TOKEN.F_CHAIN, re.compile(r'\|\>')),
    (TOKEN.PIPE.OP, re.compile(r'\|')),
    (TOKEN.GE.OP, re.compile(r'\>\=')),
    (TOKEN.LE.OP, re.compile(r'\<\=')),
    (TOKEN.LAMBDA, re.compile(r'\=\>')),
    (TOKEN.PLUS_EQ.IMP_OP, re.compile(r'\+\=')),
    (TOKEN.MINUS_EQ.IMP_OP, re.compile(r'\-\=')),
    (TOKEN.STAR_EQ.IMP_OP, re.compile(r'\*\=')),
    (TOKEN.DIV_EQ.IMP_OP, re.compile(r'/\=')),
    (TOKEN.MOD_EQ.IMP_OP, re.compile(r'%\=')),
    (TOKEN.INC.IMP, re.compile(r'\+\+')),
    (TOKEN.DEC.IMP, re.compile(r'\-\-')),
    (TOKEN.PLUS.OP, re.compile(r'\+')),
    (TOKEN.MINUS.OP, re.compile(r'\-')),
    (TOKEN.STAR.OP, re.compile(r'\*')),
    (TOKEN.DIV.OP, re.compile(r'/')),
    (TOKEN.MOD.OP, re.compile(r'%')),
    (TOKEN.ASSIGN.IMP_OP, re.compile(r'\=')),
    (TOKEN.LT.OP, re.compile(r'\<')),
    (TOKEN.GT.OP, re.compile(r'\>')),
    (TOKEN.SEMICOLON, re.compile(r'\;')),
    (TOKEN.IS.OP, re.compile(r'is\b')),
    (TOKEN.O_PAREN, re.compile(r'\(')),
    (TOKEN.C_PAREN, re.compile(r'\)')),
    (TOKEN.O_BRACKET, re.compile(r'\{')),
    (TOKEN.C_BRACKET, re.compile(r'\}')),
    (TOKEN.O_BRACE, re.compile(r'\[')),
    (TOKEN.C_BRACE, re.compile(r'\]')),
    (TOKEN.POUND, re.compile(r'#')),
    (TOKEN.CURLYQ, re.compile(r'~')),
    (TOKEN.COMMA, re.compile(r',')),
]

class Tokenizer:
    def __init__(self, src:str, c_ctx=None) -> None:
        self.src, self.c_ctx = src, c_ctx
        self._stream = self.token_stream(src)
        self.consumed_stream = collections.deque()
    
    def __iter__(self) -> typing.Iterator:
        yield from self._stream

    def release_token(self, token:TOKEN) -> None:
        self.consumed_stream.appendleft(token)

    def peek(self) -> typing.Union[None, 'TOKEN']:
        if self.consumed_stream:
            return self.consumed_stream[0]
        
        if (t:=next(self._stream, None)) is not None:
            self.consumed_stream.append(t)
            return self.consumed_stream[0]
        
    def consume(self) -> typing.Union[None, 'TOKEN']:
        if self.consumed_stream:
            return self.consumed_stream.popleft()

        if (t:=next(self._stream, None)) is not None:
            return t
        

    def match(self, token:TOKEN) -> bool:
        if self.consumed_stream:
            if self.consumed_stream[0].matches(token):
                return self.consumed_stream.popleft()
        else:
            if (t:=next(self._stream, None)) is not None:
                if t.matches(token):
                    return t
                self.consumed_stream.append(t)
        
    def token_stream(self, src:str) -> typing.Iterator:
        for i, a in enumerate(src.split('\n'),1):
            if (a:=re.sub('//[\w\W]+', '', a)):
                ch_c, w_ind, s_w_ind = 0, 0, False
                while a:
                    if (m:=next(((tk, re_m.group()) for tk, re_c in grammar if (re_m:=re_c.match(a)) is not None), None)) is None:
                        raise Exception(f'At line {i}, near {ch_c}: Invalid syntax')
                    if not m[0].matches(TOKEN.WHITESPACE):
                        if not s_w_ind:
                            yield TOKEN.INDENT(w_ind, i, 0)
                        w_ind, s_w_ind = 0, True
                        yield m[0](m[1], i, ch_c)
                    elif not s_w_ind:
                        w_ind += 1
                    a = a[(l:=len(m[1])):]
                    ch_c += l
                yield TOKEN.EOL
                

if __name__ == '__main__':
    with open('test_file.txt') as f:
        t = Tokenizer(f.read())