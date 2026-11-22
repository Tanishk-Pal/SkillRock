"""
SkillRock — Bhavishya 1.0 Python Live Batch Default Curriculum
Seeds and maintains the Physics Wallah-style Python Live Lectures Batch.
Includes:
- Batch Configuration (Teacher name, default Google Meet link, announcements)
- 8 Progressive Modules
- 16 Comprehensive Live Lectures with:
    - Google Meet live teaching links
    - Recorded YouTube replays
    - Structured Class Notes & Handouts
    - Daily Practice Problems (DPP) with solutions
    - In-browser interactive Python starter code
"""

import logging
from datetime import datetime, timezone
from models.mongo import get_db

logger = logging.getLogger(__name__)

DEFAULT_LIVE_LECTURES = [
    # --------------------------------------------------------------------------
    # MODULE 1: Python Fundamentals & Environment Setup
    # --------------------------------------------------------------------------
    {
        "lecture_id": "py-live-01",
        "batch_id": "bhavishya-1-0",
        "module_number": 1,
        "module_name": "Module 1: Python Fundamentals & Environment Setup",
        "lecture_number": 1,
        "order": 1,
        "title": "Live Lecture 01: Python Architecture, VS Code Setup & First Code",
        "description": "Understand how Python works under the hood (Bytecode & PVM), set up your VS Code IDE, run your first Python program, and master standard I/O (print & input).",
        "teacher_name": "Tanishk Pal (Lead Educator)",
        "scheduled_at": "2026-11-20T19:00:00Z",
        "scheduled_display": "Completed • Replay & Notes Available",
        "duration_minutes": 90,
        "status": "completed",
        "google_meet_url": "https://meet.google.com/new",
        "recording_url": "UrsmFxEIp5k",
        "notes_url": "https://docs.python.org/3/tutorial/",
        "notes_content": """### Lecture 01 Key Takeaways
1. **Python Interpretation Flow**: Source Code (.py) ➔ Bytecode Compiler (.pyc) ➔ Python Virtual Machine (PVM) ➔ Machine Code.
2. **VS Code Setup**: Install Python extension by Microsoft, select Python 3.x interpreter, and configure Code Runner.
3. **print() Function**: Accepts `sep` (separator, default space) and `end` (ending character, default newline `\\n`).
4. **input() Function**: Always returns user input as a string (`str`). Explicit casting is required for numbers: `int(input())` or `float(input())`.""",
        "starter_code": """# Lecture 01 — Python Basics & I/O
name = input("Enter your name: ")
age = int(input("Enter your age: "))
print(f"Welcome to Bhavishya 1.0, {name}! In 5 years you will be {age + 5} years old.")
""",
        "dpp_list": [
            {
                "id": "dpp-1-1",
                "question": "What is the return type of the built-in input() function in Python 3?",
                "options": ["int", "str", "object", "dynamic depending on input"],
                "answer_index": 1,
                "explanation": "In Python 3, input() always captures user input as a string ('str')."
            },
            {
                "id": "dpp-1-2",
                "question": "Which parameter of print() changes the string printed at the very end of the line?",
                "options": ["sep", "end", "flush", "last"],
                "answer_index": 1,
                "explanation": "The 'end' parameter defines what is appended at the end of print(). By default, end='\\n'."
            },
            {
                "id": "dpp-1-3",
                "question": "What happens during Python bytecode compilation?",
                "options": [
                    "Directly creates a .exe binary file",
                    "Translates source code into platform-independent bytecode (.pyc)",
                    "Executes code line-by-line without compilation",
                    "Links C libraries dynamically"
                ],
                "answer_index": 1,
                "explanation": "Python first compiles .py code into bytecode (.pyc files), which is then executed by the PVM."
            }
        ]
    },
    {
        "lecture_id": "py-live-02",
        "batch_id": "bhavishya-1-0",
        "module_number": 1,
        "module_name": "Module 1: Python Fundamentals & Environment Setup",
        "lecture_number": 2,
        "order": 2,
        "title": "Live Lecture 02: Dynamic Typing, Variables & Memory Management",
        "description": "Deep dive into Python's memory model: everything is an object! Learn id(), type(), mutability, references, and formatted string literals (f-strings).",
        "teacher_name": "Tanishk Pal (Lead Educator)",
        "scheduled_at": "2026-11-22T19:00:00Z",
        "scheduled_display": "Completed • Replay & Notes Available",
        "duration_minutes": 90,
        "status": "completed",
        "google_meet_url": "https://meet.google.com/new",
        "recording_url": "_uQrJ0TkZlc",
        "notes_url": "https://docs.python.org/3/library/stdtypes.html",
        "notes_content": """### Lecture 02 Key Takeaways
1. **Dynamic Typing**: Variables in Python are tags/references to objects in heap memory, not fixed memory slots.
2. **id() and is vs ==**: `==` checks value equality; `is` checks reference identity (memory address via `id()`).
3. **Small Integer Caching**: Python pre-allocates integers from -5 to 256 for rapid reuse.
4. **f-strings**: Modern formatting syntax `f"Hello {name}, score: {score:.2f}"` introduced in Python 3.6.""",
        "starter_code": """# Lecture 02 — Memory & Mutability
a = [1, 2, 3]
b = a
b.append(4)
print("a:", a, "id(a):", id(a))
print("b:", b, "id(b):", id(b))
print("Are a and b the same object?", a is b)
""",
        "dpp_list": [
            {
                "id": "dpp-2-1",
                "question": "What is the difference between '==' and 'is' in Python?",
                "options": [
                    "'==' checks identity, 'is' checks value",
                    "'==' checks value equality, 'is' checks object identity in memory",
                    "There is no difference, both are synonyms",
                    "'is' only works with boolean values"
                ],
                "answer_index": 1,
                "explanation": "'==' evaluates whether the values of two operands are equal, while 'is' checks whether both point to the exact same object in memory."
            },
            {
                "id": "dpp-2-2",
                "question": "Which of the following data types in Python is IMMUTABLE?",
                "options": ["list", "dict", "tuple", "set"],
                "answer_index": 2,
                "explanation": "Tuples, integers, floats, strings, and frozensets are immutable in Python."
            }
        ]
    },

    # --------------------------------------------------------------------------
    # MODULE 2: Operators & Decision Making
    # --------------------------------------------------------------------------
    {
        "lecture_id": "py-live-03",
        "batch_id": "bhavishya-1-0",
        "module_number": 2,
        "module_name": "Module 2: Operators & Decision Making",
        "lecture_number": 3,
        "order": 3,
        "title": "Live Lecture 03: Operators, Precedence & Short-Circuit Evaluation",
        "description": "Master arithmetic, bitwise, membership (in/not in), identity (is/is not), and logical operators. Understand short-circuit evaluation in and/or expressions.",
        "teacher_name": "Tanishk Pal (Lead Educator)",
        "scheduled_at": "2026-11-23T19:00:00Z",
        "scheduled_display": "🔴 LIVE CLASS TODAY • 07:00 PM IST",
        "duration_minutes": 90,
        "status": "live",
        "google_meet_url": "https://meet.google.com/new",
        "recording_url": "vLqTf2b6GZw",
        "notes_url": "https://docs.python.org/3/reference/expressions.html",
        "notes_content": """### Lecture 03 Key Takeaways
1. **Integer vs Float Division**: `/` always returns a float (`7 / 2 = 3.5`); `//` performs floor division (`7 // 2 = 3`).
2. **Short-Circuit Evaluation**: 
   - `A and B`: If A is falsy, returns A immediately without evaluating B.
   - `A or B`: If A is truthy, returns A immediately without evaluating B.
3. **Membership Operators**: `in` and `not in` test membership in sequences in O(1) for sets/dicts and O(n) for lists.""",
        "starter_code": """# Lecture 03 — Short-Circuit & Operators
user_input = None
default_username = "Guest"
username = user_input or default_username
print(f"Logged in as: {username}")

# Chained comparisons
x = 15
print("Is 10 < x < 20?", 10 < x < 20)
""",
        "dpp_list": [
            {
                "id": "dpp-3-1",
                "question": "What is the output of: print(10 // 3, 10 % 3)?",
                "options": ["3.33 1", "3 1", "3.0 1.0", "3 0"],
                "answer_index": 1,
                "explanation": "10 // 3 evaluates to integer quotient 3, and 10 % 3 evaluates to remainder 1."
            },
            {
                "id": "dpp-3-2",
                "question": "What will 'False or 0 or 'SkillRock' or 42' evaluate to?",
                "options": ["False", "0", "'SkillRock'", "True"],
                "answer_index": 2,
                "explanation": "The 'or' operator returns the first truthy value encountered, which is the non-empty string 'SkillRock'."
            }
        ]
    },
    {
        "lecture_id": "py-live-04",
        "batch_id": "bhavishya-1-0",
        "module_number": 2,
        "module_name": "Module 2: Operators & Decision Making",
        "lecture_number": 4,
        "order": 4,
        "title": "Live Lecture 04: Conditionals, Nested If-Else & Match-Case (Python 3.10+)",
        "description": "Build decision trees with if, elif, else, and the modern structural pattern matching (match-case). Solve real-world pricing and access control logic.",
        "teacher_name": "Tanishk Pal (Lead Educator)",
        "scheduled_at": "2026-11-25T19:00:00Z",
        "scheduled_display": "Upcoming • Wed, 25 Nov • 07:00 PM IST",
        "duration_minutes": 90,
        "status": "scheduled",
        "google_meet_url": "https://meet.google.com/new",
        "recording_url": "kqtD5dpn9C8",
        "notes_url": "https://docs.python.org/3/tutorial/controlflow.html",
        "notes_content": """### Lecture 04 Key Takeaways
1. **Truthy and Falsy**: 0, empty containers (`[]`, `{}`, `""`, `()`), `None`, and `False` evaluate to Falsy. Everything else is Truthy.
2. **Ternary Operator**: `result = value_if_true if condition else value_if_false`.
3. **Structural Pattern Matching (match-case)**: Provides clean, extensible branching without messy elif cascades.""",
        "starter_code": """# Lecture 04 — Structural Pattern Matching
status_code = 404

match status_code:
    case 200:
        print("Success! Resource loaded.")
    case 400:
        print("Bad Request.")
    case 404:
        print("Not Found: Page does not exist.")
    case 500:
        print("Internal Server Error.")
    case _:
        print("Unknown Status Code.")
""",
        "dpp_list": [
            {
                "id": "dpp-4-1",
                "question": "Which Python version introduced the structural pattern matching (match-case) syntax?",
                "options": ["Python 3.6", "Python 3.8", "Python 3.10", "Python 3.12"],
                "answer_index": 2,
                "explanation": "Structural pattern matching via 'match' and 'case' was officially added in Python 3.10 (PEP 634)."
            }
        ]
    },

    # --------------------------------------------------------------------------
    # MODULE 3: Loops & Pattern Logic
    # --------------------------------------------------------------------------
    {
        "lecture_id": "py-live-05",
        "batch_id": "bhavishya-1-0",
        "module_number": 3,
        "module_name": "Module 3: Loops & Pattern Logic",
        "lecture_number": 5,
        "order": 5,
        "title": "Live Lecture 05: While Loops, For Loops & The Range Function",
        "description": "Understand definite iteration with for-in and indefinite iteration with while. Master range(start, stop, step) and loop indexing with enumerate().",
        "teacher_name": "Tanishk Pal (Lead Educator)",
        "scheduled_at": "2026-11-27T19:00:00Z",
        "scheduled_display": "Upcoming • Fri, 27 Nov • 07:00 PM IST",
        "duration_minutes": 90,
        "status": "scheduled",
        "google_meet_url": "https://meet.google.com/new",
        "recording_url": "6iF8Xb7Z3wQ",
        "notes_url": "https://docs.python.org/3/tutorial/controlflow.html#for-statements",
        "notes_content": """### Lecture 05 Key Takeaways
1. **range() Function**: `range(1, 10, 2)` generates values 1, 3, 5, 7, 9. Memory-efficient generator (does not store list).
2. **enumerate()**: Generates tuples of `(index, item)` to avoid manual counter variables.
3. **zip()**: Pairs elements from multiple iterables in parallel.""",
        "starter_code": """# Lecture 05 — Iteration with enumerate and zip
skills = ["Python", "DSA", "Web Dev", "AI"]
levels = ["Master", "Advanced", "Intermediate", "Explorer"]

for idx, (skill, level) in enumerate(zip(skills, levels), start=1):
    print(f"Goal {idx}: Learn {skill} at {level} level")
""",
        "dpp_list": [
            {
                "id": "dpp-5-1",
                "question": "What is the output of list(range(5, 0, -2))?",
                "options": ["[5, 3, 1]", "[5, 4, 3, 2, 1]", "[5, 3]", "[0, 2, 4]"],
                "answer_index": 0,
                "explanation": "Starting at 5, stepping by -2 up to but excluding 0 yields [5, 3, 1]."
            }
        ]
    },
    {
        "lecture_id": "py-live-06",
        "batch_id": "bhavishya-1-0",
        "module_number": 3,
        "module_name": "Module 3: Loops & Pattern Logic",
        "lecture_number": 6,
        "order": 6,
        "title": "Live Lecture 06: Loop Control (Break, Continue, Else) & Pattern Printing",
        "description": "Master loop jump statements (break, continue, pass) and the unique for-else clause. Solve classic coding interview pattern printing problems.",
        "teacher_name": "Tanishk Pal (Lead Educator)",
        "scheduled_at": "2026-11-30T19:00:00Z",
        "scheduled_display": "Upcoming • Mon, 30 Nov • 07:00 PM IST",
        "duration_minutes": 90,
        "status": "scheduled",
        "google_meet_url": "https://meet.google.com/new",
        "recording_url": "4oxCAm4UfCc",
        "notes_url": "https://docs.python.org/3/tutorial/controlflow.html#break-and-continue-statements-and-else-clauses-on-loops",
        "notes_content": """### Lecture 06 Key Takeaways
1. **for-else Clause**: The `else` block executes ONLY if the loop completes without hitting a `break` statement.
2. **break**: Immediately exits the innermost loop.
3. **continue**: Skips the rest of the current iteration and jumps to the next cycle.""",
        "starter_code": """# Lecture 06 — Pyramid Pattern Printing
n = 5
for i in range(1, n + 1):
    spaces = " " * (n - i)
    stars = "*" * (2 * i - 1)
    print(spaces + stars)
""",
        "dpp_list": [
            {
                "id": "dpp-6-1",
                "question": "When does the 'else' block of a for-loop execute in Python?",
                "options": [
                    "Only when an exception occurs inside the loop",
                    "Only when the loop is terminated by a 'break' statement",
                    "Only when the loop finishes iterating all items without encountering a 'break'",
                    "Always before the loop starts"
                ],
                "answer_index": 2,
                "explanation": "The else block of a loop executes when the sequence becomes exhausted, provided no 'break' occurred."
            }
        ]
    },

    # --------------------------------------------------------------------------
    # MODULE 4: Functions & Modularity
    # --------------------------------------------------------------------------
    {
        "lecture_id": "py-live-07",
        "batch_id": "bhavishya-1-0",
        "module_number": 4,
        "module_name": "Module 4: Functions & Modularity",
        "lecture_number": 7,
        "order": 7,
        "title": "Live Lecture 07: Functions, Positional & Keyword Args, *args and **kwargs",
        "description": "Write clean, reusable functions. Master default argument pitfalls, variable-length arguments (*args, **kwargs), and keyword-only parameters.",
        "teacher_name": "Tanishk Pal (Lead Educator)",
        "scheduled_at": "2026-12-02T19:00:00Z",
        "scheduled_display": "Upcoming • Wed, 02 Dec • 07:00 PM IST",
        "duration_minutes": 90,
        "status": "scheduled",
        "google_meet_url": "https://meet.google.com/new",
        "recording_url": "9Os0o3wzS_I",
        "notes_url": "https://docs.python.org/3/tutorial/controlflow.html#defining-functions",
        "notes_content": """### Lecture 07 Key Takeaways
1. **Mutable Default Argument Trap**: Never use mutable objects like `def f(x=[])`. Use `def f(x=None)` and initialize inside.
2. `*args`: Captures arbitrary extra positional arguments into a `tuple`.
3. `**kwargs`: Captures arbitrary extra keyword arguments into a `dict`.""",
        "starter_code": """# Lecture 07 — Clean Functions with *args and **kwargs
def build_profile(name, college, *skills, **extras):
    print(f"Student: {name} ({college})")
    print("Skills:", ", ".join(skills))
    for k, v in extras.items():
        print(f" - {k.capitalize()}: {v}")

build_profile("Tanishk", "SkillRock Campus", "Python", "Flask", "MongoDB", gpa="9.4", year="Final")
""",
        "dpp_list": [
            {
                "id": "dpp-7-1",
                "question": "Why is 'def append_to(element, target=[])' dangerous in Python?",
                "options": [
                    "It causes a SyntaxError",
                    "The default list is created only once when the function is defined, causing state to persist across calls",
                    "It makes the function run in O(n^2)",
                    "Python disallows lists as arguments"
                ],
                "answer_index": 1,
                "explanation": "Default parameter values are evaluated once at function definition time. A mutable default like [] persists state across invocations."
            }
        ]
    },
    {
        "lecture_id": "py-live-08",
        "batch_id": "bhavishya-1-0",
        "module_number": 4,
        "module_name": "Module 4: Functions & Modularity",
        "lecture_number": 8,
        "order": 8,
        "title": "Live Lecture 08: Scope (LEGB Rule), Lambda Functions & Closures",
        "description": "Understand variable scope resolution with the LEGB rule (Local, Enclosing, Global, Built-in), lambda one-liners, map, filter, and functional paradigms.",
        "teacher_name": "Tanishk Pal (Lead Educator)",
        "scheduled_at": "2026-12-04T19:00:00Z",
        "scheduled_display": "Upcoming • Fri, 04 Dec • 07:00 PM IST",
        "duration_minutes": 90,
        "status": "scheduled",
        "google_meet_url": "https://meet.google.com/new",
        "recording_url": "25ovCm9jKfA",
        "notes_url": "https://docs.python.org/3/tutorial/controlflow.html#lambda-expressions",
        "notes_content": """### Lecture 08 Key Takeaways
1. **LEGB Rule**: Scope search order: Local ➔ Enclosing (closures) ➔ Global (module level) ➔ Built-in.
2. `global` and `nonlocal`: Explicitly declare intent to modify outside variables.
3. **Lambdas**: Anonymous functions limited to a single expression: `square = lambda x: x * x`.""",
        "starter_code": """# Lecture 08 — High Order Functions & Lambdas
students = [
    {"name": "Aman", "score": 88},
    {"name": "Pooja", "score": 95},
    {"name": "Rohit", "score": 72}
]

# Sort students by score descending using lambda
sorted_students = sorted(students, key=lambda s: s["score"], reverse=True)
for s in sorted_students:
    print(f"{s['name']}: {s['score']} points")
""",
        "dpp_list": [
            {
                "id": "dpp-8-1",
                "question": "What does LEGB stand for in Python variable scope resolution?",
                "options": [
                    "Local, Extended, Global, Base",
                    "Local, Enclosing, Global, Built-in",
                    "Lexical, Environment, Global, Bytecode",
                    "Linear, Enclosed, General, Built-in"
                ],
                "answer_index": 1,
                "explanation": "LEGB stands for Local, Enclosing (nested functions), Global (module namespace), and Built-in."
            }
        ]
    },

    # --------------------------------------------------------------------------
    # MODULE 5: Core Data Structures
    # --------------------------------------------------------------------------
    {
        "lecture_id": "py-live-09",
        "batch_id": "bhavishya-1-0",
        "module_number": 5,
        "module_name": "Module 5: Core Data Structures for Problem Solving",
        "lecture_number": 9,
        "order": 9,
        "title": "Live Lecture 09: Lists & Tuples — Slicing, Methods & Comprehensions",
        "description": "Master list indexing, slicing [start:stop:step], built-in algorithms (sort, reverse), list comprehensions, and tuple unpacking.",
        "teacher_name": "Tanishk Pal (Lead Educator)",
        "scheduled_at": "2026-12-07T19:00:00Z",
        "scheduled_display": "Upcoming • Mon, 07 Dec • 07:00 PM IST",
        "duration_minutes": 90,
        "status": "scheduled",
        "google_meet_url": "https://meet.google.com/new",
        "recording_url": "W8KRzm-HUcc",
        "notes_url": "https://docs.python.org/3/tutorial/datastructures.html",
        "notes_content": """### Lecture 09 Key Takeaways
1. **List Comprehensions**: `[expr for item in iterable if condition]` is faster than manual for-loop appends.
2. **Slicing Tricks**: `lst[::-1]` reverses a list; `lst[:]` creates a shallow copy.
3. **Tuple Unpacking**: `a, b, *rest = (1, 2, 3, 4, 5)` assigns `a=1`, `b=2`, `rest=[3, 4, 5]`.""",
        "starter_code": """# Lecture 09 — List Comprehensions & Slicing
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flattened = [val for row in matrix for val in row if val % 2 != 0]
print("Odd numbers from matrix:", flattened)
""",
        "dpp_list": [
            {
                "id": "dpp-9-1",
                "question": "What is the time complexity of looking up an item by index in a Python list (e.g., lst[500])?",
                "options": ["O(n)", "O(1)", "O(log n)", "O(n log n)"],
                "answer_index": 1,
                "explanation": "Python lists are implemented as dynamic arrays of pointers in contiguous memory, allowing O(1) random access by index."
            }
        ]
    },
    {
        "lecture_id": "py-live-10",
        "batch_id": "bhavishya-1-0",
        "module_number": 5,
        "module_name": "Module 5: Core Data Structures for Problem Solving",
        "lecture_number": 10,
        "order": 10,
        "title": "Live Lecture 10: Dictionaries & Sets — Hash Maps & O(1) Lookups",
        "description": "Understand hash tables, key immutability, dict comprehensions, collections.defaultdict, Counter, and set mathematical operations (union, intersection).",
        "teacher_name": "Tanishk Pal (Lead Educator)",
        "scheduled_at": "2026-12-09T19:00:00Z",
        "scheduled_display": "Upcoming • Wed, 09 Dec • 07:00 PM IST",
        "duration_minutes": 90,
        "status": "scheduled",
        "google_meet_url": "https://meet.google.com/new",
        "recording_url": "daefaLgNkw0",
        "notes_url": "https://docs.python.org/3/tutorial/datastructures.html#dictionaries",
        "notes_content": """### Lecture 10 Key Takeaways
1. **Hash Maps**: Dictionaries and sets rely on `hash(key)`. Keys MUST be hashable (immutable objects like int, str, tuple).
2. **get() with Fallback**: Avoid `KeyError` using `d.get(key, default_value)`.
3. **collections.Counter**: Computes element frequency in O(n) time.""",
        "starter_code": """# Lecture 10 — Word Frequency Counter
sentence = "python live batch in skillrock python with teacher on google meet live"
words = sentence.split()
freq = {}
for w in words:
    freq[w] = freq.get(w, 0) + 1

for word, count in sorted(freq.items(), key=lambda x: x[1], reverse=True):
    print(f"'{word}': {count} times")
""",
        "dpp_list": [
            {
                "id": "dpp-10-1",
                "question": "Can a list be used as a key in a Python dictionary?",
                "options": [
                    "Yes, any Python object can be a key",
                    "No, because lists are mutable and unhashable",
                    "Yes, but only if the list contains unique numbers",
                    "Only in Python 3.12+"
                ],
                "answer_index": 1,
                "explanation": "Dictionary keys must be hashable. Because lists can change their contents (mutable), they do not implement __hash__ and will raise TypeError: unhashable type: 'list'."
            }
        ]
    },

    # --------------------------------------------------------------------------
    # MODULE 6: Object-Oriented Programming (OOP)
    # --------------------------------------------------------------------------
    {
        "lecture_id": "py-live-11",
        "batch_id": "bhavishya-1-0",
        "module_number": 6,
        "module_name": "Module 6: Object-Oriented Programming (OOP)",
        "lecture_number": 11,
        "order": 11,
        "title": "Live Lecture 11: Classes, Objects, __init__ & Dunder Methods",
        "description": "Transition from procedural to object-oriented programming. Create custom classes, understand self, instance vs class variables, and magic methods (__str__, __repr__, __len__).",
        "teacher_name": "Tanishk Pal (Lead Educator)",
        "scheduled_at": "2026-12-11T19:00:00Z",
        "scheduled_display": "Upcoming • Fri, 11 Dec • 07:00 PM IST",
        "duration_minutes": 90,
        "status": "scheduled",
        "google_meet_url": "https://meet.google.com/new",
        "recording_url": "JeznW_74eSL",
        "notes_url": "https://docs.python.org/3/tutorial/classes.html",
        "notes_content": """### Lecture 11 Key Takeaways
1. **self**: Explicit reference to the current instance of the class.
2. `__init__`: Constructor method called when a new instance is created.
3. `__str__` vs `__repr__`: `__str__` is for human-readable output (print); `__repr__` is for unambiguous debugging output.""",
        "starter_code": """# Lecture 11 — Student Class with Dunder Methods
class Student:
    def __init__(self, name, roll_no, gpa):
        self.name = name
        self.roll_no = roll_no
        self.gpa = gpa

    def __str__(self):
        return f"Student({self.name}, Roll: {self.roll_no}, GPA: {self.gpa})"

s1 = Student("Bhumika Verma", "SR-101", 9.2)
print(s1)
""",
        "dpp_list": [
            {
                "id": "dpp-11-1",
                "question": "What is the purpose of the 'self' parameter in Python class instance methods?",
                "options": [
                    "It points to the class definition",
                    "It refers to the instance of the object calling the method",
                    "It is a mandatory keyword enforced by the compiler",
                    "It allocates heap memory for the object"
                ],
                "answer_index": 1,
                "explanation": "'self' represents the instance of the class through which attributes and methods are bound to that specific object."
            }
        ]
    },
    {
        "lecture_id": "py-live-12",
        "batch_id": "bhavishya-1-0",
        "module_number": 6,
        "module_name": "Module 6: Object-Oriented Programming (OOP)",
        "lecture_number": 12,
        "order": 12,
        "title": "Live Lecture 12: The 4 Pillars of OOP — Inheritance, Polymorphism, Encapsulation, Abstraction",
        "description": "Master enterprise software architecture: single & multiple inheritance, method resolution order (MRO), super(), private attributes (_ & __), property decorators, and abstract classes.",
        "teacher_name": "Tanishk Pal (Lead Educator)",
        "scheduled_at": "2026-12-14T19:00:00Z",
        "scheduled_display": "Upcoming • Mon, 14 Dec • 07:00 PM IST",
        "duration_minutes": 90,
        "status": "scheduled",
        "google_meet_url": "https://meet.google.com/new",
        "recording_url": "RSl87lqOXDE",
        "notes_url": "https://docs.python.org/3/tutorial/classes.html#inheritance",
        "notes_content": """### Lecture 12 Key Takeaways
1. **Inheritance & super()**: Reuses logic across class hierarchies and enables clean initialization.
2. **Encapsulation**: Private attributes are indicated by prefix `__` (which triggers Python name mangling: `_ClassName__var`).
3. `@property` Decorator: Provides getters, setters, and validation without breaking caller syntax.""",
        "starter_code": """# Lecture 12 — Encapsulation with @property
class BankAccount:
    def __init__(self, owner, balance=0.0):
        self.owner = owner
        self._balance = max(0.0, balance)

    @property
    def balance(self):
        return self._balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self._balance += amount
        print(f"Deposited ₹{amount}. New Balance: ₹{self._balance}")

acc = BankAccount("Tanishk", 500)
acc.deposit(1500)
print("Current balance:", acc.balance)
""",
        "dpp_list": [
            {
                "id": "dpp-12-1",
                "question": "What algorithm does Python use to determine Method Resolution Order (MRO) in multiple inheritance?",
                "options": ["Depth-First Search (DFS)", "Breadth-First Search (BFS)", "C3 Linearization Algorithm", "Dijkstra's Algorithm"],
                "answer_index": 2,
                "explanation": "Python uses the C3 Linearization algorithm to compute the MRO for multiple inheritance hierarchies."
            }
        ]
    },

    # --------------------------------------------------------------------------
    # MODULE 7: File I/O, Error Handling & APIs
    # --------------------------------------------------------------------------
    {
        "lecture_id": "py-live-13",
        "batch_id": "bhavishya-1-0",
        "module_number": 7,
        "module_name": "Module 7: File I/O, Error Handling & APIs",
        "lecture_number": 13,
        "order": 13,
        "title": "Live Lecture 13: Exception Handling (try-except-finally) & Context Managers",
        "description": "Never let your software crash! Write resilient code using try, except, else, finally, custom exception classes, and the with statement context managers.",
        "teacher_name": "Tanishk Pal (Lead Educator)",
        "scheduled_at": "2026-12-16T19:00:00Z",
        "scheduled_display": "Upcoming • Wed, 16 Dec • 07:00 PM IST",
        "duration_minutes": 90,
        "status": "scheduled",
        "google_meet_url": "https://meet.google.com/new",
        "recording_url": "NIWwJbo-9_8",
        "notes_url": "https://docs.python.org/3/tutorial/errors.html",
        "notes_content": """### Lecture 13 Key Takeaways
1. **try-except-else-finally**:
   - `try`: Code that might raise an error.
   - `except`: Handles specific exceptions.
   - `else`: Runs ONLY if NO exception was raised.
   - `finally`: ALWAYS runs (cleanup, closing sockets/files).
2. **Context Managers (`with`)**: Enforces deterministic cleanup via `__enter__` and `__exit__` protocols.""",
        "starter_code": """# Lecture 13 — Robust Error Handling
def safe_divide(a, b):
    try:
        res = a / b
    except ZeroDivisionError:
        return "Error: Cannot divide by zero!"
    except TypeError:
        return "Error: Both arguments must be numeric."
    else:
        return f"Calculation success: {res}"
    finally:
        print("[Log] safe_divide operation completed.")

print(safe_divide(10, 2))
print(safe_divide(10, 0))
""",
        "dpp_list": [
            {
                "id": "dpp-13-1",
                "question": "Does the 'finally' block execute if a 'return' statement is executed inside the 'try' block?",
                "options": [
                    "No, return terminates function immediately",
                    "Yes, finally always executes before the function actually returns",
                    "Only if an exception occurred",
                    "Only in Python debug mode"
                ],
                "answer_index": 1,
                "explanation": "The 'finally' clause is guaranteed to execute before the function exits, even if a return, break, or continue is executed inside try."
            }
        ]
    },
    {
        "lecture_id": "py-live-14",
        "batch_id": "bhavishya-1-0",
        "module_number": 7,
        "module_name": "Module 7: File I/O, Error Handling & APIs",
        "lecture_number": 14,
        "order": 14,
        "title": "Live Lecture 14: File I/O (CSV & JSON) and HTTP Requests / REST APIs",
        "description": "Read and write real-world datasets in JSON and CSV format. Connect your Python code to external REST APIs using the requests library and parse JSON responses.",
        "teacher_name": "Tanishk Pal (Lead Educator)",
        "scheduled_at": "2026-12-18T19:00:00Z",
        "scheduled_display": "Upcoming • Fri, 18 Dec • 07:00 PM IST",
        "duration_minutes": 90,
        "status": "scheduled",
        "google_meet_url": "https://meet.google.com/new",
        "recording_url": "tb8gHvYlCFs",
        "notes_url": "https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files",
        "notes_content": """### Lecture 14 Key Takeaways
1. **JSON Serialization**: `json.dumps()` converts Python dict ➔ JSON string; `json.loads()` converts JSON string ➔ Python dict.
2. `requests.get(url)`: Fetches data over HTTP with status codes (200 OK, 404, 500).
3. Always use `with open(filepath, 'w', encoding='utf-8') as f:` to guarantee proper file handle closure.""",
        "starter_code": """# Lecture 14 — JSON Processing & Simulation
import json

data = {
    "course": "Bhavishya 1.0",
    "batch": "Python Live Batch",
    "mode": "Google Meet",
    "lectures_count": 16,
    "platform": "SkillRock"
}

json_str = json.dumps(data, indent=2)
print("Generated JSON Payload:")
print(json_str)

parsed = json.loads(json_str)
print("Parsed Course Name:", parsed["course"])
""",
        "dpp_list": [
            {
                "id": "dpp-14-1",
                "question": "Which method is used to parse a JSON-formatted string into a Python dictionary?",
                "options": ["json.dump()", "json.dumps()", "json.load()", "json.loads()"],
                "answer_index": 3,
                "explanation": "'json.loads()' (load string) deserializes a JSON string into a Python object. 'json.load()' reads from a file object."
            }
        ]
    },

    # --------------------------------------------------------------------------
    # MODULE 8: Capstone Project & Placement Interview Prep
    # --------------------------------------------------------------------------
    {
        "lecture_id": "py-live-15",
        "batch_id": "bhavishya-1-0",
        "module_number": 8,
        "module_name": "Module 8: Capstone Real-World Project & Placement Prep",
        "lecture_number": 15,
        "order": 15,
        "title": "Live Lecture 15: End-to-End Capstone Project — Automated Data Pipeline & CLI Tool",
        "description": "Build an industry-grade Python project live with the teacher from scratch: modular structure, CLI argument parsing, API integration, CSV export, and clean Git commits.",
        "teacher_name": "Tanishk Pal (Lead Educator)",
        "scheduled_at": "2026-12-21T19:00:00Z",
        "scheduled_display": "Upcoming • Mon, 21 Dec • 07:00 PM IST",
        "duration_minutes": 90,
        "status": "scheduled",
        "google_meet_url": "https://meet.google.com/new",
        "recording_url": "X1b3C54XflU",
        "notes_url": "https://docs.python.org/3/tutorial/modules.html",
        "notes_content": """### Lecture 15 Key Takeaways
1. **Industry Project Architecture**: Separation of concerns (`main.py`, `services/`, `models/`, `utils/`).
2. **Virtual Environments**: Always isolate third-party packages using `python -m venv venv`.
3. **requirements.txt**: Freeze pinned versions using `pip freeze > requirements.txt`.""",
        "starter_code": """# Lecture 15 — Capstone Project Snippet: Student Analytics
class BatchAnalytics:
    def __init__(self, batch_name):
        self.batch_name = batch_name
        self.records = []

    def add_score(self, student_name, score):
        self.records.append({"student": student_name, "score": score})

    def summary(self):
        if not self.records:
            return "No data recorded."
        scores = [r["score"] for r in self.records]
        return {
            "batch": self.batch_name,
            "total_students": len(scores),
            "highest": max(scores),
            "average": round(sum(scores) / len(scores), 1)
        }

analytics = BatchAnalytics("Bhavishya 1.0 Python")
analytics.add_score("Aman", 94)
analytics.add_score("Bhumika", 98)
analytics.add_score("Rohit", 86)
print(analytics.summary())
""",
        "dpp_list": [
            {
                "id": "dpp-15-1",
                "question": "What is the primary purpose of 'if __name__ == \"__main__\":' in a Python module?",
                "options": [
                    "To declare a private class",
                    "To ensure code inside only executes when the file is run directly, not when imported as a module",
                    "To speed up code execution in Python",
                    "It is mandatory for all Python scripts"
                ],
                "answer_index": 1,
                "explanation": "'__name__' evaluates to '__main__' only when the script is run directly from the command line, preventing execution during module imports."
            }
        ]
    },
    {
        "lecture_id": "py-live-16",
        "batch_id": "bhavishya-1-0",
        "module_number": 8,
        "module_name": "Module 8: Capstone Real-World Project & Placement Prep",
        "lecture_number": 16,
        "order": 16,
        "title": "Live Lecture 16: Top 50 Python Campus Placement Questions & Live Mock Interview",
        "description": "Live mock interview workshop! Review the top 50 technical interview questions asked in TCS, Infosys, Wipro, Cognizant, and top tech product startups.",
        "teacher_name": "Tanishk Pal (Lead Educator)",
        "scheduled_at": "2026-12-23T19:00:00Z",
        "scheduled_display": "Upcoming • Wed, 23 Dec • 07:00 PM IST",
        "duration_minutes": 90,
        "status": "scheduled",
        "google_meet_url": "https://meet.google.com/new",
        "recording_url": "8DvywoWvM8I",
        "notes_url": "https://github.com/Tanishk-Pal/SkillRock",
        "notes_content": """### Lecture 16 Key Takeaways
1. **Top Interview Topics**: Mutability, Generators & Iterators, Decorators, GIL (Global Interpreter Lock), List vs Tuple internals.
2. **Star Interview Technique**: Structure problem answers: Situation ➔ Task ➔ Action ➔ Result.
3. **Complexity Analysis**: Always state Time & Space complexity before writing code.""",
        "starter_code": """# Lecture 16 — Classic Interview Question: Two Sum (O(n) Hash Map)
def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        diff = target - num
        if diff in seen:
            return (seen[diff], i)
        seen[num] = i
    return None

indices = two_sum([2, 7, 11, 15], 9)
print("Indices summing to 9:", indices)
""",
        "dpp_list": [
            {
                "id": "dpp-16-1",
                "question": "What is Python's Global Interpreter Lock (GIL)?",
                "options": [
                    "A security mechanism preventing unauthorized file access",
                    "A mutex that allows only one native thread to execute Python bytecodes at once in CPython",
                    "A tool for locking variable values to make them immutable",
                    "A garbage collection threshold"
                ],
                "answer_index": 1,
                "explanation": "In CPython, the GIL is a mutex that prevents multiple threads from executing Python bytecodes concurrently, ensuring thread-safe memory management."
            }
        ]
    }
]


