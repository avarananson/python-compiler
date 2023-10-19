# compiler

INTEGER ,PLUS, DIV, SUB, MULT, EOF = 'integer', 'plus', 'div', 'subtract','mult', 'eof'
LPARAN, RPARAN = '(', ')'
class Token:

    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self) -> str:
        return(f'Token : {self.type}, Value : {self.value}')
        
class AST:
    pass

class BinOp(AST):
    def __init__(self, left, token, right) -> None:
        super().__init__()
        self.lchild = left
        self.token = token
        self.rchild = right
    
    def __str__(self) -> str:
        return f'Binary op instance {self.lchild} {self.token} {self.rchild}'

class NumLiteral(AST):
    def __init__(self, value) -> None:
        super().__init__()
        self.value = value
    
    def __str__(self) -> str:
        return f'Num literal instance {self.value}'
    


class Lexer:
    def __init__(self, strcode) -> None:
        self.strcode = strcode
        self.codelen = len(strcode)
        self.curr_token = None
        self.curr_pos = 0
        self.curr_char = self.strcode[self.curr_pos]

    def consume_char(self):
        curr_char = self.curr_char
        self.curr_pos += 1
        if self.curr_pos >= self.codelen:
            self.curr_char = EOF
        else:
            self.curr_char = self.strcode[self.curr_pos]
        return curr_char

    def is_whitespace(self):
        return self.curr_char.isspace()
    
    def skip_whitespace(self):
        self.consume_char()

    
    def integer(self):
        res = ''
        while self.curr_char and not self.is_whitespace() and self.curr_char.isdigit():
            res += self.consume_char()
        return int(res)
            


    
    def get_next_token(self):
        while self.curr_char != EOF:
            if self.is_whitespace():
                self.skip_whitespace()
                continue

            if self.curr_char.isdigit():
                return Token(INTEGER, self.integer())
            
            if self.curr_char == '+':
                self.consume_char()
                return Token(PLUS, '+')
            
            if self.curr_char == '-':
                self.consume_char()
                return Token(SUB, '-')
            
            if self.curr_char == '*':
                self.consume_char()
                return Token(MULT, '*')
            
            if self.curr_char == '/':
                self.consume_char()
                return Token(DIV, '/')
            
            if self.curr_char == '(':
                self.consume_char()
                return Token(LPARAN, '(')
            
            if self.curr_char == ')':
                self.consume_char()
                return Token(RPARAN, ')')
            
        return Token(EOF,EOF)
            
class Parser:

    def __init__(self, lexer) -> None:
        self.curr_token = lexer.get_next_token()
        self.lexer = lexer
    
    def raise_error(self, msg, exit):
        if exit:
            raise Exception(msg)
        else:
            print(msg)

    def consume_token(self, TYPE):
        if self.curr_token.type != TYPE:
            print(self.curr_token ,TYPE)
            self.raise_error(f'Syntax error at position {self.lexer.curr_pos }', exit=1)
        else:
            self.curr_token = self.lexer.get_next_token()
            # print(self.curr_token)

    def factor(self):
        if self.curr_token.type == LPARAN:
            self.consume_token(LPARAN)
            node = self.parse()
            self.consume_token(RPARAN)
            return node
        else:
            token = self.curr_token
            # print(token)
            self.consume_token(INTEGER)
            # print(token.value)
            return NumLiteral(token.value)

    def term(self):
        node = self.factor()
        while self.curr_token.type in (MULT, DIV) and self.curr_token != EOF:
            tok = self.curr_token
            if self.curr_token.type == MULT:
                self.consume_token(MULT)
                # res *= self.factor()
            elif self.curr_token.type == DIV:
                self.consume_token(DIV)
                # res /= self.factor()
            node = BinOp(left=node, token=tok, right=self.factor())
        return node
    
    def parse(self):
        """
        expr   : term ((PLUS | SUB) term)*
        term   : factor ((MULT | DIV) factor)* 
        factor : INTEGER | LPARAN expr RPARAN
        """
        node = self.term()
        # print(res)
        while self.curr_token.type in (PLUS, SUB) and self.curr_token != EOF:
            # print(self.curr_token)
            tok = self.curr_token
            if self.curr_token.type == PLUS:
                self.consume_token(PLUS)
                # node =  self.term()
            elif self.curr_token.type == SUB:
                self.consume_token(SUB)
                # node =  self.term()
            node = BinOp(left=node, token=tok, right=self.term())
            

        return node

class Interpreter:
    def __init__(self, root) -> None:
        self.root = root
    
    def interpret(self):
        return self.visit(self.root)

    def visit(self, node):

        if isinstance(node, BinOp):
            if node.token.type == PLUS:
                return (self.visit(node.lchild) +  self.visit(node.rchild))
            if node.token.type == SUB:
                return (self.visit(node.lchild) -  self.visit(node.rchild))
            if node.token.type == DIV:
                return (self.visit(node.lchild) /  self.visit(node.rchild))
            if node.token.type == MULT:
                return (self.visit(node.lchild) *  self.visit(node.rchild))
            
        if isinstance(node, NumLiteral):
            return node.value


def compile_ast(root):
    pass




def main():
    lexer  = Lexer('1+')
    parser = Parser(lexer=lexer)
    root = parser.parse()
    ir = Interpreter(root=root)
    print(ir.interpret())


    compile_ast(root)
    
   


if __name__ == '__main__':
    main()








