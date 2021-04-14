import re, typing
from caspian_token_objs import *

__all__ = ('Token', 'tokens', 'grammar')

Token = TokenMain.TokenBase()

tokens = [
    (Token.Space, r'^\s+'),
    (Token.Label, r'^[a-zA-Z_]{1}(?:[a-zA-Z0-9_])+'),
    (Token.String, r'^".*?"'),
    (Token.String, r"^'.*?'"),
    (Token.String, r'^`.*?`'),
    (Token.Float, r'^\d+\.\d+'),
    (Token.Integer, r'^\d+'),
    (Token.OParen, r'^\('),
    (Token.CParen, r'^\)'),
    (Token.OBracket, r'^\['),
    (Token.CBracket, r'^\]'),
    (Token.OBrace, r'^\{'),
    (Token.CBrace, r'^\}'),
    (Token.Slash, r'^/'),
    (Token.Plus, r'^\+'),
    (Token.Minus, r'^\-'),
    (Token.Star, r'^\*'),
    (Token.Mod, r'^%'),
    (Token.Eq, r'^\='),
    (Token.LArrow, r'^\<'),
    (Token.RArrow, r'^\>'),
    (Token.Not, r'^\!'),
    (Token.And, r'^\&'),
    (Token.Or, r'^\|'),
    (Token.Comma, r'^,'),
    (Token.Colon, r'^:'),
    (Token.Dot, r'^\.'),
    (Token.Pound, r'^#'),
    (Token.At, r'^@')
]

grammar = [
    (Token.Expr, Token.Label._('name'))
]