def ensure_default_bhavishya_live_batch():
    """
    Seeds and ensures the Bhavishya 1.0 Physics Wallah-style Python Live Batch
    and all 16 live lectures exist in MongoDB.
    Safe and idempotent.
    """
    from models.bhavishya import BhavishyaBatchConfig, BhavishyaLiveLecture

    try:
        # 1. Seed or refresh Batch Config
        config = BhavishyaBatchConfig.get_config("bhavishya-1-0")
        config.title = "Bhavishya 1.0 — Python Master Live Batch"
        config.tagline = "Interactive Live Lectures on Google Meet with Teacher, Daily Practice Problems (DPP), Handwritten Notes, and 24/7 AI Doubt Solving"
        config.teacher_name = "Tanishk Pal"
        config.teacher_title = "Lead Python Educator & Software Architect"
        config.global_meet_url = config.global_meet_url or "https://meet.google.com/new"
        config.save()

        # 2. Seed or update each of the 16 live lectures
        db = get_db()
        seeded = 0
        updated = 0
        for data in DEFAULT_LIVE_LECTURES:
            lid = data["lecture_id"]
            existing = db.bhavishya_live_lectures.find_one({"lecture_id": lid})
            if not existing:
                lec = BhavishyaLiveLecture(data)
                lec.save()
                seeded += 1
            else:
                # Update content, notes, DPPs while preserving custom status/meet URL if set by admin
                update_fields = {
                    "module_number": data["module_number"],
                    "module_name": data["module_name"],
                    "lecture_number": data["lecture_number"],
                    "order": data["order"],
                    "title": data["title"],
                    "description": data["description"],
                    "teacher_name": data["teacher_name"],
                    "duration_minutes": data["duration_minutes"],
                    "recording_url": data["recording_url"],
                    "notes_url": data["notes_url"],
                    "notes_content": data["notes_content"],
                    "starter_code": data["starter_code"],
                    "dpp_list": data["dpp_list"],
                }
                # If existing has default placeholder meet url, update it
                if not existing.get("google_meet_url"):
                    update_fields["google_meet_url"] = data["google_meet_url"]
                if not existing.get("status"):
                    update_fields["status"] = data["status"]
                db.bhavishya_live_lectures.update_one({"lecture_id": lid}, {"$set": update_fields})
                updated += 1

        print(f"[BHAVISHYA LIVE] Seeded {seeded} new live lectures, refreshed {updated} existing lectures in MongoDB.")
        return True
    except Exception as e:
        logger.warning(f"[BHAVISHYA LIVE SEED NOTICE] {e}")
        return False
