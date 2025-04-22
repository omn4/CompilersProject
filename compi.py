import ply.lex as lex
import ply.yacc as yacc
from collections import defaultdict
# final1 LoopUnrolling , Loop Fusion , LICM 
# --- Lexer ---
tokens = (
    'NUMBER', 'ID', 'FOR', 'INT', 'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE',
    'SEMICOLON', 'EQUALS', 'PLUS', 'LBRACKET', 'RBRACKET', 'LE', 'LT', 'PLUSPLUS', 'PLUSEQUAL',
)

# Reserved words
reserved = {
    'for': 'FOR',
    'int': 'INT',
}

t_FOR = r'for'
t_INT = r'int'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_SEMICOLON = r';'
t_EQUALS = r'='
t_PLUS = r'\+'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_LE = r'<='
t_LT = r'<'
t_PLUSPLUS = r'\+\+'
t_PLUSEQUAL = r'\+='

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')  # Check for reserved words
    return t

t_ignore = ' \t'

def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()

# --- Debug Lexer ---
def debug_lexer(input_code):
    lexer.input(input_code)
    print("Lexer tokens:")
    while True:
        tok = lexer.token()
        if not tok:
            break
        print(f"Token: {tok.type}, Value: {tok.value}, Line: {tok.lineno}")

# --- Parser ---
class ASTNode:
    def __init__(self, type, children=None, value=None):
        self.type = type
        self.children = children or []
        self.value = value

def print_ast(node, indent=0):
    """Print the AST in a hierarchical format."""
    indent_str = "  " * indent
    print(f"{indent_str}Node(type={node.type}, value={node.value})")
    for child in node.children:
        print_ast(child, indent + 1)

def p_program(p):
    '''program : statements'''
    p[0] = ASTNode('program', children=[p[1]])

def p_statements(p):
    '''statements : statement statements
                  | statement'''
    if len(p) == 3:
        p[0] = ASTNode('statements', children=[p[1], p[2]])
    else:
        p[0] = ASTNode('statements', children=[p[1]])

def p_statement(p):
    '''statement : declaration
                 | for_loop
                 | assignment'''
    p[0] = p[1]

def p_declaration(p):
    '''declaration : INT ID LBRACKET NUMBER RBRACKET SEMICOLON'''
    p[0] = ASTNode('decl', value={'id': p[2], 'size': p[4]})

def p_for_loop(p):
    '''for_loop : FOR LPAREN for_init SEMICOLON for_cond SEMICOLON for_incr RPAREN LBRACE statements RBRACE'''
    p[0] = ASTNode('for', children=[p[10]], value={
        'var': p[3].value['var'], 'start': p[3].value['start'], 
        'end': p[5].value['end'], 'body': p[10], 'cond_op': p[5].value['op']
    })

def p_for_init(p):
    '''for_init : INT ID EQUALS NUMBER
                | ID EQUALS NUMBER'''
    p[0] = ASTNode('for_init', value={'var': p[2], 'start': p[4] if len(p) == 5 else p[3]})

def p_for_cond(p):
    '''for_cond : ID LE NUMBER
                | ID LT NUMBER'''
    p[0] = ASTNode('for_cond', value={'var': p[1], 'op': p[2], 'end': p[3]})

def p_for_incr(p):
    '''for_incr : ID PLUSPLUS
                | ID PLUSEQUAL NUMBER'''
    p[0] = ASTNode('for_incr', value={'var': p[1], 'type': '++' if p[2] == '++' else '+='})

def p_assignment(p):
    '''assignment : ID LBRACKET ID RBRACKET EQUALS expression SEMICOLON
                  | ID LBRACKET NUMBER RBRACKET EQUALS expression SEMICOLON
                  | ID EQUALS expression SEMICOLON'''
    if len(p) == 8:
        p[0] = ASTNode('assign', children=[p[6]], value={'array': p[1], 'index': p[3], 'is_array': True})
    elif len(p) == 5:
        p[0] = ASTNode('assign', children=[p[3]], value={'var': p[1], 'is_array': False})

