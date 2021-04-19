import typing, collections, itertools
import caspian_errors, caspian_grammar
import re

class TokenizedLine:
    def __init__(self) -> None:
        self.token_line = collections.deque()
        self.whitespace_count = 0

    def remove_whitespace(self) -> 'TokenizedLine':
        self.token_line = collections.deque([i for i in self.token_line if i != caspian_grammar.Token.Space])
        return self

    def decrement_whitespace(self) -> 'TokenizedLine':
        self.whitespace_count -= 5
        return self

    def restore_token(self, _token:caspian_grammar.Token) -> None:
        self.token_line.appendleft(_token)

    def add_token(self, _token:caspian_grammar.Token) -> None:
        self.token_line.append(_token)

    def __repr__(self) -> str:
        return f'<Tokenline: {", ".join(map(str, self.token_line))}; indent={self.whitespace_count}>'

class Parser:
    def __init__(self, *args, **kwargs) -> None:
        self.stack = None
        
    def __enter__(self) -> 'Parser':
        return self
    
    def parse_line(self, _line_num:int, _line:str) -> typing.Union[caspian_errors.ErrorPacket, TokenizedLine]:
        _o_line, t_lines = _line, TokenizedLine()
        _char_count, seen_non_space = 0, False
        while _line:
            _f = False
            for t_p, _pattern in caspian_grammar.tokens:
                if (m:=_pattern.match(_line)) is not None:
                    _f = True
                    t_lines.add_token((full_token:=t_p(_line_num, _char_count, (m_val:=m.group()))))
                    if full_token != caspian_grammar.Token.Space:
                        if not seen_non_space and t_lines.whitespace_count%4:
                            return caspian_errors.ErrorPacket(_line_num, _char_count, caspian_errors.InvalidIndentation, self.stack, caspian_errors.ErrorPacket.char_error_marker(_char_count, _o_line, caspian_errors.InvalidIndentation))
                        seen_non_space = True
                    elif not seen_non_space:
                        t_lines.whitespace_count += 1
                    _char_count += (l:=len(m_val))
                    _line = _line[l:]
                    break

            if not _f:
                return caspian_errors.ErrorPacket(_line_num, _char_count, caspian_errors.InvalidSyntax, self.stack, caspian_errors.ErrorPacket.char_error_marker(_char_count, _o_line, caspian_errors.InvalidSyntax))
                
        return t_lines.remove_whitespace()


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

class ASTGen:
    def __enter__(self) -> 'ASTGen':
        return self


    def parse_group_block(self, _block:caspian_grammar.BlockTokenGroup) -> typing.Iterator:
        full_blocked_result, running_block = [], []
        for line in _block:
            if line.whitespace_count:
                running_block.append(line)
            else:
                if running_block:
                    yield (new_block:=caspian_grammar.BlockTokenGroup.form_new_block(running_block))
                    full_blocked_result.append(new_block)
                    running_block = []
                full_blocked_result.append(line)

        if running_block:
            yield (new_block:=caspian_grammar.BlockTokenGroup.form_new_block(running_block))
            full_blocked_result.append(new_block)
            running_block = []
        
        print(full_blocked_result)

    def create_ast(self, token_lines:typing.List[TokenizedLine]) -> caspian_grammar.BlockTokenGroup:
        block_head = caspian_grammar.BlockTokenGroup(token_lines)
        block_queue = collections.deque([block_head])
        while block_queue:
            for sub_block in self.parse_group_block(block_queue.popleft()):
                block_queue.append(sub_block)

        return block_head
    
    def __exit__(self, *_) -> None:
        pass


if __name__ == '__main__':
    with open('testing_file.txt') as f, Parser() as p, ASTGen() as astgen:
        status, _r_obj = p.parse(f.read())
        if not status['status']:
            print(_r_obj.gen_error)
        else:
            ast = astgen.create_ast(_r_obj)
        

