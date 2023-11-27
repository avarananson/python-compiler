from components import Main, IfElseBlock, VarAssign,VarDeclare, LogicalOP,NumLiteral, \
    Print, Var,BinOp, RelationalEqualityOp, Token ,TokConsts, ScopeContainer, SymScope, WhileBlock
from typing import Union

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
            self.scope_container.declare_symbol_to_head(node_name, node)
            value = self.visit(node.value) if node.value else 0
            node.value = value

        if isinstance(node, VarAssign):
            node_name = node.var.name
            value = self.visit(node.right_expr)
            self.scope_container.assign_symbol(node_name, value)
            # self.scope_container.current_scope_head._table[node_name].value = value
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

        if isinstance(node , WhileBlock):
            while self.visit(node.lchild):
                self.scope_container.add_scope(SymScope())
                for stmt in node.rchild:
                    self.visit(stmt)
                self.scope_container.remove_scope()

        if isinstance(node , Var) :
            return self.scope_container.get_symbol(node.name).value
        
        if isinstance(node ,Print):
            print(self.visit(node.value))


