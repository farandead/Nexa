# imports
from string_with_errors import *

# CONSTANTS
DIGITS = '0123456789'


# ERROR CLASS
class Error:
    def __init__(self,pos_start,pos_end, error_name,details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def as_string(self):
        result = f'{self.error_name}:{self.details}'
        # to show the file name and line number of the error
        result+= f'\nFile{self.pos_start.file_name} ,line {self.pos_start.line_num + 1}'
        result+='\n\n' + string_with_errors(self.pos_start.file_text,self.pos_start,self.pos_end)
        return result
    # standard method used by lexer when it comes accross the char it doesn't support

class IllegalCharError(Error):
    def __init__(self,pos_start,pos_end,details):
        super().__init__(pos_start,pos_end,"Illegal Character ",details)

class InvalidSyntaxError(Error):
    def __init__(self,pos_start,pos_end,details=''):
        super().__init__(pos_start,pos_end,"Invalid Syntax ",details)
# Postion class to keep track of line number and column no and index no to pin point the exact source of error for instance
class Position:
    def __init__(self, index, line_num,col,file_name,file_text):
        self.index = index
        self.line_num = line_num
        self.col = col
        self.file_name = file_name
        self.file_text = file_text

    def advance(self, current_char=None):
        self.index+=1
        self.col+=1

        if current_char == '\n':
            self.line_num+=1
            self.column = 0

        return self
    
    def copy(self):
        return Position(self.index, self.line_num,self.col,self.file_name,self.file_text)

# TOKENS
TT_INT = 'TT_INT'
TT_FLOAT = 'FLOAT'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_EOF = 'EOF'
class Token:
    def __init__(self, type_,value=None,pos_start=None,pos_end= None):
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()
        if pos_end:
            self.pos_end = pos_end
    
    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'

# LEXER CLASS

class Lexer:
    def __init__(self,file_name,text):
        self.file_name = file_name
        self.text = text
        # the reason for this is that advance method will imediatly increment it with one
        # we intiate the postition method to update the columns, index and line position
        self.pos = Position(-1,0,-1,file_name,text)
        self.current_char = None
        self.advance()

    # advances to the next character
    def advance( self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.index] if self.pos.index < len(self.text) else None

    def make_tokens(self):
        tokens = []
        while self.current_char != None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char == '+':
                print("goes here")
                tokens.append(Token(TT_PLUS,pos_start=self.pos))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS,pos_start=self.pos))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL,pos_start=self.pos))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV,pos_start=self.pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN,pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN,pos_start=self.pos))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                # we use self.pos because we already called the advance method
                return [], IllegalCharError(pos_start,self.pos,"'"  + char + "'")
        # this none is for the error if there is not error in the tokens

        tokens.append(Token(TT_EOF,pos_start=self.pos))
        return tokens,None

    def make_number(self):
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()
        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == ".":
                if dot_count == 1 : 
                    break
                dot_count+=1
                num_str+="."
            else:
                num_str+= self.current_char
            self.advance()
        
        if dot_count == 0:
            return Token(TT_INT,int(num_str),pos_start,self.pos)
        else:
            return Token(TT_FLOAT,float(num_str),pos_start,self.pos)


#    im using a (AST) tree structure for making an experessions and we are defining the nodes for it
class NumberNode:
    def __init__(self, token):
        self.token = token
    
    def __repr__(self):
        return f'{self.token}'

# This is a binary operation node that would be for operations in between the numbers

class BinOpNode:
    def __init__(self, left_node,operater_node,right_node):
        self.left_node = left_node
        self.operater_node = operater_node
        self.right_node = right_node

    def __repr__(self):
        return f'({self.left_node},{self.operater_node},{self.right_node})'  

# The parser class for making the experessions
class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None

    def register(self,res):
        if isinstance(res,ParseResult):
            if res.error: self.error = res.error
            return res.node
            
        return res

    def success(self,node):
        self.node = node
        return self
        
    
    def failure(self,error):
        self.error = error
        return self
        
    

class Parser:
    def __init__(self,tokens):
        self.tokens = tokens
        self.token_index = 1
        self.advance()

    def advance(self,current_char=None):
        self.token_index+=1 
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
        return self.current_token

    def parse(self):
        res = self.expr()
        if not res.error and self.current_token.type != TT_EOF:
            return res.failure(InvalidSyntaxError(self.current_token.self.current_token.pos_start,self.current_token.pos_end,"Expected '+', '-', '*' or '/ "))
        return res

    def factor(self):
        res = ParseResult()
        token = self.current_token

        if token.type in (TT_FLOAT,TT_INT):
            res.register(self.advance())
            return res.success(NumberNode(token))
    
        return res.failure(InvalidSyntaxError(token.pos_start,token.pos_end,"Expected int or float"))
    def term(self):
        return self.bin_op(self.factor,(TT_MUL,TT_DIV))
    
    def expr(self):
        return self.bin_op(self.term,(TT_PLUS,TT_MINUS))
    # it is going to take terms in case of experssions for func and factors when it comes to terms
    def bin_op(self,func,ops):
        res = ParseResult()
        # it will take the parseresult and take the node from it and assign the node not the whole parse result
        left = res.register(func())
        if res.error: return res

        while self.current_token.type in ops:
            operator_token = self.current_token
            res.register(self.advance())
            right = res.register(func())
            if res.error: return res
            left = BinOpNode(left,operator_token,right)
        
        return res.success(left)
    
def run(fn,text):
    # Generating Tokens
    lexer = Lexer(fn,text)
    tokens,error = lexer.make_tokens()
    if error: return None,error
    # Generating AST 
    parser = Parser(tokens)
    ast = parser.parse()
    return ast.node, ast.error
