# Tree-sitter Code Parsing and Analysis

## Overview

This project demonstrates how to use Tree-sitter to parse and analyze source code. Tree-sitter is a parser generator tool and an incremental parsing library that builds concrete syntax trees for source files and updates them efficiently as the file changes. This README explains how to set up and use the provided Python program to parse source code, visualize the parse tree, and extract information such as function definitions and calls.

## Features

- Parse Source Code: Parses Python source code using Tree-sitter.
- Visualize Parse Tree: Draw a graph of the parse tree with nodes representing syntax elements.
- Extract Information: Queries and prints function definitions, names, and calls.
- Analyze Code Repository: Clones a repository, parses Python files, and builds a call graph.

## Prerequisites

- Python 3.x
- matplotlib for plotting graphs
- networkx for graph handling
- sh for shell command execution
- tree-sitter for parsing

You can install the required Python packages using pip:
```
pip install matplotlib networkx sh tree-sitter
```
## Getting Started

### 1. Clone the Repository

Clone the repository to your local machine:
```
git clone <repository-url>
cd <repository-directory>
```
### 2. Install Dependencies

Install the required Python packages:
```
pip install matplotlib networkx sh tree-sitter
```
### 3. Run the Program

The program demonstrates parsing, visualization, and analysis. You can run the provided script as follows:
```
python tree_sitter_analysis.py
```
### 4. Optional: Clone and Analyze a Repository

The script includes an optional section to clone and analyze a GitHub repository. Modify the sh.git.clone("https://github.com/dioptra-io/iris.git") line if you want to use a different repository URL.

## Code Explanation

### Imports and Setup
```
import matplotlib.pyplot as plt
import networkx as nx
import sh
from pathlib import Path
from tree_sitter import Language, Parser
```
- **`matplotlib.pyplot**: For plotting the parse tree.
- **networkx**: For graph manipulation and visualization.
- **sh**: For executing shell commands.
- **pathlib.Path**: For file path handling.
- **tree_sitter**: For parsing source code.

### Helper Functions

- **draw_graph(G, label=None)**: Draws a NetworkX graph G with optional labels.
- **print_captures(captures)**: Prints query captures with details.
- **quote(s)**: Formats text for display.
- **text(node)**: Decodes text from a Tree-sitter node.

### Language and Parser Setup

```
def instantiate_language(name, url):
    try:
        sh.git.clone(url, name)
    except sh.ErrorReturnCode as e:
        print(e.stderr.decode())
    Language.build_library(f"{name}.so", [name])
    return Language(f"{name}.so", name)
```
- Downloads and compiles Tree-sitter language definitions.
- Sets up the parser with the specified language.

### Parsing and Analyzing Source Code

```
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
```
- Defines sample Python code and parses it using Tree-sitter.
- Converts the parse tree to a graph and visualizes it.

### Queries and Information Extraction

- **Function Definitions**: Queries and prints function definitions and names.
- **Function Matching Regex**: Extracts functions with names matching specific patterns.
- **Function Calls**: Extracts function calls with specified argument types.

### Call Graph

```
def call_graph(root):
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
```

- Builds a call graph from the parsed source code.

### Repository Analysis

- Optionally clones a GitHub repository and analyzes Python files within it.
- Builds and displays a call graph for the repository's code.

## Conclusion

This program provides a comprehensive example of using Tree-sitter for source code parsing and analysis. You can visualize syntax trees, extract function information, and analyze code repositories.

## References

- [Tree-sitter Documentation](https://tree-sitter.github.io/tree-sitter/)
- [Tree-sitter Python Bindings](https://github.com/tree-sitter/py-tree-sitter)
