import typing, collections, itertools
import caspian_errors, caspian_grammar
import re

class TokenizedLine:
    def __init__(self) -> None:
        self.token_line = collections.deque()

    def _remove_non_leading_whitespace(self) -> 'TokenizedLine':
        self.token_line = collections.deque([a for i, a in enumerate(self.token_line) if a != caspian_grammar.Token.Token.Space or not i])
        return self

    def restore_token(self, _token:caspian_grammar.Token) -> None:
        self.token_line.appendleft(_token)

    def __repr__(self) -> str:
        return f'<Tokenline: {", ".join(self.token_line)}>'

class Parser:
    def __init__(self, *args, **kwargs) -> None:
        self.stack = None
        
    def __enter__(self) -> None:
        return self
    
    def parse_line(self, _line_num:int, _line:str) -> typing.Union[caspian_errors.ErrorPacket, TokenizedLine]:
        _o_line, t_lines = _line, TokenizedLine()
        _char_count = 0
        while _line:
            for a, b in caspian_grammar.tokens:
                pass


    def parse(self, str_content:str) -> typing.Tuple[dict, typing.Union[caspian_errors.ErrorPacket, typing.List[TokenizedLine]]]:
        tokenized_lines = []
        for i, line in enumerate(filter(None, str_content.split('\n'))):
            if line:
                if isinstance((p_r:=self.parse_line(i, line)), caspian_errors.ErrorPacket):
                    return {'status':False}, p_r
                tokenized_lines.append(p_r)

        return {'status':True}, tokenized_lines

    def __exit__(self, *_) -> None:
        pass


if __name__ == '__main__':
    with open('testing_file.txt') as f, Parser() as p:
        print(p.parse(f.read()))