def p_expression(p):
    '''expression : ID LBRACKET ID RBRACKET PLUS ID LBRACKET ID RBRACKET
                  | ID LBRACKET NUMBER RBRACKET PLUS ID LBRACKET NUMBER RBRACKET
                  | ID LBRACKET ID RBRACKET PLUS NUMBER
                  | ID LBRACKET NUMBER RBRACKET PLUS NUMBER
                  | ID LBRACKET ID RBRACKET
                  | ID LBRACKET NUMBER RBRACKET
                  | NUMBER'''
    if len(p) == 10:
        p[0] = ASTNode('plus', value={
            'left': {'array': p[1], 'index': p[3]},
            'right': {'array': p[6], 'index': p[8]}
        })
    elif len(p) == 7 and isinstance(p[3], int):
        p[0] = ASTNode('plus', value={
            'left': {'array': p[1], 'index': p[3]},
            'right': {'number': p[6]}
        })
    elif len(p) == 7 and isinstance(p[3], str):
        p[0] = ASTNode('plus', value={
            'left': {'array': p[1], 'index': p[3]},
            'right': {'number': p[6]}
        })
    elif len(p) == 5 and isinstance(p[3], (int, str)):
        p[0] = ASTNode('array', value={'array': p[1], 'index': p[3]})
    elif len(p) == 2:
        p[0] = ASTNode('number', value={'number': p[1]})

def p_error(p):
    if p:
        lines = parser.input_code.split('\n')
        line = lines[p.lineno - 1].strip() if 0 < p.lineno <= len(lines) else "<unknown>"
        print(f"Syntax error at token '{p.value}' (line {p.lineno}): {line}")
    else:
        print("Syntax error at EOF")

parser = yacc.yacc(debug=True)
parser.input_code = ""

# --- Intermediate Representation ---
class IRInstruction:
    def __init__(self, op, args=None, result=None):
        self.op = op
        self.args = args or []
        self.result = result

class IRLoop:
    def __init__(self, var, start, end, body, cond_op):
        self.var = var
        self.start = start
        self.end = end
        self.body = body
        self.cond_op = cond_op

class IRProgram:
    def __init__(self):
        self.decls = []
        self.loops = []
        self.instructions = []

def ast_to_ir(ast):
    if ast is None:
        raise ValueError("AST is None, parsing failed")
    program = IRProgram()
    def traverse(node):
        print(f"Traversing node: {node.type}")
        if node.type == 'program':
            traverse(node.children[0])
        elif node.type == 'statements':
            for child in node.children:
                traverse(child)
        elif node.type == 'decl':
            program.decls.append(node.value)
        elif node.type == 'for':
            body = []
            loop = IRLoop(node.value['var'], node.value['start'], node.value['end'], body, node.value['cond_op'])
            program.loops.append(loop)
            traverse(node.children[0])
        elif node.type == 'assign':
            if node.value.get('is_array', False):
                result = f"{node.value['array']}[{node.value['index']}]"
            else:
                result = node.value['var']
            expr = node.children[0]
            if expr.type == 'plus':
                v = expr.value
                if 'array' in v['right']:
                    args = [f"{v['left']['array']}[{v['left']['index']}]",
                            f"{v['right']['array']}[{v['right']['index']}]"]
                else:
                    args = [f"{v['left']['array']}[{v['left']['index']}]",
                            str(v['right']['number'])]
                instr = IRInstruction('add', args=args, result=result)
            elif expr.type == 'array':
                v = expr.value
                instr = IRInstruction('assign',
                                     args=[f"{v['array']}[{v['index']}]"],
                                     result=result)
            elif expr.type == 'number':
                instr = IRInstruction('assign',
                                     args=[str(expr.value['number'])],
                                     result=result)
            if program.loops:
                program.loops[-1].body.append(instr)
            else:
                program.instructions.append(instr)
    traverse(ast)
    return program

