from components import Token, TokConsts, ErrWarnHandler, DATATYPES, RESERVED_KEYWORDS
class Lexer:
    def __init__(self, strcode: str) -> None:
        self.strcode = strcode
        self.codelen = len(strcode)
        self.identified_str_token = None
        self.curr_pos = 0
        self.curr_char = self.strcode[self.curr_pos]
        self.errhandler = ErrWarnHandler()
        self.lineno = 1

    def raise_error(self, msg:str, exit:int) -> None:
        if exit:
            raise Exception(msg)
        else:
             print(msg)

    def consume_char(self) -> str:
        curr_char = self.curr_char
        self.curr_pos += 1
        if self.curr_pos >= self.codelen:
            self.curr_char = TokConsts.EOF
        else:
            self.curr_char = self.strcode[self.curr_pos]
        return curr_char

    def is_whitespace(self) -> bool:
        isspace = self.curr_char.isspace()
        if self.curr_char == '\n':
            self.lineno +=1
        return isspace
    
    def skip_whitespace(self) -> None:
        self.consume_char()

    
    def integer(self) -> int:
        res = ''
        while self.curr_char and not self.is_whitespace() and self.curr_char.isdigit():
            res += self.consume_char()
        return int(res)
    
    def string(self) -> str:
        res = ''
        self.consume_char()
        while  self.curr_char != TokConsts.EOF and self.curr_char != '"':
            res += self.consume_char()
        self.consume_char()
        return res
            
    def peek(self) -> str:
        if self.curr_pos < self.codelen-1:
            # print(self.codelen, self.curr_pos, self.strcode)
            return self.strcode[self.curr_pos + 1]
        else:
            return TokConsts.EOF

    def get_next_token_word(self) -> str:
        res = ''
        while self.curr_char != TokConsts.EOF and self.curr_char.isalpha():
            res += self.consume_char()
        return res

    def match(self, tokens_to_check):
        '''
        Match a whole token instead of individual chars
        NOTE: use this function throughout
        '''
        pass
    def is_comment(self) -> bool:
        if self.curr_char == '/' and self.peek() == '/':
            return True
        return False
    
    def move_to_next_line(self) -> None:
        pass
        
    def skip_comments(self) -> None:
        while self.curr_char != TokConsts.EOF and self.curr_char != '\n': 
            self.consume_char()
    
    def get_next_token(self) -> Token:
        while self.curr_char != TokConsts.EOF:
            if self.is_whitespace():
                self.skip_whitespace()
                continue
            if self.is_comment():
                self.skip_comments()
                continue

            if self.curr_char.isdigit():
                return Token(TokConsts.INTEGER, self.integer())
            
            if self.curr_char == '"':
                return Token(TokConsts.STRING, self.string())
            
            if self.curr_char.isalpha():
                token_word = self.get_next_token_word()
                if token_word in DATATYPES:
                    return Token(TokConsts.DATATYPE ,token_word)
                elif token_word in RESERVED_KEYWORDS:
                    return Token(token_word ,token_word)
                else:
                    return Token(TokConsts.IDENTIFIER, token_word)
            
            if self.curr_char == TokConsts.GREATER:
                self.consume_char()
                return Token(TokConsts.GREATER, TokConsts.GREATER)
            
            if self.curr_char == TokConsts.LESSTHAN:
                self.consume_char()
                return Token(TokConsts.LESSTHAN, TokConsts.LESSTHAN)

            if self.curr_char + self.peek() == TokConsts.EQUAL:
                self.consume_char()
                self.consume_char()
                return Token(TokConsts.EQUAL, TokConsts.EQUAL)
            
            if self.curr_char + self.peek() == TokConsts.NT_EQUAL:
                self.consume_char()
                self.consume_char()
                return Token(TokConsts.NT_EQUAL, TokConsts.NT_EQUAL)
            
            if self.curr_char + self.peek() == TokConsts.LOGICAL_OR:
                self.consume_char()
                self.consume_char()
                return Token(TokConsts.LOGICAL_OR, TokConsts.LOGICAL_OR)
            
            if self.curr_char + self.peek() == TokConsts.LOGICAL_AND:
                self.consume_char()
                self.consume_char()
                return Token(TokConsts.LOGICAL_AND, TokConsts.LOGICAL_AND)

            if self.curr_char == TokConsts.PLUS:
                self.consume_char()
                return Token(TokConsts.PLUS, TokConsts.PLUS)
            
            if self.curr_char == TokConsts.SUB:
                self.consume_char()
                return Token(TokConsts.SUB,TokConsts. SUB)
            
            if self.curr_char == TokConsts.MULT:
                self.consume_char()
                return Token(TokConsts.MULT, TokConsts.MULT)
            
            if self.curr_char == TokConsts.DIV:
                self.consume_char()
                return Token(TokConsts.DIV, TokConsts.DIV)
            
            if self.curr_char == TokConsts.LPARAN:
                self.consume_char()
                return Token(TokConsts.LPARAN, TokConsts.LPARAN)
            
            if self.curr_char == TokConsts.RPARAN:
                self.consume_char()
                return Token(TokConsts.RPARAN, TokConsts.RPARAN)

            if self.curr_char == TokConsts.SEMICOLON:
                self.consume_char()
                return Token(TokConsts.SEMICOLON, TokConsts.SEMICOLON)
            
            if self.curr_char == TokConsts.ASSIGN:
                self.consume_char()
                return Token(TokConsts.ASSIGN, TokConsts.ASSIGN)
            
            if self.curr_char == TokConsts.LCURLY:
                self.consume_char()
                return Token(TokConsts.LCURLY, TokConsts.LCURLY)

            if self.curr_char == TokConsts.RCURLY:
                self.consume_char()
                return Token(TokConsts.RCURLY, TokConsts.RCURLY)
            
            self.errhandler.unknown_syntax(self.curr_char, self.lineno)
            self.consume_char()
            return Token(TokConsts.UNKNOWN,TokConsts.UNKNOWN)
        
        return Token(TokConsts.EOF,TokConsts.EOF)
