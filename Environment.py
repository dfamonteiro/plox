from typing import Dict, Any, Union

import Token
import Interpreter

class Environment:
    values : Dict[str, Any]

    def __init__(self, enclosing = None):
        self.values = {}
        self.enclosing = enclosing
    
    def define(self, name : str, value : Any):
        self.values[name] = value
    
    def get(self, name : Token.Token) -> Any:
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        if self.enclosing != None:
            return self.enclosing.get(name)

        raise Interpreter.RuntimeError(
            name, 
            f"Undefined variable '{name.lexeme}'.'"
        )
    
    def assign(self, name : Token.Token, value : Any):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return

        if self.enclosing != None:
            self.enclosing.assign(name, value)
            return

        raise Interpreter.RuntimeError(
            name,
            f"Undefined variable '{name.lexeme}'."
        )
    
    def get_at(self, distance : int, name : str):
        return self.ancestor(distance).values.get(name)
    
    def assign_at(self, distance : int, name : Token.Token, value : Any):
        self.ancestor(distance).values[name.lexeme] = value
    
    def ancestor(self, distance : int):
        environment = self

        for _ in range(distance):
            environment = environment.enclosing
        
        return environment