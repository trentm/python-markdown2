"""
Compare our heuristic detect_language() against Pygments guess_lexer()
on short code snippets — the typical case for markdown fenced code blocks.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))

from markdown2 import detect_language

# Try importing Pygments guess_lexer (may not be available)
try:
    from pygments.lexers import guess_lexer as pygments_detect
    HAS_PYGMENTS = True
except ImportError:
    HAS_PYGMENTS = False
    def pygments_detect(code):
        return None

# ----- test cases: (language, code_snippet) -----
# These are short (< 10 lines), simulating real-world markdown code blocks.
TEST_CASES = [
    ("python", '''def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)'''),

    ("python", '''import os
import sys

print(os.path.join("a", "b"))'''),

    ("python", '''class Dog:
    def __init__(self, name):
        self.name = name

    def bark(self):
        print(f"{self.name} says woof!")'''),

    ("javascript", '''function add(a, b) {
    return a + b;
}
console.log(add(1, 2));'''),

    ("javascript", '''const items = [1, 2, 3];
const doubled = items.map(x => x * 2);
console.log(doubled);'''),

    ("javascript", '''export default function App() {
    return <div>Hello</div>;
}'''),

    ("html", '''<div class="container">
    <h1>Hello World</h1>
    <p>This is a paragraph.</p>
</div>'''),

    ("html", '''<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body><p>content</p></body>
</html>'''),

    ("css", '''.button {
    color: white;
    background-color: blue;
    padding: 10px 20px;
    border-radius: 4px;
}'''),

    ("css", '''@media (max-width: 768px) {
    .container {
        width: 100%;
        margin: 0;
    }
}'''),

    ("sql", '''SELECT u.name, o.total
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE o.created_at > '2024-01-01'
ORDER BY o.total DESC
LIMIT 10;'''),

    ("sql", '''CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2)
);'''),

    ("bash", '''#!/bin/bash
echo "Starting backup..."
tar -czf backup.tar.gz /data
echo "Done!"'''),

    ("bash", '''for file in *.txt; do
    if [ -f "$file" ]; then
        echo "Processing $file"
    fi
done'''),

    ("java", '''public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}'''),

    ("java", '''private String formatName(String first, String last) {
    return last + ", " + first;
}'''),

    ("go", '''package main

import "fmt"

func main() {
    name := "world"
    fmt.Printf("Hello, %s!\\n", name)
}'''),

    ("go", '''type Server struct {
    host string
    port int
}

func (s *Server) Start() error {
    return nil
}'''),

    ("rust", '''fn factorial(n: u64) -> u64 {
    match n {
        0 | 1 => 1,
        _ => n * factorial(n - 1),
    }
}

fn main() {
    println!("{}", factorial(5));
}'''),

    ("ruby", '''def greet(name)
    puts "Hello, #{name}!"
end

class Person
    attr_accessor :name
end'''),

    ("json", '''{
    "name": "John",
    "age": 30,
    "city": "New York",
    "skills": ["Python", "JavaScript"]
}'''),

    ("yaml", '''---
name: MyApp
version: "1.0"
dependencies:
  - python>=3.8
  - requests
config:
  debug: true
  port: 8080'''),

    ("cpp", '''#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[]) {
    printf("Hello, World!\\n");
    return 0;
}'''),

    ("php", '''<?php
$name = "World";
echo "Hello, $name!";
function add($a, $b) {
    return $a + $b;
}'''),
]


def normalize_lang(name):
    """Normalize language names for comparison."""
    if name is None:
        return None
    name = name.lower()
    # Map Pygments names to our canonical names
    mapping = {
        'js': 'javascript',
        'ts': 'javascript',
        'typescript': 'javascript',
        'c': 'cpp',
        'c++': 'cpp',
        'sh': 'bash',
        'shell': 'bash',
        'xml': 'html',
        'xml+jango': 'html',
        'teraterm': None,  # Pygments common mis-classification
        'scdoc': None,
        'smali': None,
        'gdscript': None,
        'text': None,
        'text only': None,
        'css+lasso': 'css',
    }
    if name in mapping:
        return mapping[name]
    return name


def pygments_name(lexer):
    """Get a string name from a Pygments lexer, if available."""
    try:
        return lexer.aliases[0] if lexer and lexer.aliases else str(lexer)
    except Exception:
        return None


def run_tests():
    our_correct = 0
    pyg_correct = 0
    total = len(TEST_CASES)

    col_w = 14
    header = f"{'Snippet':<{col_w}} {'Expected':<12} {'Ours':<14} {'Pygments':<14}"
    print(header)
    print("-" * len(header))

    for i, (expected, code) in enumerate(TEST_CASES):
        # Our detection
        our_result = detect_language(code)
        our_norm = normalize_lang(our_result)
        our_ok = (our_norm == expected)

        # Pygments detection
        pyg_result = None
        pyg_norm = None
        pyg_ok = False
        if HAS_PYGMENTS:
            try:
                lexer = pygments_detect(code)
                pyg_result = pygments_name(lexer)
                pyg_norm = normalize_lang(pyg_result)
                pyg_ok = (pyg_norm == expected)
            except Exception:
                pyg_result = "error"

        if our_ok:
            our_correct += 1
        if pyg_ok:
            pyg_correct += 1

        snippet_label = f"case {i+1}"
        our_disp = f"{our_result} {'[OK]' if our_ok else '[!!]'}"
        pyg_disp = f"{pyg_result} {'[OK]' if pyg_ok else '[!!]'}" if pyg_result else "N/A"

        print(f"{snippet_label:<{col_w}} {expected:<12} {our_disp:<14} {pyg_disp:<14}")

    print()
    print("=" * 60)
    print(f"  Our heuristic accuracy:     {our_correct}/{total} = {our_correct/total*100:.1f}%")
    if HAS_PYGMENTS:
        print(f"  Pygments guess_lexer accuracy: {pyg_correct}/{total} = {pyg_correct/total*100:.1f}%")
    else:
        print("  Pygments not available for comparison")
    print("=" * 60)

    if our_correct == total:
        print("\n  All test cases passed!")
    else:
        print(f"\n  {total - our_correct} case(s) misclassified.")


if __name__ == '__main__':
    run_tests()
