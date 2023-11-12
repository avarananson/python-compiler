# compiler
import argparse
import os
from asm_helper import printintinstr, exitinstr, startinstr, addinstr, numlitinstr, divinstr, multinstr, subinstr,assigninstr, getvarinstr,\
                        callprintinstr, textinstr
from dataclasses import dataclass, field
from typing import List
from enum import Enum

class TokConsts(str,Enum):
    INTEGER = 'integer'
    PLUS =  '+'
    DIV  =  '/'
    SUB  = '-'
    MULT = '*'
    EOF  = 'eof'
    LPARAN = '('
    RPARAN = ')'
    ASSIGN = '='
    SEMICOLON = ';'
    DATATYPE = 'datatype'
    IDENTIFIER = 'identifier'
    PRINT = 'print'
    GREATER = '>'
    LESSTHAN = '<'
    EQUAL = '=='
    NT_EQUAL = '!='


#Define supported datatypes
DATATYPES = set(['int'])
RESERVED_KEYWORDS = set([TokConsts.PRINT])

@dataclass
class BssData:
    declared_data : List[list] = field(default_factory=list)

    def add_variable(self, name, res='resq', size='8'):
        self.declared_data.append([name, res, size])
    
    def __str__(self):
        return 'section .bss\n  ' + '\n   '.join([' '.join(data) for data in self.declared_data])
    
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
        self._id = -1

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

