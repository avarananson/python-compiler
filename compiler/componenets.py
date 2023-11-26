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
    UNKNOWN = 'unknown'


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

class ErrWarnHandler:
    # err_count = 0
    def __init__(self) -> None:
        self.err_count = 0
        self.errors = []
        self.warnings = []
    @staticmethod
    def syntaxerror(msg):
        return f'SyntaxError: {msg}'
    def inc_error(func):
        def wrap(self, *args, **kwargs):
            self.err_count +=1
            # print(self.errors, args[0])
            ret = func(self, *args, **kwargs)
            print(ret)
            exit(1)
        return wrap
    
    @inc_error
    def unknown_syntax(self, char, lineno):
        err = f'Unrecognized syntax `{char}` at line {lineno}.'
        self.errors.append(self.syntaxerror(err))
        return err
    @inc_error
    def unexpected_syntax(self, found, expected, lineno):
        err = f'Unexpected syntax found  at line {lineno}.'
        self.errors.append(self.syntaxerror(err))
        return err
        # print()

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

    def declare_symbol_to_head(self,node_name:str, node:Any) -> None:
        if node_name in self.current_scope_head._table:
            raise ValueError(f'ERROR: {node_name} symbol already defined in the scope. ')
        self.current_scope_head._table[node_name] = node
        # self.current_scope_head._table[node_name].value = 0  # By default we assign not garbage, but 0

    def get_symbol(self, name:str) -> Any:
        curr_scope = self.current_scope_head
        while curr_scope:
            if name in curr_scope._table:
                return curr_scope._table[name]
            curr_scope = curr_scope.prev
        raise ValueError(f'ERROR: {name} symbol not defined. ')
    
    def assign_symbol(self, name:str, value:int) -> None:
        curr_scope = self.current_scope_head
        # print(f'========= CURRENT SCOPES NOW FOR  {name}===========')
        # curr_scope1= self.current_scope_head
        # while curr_scope1:
        #     print(curr_scope1.name, curr_scope1._table)
        #     curr_scope1 = curr_scope1.prev
        # print('========= END  NOW ===========')
        while curr_scope:
            if name in curr_scope._table:
                curr_scope._table[name].value = value
                break
            curr_scope = curr_scope.prev
        else:
            raise ValueError(f'ERROR: Assigning to an undeclared variable {name}.')

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
            if curr_scope.prev == None:
                return '-1'          # IF IN GLOBAL AT THE START ITSELF
            idx = curr_scope._table[name].var_id
            return f'-{(8 * idx)}'                       # IF ITS NOT IN GLOBAL AND IN THE FIRST SCOPE ITSELF
        curr_scope = curr_scope.prev
        prev_table_len = 0
        while curr_scope and curr_scope.name == LOCAL:
            if name in curr_scope._table:
                tot_variables_cnt = len(curr_scope._table)
                idx = curr_scope._table[name].var_id
                idx = ((tot_variables_cnt - idx) + 1 + prev_table_len) * 8 
                # print(f'found varibale in LOCAL scope {curr_scope.level}', name)
                return  f'+{idx}'                   # IF ITS IN LATER ON DOWN SCOPE
            prev_table_len = prev_table_len + len(curr_scope._table) + 1

            curr_scope = curr_scope.prev
        
        if curr_scope and  name in curr_scope._table :
            # print(f'found varibale in GLOBAL scope {curr_scope.level}',name)
            return '-1'                # IF STILL NOT FOUND AND NOW ITS IN GLOBAL NOW
        
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
    
