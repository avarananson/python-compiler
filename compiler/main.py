# compiler
import argparse
import os
from asm_helper import printintinstr, exitinstr, startinstr, addinstr, numlitinstr, divinstr, multinstr, subinstr
INTEGER ,PLUS, DIV, SUB, MULT, EOF = 'integer', '+', '/', '-','*', 'eof'
LPARAN, RPARAN, ASSIGN, SEMICOLON = '(', ')', '=', ';'
DATATYPE = 'datatype'
IDENTIFIER = 'identifier'
PRINT = 'print'

#Define supported datatypes
DATATYPES = set(['int'])
RESERVED_KEYWORDS = set([PRINT])
class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self) -> str:
        return(f'Token : {self.type}, Value : {self.value}')
        
class AST:
    pass

class Print:
    def __init__(self, value) -> None:
        self.value = value
    def __str__(self) -> str:
        return(f'PrintValue: {self.value}')
    
        
class Main:
    def __init__(self) -> None:
        self.children = []

class Var:
    def __init__(self, name) -> None:
        self.name = name
    def __str__(self) -> str:
        return(f'Var: {self.name}')
            
class VarDeclare:
    def __init__(self, type_node, var_node , value_node) -> None:
        self.var = var_node
        self.type = type_node
        self.value = value_node
    def __str__(self) -> str:
        return(f'VarDeclare : {self.var}, Value : {self.value}, Type : {self.type}')

