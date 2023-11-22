# compiler
import argparse
import os
from asm_helper import printintinstr, exitinstr, startinstr, addinstr, numlitinstr, divinstr, multinstr, subinstr,assigninstr, getvarinstr,\
                        callprintinstr, textinstr, relationalequalityinstr, logicalistr, preblockinstr, blockconditioninstr, jneinstr, postblockconditioninstr,\
                        jmpinstr, localvarinstr
from dataclasses import dataclass, field
from typing import List ,Union, Any
from enum import Enum
UNKNOWN, LOCAL = 'unknown', 'local'

class TokConsts(str, Enum):
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
    LOGICAL_OR = '||'
    LOGICAL_AND = '&&'
    IF = 'if'
    ELSE = 'else'
    LCURLY = '{'
    RCURLY = '}'


#Define supported datatypes
DATATYPES = set(['int'])
RESERVED_KEYWORDS = set([TokConsts.PRINT, TokConsts.IF, TokConsts.ELSE])
 
@dataclass
class SymScope:
    name:str = LOCAL
    _table:dict = field(default_factory=dict)
    level:Union[str, int] = UNKNOWN
    prev: Union[Any, None] = None
    var_id : int = 0

    
class ScopeContainer:
    # Linked list ds for storing block scopes
    # |local_scope2| -->(prev) |local_scope1| -->(prev) |global_scope|
    def __init__(self) -> None:
        self.current_scope_head = None
        self.prev = None
        self.total_active_scopes = 0
    
    def add_scope(self, scope:SymScope) -> None:
        if not self.current_scope_head and not self.prev:
            self.current_scope_head = scope
            self.current_scope_head.level = 0
            # self.prev = scope
        else:
            scope.prev = self.current_scope_head
            self.current_scope_head = scope
            self.total_active_scopes +=1
            self.current_scope_head.level = self.current_scope_head.prev.level+1
        
    def get_symbol(self, name:str) -> Any:
        curr_scope = self.current_scope_head
        while curr_scope:
            if name in curr_scope._table:
                return curr_scope._table[name]
            curr_scope = curr_scope.prev
        raise ValueError(f'ERROR: {name} symbol not defined. ')

    def remove_scope(self) -> None:
        if self.current_scope_head:
            # print(f'Removing scope {self.current_scope_head} at level {self.current_scope_head.level} ..')
            prev = self.current_scope_head.prev
            self.current_scope_head = prev
        # print('After removal , below are the remaining ones.....')
        # print('====================================')
        sc = self.current_scope_head
        while sc:
            # print(f'sc {sc.level} ==> {sc._table}')
            sc = sc.prev
        # print('====================================')

class CompileScopeContainer(ScopeContainer):
    def __init__(self) -> None:
        super().__init__()   

    def get_symbol(self, name:str) -> Any:

        # print(f'========= CURRENT SCOPES NOW FOR  {name}===========')
        # curr_scope1= self.current_scope_head
        # while curr_scope1:
        #     print(curr_scope1._table)
        #     curr_scope1 = curr_scope1.prev
        # print('========= END  NOW ===========')

        curr_scope = self.current_scope_head
        if name in curr_scope._table:
            idx = curr_scope._table[name].var_id
            # f = 'GLOBAL' if curr_scope.prev == None else 'FIRST'
            # print(F'found varibale in {f} scope in level {curr_scope.level}',name)
            return f'-{(8 * idx)}'
        curr_scope = curr_scope.prev
        prev_table_len = 0
        while curr_scope and curr_scope.name == LOCAL:
            if name in curr_scope._table:
                tot_variables_cnt = len(curr_scope._table)
                idx = curr_scope._table[name].var_id
                idx = ((tot_variables_cnt - idx) + 1 + prev_table_len) * 8 
                # print(f'found varibale in LOCAL scope {curr_scope.level}', name)
                return  f'+{idx}'
            prev_table_len = prev_table_len + len(curr_scope._table) + 1

            curr_scope = curr_scope.prev
        
        if name in curr_scope._table:
            # print(f'found varibale in GLOBAL scope {curr_scope.level}',name)
            return '-1'
        
        raise ValueError(f'ERROR: {name} symbol not defined. ')

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