class RelationalEqualityOp(BinOp):
    def __str__(self) -> str:
        return f'RelationalEqualityOp  instance {self.lchild} {self.token} {self.rchild}'

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
            self.curr_char = TokConsts.EOF
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
        if self.curr_pos < self.codelen-1:
            # print(self.codelen, self.curr_pos, self.strcode)
            return self.strcode[self.curr_pos + 1]
        else:
            return TokConsts.EOF

    def get_next_token_word(self):
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
    def is_comment(self):
        if self.curr_char == '/' and self.peek() == '/':
            return True
        return False
    
    def skip_comments(self):
        while self.curr_char != TokConsts.EOF and self.curr_char != '\n': 
            self.consume_char()

    def get_next_token(self):
        while self.curr_char != TokConsts.EOF:
            if self.is_whitespace():
                self.skip_whitespace()
                continue
            if self.is_comment():
                self.skip_comments()
                continue
            if self.curr_char.isdigit():
                return Token(TokConsts.INTEGER, self.integer())
            
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

            self.raise_error(f'Unrecognized syntax "{self.curr_char}" at position {self.curr_pos }', exit=1)

            
        return Token(TokConsts.EOF,TokConsts.EOF)
            
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
            print(self.curr_token.type ,TYPE)
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
        while self.curr_token.type != TokConsts.EOF:
            # print('in HHH', self.curr_token)
            if self.curr_token.type == TokConsts.DATATYPE:
                # print(self.curr_token)
                _statements.append(self.var_declare())
            elif self.curr_token.type == TokConsts.IDENTIFIER:
                _statements.append(self.var_assign())
            elif self.curr_token.type == TokConsts.PRINT:
                
                _statements.append(self.eprint())
            else:
                self.raise_error(f'Unrecognized statement {self.curr_token} .', exit=1)

        return _statements

    def eprint(self):
        self.consume_token(TokConsts.PRINT)
        self.consume_token(TokConsts.LPARAN)
        print_node = Print(self.equality())
        self.consume_token(TokConsts.RPARAN)
        self.consume_token(TokConsts.SEMICOLON)
        return print_node


    def var_assign(self):
        curr_tok_var = Var(self.curr_token.value)
        self.consume_token(TokConsts.IDENTIFIER)
        self.consume_token(TokConsts.ASSIGN)
        eq_node = self.equality()
        varassign = VarAssign(curr_tok_var, eq_node)
        self.consume_token(TokConsts.SEMICOLON)
        return varassign

    def var_declare(self):
        curr_tok_dt = self.curr_token
        self.consume_token(TokConsts.DATATYPE)
        curr_tok_var = Var(self.curr_token.value)
        self.consume_token(TokConsts.IDENTIFIER)
        
        if self.curr_token.type == TokConsts.ASSIGN:
            self.consume_token(TokConsts.ASSIGN)
            eq_node = self.equality()
            # identifier = Identifier(curr_tok_var, curr_tok_dt , node)
            varassign = VarAssign(curr_tok_var, eq_node)
            vardecl = VarDeclare(curr_tok_dt, curr_tok_var,  varassign)
        else:
            # identifier = Identifier(curr_tok_var, curr_tok_dt , None)
            vardecl = VarDeclare(curr_tok_dt, curr_tok_var,  None)
            
        self.consume_token(TokConsts.SEMICOLON)
        return vardecl
    
    def equality(self):
        chain_count_eq = 0
        node = self.relational()
        while self.curr_token.type in (TokConsts.EQUAL, TokConsts.NT_EQUAL) and self.curr_token!= TokConsts.EOF:
            curr_token = self.curr_token
            self.consume_token(self.curr_token.type)
            chain_count_eq +=1
            node = RelationalEqualityOp(left=node, token=curr_token, right=self.relational())
        node.chain_count_eq = chain_count_eq
        return node

    def relational(self):
        chain_count_rel = 0
        node = self.expr()
        while self.curr_token.type in (TokConsts.GREATER, TokConsts.LESSTHAN) and self.curr_token!= TokConsts.EOF:
            curr_token = self.curr_token
            self.consume_token(self.curr_token.type)
            chain_count_rel +=1
            node = RelationalEqualityOp(left=node, token=curr_token, right=self.expr())
        node.chain_count_rel = chain_count_rel
        # print(node, '\n','---' ,node.chain_count_rel)
        return node

    def factor(self):
        # print()
        if self.curr_token.type == TokConsts.LPARAN:
            self.consume_token(TokConsts.LPARAN)
            node = self.equality()
            self.consume_token(TokConsts.RPARAN)
            return node
        elif self.curr_token.type == TokConsts.INTEGER:
            token = self.curr_token
            self.consume_token(TokConsts.INTEGER)
            return NumLiteral(token.value)
        elif self.curr_token.type == TokConsts.IDENTIFIER:
            token = self.curr_token
            self.consume_token(TokConsts.IDENTIFIER)
            return Var(token.value)


    def term(self):
        node = self.factor()
        while self.curr_token.type in (TokConsts.MULT, TokConsts.DIV) and self.curr_token != TokConsts.EOF:
            tok = self.curr_token
            if self.curr_token.type == TokConsts.MULT:
                self.consume_token(TokConsts.MULT)
                # res *= self.factor()
            elif self.curr_token.type == TokConsts.DIV:
                self.consume_token(TokConsts.DIV)
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
        while self.curr_token.type in (TokConsts.PLUS, TokConsts.SUB) and self.curr_token != TokConsts.EOF:
            # print(self.curr_token)
            tok = self.curr_token
            if self.curr_token.type == TokConsts.PLUS:
                self.consume_token(TokConsts.PLUS)
                # node =  self.term()
            elif self.curr_token.type == TokConsts.SUB:
                self.consume_token(TokConsts.SUB)
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
    def raise_error(self, msg, exit):
        if exit:
            raise Exception(msg)
        else:
             print(msg)

    def visit(self, node):

        if isinstance(node, BinOp):
            if node.token.type == TokConsts.PLUS:
                return (self.visit(node.lchild) +  self.visit(node.rchild))
            if node.token.type == TokConsts.SUB:
                return (self.visit(node.lchild) -  self.visit(node.rchild))
            if node.token.type == TokConsts.DIV:
                return (self.visit(node.lchild) //  self.visit(node.rchild))
            if node.token.type == TokConsts.MULT:
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
        
        if isinstance(node, RelationalEqualityOp):
            # print(n÷ßode)
            # print('node',node, '->')
            # print( node.chain_count)
            if getattr(node,'chain_count_eq',0)>1 or getattr(node,'chain_count_rel',0)>1:
                
                self.raise_error(f'Chained equality/comparison operators are found. It could result in ambigius results',exit=1)
            if node.token.type == TokConsts.GREATER:
                return int((self.visit(node.lchild) >  self.visit(node.rchild)))
            if node.token.type == TokConsts.LESSTHAN:
                return int((self.visit(node.lchild) <  self.visit(node.rchild)))
            if node.token.type == TokConsts.EQUAL:
                return int((self.visit(node.lchild) ==  self.visit(node.rchild)))
            if node.token.type == TokConsts.NT_EQUAL:
                return int((self.visit(node.lchild) !=  self.visit(node.rchild)))
            
        if isinstance(node , Var):
            return self.__SYMBOL_TABLE[node.name].value
        
        if isinstance(node ,Print):
            print(self.visit(node.value))



class Compile:
    def __init__(self) -> None:
        self.asmFile = './compile.asm'
        self.asmList = ["{}"]
        self.bss = BssData()
        self.__SYMBOL_TABLE = {}
        self.__varcount = 0
        # self.all_available_regs = { "r8", "r9", "r10", "r11" }
    
    @property
    def varcount(self):
        self.__varcount +=1
        return self.__varcount

    def get_required_pre_asm(self):
        ##############
        #try to optimize this rather than extending and creating of large list
        ############## 
        self.asmList.append(textinstr)
        self.asmList.append(printintinstr)
        self.asmList.append(startinstr)
    
    def get_required_post_asm(self):
        self.asmList[0] = self.asmList[0].format(self.bss)
        self.asmList.append(exitinstr.format(0))

    def __gen_code_binary_op(self, opA, opB, otype):
        # self.__get_free_reg()
        if otype == TokConsts.PLUS:
            self.asmList.append(addinstr)
        if otype == TokConsts.SUB:
            self.asmList.append(subinstr)
        if otype == TokConsts.MULT:
            self.asmList.append(multinstr)
        if otype == TokConsts.DIV:
            self.asmList.append(divinstr)
            

    def __gen_code_numliteral(self, num):
        self.asmList.append(numlitinstr.format(num))

    def __gen_code_assign(self, node_name):
        self.asmList.append(assigninstr.format(node_name))
    
    def __gen_code_get_variable(self,node_name):
        self.asmList.append(getvarinstr.format(node_name))
    
    def __gen_code_print(self):
        self.asmList.append(callprintinstr)

    def visit(self, node):
        if isinstance(node, BinOp):
            if node.token.type == TokConsts.PLUS:
                self.__gen_code_binary_op(self.visit(node.lchild), self.visit(node.rchild), TokConsts.PLUS)
            if node.token.type == TokConsts.SUB:
                self.__gen_code_binary_op(self.visit(node.lchild), self.visit(node.rchild), TokConsts.SUB)
            if node.token.type == TokConsts.DIV:
                self.__gen_code_binary_op(self.visit(node.lchild), self.visit(node.rchild), TokConsts.DIV)
            if node.token.type == TokConsts.MULT:
                self.__gen_code_binary_op(self.visit(node.lchild), self.visit(node.rchild), TokConsts.MULT)
        
        if isinstance(node, NumLiteral):
            self.__gen_code_numliteral(node.value) 
        
        if isinstance(node, VarDeclare):
            node_name = node.var.name
            self.bss.add_variable(node_name)
            self.__SYMBOL_TABLE[node_name] = node
            self.visit(node.value) if node.value else None
            # self.__SYMBOL_TABLE[node_name] = node

        if isinstance(node, VarAssign):
            node_name = node.var.name
            self.visit(node.right_expr)
            self.__gen_code_assign(node_name) 
            # node.value = value
            self.__SYMBOL_TABLE[node_name]._id = self.varcount

        if isinstance(node , Var):
            self.__gen_code_get_variable(node.name)
        
        if isinstance(node ,Print):
            self.visit(node.value)
            self.__gen_code_print()

    def write_asm(self):
        with open(self.asmFile, 'w') as asm:
            asm.writelines('\n'.join(self.asmList))

    def compile_ast(self, root):
        self.get_required_pre_asm()
        for child in root.children:
            self.visit(child)
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
            if x.value == TokConsts.EOF:
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





