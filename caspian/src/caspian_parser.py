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

    def __iter__(self) -> typing.Iterator:
        yield from self.queue

    def copy(self) -> 'MatchQueue':
        return self.__class__(*self.queue, op_queue = self.op_queue, op_count = self.op_count)
    
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({list(self.queue)} | {self.op_count})'

class LRQueue:
    def __init__(self, *args, **kwargs) -> None:
        self.q_vals = collections.deque([*args])
    
    def copy(self) -> 'LRQueue':
        return self.__class__(*self.q_vals)

    def add_token(self, _token:caspian_grammar.Token) -> None:
        self.q_vals.append(_token)

    def load_token_line(self, _tokenline:TokenizedLine) -> None:
        for token in _tokenline:
            self.add_token(token)

    def peek(self) -> typing.Union['Token', None]:
        return None if not self.q_vals else self.q_vals[0]

    def shift(self) -> caspian_grammar.Token:
        return self.q_vals.popleft()

    def shift_reduce(self, new_token:caspian_grammar.Token, offset:int) -> 'LRQqueue':
        for _ in range(offset):
            _ = self.q_vals.pop()

        self.q_vals.append(new_token)
        return self

    def __add__(self, _token:caspian_grammar.Token) -> 'LRQueue': 
        self.q_vals.append(_token)
        return self

    def __eq__(self, _lr_queue:'LRQueue') -> bool:
        return len(self.q_vals) == len(_lr_queue.q_vals) and all(a.raw_token_name == b.raw_token_name for a, b in zip(self.q_vals, _lr_queue.q_vals))

    def __getitem__(self, _ind) -> caspian_grammar.Token:
        return self.q_vals[_ind]

    def __bool__(self) -> bool:
        return bool(self.q_vals)

    def __iter__(self) -> typing.Iterator:
        yield from self.q_vals

    def __len__(self) -> int:
        return len(self.q_vals)

    def to_match_queue(self, reverse:bool=False) -> MatchQueue:
        return MatchQueue(*self) if not reverse else MatchQueue(*list(self)[::-1])
    
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
        self.streams:list[LRQueue] = collections.deque()

    def add_tokens(self, *tokens:list[caspian_grammar.Token]) -> None:
        def _add_tokens():
            if not self:
                yield from (LRQueue(i) for i in tokens)
            else:
                for t in self:
                    for i in tokens:
                        yield t + i

        self.streams = collections.deque(list(_add_tokens()))

    def set_stack(self, _stack:list[LRQueue]) -> None:
        self.streams = collections.deque(_stack)

    def queue_status(self) -> bool:
        return self.streams and all(self.streams)

    def __iter__(self) -> typing.Iterator:
        while self.streams:
            yield self.streams.popleft()

    def __bool__(self) -> bool:
        return bool(self.streams)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} ({(k:=len(self.streams))} stream{"" if k == 1 else "s"})>'

class SeenTokenQueue:
    def __init__(self, *starting_tokens:list[caspian_grammar.Token]) -> None:
        self.seen_tokens = list(starting_tokens)

    def add(self, _token:caspian_grammar.Token) -> None:
        self.seen_tokens.append(_token)
    
    def __contains__(self, _token:caspian_grammar.Token) -> bool:
        return any(i == _token for i in self.seen_tokens)

class SeenLRQueue(SeenTokenQueue):
    def __contains__(self, _lr_queue:LRQueue) -> bool:
        return any(i == _lr_queue for i in self.seen_tokens)

    def __repr__(self) -> str:
        return f'<{", ".join(map(str, self.seen_tokens))}>'