class LogicalOP(BinOp):
    def __str__(self) -> str:
        return f'LogicalOP  instance {self.lchild} {self.token} {self.rchild}'

class IfElseBlock:
    def __init__(self, condition,type, block ) -> None:
        self.lchild  =condition
        self.token = type
        self.rchild = block
        self.elsechild = None

    def __str__(self) -> str:
        return f'IfElseBlock  instance {self.lchild} {self.token} {self.rchild}'


class NumLiteral(AST):
    def __init__(self, value) -> None:
        super().__init__()
        self.value = value
    
    def __str__(self) -> str:
        return f'Num literal instance {self.value}'
    


class Lexer:
    def __init__(self, strcode: str) -> None:
        self.strcode = strcode
        self.codelen = len(strcode)
        self.identified_str_token = None
        self.curr_pos = 0
        self.curr_char = self.strcode[self.curr_pos]

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
        return self.curr_char.isspace()
    
    def skip_whitespace(self) -> None:
        self.consume_char()

    
    def integer(self) -> int:
        res = ''
        while self.curr_char and not self.is_whitespace() and self.curr_char.isdigit():
            res += self.consume_char()
        return int(res)
            
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



            self.raise_error(f'Unrecognized syntax "{self.curr_char}" at position {self.curr_pos }', exit=1)

            
        return Token(TokConsts.EOF,TokConsts.EOF)
            
