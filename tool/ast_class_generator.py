from typing import List
from pathlib import Path

INDENT = " " * 4

def defineAst(output_dir : str, base_name : str, types : List[str]):
    target = Path(output_dir) / Path(base_name.lower() + ".py")

    with open(target, "w") as f:
        f.write("\n".join(
            [
                "# Autogenerated file",
                "",
                "from Token import Token",
                "",
            ])
        )
        f.write(gen_visitor(base_name, types))
        
        f.write("\n".join(
            [
                f"class {base_name}:",
                INDENT + f"def accept(self, visitor : {base_name}Visitor):",
                INDENT * 2 + "raise NotImplementedError()",
                "\n"
            ])
        )

        for i in types:
            f.write(gen_class(base_name, i))
            

def gen_class(base_name : str, production : str) -> str:

    class_name, fields_str = map(lambda s: s.strip(), production.split(":"))

    fields = list(map(lambda s: s.strip().split(), fields_str.split(",")))

    for i in range(len(fields)):
        if fields[i][0] == "Object":
            fields[i][0] = "object"

    code = [ f"class {class_name}({base_name}):"]

    for _type, name in fields:
        code.append(
            INDENT  + f"{name} : {_type}"
        )
    
    code.append("")

    init_params = ', '.join([name + ' : ' + _type for _type, name in fields])

    init = INDENT  + f"def __init__(self, {init_params}):"

    code.append(init)

    for _type, name in fields:
        code.append(
            INDENT * 2 + f"self.{name} = {name}"
        )
    
    code.append("")

    code.extend(
            [
                INDENT + f"def accept(self, visitor : {base_name}Visitor):",
                INDENT * 2 + f"return visitor.visit_{class_name.lower()}_{base_name.lower()}(self)"
            ]
        )

    code.append("\n\n")
    return "\n".join(code)

def gen_visitor(base_name : str, productions : List[str]) -> str:
    INDENT = " " * 4

    code = ["", f"class {base_name}Visitor:"]

    for prod in productions:
        class_name, fields_str = map(lambda s: s.strip(), prod.split(":"))
        
        code.append(
            INDENT  + 
            f"def visit_{class_name.lower()}_{base_name.lower()}(self, {base_name.lower()}):"
        )
        code.append(INDENT * 2 + "raise NotImplementedError()")
    
    code.append("\n\n")
    return "\n".join(code)

if __name__ == "__main__":
    defineAst(".", "Expr",
        [
            "Assign   : Token name, Expr value",
            "Binary   : Expr left, Token operator, Expr right",
            "Grouping : Expr expression",
            "Literal  : Object value",
            "Logical  : Expr left, Token operator, Expr right",
            "Unary    : Token operator, Expr right",
            "Variable : Token name"
        ]
    )

    defineAst(".", "Stmt",
        [
            "Block      : List[Stmt] statements",
            "Expression : Expr expression",
            "If         : Expr condition, Stmt then_branch, Stmt else_branch",
            "Print      : Expr expression",
            "Var        : Token name, Expr initializer"
        ]
    )