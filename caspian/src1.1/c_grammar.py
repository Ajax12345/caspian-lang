import c_tokens, re
import collections, typing

__all__ = ('grammar', 'TOKEN')

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
    (TOKEN.NAME, re.compile(r'[a-zA-Z_](?:\w+)*\b')),
    (TOKEN.DOT, re.compile(r'\.\b')),
    (TOKEN.COLON, re.compile(r'\:\b')),
    (TOKEN.EQ.OP, re.compile(r'\=\=\b')),
    (TOKEN.NOT_EQ.OP, re.compile(r'\!\=\b')),
    (TOKEN.AMP.OP, re.compile(r'\&\b')),
    (TOKEN.F_CHAIN, re.compile(r'\|\>\b')),
    (TOKEN.PIPE.OP, re.compile(r'\|\b')),
    (TOKEN.GE.OP, re.compile(r'\>\=\b')),
    (TOKEN.LE.OP, re.compile(r'\<\=\b')),
    (TOKEN.LAMBDA, re.compile(r'\=\>\b')),
    (TOKEN.PLUS_EQ.IMP_OP, re.compile(r'\+\=\b')),
    (TOKEN.MINUS_EQ.IMP_OP, re.compile(r'\-\=\b')),
    (TOKEN.STAR_EQ.IMP_OP, re.compile(r'\*\=\b')),
    (TOKEN.DIV_EQ.IMP_OP, re.compile(r'/\=\b')),
    (TOKEN.MOD_EQ.IMP_OP, re.compile(r'%\=\b')),
    (TOKEN.INC.IMP, re.compile(r'\+\+\b')),
    (TOKEN.DEC.IMP, re.compile(r'\-\-\b')),
    (TOKEN.PLUS.OP, re.compile(r'\+\b')),
    (TOKEN.MINUS.OP, re.compile(r'\-\b')),
    (TOKEN.STAR.OP, re.compile(r'\*\b')),
    (TOKEN.DIV.OP, re.compile(r'/\b')),
    (TOKEN.MOD.OP, re.compile(r'%\b')),
    (TOKEN.ASSIGN.IMP_OP, re.compile(r'\=\b')),
    (TOKEN.LT.OP, re.compile(r'\<\b')),
    (TOKEN.GT.OP, re.compile(r'\>\b')),
    (TOKEN.SEMICOLON, re.compile(r'\;\b')),
    (TOKEN.IS.OP, re.compile(r'is\b')),
    (TOKEN.O_PAREN, re.compile(r'\(\b')),
    (TOKEN.C_PAREN, re.compile(r'\)\b')),
    (TOKEN.O_BRACKET, re.compile(r'\{\b')),
    (TOKEN.C_BRACKET, re.compile(r'\}\b')),
    (TOKEN.O_BRACE, re.compile(r'\[\b')),
    (TOKEN.C_BRACE, re.compile(r'\]\b')),
    (TOKEN.POUND, re.compile(r'#\b')),
    (TOKEN.CURLYQ, re.compile(r'~\b')),
    (TOKEN.COMMA, re.compile(r',\b')),
]

class Tokenizer:
    def __init__(self, src:str, c_ctx=None) -> None:
        self.src, self.c_ctx = src, c_ctx
        self._stream = self.token_stream(src)

    def token_stream(self, src:str) -> typing.Iterator:
        for i, a in enumerate(filter(None, src.split('\n')),1):
            ch_c, w_ind, s_w_ind = 0, 0, False
            while a:
                if (m:=next(((tk, re_m.group()) for tk, re_c in grammar if (re_m:=re_c.match(src)) is not None), None)) is None:
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
    print(grammar)