class Parser:

    def __init__(self, lexer:Lexer) -> None:
        self.curr_token = lexer.get_next_token()
        self.lexer = lexer
    
    def raise_error(self, msg:str, exit:int) -> None:
        if exit:
            raise Exception(msg)
        else:
            print(msg)

    def consume_token(self, TYPE:str) -> None:
        if self.curr_token.type != TYPE:
            # print(self.curr_token.type ,TYPE)
            self.raise_error(f'Syntax error at position {self.lexer.curr_pos }', exit=1)
        else:
            self.curr_token = self.lexer.get_next_token()

    def parse(self) -> Main:
        stmts =  self.statements()
        root = Main()
        for node in stmts:
            root.children.append(node)
        return root

    
    def statements(self) ->None:
        _statements = []
        while self.curr_token.type != TokConsts.EOF:
            _statements.append(self.statement())
        return _statements

    def statement(self) -> Any:

        if self.curr_token.type == TokConsts.DATATYPE:
                # print(self.curr_token)
            return(self.var_declare())
        elif self.curr_token.type == TokConsts.IDENTIFIER:
            return(self.var_assign())
        elif self.curr_token.type == TokConsts.PRINT:
            return(self.eprint())
        elif self.curr_token.type == TokConsts.IF:
            return(self.ifstmt())

        else:
            self.raise_error(f'Unrecognized statement {self.curr_token} .', exit=1)


    def ifstmt(self) -> None:
        self.consume_token(TokConsts.IF)
        condition = self.logical_or()
        self.consume_token(TokConsts.LCURLY)
        block = []
        while self.curr_token.type != TokConsts.RCURLY:
            block.append(self.statement())
        node = IfElseBlock(condition, TokConsts.IF, block)
        self.consume_token(TokConsts.RCURLY)

        if self.curr_token.type == TokConsts.ELSE:
            self.consume_token(TokConsts.ELSE)
            self.consume_token(TokConsts.LCURLY)
            block = []
            while self.curr_token.type != TokConsts.RCURLY:
                block.append(self.statement())
            node.elsechild = block
            self.consume_token(TokConsts.RCURLY)
            
        return node

    def eprint(self) -> Print:
        self.consume_token(TokConsts.PRINT)
        self.consume_token(TokConsts.LPARAN)
        print_node = Print(self.logical_or())
        self.consume_token(TokConsts.RPARAN)
        self.consume_token(TokConsts.SEMICOLON)
        # print(self.curr_token)
        return print_node


    def var_assign(self) -> VarAssign:
        curr_tok_var = Var(self.curr_token.value)
        self.consume_token(TokConsts.IDENTIFIER)
        self.consume_token(TokConsts.ASSIGN)
        eq_node = self.logical_or()
        varassign = VarAssign(curr_tok_var, eq_node)
        self.consume_token(TokConsts.SEMICOLON)
        return varassign

    def var_declare(self) -> VarDeclare:
        curr_tok_dt = self.curr_token
        self.consume_token(TokConsts.DATATYPE)
        curr_tok_var = Var(self.curr_token.value)
        self.consume_token(TokConsts.IDENTIFIER)
        
        if self.curr_token.type == TokConsts.ASSIGN:
            self.consume_token(TokConsts.ASSIGN)
            eq_node = self.logical_or()
            varassign = VarAssign(curr_tok_var, eq_node)
            vardecl = VarDeclare(curr_tok_dt, curr_tok_var,  varassign)
        else:
            vardecl = VarDeclare(curr_tok_dt, curr_tok_var,  None)
            
        self.consume_token(TokConsts.SEMICOLON)
        return vardecl
    
    def logical_or(self) -> LogicalOP:
        node = self.logical_and()
        while self.curr_token.type == TokConsts.LOGICAL_OR and self.curr_token!= TokConsts.EOF:
            curr_token = self.curr_token
            self.consume_token(self.curr_token.type)
            node = LogicalOP(left=node, token=curr_token, right=self.logical_and())
        return node
    
    def logical_and(self) -> LogicalOP:
        node = self.equality()
        while self.curr_token.type == TokConsts.LOGICAL_AND and self.curr_token!= TokConsts.EOF:
            curr_token = self.curr_token
            self.consume_token(self.curr_token.type)
            node = LogicalOP(left=node, token=curr_token, right=self.equality())
        return node

    def equality(self) ->RelationalEqualityOp:
        chain_count_eq = 0
        node = self.relational()
        while self.curr_token.type in (TokConsts.EQUAL, TokConsts.NT_EQUAL) and self.curr_token!= TokConsts.EOF:
            curr_token = self.curr_token
            self.consume_token(self.curr_token.type)
            chain_count_eq +=1
            node = RelationalEqualityOp(left=node, token=curr_token, right=self.relational())
        node.chain_count_eq = chain_count_eq
        return node

    def relational(self) -> RelationalEqualityOp:
        chain_count_rel = 0
        node = self.expr()
        while self.curr_token.type in (TokConsts.GREATER, TokConsts.LESSTHAN) and self.curr_token!= TokConsts.EOF:
            curr_token = self.curr_token
            self.consume_token(self.curr_token.type)
            chain_count_rel +=1
            node = RelationalEqualityOp(left=node, token=curr_token, right=self.expr())
        node.chain_count_rel = chain_count_rel
        return node

    def factor(self) -> Var:
        # print()
        if self.curr_token.type == TokConsts.LPARAN:
            self.consume_token(TokConsts.LPARAN)
            node = self.logical_or()
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
        # print('NNNNNNNNN', self.curr_token)


    def term(self) -> BinOp:
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
    
    def expr(self) -> BinOp:
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
    def __init__(self, root:Main) -> None:
        self.root = root
        self.scope_container = ScopeContainer()
        self.scope_container.add_scope(SymScope('GLOBAL')) 
    
    def interpret(self) -> None:
        for child in self.root.children:
            self.visit(child)

    def raise_error(self, msg:str, exit:int) -> None:
        if exit:
            raise Exception(msg)
        else:
             print(msg)

    def visit(self, node: Union[BinOp, NumLiteral, VarAssign, RelationalEqualityOp, LogicalOP, Var,Print]) -> Union[int, str, None]:

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
            self.scope_container.current_scope_head._table[node_name] = node
            value = self.visit(node.value) if node.value else None
            node.value = value
            # self.__SYMBOL_TABLE[node_name] = node

        if isinstance(node, VarAssign):
            node_name = node.var.name
            value = self.visit(node.right_expr) 
            # node.value = value
            self.scope_container.current_scope_head._table[node_name].value = value
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
            
        if isinstance(node, LogicalOP) :
            if node.token.type == TokConsts.LOGICAL_OR:
                return int((self.visit(node.lchild) or  self.visit(node.rchild)))
            if node.token.type == TokConsts.LOGICAL_AND:
                return int((self.visit(node.lchild) and  self.visit(node.rchild)))
        
        if isinstance(node, IfElseBlock):
            condition = self.visit(node.lchild)
            if condition:
                self.scope_container.add_scope(SymScope()) 
                for stmt in node.rchild:
                    self.visit(stmt)
                self.scope_container.remove_scope()
            elif node.elsechild:
                self.scope_container.add_scope(SymScope())
                for stmt in node.elsechild:
                    self.visit(stmt)
                self.scope_container.remove_scope()

            
        if isinstance(node , Var) :
            return self.scope_container.get_symbol(node.name).value
        
        if isinstance(node ,Print):
            print(self.visit(node.value))



