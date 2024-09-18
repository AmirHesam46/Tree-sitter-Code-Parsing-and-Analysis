import matplotlib.pyplot as plt
import networkx as nx
import sh
from pathlib import Path
from tree_sitter import Language, Parser

def draw_graph(G, label=None):
    """Draw a graph using NetworkX and matplotlib."""
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.axis(False)
    pos = nx.nx_agraph.graphviz_layout(G, 'dot')
    if label:
        labels = nx.get_node_attributes(G, label)
    else:
        labels = None
    nx.draw_networkx(G, pos, ax=ax, font_size=8, labels=labels, node_color="white")
    plt.show()

def print_captures(captures):
    """Print captures from Tree-sitter queries."""
    for capture, tag in captures:
        print(f"@{tag} [{capture.type}] ({capture.start_byte}:{capture.end_byte})")
        print(quote(text(capture)), "\n")

def quote(s):
    """Format text for display."""
    return '\n'.join(f"> {line}" for line in s.splitlines())
    
def text(node):
    """Decode text from a Tree-sitter node."""
    return node.text.decode()

def instantiate_language(name, url):
    """Download and compile Tree-sitter language definition."""
    try:
        sh.git.clone(url, name)
    except sh.ErrorReturnCode as e:
        print(e.stderr.decode())
    Language.build_library(f"{name}.so", [name])
    return Language(f"{name}.so", name) 

# Instantiate language and parser
PY = instantiate_language("python", "https://github.com/tree-sitter/tree-sitter-python")
parser = Parser()
parser.set_language(PY)

def tree_to_graph(root, with_anon=False):
    """Convert a Tree-sitter parse tree to a NetworkX graph."""
    G = nx.DiGraph()
    todo = [root]
    while todo:
        node = todo.pop()
        if with_anon or node.is_named:
            G.add_node(node.id, type=node.type)
        for child in node.children:
            if with_anon or child.is_named:
                G.add_edge(node.id, child.id)
            todo.append(child)
    return G

def call_graph(root):
    """Create a call graph from the parsed source code."""
    functions_query = PY.query("(function_definition) @function")
    calls_query = PY.query("(call) @call")

    functions = functions_query.captures(root)
    G = nx.DiGraph()

    for func, _ in functions:
        name = func.child_by_field_name('name')
        calls = calls_query.captures(func)
        G.add_node(text(name))
        for call, _ in calls:
            target = call.child_by_field_name('function')
            G.add_edge(text(name), text(target))

    return G

# Example code for parsing
source = b"""
def add(a, b):
    return a + b

def hello(name):
    print(f"Hello {name}")

def main():
    add(2022, 1)
    add(2022, 1.0)
    hello("🌍")
"""

# Parse the source code
tree = parser.parse(source)
root = tree.root_node

# Draw the parse tree
draw_graph(tree_to_graph(root), "type")

# Extract function definitions
query = PY.query("""
(function_definition) @function
""")
captures = query.captures(root)
print_captures(captures)

# Extract function names
query = PY.query("""
(function_definition (identifier) @function.name)
""")
captures = query.captures(root)
print_captures(captures)

# Extract functions matching regex
query = PY.query("""
(function_definition (identifier) @function.name) (#match? @function.name "h.+")
""")
captures = query.captures(root)
print_captures(captures)

# Extract functions with one or two parameters
query = PY.query("""
(function_definition (parameters . (identifier) .)) @unary_function
(function_definition (parameters . (identifier) . (identifier) .)) @binary_function
""")
captures = query.captures(root)
print_captures(captures)

# Extract function calls with two integers or one integer and one float
query = PY.query("""
(call (argument_list . (integer) (integer) .)) @int_call
(call (argument_list . (integer) [(integer) (float)] .)) @int_float_call
""")
captures = query.captures(root)
print_captures(captures)

# Create a call graph
G = call_graph(root)
draw_graph(G)

# Optional: Clone and analyze a repository
try:
    sh.git.clone("https://github.com/dioptra-io/iris.git")
except sh.ErrorReturnCode as e:
    print(e.stderr.decode())
    files = Path("iris/iris").glob("**/*.py")
G = nx.DiGraph()

for file in files:
    tree = parser.parse(file.read_bytes())
    subgraph = call_graph(tree.root_node)
    G.add_edges_from(subgraph.edges())

print("Top 10 nodes by out-degree:")
print(sorted(G.out_degree(), key=lambda x: x[1], reverse=True)[:10])
print("Top 10 nodes by in-degree:")
print(sorted(G.in_degree(), key=lambda x: x[1], reverse=True)[:10])

# Display the longest path in the DAG
print("Longest path in the DAG:")
print(nx.dag_longest_path(G))