class VarAssign:
    def __init__(self ,var_node, expr) -> None:
        self.var = var_node
        self.right_expr = expr
    def __str__(self) -> str:
        return(f'VarAssign : Name : {self.var} , right_expr : {self.right_expr}')

        
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
        self.identified_str_token = None
        self.curr_pos = 0
        self.curr_char = self.strcode[self.curr_pos]

    def raise_error(self, msg, exit):
        if exit:
            raise Exception(msg)
        else:
             print(msg)

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
            
    def peek(self):
        if self.curr_pos < self.codelen:
            return self.strcode[self.curr_pos + 1]
        else:
            return EOF

    def get_next_token_word(self):
        res = ''
        while self.curr_char != EOF and self.curr_char.isalpha():
            res += self.consume_char()
        return res

    def match(self, tokens_to_check):
        '''
        Match a whole token instead of individual chars
        NOTE: use this function throughout
        '''
        pass
    def is_comment(self):
        if self.curr_char == '/' and self.peek() == '/':
            return True
        return False
    
    def skip_comments(self):
        while self.curr_char != EOF and self.curr_char != '\n': 
            self.consume_char()

    def get_next_token(self):
        while self.curr_char != EOF:
            if self.is_whitespace():
                self.skip_whitespace()
                continue
            if self.is_comment():
                self.skip_comments()
                continue
            if self.curr_char.isdigit():
                return Token(INTEGER, self.integer())
            
            if self.curr_char.isalpha():
                token_word = self.get_next_token_word()
                if token_word in DATATYPES:
                    return Token(DATATYPE ,token_word)
                elif token_word in RESERVED_KEYWORDS:
                    return Token(token_word ,token_word)
                else:
                    return Token(IDENTIFIER, token_word)
            
            if self.curr_char == PLUS:
                self.consume_char()
                return Token(PLUS, PLUS)
            
            if self.curr_char == SUB:
                self.consume_char()
                return Token(SUB, SUB)
            
            if self.curr_char == MULT:
                self.consume_char()
                return Token(MULT, MULT)
            
            if self.curr_char == DIV:
                self.consume_char()
                return Token(DIV, DIV)
            
            if self.curr_char == LPARAN:
                self.consume_char()
                return Token(LPARAN, LPARAN)
            
            if self.curr_char == RPARAN:
                self.consume_char()
                return Token(RPARAN, RPARAN)

            if self.curr_char == SEMICOLON:
                self.consume_char()
                return Token(SEMICOLON, SEMICOLON)
            
            if self.curr_char == ASSIGN:
                self.consume_char()
                return Token(ASSIGN, ASSIGN)

            self.raise_error(f'Unrecognized syntax "{self.curr_char}" at position {self.curr_pos }', exit=1)

            
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
            # print(self.curr_token ,TYPE)
            self.raise_error(f'Syntax error at position {self.lexer.curr_pos }', exit=1)
        else:
            self.curr_token = self.lexer.get_next_token()

    def parse(self):
        stmts =  self.statements()
        root = Main()
        for node in stmts:
            root.children.append(node)
        return root

    
    def statements(self):
        _statements = []
        # print(self.curr_token)
        while self.curr_token.type != EOF:
            # print('in HHH', self.curr_token)
            if self.curr_token.type == DATATYPE:
                # print(self.curr_token)
                _statements.append(self.var_declare())
            elif self.curr_token.type == IDENTIFIER:
                _statements.append(self.var_assign())
            elif self.curr_token.type == PRINT:
                
                _statements.append(self.eprint())
            else:
                self.raise_error(f'Unrecognized statement {self.curr_token} .', exit=1)

        return _statements

    def eprint(self):
        self.consume_token(PRINT)
        self.consume_token(LPARAN)
        print_node = Print(self.expr())
        self.consume_token(RPARAN)
        self.consume_token(SEMICOLON)
        return print_node


    def var_assign(self):
        curr_tok_var = Var(self.curr_token.value)
        self.consume_token(IDENTIFIER)
        self.consume_token(ASSIGN)
        expr_node = self.expr()
        varassign = VarAssign(curr_tok_var, expr_node)
        self.consume_token(SEMICOLON)
        return varassign

    def var_declare(self):
        curr_tok_dt = self.curr_token
        self.consume_token(DATATYPE)
        curr_tok_var = Var(self.curr_token.value)
        self.consume_token(IDENTIFIER)
        
        if self.curr_token.type == ASSIGN:
            self.consume_token(ASSIGN)
            expr_node = self.expr()
            # identifier = Identifier(curr_tok_var, curr_tok_dt , node)
            varassign = VarAssign(curr_tok_var, expr_node)
            vardecl = VarDeclare(curr_tok_dt, curr_tok_var,  varassign)
        else:
            # identifier = Identifier(curr_tok_var, curr_tok_dt , None)
            vardecl = VarDeclare(curr_tok_dt, curr_tok_var,  None)
            
        self.consume_token(SEMICOLON)
        return vardecl
    

    def factor(self):
        # print()
        if self.curr_token.type == LPARAN:
            self.consume_token(LPARAN)
            node = self.expr()
            self.consume_token(RPARAN)
            return node
        elif self.curr_token.type == INTEGER:
            token = self.curr_token
            self.consume_token(INTEGER)
            return NumLiteral(token.value)
        elif self.curr_token.type == IDENTIFIER:
            token = self.curr_token
            self.consume_token(IDENTIFIER)
            return Var(token.value)


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

    # def prog(self)
    
    def expr(self):
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
        self.__SYMBOL_TABLE = {}
    
    def interpret(self):
        for child in self.root.children:
            self.visit(child)
        # print(self.__SYMBOL_TABLE)
        # print(self.__SYMBOL_TABLE['x'].value)


    def visit(self, node):

        if isinstance(node, BinOp):
            if node.token.type == PLUS:
                return (self.visit(node.lchild) +  self.visit(node.rchild))
            if node.token.type == SUB:
                return (self.visit(node.lchild) -  self.visit(node.rchild))
            if node.token.type == DIV:
                return (self.visit(node.lchild) //  self.visit(node.rchild))
            if node.token.type == MULT:
                return (self.visit(node.lchild) *  self.visit(node.rchild))
            
        if isinstance(node, NumLiteral):
            return node.value
         
        if isinstance(node, VarDeclare):
            node_name = node.var.name
            self.__SYMBOL_TABLE[node_name] = node
            value = self.visit(node.value) if node.value else None
            node.value = value
            # self.__SYMBOL_TABLE[node_name] = node

        if isinstance(node, VarAssign):
            node_name = node.var.name
            value = self.visit(node.right_expr) 
            # node.value = value
            self.__SYMBOL_TABLE[node_name].value = value
            return value

        if isinstance(node , Var):
            return self.__SYMBOL_TABLE[node.name].value
        
        if isinstance(node ,Print):
            print(self.visit(node.value))



class Compile:
    def __init__(self) -> None:
        self.asmFile = './compile.asm'
        self.asmList = []
        # self.all_available_regs = { "r8", "r9", "r10", "r11" }

    def get_required_pre_asm(self):
        ##############
        #try to optimize this rather than extending and creating of large list
        ############## 
        self.asmList.append(printintinstr)
        self.asmList.append(startinstr)
    
    def get_required_post_asm(self):
        self.asmList.append(exitinstr.format(0))

    def __gen_code_binary_op(self, opA, opB, otype):
        # self.__get_free_reg()
        if otype == PLUS:
            self.asmList.append(addinstr)
        if otype == SUB:
            self.asmList.append(subinstr)
        if otype == MULT:
            self.asmList.append(multinstr)
        if otype == DIV:
            self.asmList.append(divinstr)
            

    def __gen_code_numliteral(self, num):
        self.asmList.append(numlitinstr.format(num))


    def visit(self, node):
        if isinstance(node, BinOp):
            if node.token.type == PLUS:
                self.__gen_code_binary_op(self.visit(node.lchild), self.visit(node.rchild), PLUS)
            if node.token.type == SUB:
                self.__gen_code_binary_op(self.visit(node.lchild), self.visit(node.rchild), SUB)
            if node.token.type == DIV:
                self.__gen_code_binary_op(self.visit(node.lchild), self.visit(node.rchild), DIV)
            if node.token.type == MULT:
                self.__gen_code_binary_op(self.visit(node.lchild), self.visit(node.rchild), MULT)
        
        if isinstance(node, NumLiteral):
            self.__gen_code_numliteral(node.value) 

    def write_asm(self):
        with open(self.asmFile, 'w') as asm:
            asm.writelines('\n'.join(self.asmList))

    def compile_ast(self, root):
        self.get_required_pre_asm()
        self.visit(root)
        self.get_required_post_asm()
        self.write_asm()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='File to run')
    parser.add_argument('-sim', dest='sim', action='store_true',help='Simulate it')
    parser.add_argument('-compile', dest='compile', action='store_true', help='Compiile it')
    parser.add_argument('-debug', dest='debug', action='store_true', help='debug it')

    return parser.parse_args()

def main():
    args = parse_args()
    code = open(args.file, 'r').read()
    lexer  = Lexer(code)
    if args.debug:
        while 1:
            x = lexer.get_next_token()
            print(x)
            if x.value == EOF:
                break
        # return
    lexer  = Lexer(code)
    parser = Parser(lexer=lexer)
    root = parser.parse()
    if args.debug:
        for child in root.children:
            print(child)
    if args.sim:
        ir = Interpreter(root=root)
        ir.interpret()
    elif args.compile:
        compiler = Compile()
        compiler.compile_ast(root)
        os.system('nasm -f elf64 -o hello.o compile.asm && ld -o hello hello.o && ./hello')
        # os.system('nasm -f macho64 -o hello.o compile.asm && ld -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lSystem -arch x86_64 -macosx_version_min 10.13 -o hello hello.o && ./hello')
    
   


if __name__ == '__main__':
    main()