class Compile:
    def __init__(self) -> None:
        self.asmFile = './compile.asm'
        self.asmList = ["{}"]
        self.bss = BssData()
        self.scope_container = CompileScopeContainer()
        self.scope_container.add_scope(SymScope('GLOBAL'))
        self.__varcount = 0
        self.label_count = 0
        self.map_relational_eq = {TokConsts.GREATER: 'cmovg', TokConsts.LESSTHAN: 'cmovl', TokConsts.EQUAL: 'cmove', TokConsts.NT_EQUAL: 'cmovne'}
        self.map_logical = {TokConsts.LOGICAL_AND:'and', TokConsts.LOGICAL_OR:'or'}
        # self.all_available_regs = { "r8", "r9", "r10", "r11" }
    
    @property
    def varcount(self) -> int:
        self.__varcount +=1
        return self.__varcount
    
    def gen_label(self):
        self.label_count += 1
        return f'L{self.label_count}'

    def get_required_pre_asm(self) -> None:
        ##############
        #try to optimize this rather than extending and creating of large list
        ############## 
        self.asmList.append(textinstr)
        self.asmList.append(printintinstr)
        self.asmList.append(startinstr)
    
    def get_required_post_asm(self) -> None:
        self.asmList[0] = self.asmList[0].format(self.bss)
        self.asmList.append(exitinstr.format(0))

    def __gen_code_binary_op(self, opA:Token, opB:Token, otype:str) -> None:
        # self.__get_free_reg()
        if otype == TokConsts.PLUS:
            self.asmList.append(addinstr)
        if otype == TokConsts.SUB:
            self.asmList.append(subinstr)
        if otype == TokConsts.MULT:
            self.asmList.append(multinstr)
        if otype == TokConsts.DIV:
            self.asmList.append(divinstr)
            

    def __gen_code_numliteral(self, num:int) -> None:
        self.asmList.append(numlitinstr.format(num))

    def __gen_code_assign(self, node_name:str) -> None:
        self.asmList.append(assigninstr.format(node_name))
    
    def __gen_code_get_global_variable(self,node_name:str) -> None:
        self.asmList.append(getvarinstr.format(node_name))
    
    def __gen_code_relational_equality_op(self,opA:Token, opB:Token, token:str) -> None:

        self.asmList.append(relationalequalityinstr.format(self.map_relational_eq[token]))
    
    def __gen_code_logical_op(self, opA:Token, opB:Token, token:str) -> None:
        self.asmList.append(logicalistr.format(self.map_logical[token]))
    
    def __gen_code_print(self) -> None:
        self.asmList.append(callprintinstr)

    def __gen_code_pre_stack_block(self) -> None:
        self.asmList.append(preblockinstr)
    
    def __gen_code_check_block_condition(self) -> None:
        self.asmList.append(blockconditioninstr)
    
    def __gen_code_jne(self, label) -> None:
        self.asmList.append(jneinstr.format(label))

    def __gen_code_add_label(self, label) -> None:
        self.asmList.append(f'  {label}:')

    def __gen_code_jmp(self,label) -> None:
        self.asmList.append(jmpinstr.format(label))
    
    def __gen_code_post_stack_block(self) -> None:
        self.asmList.append(postblockconditioninstr)
    
    def __gen_code_get_local_variable(self, idx) -> None:
        self.asmList.append(localvarinstr.format(idx)) 




    def visit(self, node:Union[BinOp, NumLiteral, VarAssign, RelationalEqualityOp, LogicalOP, Var,Print]) -> None:
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
            if self.scope_container.current_scope_head.name == 'GLOBAL':
                self.bss.add_variable(node_name)
            self.scope_container.current_scope_head._table[node_name] = node
            # self.__SYMBOL_TABLE[node_name] = node
            self.visit(node.value) if node.value else None
            # self.__SYMBOL_TABLE[node_name] = node

        if isinstance(node, VarAssign):
            node_name = node.var.name
            self.visit(node.right_expr)
            if self.scope_container.current_scope_head.name == 'GLOBAL':
                self.__gen_code_assign(node_name)
            elif  self.scope_container.current_scope_head.name == LOCAL:
                self.scope_container.current_scope_head.var_id +=1
                self.scope_container.current_scope_head._table[node_name].var_id = self.scope_container.current_scope_head.var_id 

        if isinstance(node, RelationalEqualityOp):

            if getattr(node,'chain_count_eq',0)>1 or getattr(node,'chain_count_rel',0)>1:
                self.raise_error(f'Chained equality/comparison operators are found. It could result in ambigous results',exit=1)
            if node.token.type == TokConsts.GREATER:
                self.__gen_code_relational_equality_op(self.visit(node.lchild) , self.visit(node.rchild), TokConsts.GREATER)
            if node.token.type == TokConsts.LESSTHAN:
                self.__gen_code_relational_equality_op(self.visit(node.lchild) , self.visit(node.rchild), TokConsts.LESSTHAN)
            if node.token.type == TokConsts.EQUAL:
                self.__gen_code_relational_equality_op(self.visit(node.lchild) , self.visit(node.rchild), TokConsts.EQUAL)
            if node.token.type == TokConsts.NT_EQUAL:
                self.__gen_code_relational_equality_op(self.visit(node.lchild) , self.visit(node.rchild), TokConsts.NT_EQUAL)
        
        if isinstance(node, LogicalOP):
            if node.token.type == TokConsts.LOGICAL_OR:
                self.__gen_code_logical_op(self.visit(node.lchild) , self.visit(node.rchild), TokConsts.LOGICAL_OR)
            
            if node.token.type == TokConsts.LOGICAL_AND:
                self.__gen_code_logical_op(self.visit(node.lchild) , self.visit(node.rchild), TokConsts.LOGICAL_AND)
        
        if isinstance(node, IfElseBlock):
            self.visit(node.lchild)
            self.__gen_code_check_block_condition()
            self.__gen_code_pre_stack_block()
            self.scope_container.add_scope(SymScope())
            elselabel = self.gen_label()
            self.__gen_code_jne(elselabel) 
            for stmt in node.rchild:
                self.visit(stmt)
            endlabel = self.gen_label()
            endlabel = elselabel if not node.elsechild else endlabel
            self.__gen_code_jmp(endlabel)
            if node.elsechild:
                self.scope_container.remove_scope()
                self.scope_container.add_scope(SymScope())
                self.__gen_code_add_label(elselabel)
                for stmt in node.elsechild:
                    self.visit(stmt)
            self.scope_container.remove_scope()
            self.__gen_code_add_label(endlabel)
            self.__gen_code_post_stack_block()

        if isinstance(node , Var):
            if self.scope_container.current_scope_head.name == 'GLOBAL':
                # If its directly started in global
                self.__gen_code_get_global_variable(node.name)
            elif self.scope_container.current_scope_head.name == LOCAL:
                # Started from some local scope
                idx = self.scope_container.get_symbol(node.name)
                if idx == '-1':
                    # Means the search ended in global scope 
                    self.__gen_code_get_global_variable(node.name)
                else:
                    self.__gen_code_get_local_variable(idx)
        
        if isinstance(node ,Print):
            self.visit(node.value)
            self.__gen_code_print()

    def write_asm(self) -> None:
        with open(self.asmFile, 'w') as asm:
            asm.writelines('\n'.join(self.asmList))

    def compile_ast(self, root:Main) -> None:
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


