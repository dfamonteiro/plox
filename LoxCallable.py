from typing import List, Any

import interpreter as i

class LoxCallable():
    def call(self, interpreter : i, arguments : List[Any]) -> Any:
        raise NotImplementedError()