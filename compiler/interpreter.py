from components import Main, IfElseBlock, VarAssign,VarDeclare, LogicalOP,NumLiteral, \
    Print, Var,BinOp, RelationalEqualityOp, Token ,TokConsts, ScopeContainer, SymScope, WhileBlock, StringLiteral, Result, ErrWarnHandler, SUPPORTED_OPERATIONS
from typing import Union

class Interpreter:
    def __init__(self, root:Main) -> None:
        self.root = root
        self.scope_container = ScopeContainer()
        self.scope_container.add_scope(SymScope('GLOBAL')) 
        self.error_handler = ErrWarnHandler()
    
    def interpret(self) -> None:
        for child in self.root.children:
            self.visit(child)

    def check_type_and_eligibilty(self,lchild: Result, rchild: Result, operator: str ) -> None:
        # print(lchild.type)
        # print(rchild.type)
        if lchild.type != rchild.type:
            self.error_handler.operand_type_error(operator)
        if operator not in SUPPORTED_OPERATIONS[lchild.type]:
            self.error_handler.operation_not_supported(operator)


    def raise_error(self, msg:str, exit:int) -> None:
        if exit:
            raise Exception(msg)
        else:
             print(msg)
    # @profile
    def visit(self, node: Union[BinOp, NumLiteral, VarAssign, RelationalEqualityOp, LogicalOP, Var,Print]) -> Union[int, str, None]:

        if isinstance(node, BinOp):
            lchild = self.visit(node.lchild)
            rchild = self.visit(node.rchild)
            # print('l;',rchild.value)
            self.check_type_and_eligibilty(lchild, rchild, node.token.type)

            if node.token.type == TokConsts.PLUS:
                return Result((lchild.value + rchild.value), lchild.type )
            if node.token.type == TokConsts.SUB:
                return Result((lchild.value - rchild.value), lchild.type )
            if node.token.type == TokConsts.DIV:
                return Result((lchild.value // rchild.value), lchild.type )
            if node.token.type == TokConsts.MULT:
                return Result((lchild.value * rchild.value), lchild.type )
            
        if isinstance(node, NumLiteral):
            return Result(node.value, 'int')
        
        if isinstance(node, StringLiteral):
            return Result(node.value, 'str')
         
        if isinstance(node, VarDeclare):
            node_name = node.var.name
            self.scope_container.declare_symbol_to_head(node_name, node)
            value_node = self.visit(node.value) if node.value else Result(0, 'int')
            node.value = value_node

        if isinstance(node, VarAssign):
            node_name = node.var.name
            node = self.visit(node.right_expr)
            self.scope_container.assign_symbol(node_name, node)
            # print('a',node.value)
            # self.scope_container.current_scope_head._table[node_name].value = value
            return node
        
        if isinstance(node, RelationalEqualityOp):
            lchild = self.visit(node.lchild)
            rchild = self.visit(node.rchild)
            # print('l;',rchild.value)
            self.check_type_and_eligibilty(lchild, rchild, node.token.type)
            if getattr(node,'chain_count_eq',0)>1 or getattr(node,'chain_count_rel',0)>1:
                self.raise_error(f'Chained equality/comparison operators are found. It could result in ambigius results',exit=1)
            if node.token.type == TokConsts.GREATER:
                return Result(int(lchild.value > rchild.value), lchild.type)
            if node.token.type == TokConsts.LESSTHAN:
                return Result(int(lchild.value < rchild.value), lchild.type)
            if node.token.type == TokConsts.EQUAL:
                return Result(int(lchild.value == rchild.value), lchild.type)
            if node.token.type == TokConsts.NT_EQUAL:
                return Result(int(lchild.value != rchild.value), lchild.type)
            
        if isinstance(node, LogicalOP) :
            lchild = self.visit(node.lchild)
            rchild = self.visit(node.rchild)
            self.check_type_and_eligibilty(lchild, rchild, node.token.type)
            if node.token.type == TokConsts.LOGICAL_OR:
                return Result(int(lchild.value or rchild.value), lchild.type)
            if node.token.type == TokConsts.LOGICAL_AND:
                return Result(int(lchild.value and rchild.value), lchild.type)
        
        if isinstance(node, IfElseBlock):
            condition = self.visit(node.lchild).value
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

        if isinstance(node , WhileBlock):
            while self.visit(node.lchild).value:
                self.scope_container.add_scope(SymScope())
                for stmt in node.rchild:
                    self.visit(stmt)
                self.scope_container.remove_scope()

        if isinstance(node , Var) :
            # print('kamui',self.scope_container.get_symbol(node.name))
            value = self.scope_container.get_symbol(node.name).value
            # print(node.name, value.value)
            type = self.scope_container.get_symbol(node.name).value.type
            return Result(value.value, type)
        
        if isinstance(node ,Print):
            print(self.visit(node.value).value)

