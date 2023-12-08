from components import Main, IfElseBlock, VarAssign,VarDeclare, LogicalOP, NumLiteral, \
    Print, Var,BinOp, RelationalEqualityOp, Token ,TokConsts, WhileBlock, StringLiteral
from lexer import Lexer
from typing import List ,Union, Any

class Parser:

    def __init__(self, lexer:Lexer) -> None:
        self.curr_token = lexer.get_next_token()
        self.lexer = lexer
        self.prev = 0
    
    def raise_error(self, msg:str, exit:int) -> None:
        if exit:
            raise Exception(msg)
        else:
            print(msg)

    def consume_token(self, TYPE:str) -> None:
        
        if self.curr_token.type != TYPE and self.curr_token.type != TokConsts.UNKNOWN:
            # print(self.curr_token.type ,TYPE)
            # self.raise_error(f'Syntax error at position {self.lexer.curr_pos }', exit=1)
            self.lexer.errhandler.unexpected_syntax(self.curr_token.type,TYPE, self.prev if TYPE == ';' else self.lexer.lineno)
        else:
            self.prev = self.lexer.lineno
            self.curr_token = self.lexer.get_next_token()

    def parse(self) -> Main:
        stmts =  self.statements()
        root = Main()
        for node in stmts:
            root.children.append(node)
        return root

    
    def statements(self) ->None:
        _statements = []
        while self.curr_token.type != TokConsts.EOF and self.curr_token.type != TokConsts.UNKNOWN:
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
        elif self.curr_token.type == TokConsts.WHILE:
            return(self.whilestmt())

        else:
            self.lexer.errhandler.unexpected_syntax(self.curr_token.type, str((TokConsts.DATATYPE,TokConsts.IDENTIFIER,TokConsts.PRINT,TokConsts.IF)), self.lexer.lineno)
            self.curr_token = Token(TokConsts.UNKNOWN, TokConsts.UNKNOWN)
            return None

    def whilestmt(self) -> None:
        self.consume_token(TokConsts.WHILE)
        condition = self.logical_or()
        self.consume_token(TokConsts.LCURLY)
        block = []
        while self.curr_token.type != TokConsts.RCURLY:
            block.append(self.statement())
        self.consume_token(TokConsts.RCURLY)
        return WhileBlock(condition, TokConsts.WHILE, block)

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
        elif self.curr_token.type == TokConsts.STRING:
            token = self.curr_token
            self.consume_token(TokConsts.STRING)
            return StringLiteral(token.value)
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