class ASTGen:
    def __init__(self) -> None:
        self.stack = None

    def __enter__(self) -> 'ASTGen':
        return self

    def reduce_tokens(self, stack:ReduceQueue, running_l_stream:LRQueue = None, multiline:bool=False) -> typing.Iterator:
        r_queue, seen = collections.deque(), SeenLRQueue()
        for i in stack:
            r_queue.append(i.to_match_queue())
            seen.add(i)

        while r_queue:
            yield (n_lr:=LRQueue(*(n_mq:=r_queue.popleft())))
            for t1, t_m_obj in caspian_grammar.grammar:
                tr_match_queue, tr, _status = t_m_obj.is_match(n_mq.copy(), l_queue = running_l_stream)
                if _status:
                    if (new_lr:=n_lr.copy().shift_reduce(tr.set_token_head(t1), tr_match_queue.op_count)) not in seen:
                        r_queue.append(new_lr.to_match_queue())
                        seen.add(new_lr)
                    
    def get_token_bases(self, *args) -> typing.Iterator:
        for i in args:
            if isinstance(i, caspian_grammar.TokenMain.TokenRoot) and i.pointer_next is None:
                yield i
            elif (v:=getattr(i, 'ast_blocks', [])):
                yield from get_token_bases(*v)
            elif (v:=getattr(i, 'pointer_next', None)) is not None:
                yield from get_token_bases(v)

    def to_ast_stream(self, _row_blocks:StreamQueue) -> typing.Union[typing.Tuple[dict, caspian_errors.ErrorPacket], LRQueue]:
        full_stack, line_stack, running_l_stream = ReduceQueue(), ReduceQueue(), LRQueue()
        ml_state = False
        while True:
            if not running_l_stream:
                if (nl_obj:=_row_blocks.n_t_block()) is not None:
                    if isinstance(nl_obj, TokenizedLine):
                        running_l_stream.load_token_line(nl_obj)
                    else:
                        if not line_stack:
                            full_stack.add_tokens(nl_obj)
                            full_stack_reduced_results = list(self.reduce_tokens(full_stack, running_l_stream = running_l_stream))
                            #print('full stack reduced results', full_stack_reduced_results)
                            #print('line stack status new', line_stack, line_stack.queue_status())
                            full_stack.set_stack(full_stack_reduced_results)
                        else:
                            running_l_stream.add_token(nl_obj)
                    
                    ml_state = line_stack.queue_status()
                    continue

                if line_stack.queue_status():
                    token_base = next(self.get_token_bases(*[i for j in line_stack.streams for i in j]))
                    l_num, char_num = token_base.line_num, token_base.char_num
                    return {'status':False}, caspian_errors.ErrorPacket(l_num, char_num, caspian_errors.InvalidSyntax, self.stack, caspian_errors.ErrorPacket.char_error_marker(char_num, l_num, caspian_errors.InvalidSyntax))
                
                if not full_stack:
                    return {'status':True}, []

                m_len = min([len(i) for i in full_stack.streams])
                return {'status':True}, [i for i in full_stack if len(i) == m_len]

            #print('running_l_stream', running_l_stream)
            line_stack.add_tokens(running_l_stream.shift())
            #print('line_stack below')
            #print(line_stack)
            reduced_results = list(self.reduce_tokens(line_stack, running_l_stream = running_l_stream, multiline = ml_state))
            #print('reduced results in here', reduced_results)
            if not running_l_stream and (single_reduced:=[i[0] for i in reduced_results if len(i) == 1]):
                full_stack.add_tokens(*single_reduced)
                full_stack_reduced_results = list(self.reduce_tokens(full_stack, running_l_stream = running_l_stream))
                #print('full stack reduced results 2', full_stack_reduced_results)
                full_stack.set_stack(full_stack_reduced_results)
                reduced_results = []

            line_stack.set_stack(reduced_results)
            #print('-'*20)
                
    def parse_group_block(self, _block:caspian_grammar.BlockTokenGroup) -> typing.Iterator:
        full_blocked_result, running_block = [], []
        for line in _block:
            if line.whitespace_count:
                running_block.append(line)
            else:
                if running_block:
                    yield {'status':True}, (new_block:=caspian_grammar.BlockTokenGroup.form_new_block(running_block))
                    full_blocked_result.append(new_block)
                    running_block = []
                full_blocked_result.append(line)

        if running_block:
            yield {'status':True}, (new_block:=caspian_grammar.BlockTokenGroup.form_new_block(running_block))
            full_blocked_result.append(new_block)
            running_block = []
        
        _status, _s_obj = self.to_ast_stream(StreamQueue.to_queue(full_blocked_result))
        if not _status['status']:
            print(_s_obj.gen_error)
            #add error yielding here
            yield {'status':False}, _s_obj
            return

        print('='*20)
        print('final ast obj', _s_obj)
        _block.tokenized_statements = _s_obj

    def create_ast(self, token_lines:typing.List[TokenizedLine]) -> caspian_grammar.BlockTokenGroup:
        block_head = caspian_grammar.BlockTokenGroup(token_lines)
        block_queue = collections.deque([block_head])
        while block_queue:
            for status, sub_block in self.parse_group_block(block_queue.popleft()):
                if not status['status']:
                    return status, sub_block

                block_queue.append(sub_block)
            
            #break #REMOVE THIS LATER
        
        return {'status':True}, block_head
    
    def __exit__(self, *_) -> None:
        pass