# --- Loop Optimizations ---
class Optimizer:
    def __init__(self, program):
        self.program = program

    def loop_invariant_code_motion(self):
        for loop in self.program.loops:
            invariants = []
            new_body = []
            for instr in loop.body:
                args_str = ''.join(instr.args)
                result_str = instr.result if instr.result else ''
                if loop.var not in args_str and loop.var not in result_str:
                    invariants.append(instr)
                else:
                    new_body.append(instr)
            loop.body = new_body
            self.program.instructions.extend(invariants)

    def loop_unrolling(self, factor=2):
        for loop in self.program.loops:
            if loop.cond_op == '<=':
                iterations = loop.end - loop.start + 1
            else:  # '<'
                iterations = loop.end - loop.start
            if iterations % factor == 0:
                new_body = []
                for i in range(factor):
                    for instr in loop.body:
                        # Use original loop.var if offset is 0, otherwise add offset
                        new_var = loop.var if i == 0 else f"{loop.var}+{i}"
                        new_args = [arg.replace(loop.var, new_var) for arg in instr.args]
                        new_result = instr.result.replace(loop.var, new_var) if instr.result else None
                        new_instr = IRInstruction(instr.op, args=new_args, result=new_result)
                        new_body.append(new_instr)
                loop.body = new_body
                # loop.end = loop.start + (loop.end - loop.start) // factor
                loop.body.append(IRInstruction('inc', args=[loop.var, str(factor-1)]))
            else:
                print(f"Warning: Loop from {loop.start} to {loop.end} not unrollable by factor {factor}")

    def loop_fusion(self):
        new_loops = []
        i = 0
        while i < len(self.program.loops):
            if i + 1 < len(self.program.loops):
                loop1 = self.program.loops[i]
                loop2 = self.program.loops[i + 1]
                if (loop1.start == loop2.start and loop1.end == loop2.end and
                    loop1.var == loop2.var and loop1.cond_op == loop2.cond_op):
                    loop1.body.extend(loop2.body)
                    i += 2
                    new_loops.append(loop1)
                    continue
            new_loops.append(self.program.loops[i])
            i += 1
        self.program.loops = new_loops

# --- Code Generation ---
def ir_to_code(program):
    code = []
    for decl in program.decls:
        code.append(f"int {decl['id']}[{decl['size']}];")
    for instr in program.instructions:
        if instr.op == 'add':
            code.append(f"{instr.result} = {instr.args[0]} + {instr.args[1]};")
        elif instr.op == 'assign':
            code.append(f"{instr.result} = {instr.args[0]};")
    for loop in program.loops:
        cond = '<=' if loop.cond_op == '<=' else '<'
        code.append(f"for (int {loop.var} = {loop.start}; {loop.var} {cond} {loop.end}; {loop.var}++) {{")
        for instr in loop.body:
            if instr.op == 'add':
                code.append(f"  {instr.result} = {instr.args[0]} + {instr.args[1]};")
            elif instr.op == 'assign':
                code.append(f"  {instr.result} = {instr.args[0]};")
            elif instr.op == 'inc':
                code.append(f"  {instr.args[0]} += {instr.args[1]};")
        code.append("}")
    return "\n".join(code)

# --- Main Compiler ---
def compile_code(input_code):
    print("Parsing input code...")
    debug_lexer(input_code)
    parser.input_code = input_code
    ast = parser.parse(input_code)
    if ast is None:
        raise ValueError("Parsing failed, AST is None")
    print("\nAST Structure:")
    print_ast(ast)
    print("\nConverting AST to IR...")
    ir = ast_to_ir(ast)
    print("Applying optimizations...")
    optimizer = Optimizer(ir)
    optimizer.loop_invariant_code_motion()
    optimizer.loop_fusion()
    optimizer.loop_unrolling(factor=2)
    print("Generating output code...")
    return ir_to_code(ir)

# --- Example Usage ---
if __name__ == "__main__":
    input_code = """
    int a[100];
    int b[100];
    int c[100];
    int x;
    for (int i = 0; i <= 100; i++) {
        a[i] = b[i] + c[i];
        x = b[0] + c[0];
    }
    for (int i = 0; i <= 100; i++) {
        a[i] = a[i] + 1;
    }
    """
    try:
        optimized_code = compile_code(input_code)
        print("\nOptimized Code:")
        print(optimized_code)
    except ValueError as e:
        print(f"Error: {e}")
        print("\nTrying minimal test input...")
        minimal_input = """
        int a[100];
        int x;
        for (int i = 0; i <= 100; i++) {
            x = a[i] + 1;
        }
        """
        try:
            optimized_code = compile_code(minimal_input)
            print("\nOptimized Code (minimal input):")
            print(optimized_code)
        except ValueError as e:
            print(f"Error with minimal input: {e}")