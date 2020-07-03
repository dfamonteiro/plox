from typing import List

from token import Token, TokenType
import lox

class Scanner:
    source  : str
    tokens  : List[Token]

    start   : int
    current : int
    line    : int

    def __init__(self, source : str):
        self.source  = source
        self.tokens  = []
        self.start   = 0
        self.current = 0
        self.line    = 1

    def scan_tokens(self) -> List[Token]:
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        
        return self.tokens
    
    def is_at_end(self) -> bool:
        return self.current >= len(self.source)
    
    def scan_token(self) -> None:
        char = self.advance()

        if   char == "(":
            self.add_token(TokenType.LEFT_PAREN)
        elif char == ")":
            self.add_token(TokenType.RIGHT_PAREN)
        elif char == "{":
            self.add_token(TokenType.LEFT_BRACE)
        elif char == "}":
            self.add_token(TokenType.RIGHT_BRACE)
        elif char == ",":
            self.add_token(TokenType.COMMA)
        elif char == ".":
            self.add_token(TokenType.DOT)
        elif char == "-":
            self.add_token(TokenType.MINUS)
        elif char == "+":
            self.add_token(TokenType.PLUS)
        elif char == ";":
            self.add_token(TokenType.SEMICOLON)
        elif char == "*":
            self.add_token(TokenType.STAR)
        elif char == "!":
            if self.match("="):
                self.add_token(TokenType.BANG_EQUAL)
            else:
                self.add_token(TokenType.BANG)   
        elif char == "=":
            if self.match("="):
                self.add_token(TokenType.EQUAL_EQUAL)
            else:
                self.add_token(TokenType.EQUAL)
        elif char == "<":
            if self.match("="):
                self.add_token(TokenType.LESS_EQUAL)
            else:
                self.add_token(TokenType.LESS)
        elif char == ">":
            if self.match("="):
                self.add_token(TokenType.GREATER_EQUAL)
            else:
                self.add_token(TokenType.GREATER)
        
        elif char == "/":
            if self.match("/"): # It's a comment
                while self.peek() != "\n" and not self.is_at_end():
                    self.advance()
            else:
                self.add_token(TokenType.SLASH)
        
        elif char in " \r\t":
            pass
        elif char == "\n":
            self.line += 1

        elif char == "\"":
            self.string()
        
        elif char.isdigit():
            self.number()

        else:
            lox.error(self.line, "Unexpected character")
    
    def advance(self):
        self.current += 1
        return self.source[self.current - 1]
    
    def add_token(self, token_type : TokenType, literal : object = None):
        text = self.source[self.start : self.current]
        self.tokens.append(Token(token_type, text, literal, self.line))
    
    def match(self, expected : str) -> bool:
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False

        self.current += 1
        return True
    
    def peek(self) -> str:
        if self.is_at_end():
            return "\0"
        else:
            return self.source[self.current]
    
    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        else:
            return self.source[self.current + 1]
    
    def string(self):
        while self.peek() != "\"" and not self.is_at_end():
            if self.peek() == "\n":
                self.line += 1
            self.advance()
        
        if self.is_at_end():
            lox.error(self.line, "Unterminated string.")
            return
        
        # The closing ".
        self.advance()

        # Trim the surrounding quotes.
        value = self.source[self.start + 1 : self.current - 1]
        self.add_token(TokenType.STRING, value)
    
    def number(self):
        while self.peek().isdigit():
            self.advance()
        
        # Look for a fractional part.
        if self.peek() == "." and self.peek_next().isdigit():
            self.advance() # Consume the "."

            while self.peek().isdigit():
                self.advance()
        
        self.add_token(
            TokenType.NUMBER,
            float(self.source[self.start : self.current])
        )