if __name__ == '__main__':
    def display_ast(ast):
        import matplotlib.pyplot as plt
        import networkx as nx
        from networkx.drawing.nx_agraph import graphviz_layout
        ast_graph, c_obj = nx.DiGraph(), itertools.count(1)
        def load_ast_graph(graph, ast_obj, parent_id = None):
            l_val, trav_obj, ignore = None, [], False
            if hasattr(ast_obj, 'tokenized_statements'):
                l_val, trav_obj = ast_obj.__class__.__name__, ast_obj.tokenized_statements
            elif hasattr(ast_obj, 'q_vals'):
                ignore = True
                trav_obj = ast_obj.q_vals
            elif hasattr(ast_obj, 'ast_blocks'):
                l_val = ast_obj.raw_token_name
                trav_obj = ast_obj.ast_blocks
            elif hasattr(ast_obj, 'pointer_next'):
                l_val = ast_obj.raw_token_name
                if ast_obj.pointer_next is not None:
                    trav_obj = [ast_obj.pointer_next]
            
            n_id = parent_id
            if not ignore:
                n_id = next(c_obj)
                yield (n_id, f'{l_val}')
                graph.add_node(n_id)
                if parent_id is not None:
                    graph.add_edge(parent_id, n_id)

            for i in trav_obj:
                yield from load_ast_graph(graph, i, n_id)
        
        labels = dict(load_ast_graph(ast_graph, ast))
        print(labels)
        nx.nx_agraph.write_dot(ast_graph,'ast_stuff.dot')
        pos=graphviz_layout(ast_graph, prog='dot')
        nx.draw(ast_graph, pos, labels=labels, with_labels = True)
        plt.show()

    with open('testing_file.txt') as f, Parser() as p, ASTGen() as astgen:
        status, _r_obj = p.parse(f.read())
        if not status['status']:
            print(_r_obj.gen_error)
        else:
            status, ast = astgen.create_ast(_r_obj)
            print('+'*20)
            if status['status']:
                print('resulting ast', ast)
                display_ast(ast)
            else:
                print(ast.gen_error)
    
    '''
    Token = caspian_grammar.Token
    BlockTokenGroup = caspian_grammar.BlockTokenGroup
    #tokens = [Token.ValueLabel, Token.Eq, Token.Expr]
    #tokens = [Token.Label(0, 0, 'if')]
    #tokens = [Token.OBracket, Token.Expr, Token.ForExpr, Token.IfCond, Token.CBracket]
    #tokens = [Token.If, Token.Expr]
    #tokens = [Token.ForExpr, BlockTokenGroup]
    #tokens = [Token.At, Token.Expr, Token.FunctionBlock]
    #tokens = [Token.Label(0, 0, 'raise'), Token.Expr.eof]
    #tokens = [Token.Switch, Token.Expr, BlockTokenGroup, Token.CaseBlock]
    #tokens = [Token.CaseBlock, Token.CaseBlock]
    #tokens = [Token.Expr, Token.OParen, Token.CParen]
    #tokens = [Token.ClassStub, BlockTokenGroup]
    #tokens = [Token.Expr, Token.Comma, Token.CommaList]
    #tokens = [Token.Expr, Token.Operator, Token.Expr]
    #tokens = [Token.Async, Token.FunctionBlock]
    #tokens = [Token.Label(0, 0, 'fun')]
    #tokens = [Token.Label(0, 0, 'fun'), Token.ValueLabel]
    #tokens = [Token.Fun, Token.Expr, Token.OParen, Token.CParen]
    tokens = [Token.Expr, Token.Pipe, Token.RArrow, Token.Expr]
    for a, b in caspian_grammar.grammar:
        t, j, k = b.is_match(MatchQueue(*tokens), l_queue = LRQueue())
        if k:
            print(a, t.op_count)
    print(tokens)
    '''