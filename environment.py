from typing import Dict, Any

import Token
import interpreter

class Environment:
    values : Dict[str, Any]

    def __init__(self):
        self.values = {}
    
    def define(self, name : str, value : Any):
        self.values[name] = value
    
    def get(self, name : Token.Token) -> Any:
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        else:
            raise interpreter.RuntimeError(
                name, 
                f"Undefined variable '{name.lexeme}'.'"
            )
    
    def assign(self, name : Token.Token, value : Any):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        else:
            raise interpreter.RuntimeError(
                name,
                f"Undefined variable '{name.lexeme}'."
            )