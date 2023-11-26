
from componenets import Main, IfElseBlock, VarAssign,VarDeclare, LogicalOP,NumLiteral, \
    Print, Var,BinOp, RelationalEqualityOp, Token ,TokConsts, CompileScopeContainer, BssData, SymScope
from asm_helper import *
from typing import Union

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
        # if val == 0:
        #     self.asmList.append(assignconstinstr.format(node_name, 0))
        # else:
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
    
    def __gen_code_get_local_variable(self, idx:str) -> None:
        self.asmList.append(localvarinstr.format(idx)) 

    def __gen_code_change_stack_var(self, idx:str) -> None:
        self.asmList.append(changestackvarinstr.format(idx))



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
            self.scope_container.declare_symbol_to_head(node_name , node)
            if self.scope_container.current_scope_head.name == 'GLOBAL':
                self.bss.add_variable(node_name)
                # Defaulting the declared variable to be 0 always not garbage value
                self.__gen_code_numliteral(0)
                self.__gen_code_assign(node_name)
            elif  self.scope_container.current_scope_head.name == LOCAL:
                self.__gen_code_numliteral(0)
            self.scope_container.current_scope_head.var_id +=1
            self.scope_container.current_scope_head._table[node_name].var_id = self.scope_container.current_scope_head.var_id 
            self.visit(node.value) if node.value else None
            # self.__SYMBOL_TABLE[node_name] = node

        if isinstance(node, VarAssign):
            node_name = node.var.name
            self.visit(node.right_expr)
            idx = self.scope_container.get_symbol(node_name)
            if idx == '-1':
                self.__gen_code_assign(node_name)
            else:
                self.__gen_code_change_stack_var(idx)


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