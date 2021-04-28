import typing, collections, itertools
import caspian_errors, caspian_grammar
import re, copy

class TokenizedLine:
    def __init__(self) -> None:
        self.token_line = collections.deque()
        self.whitespace_count = 0

    def remove_whitespace(self) -> 'TokenizedLine':
        self.token_line = collections.deque([i for i in self.token_line if i != caspian_grammar.Token.Space])
        return self

    def decrement_whitespace(self) -> 'TokenizedLine':
        self.whitespace_count -= 4
        return self

    def restore_token(self, _token:caspian_grammar.Token) -> None:
        self.token_line.appendleft(_token)

    def add_token(self, _token:caspian_grammar.Token) -> None:
        self.token_line.append(_token)

    def __iter__(self) -> typing.Iterator:
        yield from self.token_line

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

class MatchQueue:
    def __init__(self, *_start_queue:typing.Iterable, op_queue:collections.deque=collections.deque(), op_count:int = 0) -> None:
        self.queue = collections.deque([*_start_queue])
        self.op_queue, self.op_count = op_queue, op_count
        self.previous, self.found_match = None, False
    
    def pop(self) -> caspian_grammar.Token:
        self.op_queue.append((t_p:=self.queue.pop()))
        self.op_count += 1
        return t_p

    def __bool__(self) -> bool:
        return bool(self.queue)

    def copy(self) -> 'MatchQueue':
        return self.__class__(*self.queue, op_queue = self.op_queue, op_count = self.op_count)
    
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({list(self.queue)})'

class LRQueue:
    def __init__(self, *args, **kwargs) -> None:
        self.q_vals = collections.deque([*args])

    def add_token(self, _token:caspian_grammar.Token) -> None:
        self.q_vals.append(_token)

    def load_token_line(self, _tokenline:TokenizedLine) -> None:
        for token in _tokenline:
            self.add_token(token)

    def peek(self) -> typing.Union['Token', None]:
        return None if not self.q_vals else self.q_vals[0]

    def shift(self) -> caspian_grammar.Token:
        return self.q_vals.popleft()

    def __add__(self, _token:caspian_grammar.Token) -> 'LRQueue': 
        self.q_vals.append(_token)
        return self

    def __getitem__(self, _ind) -> caspian_grammar.Token:
        return self.q_vals[_ind]

    def __bool__(self) -> bool:
        return bool(self.q_vals)

    def __iter__(self) -> typing.Iterator:
        yield from self.q_vals

    def to_match_queue(self) -> MatchQueue:
        return MatchQueue(*self)
    
    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}[{", ".join(map(str, self.q_vals))}], ({len(self.q_vals)} items)>'

class StreamQueue:
    def __init__(self, _line_tokens) -> None:
        self.stream_vals = collections.deque(_line_tokens)
        self.last_popped = collections.deque()

    def n_t_block(self) -> caspian_grammar.Token:
        if not self.stream_vals:
            return None
        
        self.last_popped.append(copy.deepcopy(l_obj:=self.stream_vals.popleft()))
        return l_obj

    def recover_token(self) -> None:
        self.stream_vals.appendleft(self.last_popped.popleft())

    @classmethod
    def to_queue(cls, _line_tokens:list[caspian_grammar.Token]) -> 'StreamQueue':
        return cls(_line_tokens)

class ReduceQueue:  
    def __init__(self) -> None:
        self.streams:list[LRQueue] = []

    def add_tokens(self, *tokens:list[caspian_grammar.Token]) -> None:
        def _add_tokens():
            if not self.streams:
                yield from (LRQueue(i) for i in tokens)
            else:
                for t in self.streams:
                    for i in tokens:
                        yield t + i

        self.streams = list(_add_tokens())

    def __bool__(self) -> bool:
        return bool(self.streams)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} ({(k:=len(self.streams))} stream{"" if k == 1 else "s"})>'

class SeenTokenQueue:
    def __init__(self, *starting_tokens:list[caspian_grammar.Token]) -> None:
        self.seen_tokens = starting_tokens

    def add(self, _token:caspian_grammar.Token) -> None:
        self.seen_tokens.append(_token)
    
    def __contains__(self, _token:caspian_grammar.Token) -> bool:
        return any(i == _token for i in self.seen_tokens)

class ASTGen:
    def __init__(self) -> None:
        self.stack = None

    def __enter__(self) -> 'ASTGen':
        return self

    def reduce_token(self, _token:caspian_grammar.Token) -> typing.Iterator:
        r_queue, seen = collections.deque([_token]), SeenTokenQueue()
        while r_queue:
            yield (_s_t:=r_queue.popleft())
            seen.add(_s_t)
            for t1, t_m_obj in caspian_grammar.grammar:
                if t1 not in seen:
                    _, tr, _status = t_m_obj.is_match(MatchQueue(_s_t))
                    if _status:
                        r_queue.append(tr.set_token_head(t1))


    def to_ast_stream(self, _row_blocks:StreamQueue) -> typing.Union[typing.Tuple[dict, caspian_errors.ErrorPacket], LRQueue]:
        full_stack, line_stack, running_l_stream = ReduceQueue(), ReduceQueue(), LRQueue()
        while True:
            if not running_l_stream:
                if (nl_obj:=_row_blocks.n_t_block()) is not None: 
                    if isinstance(nl_obj, TokenizedLine):
                        running_l_stream.load_token_line(nl_obj)
                    else:
                        full_stack.add_tokens(nl_obj)
                        #run reduce on full_stack
                    continue

            line_stack.add_tokens(*self.reduce_token(running_l_stream.shift()))

        return None, None


                
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
        _status, _s_obj = self.to_ast_stream(StreamQueue.to_queue(full_blocked_result))
        if not _status['status']:
            print(_s_obj.gen_error)
            return
        _block.tokenized_statements = _s_obj

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
    '''
    with open('testing_file.txt') as f, Parser() as p, ASTGen() as astgen:
        status, _r_obj = p.parse(f.read())
        if not status['status']:
            print(_r_obj.gen_error)
        else:
            ast = astgen.create_ast(_r_obj)
    '''
    Token = caspian_grammar.Token
    BlockTokenGroup = caspian_grammar.BlockTokenGroup
    #tokens = [Token.ValueLabel, Token.Eq, Token.Expr]
    #tokens = [Token.Label(0, 0, 'if')]
    tokens = [Token.OBracket, Token.Expr, Token.ForExpr, Token.IfCond, Token.CBracket]
    #tokens = [Token.If, Token.Expr]
    #tokens = [Token.ForExpr, BlockTokenGroup]
    #tokens = [Token.At, Token.Expr, Token.FunctionBlock]
    #tokens = [Token.Label(0, 0, 'raise'), Token.Expr.eof]
    #tokens = [Token.Switch, Token.Expr, BlockTokenGroup, Token.CaseBlock]
    #tokens = [Token.CaseBlock, Token.CaseBlock]
    #tokens = [Token.Expr, Token.OParen, Token.CParen]
    #tokens = [Token.ClassStub, BlockTokenGroup]
    #tokens = [Token.Expr, Token.Comma, Token.CommaList]
    for a, b in caspian_grammar.grammar:
        t, j, k = b.is_match(MatchQueue(*tokens), l_queue = LRQueue())
        if k:
            print(a, t.op_count)
    print(tokens)

