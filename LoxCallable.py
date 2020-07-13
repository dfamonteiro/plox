from typing import List, Any

class LoxCallable():
    def call(self, interpreter, arguments : List[Any]) -> Any:
        raise NotImplementedError()

    def arity(self) -> int:
        raise NotImplementedError()