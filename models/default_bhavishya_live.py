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
        "subject_slug": "python",
        "teacher_avatar": "/static/img/teacher_tanishk.svg",
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
        "subject_slug": "python",
        "teacher_avatar": "/static/img/teacher_tanishk.svg",
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
        "subject_slug": "python",
        "teacher_avatar": "/static/img/teacher_tanishk.svg",
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
        "subject_slug": "python",
        "teacher_avatar": "/static/img/teacher_tanishk.svg",
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
        "subject_slug": "python",
        "teacher_avatar": "/static/img/teacher_tanishk.svg",
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
        "subject_slug": "python",
        "teacher_avatar": "/static/img/teacher_tanishk.svg",
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
        "subject_slug": "python",
        "teacher_avatar": "/static/img/teacher_tanishk.svg",
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
        "subject_slug": "python",
        "teacher_avatar": "/static/img/teacher_tanishk.svg",
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
        "subject_slug": "python",
        "teacher_avatar": "/static/img/teacher_tanishk.svg",
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
        "subject_slug": "python",
        "teacher_avatar": "/static/img/teacher_tanishk.svg",
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
        "subject_slug": "python",
        "teacher_avatar": "/static/img/teacher_tanishk.svg",
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
        "subject_slug": "python",
        "teacher_avatar": "/static/img/teacher_tanishk.svg",
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
        "subject_slug": "python",
        "teacher_avatar": "/static/img/teacher_tanishk.svg",
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
        "subject_slug": "python",
        "teacher_avatar": "/static/img/teacher_tanishk.svg",
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
        "subject_slug": "python",
        "teacher_avatar": "/static/img/teacher_tanishk.svg",
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
        "subject_slug": "python",
        "teacher_avatar": "/static/img/teacher_tanishk.svg",
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



DEFAULT_ENGLISH_LIVE_LECTURES = [
    # --------------------------------------------------------------------------
    # MODULE 1: Spoken English & Accent Foundations
    # --------------------------------------------------------------------------
    {
        "lecture_id": "eng-live-01",
        "batch_id": "bhavishya-1-0",
        "subject_slug": "english",
        "module_number": 1,
        "module_name": "Module 1: Spoken English & Accent Foundations",
        "lecture_number": 1,
        "order": 1,
        "title": "Live Lecture 01: Breaking Fear & Building Natural Speaking Fluency",
        "description": "Overcome hesitations, build instant conversational confidence, learn the daily 15-minute speaking habit, and master clear articulation without fake accents.",
        "teacher_name": "Ananya Sharma (Senior English Faculty)",
        "teacher_title": "Communication & Soft Skills Coach",
        "teacher_avatar": "/static/img/teacher_ananya.svg",
        "scheduled_at": "2026-11-20T20:30:00Z",
        "scheduled_display": "Completed • Replay & Notes Available",
        "duration_minutes": 60,
        "status": "completed",
        "google_meet_url": "https://meet.google.com/new",
        "recording_url": "60ItHLz5WEA",
        "notes_url": "",
        "notes_content": """### Spoken English Masterclass 01 Notes
1. **The 3-Second Rule**: Avoid internal translation from regional language. Form simple, active English sentences directly.
2. **Clarity Over Accent**: Neutral Indian English with clear pronunciation of consonant endings (e.g. -ed, -s, -th) is the global gold standard in tech.
3. **Daily Habit**: Read aloud 1 technical or news article for 10 minutes every morning to calibrate mouth muscle memory.""",
        "starter_code": """# Interactive Speaking Exercise
name = input("Enter your full name: ")
city = input("Enter your college/city: ")
dream_role = input("What role are you targeting (e.g. Python Developer)? ")

print(f"Self-Intro Practice:\n'Hello everyone, my name is {name}. I am based in {city} and currently preparing to excel as a {dream_role}. Excited to connect!'")
""",
        "dpp_list": [
            {
                "id": "eng-dpp-1-1",
                "question": "Which of the following is grammatically correct and standard in professional English?",
                "options": ["Please revert back at the earliest.", "Please revert at your earliest convenience.", "Please revert back again.", "Revert back to me."],
                "answer_index": 1,
                "explanation": "'Revert' already means to return or reply; adding 'back' is redundant. The correct phrase is 'Please revert at your earliest convenience' or 'Please reply'."
            },
            {
                "id": "eng-dpp-1-2",
                "question": "Choose the most appropriate response when someone says: 'Thank you for your assistance today!'",
                "options": ["Mention not.", "You're most welcome! Glad I could help.", "No problem at all, leave it.", "Why thank you?"],
                "answer_index": 1,
                "explanation": "'You're most welcome! Glad I could help.' is professional and warm. 'Mention not' is an informal Indianism."
            },
            {
                "id": "eng-dpp-1-3",
                "question": "Identify the sentence free from grammatical errors:",
                "options": ["I am having two years of coding experience.", "I have two years of coding experience.", "I am possessing two years experience.", "I have been having two years experience."],
                "answer_index": 1,
                "explanation": "State of possession uses the simple present 'I have', not continuous 'I am having'."
            }
        ]
    },
    {
        "lecture_id": "eng-live-02",
        "batch_id": "bhavishya-1-0",
        "subject_slug": "english",
        "module_number": 1,
        "module_name": "Module 1: Spoken English & Accent Foundations",
        "lecture_number": 2,
        "order": 2,
        "title": "Live Lecture 02: English Phonetics, Silent Letters & Sentence Rhythm",
        "description": "Master silent letters (doubt, subtle, receipt, pseudo), correct syllable stress, intonation patterns, and speaking with a pleasant, confident rhythm.",
        "teacher_name": "Ananya Sharma (Senior English Faculty)",
        "teacher_title": "Communication & Soft Skills Coach",
        "teacher_avatar": "/static/img/teacher_ananya.svg",
        "scheduled_at": "2026-11-21T20:30:00Z",
        "scheduled_display": "Completed • Replay & Notes Available",
        "duration_minutes": 60,
        "status": "completed",
        "google_meet_url": "https://meet.google.com/new",
        "recording_url": "FGa8xO6mUio",
        "notes_url": "",
        "notes_content": """### Phonetics & Silent Letters Cheatsheet
- **Silent B**: Doubt, subtle, debt, thumb, tomb.
- **Silent P**: Receipt, psychology, pneumonia, pseudo.
- **Silent K**: Knife, knee, knock, knowledge.
- **Silent W**: Write, wrong, sword, wrist.
- **Intonation**: Rising tone for questions, falling tone for definitive statements.""",
        "starter_code": """# Pronunciation Practice
words = ["subtle", "receipt", "cache", "hierarchy", "suite"]
print("Commonly Mispronounced Words in Tech:")
for w in words:
    print(f"Practice saying: {w}")
""",
        "dpp_list": [
            {
                "id": "eng-dpp-2-1",
                "question": "In the word 'RECEIPT', which letter is silent?",
                "options": ["C", "P", "T", "E"],
                "answer_index": 1,
                "explanation": "'P' is silent in 'receipt' (pronounced ri-seet)."
            },
            {
                "id": "eng-dpp-2-2",
                "question": "How is the word 'CACHE' (as in memory cache) pronounced?",
                "options": ["Catch", "Cash", "Kay-sh", "Cash-ay"],
                "answer_index": 1,
                "explanation": "'Cache' is pronounced exactly like 'cash'."
            },
            {
                "id": "eng-dpp-2-3",
                "question": "In the word 'SUBTLE', which letter is silent?",
                "options": ["B", "T", "L", "E"],
                "answer_index": 0,
                "explanation": "The letter 'B' is silent; it is pronounced 'suh-tl'."
            }
        ]
    },

    # --------------------------------------------------------------------------
    # MODULE 2: Daily Life & Conversational Confidence
    # --------------------------------------------------------------------------
    {
        "lecture_id": "eng-live-03",
        "batch_id": "bhavishya-1-0",
        "subject_slug": "english",
        "module_number": 2,
        "module_name": "Module 2: Daily Life & Conversational Confidence",
        "lecture_number": 3,
        "order": 3,
        "title": "Live Lecture 03: Everyday Conversations: Introductions & Small Talk",
        "description": "Interactive speaking circle on Google Meet: making friends, engaging senior developers at hackathons, networking on LinkedIn, and keeping dialogues lively.",
        "teacher_name": "Ananya Sharma (Senior English Faculty)",
        "teacher_title": "Communication & Soft Skills Coach",
        "teacher_avatar": "/static/img/teacher_ananya.svg",
        "scheduled_at": "2026-11-23T20:30:00Z",
        "scheduled_display": "Live Tonight at 8:30 PM • Google Meet",
        "duration_minutes": 60,
        "status": "live",
        "google_meet_url": "https://meet.google.com/new",
        "recording_url": "",
        "notes_url": "",
        "notes_content": """### Small Talk & Networking Framework
1. **FORD Framework for Small Talk**: Family, Occupation, Recreation, Dreams.
2. **Open-Ended Starters**:
   - 'What brought you to this hackathon/webinar?'
   - 'How do you usually structure your Python projects?'
3. **Graceful Exit**:
   - 'It was great chatting with you, let me grab a quick drink. Let's connect on LinkedIn!'""",
        "starter_code": """# Small Talk Icebreakers
topics = ["Project tech stacks", "Favorite IDE shortcuts", "Upcoming college fests"]
print("Try initiating a conversation about:", topics[0])
""",
        "dpp_list": [
            {
                "id": "eng-dpp-3-1",
                "question": "Which question is best suited to initiate small talk at a tech conference?",
                "options": ["Why are you sitting here?", "How did you find the keynote session on AI?", "Tell me your salary.", "Do you know who I am?"],
                "answer_index": 1,
                "explanation": "Asking about shared experiences (like a keynote speech) is polite, engaging, and professional."
            },
            {
                "id": "eng-dpp-3-2",
                "question": "What is an effective way to keep an English conversation flowing?",
                "options": ["Answer with only 'Yes' or 'No'.", "Answer and follow up with an open-ended question.", "Interrupt constantly.", "Look at your phone while speaking."],
                "answer_index": 1,
                "explanation": "Adding context and returning an open-ended question keeps the conversational ball rolling smoothly."
            },
            {
                "id": "eng-dpp-3-3",
                "question": "Choose the most polite way to ask for someone's contact information:",
                "options": ["Give me your phone number now.", "Could we connect on LinkedIn to stay in touch?", "What is your secret email?", "I demand your WhatsApp."],
                "answer_index": 1,
                "explanation": "'Could we connect on LinkedIn to stay in touch?' is courteous, professional, and standard."
            }
        ]
    },
    {
        "lecture_id": "eng-live-04",
        "batch_id": "bhavishya-1-0",
        "subject_slug": "english",
        "module_number": 2,
        "module_name": "Module 2: Daily Life & Conversational Confidence",
        "lecture_number": 4,
        "order": 4,
        "title": "Live Lecture 04: Expressing Opinions, Agreeing & Diplomatically Disagreeing",
        "description": "Learn professional disagreement phrases for code reviews and team meetings without sounding rude, defensive, or insecure.",
        "teacher_name": "Ananya Sharma (Senior English Faculty)",
        "teacher_title": "Communication & Soft Skills Coach",
        "teacher_avatar": "/static/img/teacher_ananya.svg",
        "scheduled_at": "2026-11-25T20:30:00Z",
        "scheduled_display": "Wednesday, Nov 25 • 8:30 PM",
        "duration_minutes": 60,
        "status": "scheduled",
        "google_meet_url": "https://meet.google.com/new",
        "recording_url": "",
        "notes_url": "",
        "notes_content": """### Diplomatic Disagreement Formulas
- Instead of 'You are completely wrong', say:
  'I see your perspective, however, considering performance benchmarks, we might encounter a latency bottleneck here.'
- Instead of 'That makes no sense', say:
  'Could you walk me through the edge cases this approach handles?'""",
        "starter_code": """# Diplomatic Code Review Feedback Generator
def feedback(issue, suggestion):
    return f"Great work on this module! One minor observation: regarding {issue}, could we explore {suggestion} to optimize runtime?"

print(feedback("nested loops", "using a hash set"))
""",
        "dpp_list": [
            {
                "id": "eng-dpp-4-1",
                "question": "Select the most diplomatic way to disagree during a team meeting:",
                "options": ["Your idea is terribly flawed.", "I see what you mean, but have we considered the cost implications?", "Nobody agrees with that.", "Quiet down, listen to me."],
                "answer_index": 1,
                "explanation": "'I see what you mean, but have we considered...' acknowledges the speaker while steering focus toward objective facts."
            },
            {
                "id": "eng-dpp-4-2",
                "question": "Which phrase expresses strong yet professional agreement?",
                "options": ["I couldn't agree more with that approach.", "Fine, whatever you say.", "You might be right or wrong.", "I tolerate this."],
                "answer_index": 0,
                "explanation": "'I couldn't agree more with that approach' is an idiomatic and confident expression of alignment."
            },
            {
                "id": "eng-dpp-4-3",
                "question": "What does the phrase 'Devil's advocate' mean in a discussion?",
                "options": ["Someone who is malicious.", "Taking an opposing viewpoint to test the strength of an idea.", "A lawyer who fights crime.", "Someone who refuses to talk."],
                "answer_index": 1,
                "explanation": "Playing Devil's advocate means putting forward counterarguments to rigorously evaluate a proposal."
            }
        ]
    },

    # --------------------------------------------------------------------------
    # MODULE 3: Grammar That Actually Matters in Speaking
    # --------------------------------------------------------------------------
    {
        "lecture_id": "eng-live-05",
        "batch_id": "bhavishya-1-0",
        "subject_slug": "english",
        "module_number": 3,
        "module_name": "Module 3: Grammar That Actually Matters in Speaking",
        "lecture_number": 5,
        "order": 5,
        "title": "Live Lecture 05: Practical Tenses: Past vs Present vs Future in Tech Discussions",
        "description": "Eliminate tense confusion once and for all: Simple Past ('I built the feature') vs Present Perfect ('I have built three web apps').",
        "teacher_name": "Ananya Sharma (Senior English Faculty)",
        "teacher_title": "Communication & Soft Skills Coach",
        "teacher_avatar": "/static/img/teacher_ananya.svg",
        "scheduled_at": "2026-11-27T20:30:00Z",
        "scheduled_display": "Friday, Nov 27 • 8:30 PM",
        "duration_minutes": 60,
        "status": "scheduled",
        "google_meet_url": "https://meet.google.com/new",
        "recording_url": "",
        "notes_url": "",
        "notes_content": """### Practical Tenses for Engineers
- **Simple Past**: Specific completed event at a stated time.
  'I fixed that bug yesterday afternoon.'
- **Present Perfect**: Experience or result with present relevance.
  'I have worked extensively with MongoDB.'
- **Past Continuous**: Action in progress interrupted by another.
  'I was refactoring the auth controller when the server crashed.'""",
        "starter_code": """# Tense Converter Helper
activities = [
    ("Yesterday", "I refactored the database schema."),
    ("So far in my career", "I have deployed 5 web apps."),
    ("Tomorrow", "I will lead the sprint demonstration.")
]
for time, sentence in activities:
    print(f"[{time}]: {sentence}")
""",
        "dpp_list": [
            {
                "id": "eng-dpp-5-1",
                "question": "Fill in the blank: 'I ______ in this tech startup since January 2024.'",
                "options": ["am working", "have been working", "was working", "worked"],
                "answer_index": 1,
                "explanation": "Actions starting in the past and continuing into the present require Present Perfect Continuous: 'have been working'."
            },
            {
                "id": "eng-dpp-5-2",
                "question": "Choose the correct sentence:",
                "options": ["Yesterday I have submitted the assignment.", "Yesterday I submitted the assignment.", "Yesterday I had been submitting the assignment.", "Yesterday I submit the assignment."],
                "answer_index": 1,
                "explanation": "Specific past time markers ('yesterday', 'in 2023', 'last week') strictly require Simple Past ('submitted')."
            },
            {
                "id": "eng-dpp-5-3",
                "question": "Which tense is best suited for sharing an overarching career achievement?",
                "options": ["Simple Future", "Present Perfect ('I have developed...')", "Past Perfect Continuous", "Future Continuous"],
                "answer_index": 1,
                "explanation": "Present Perfect highlights life experience and ongoing relevance without pinning down a single timestamp."
            }
        ]
    },
    {
        "lecture_id": "eng-live-06",
        "batch_id": "bhavishya-1-0",
        "subject_slug": "english",
        "module_number": 3,
        "module_name": "Module 3: Grammar That Actually Matters in Speaking",
        "lecture_number": 6,
        "order": 6,
        "title": "Live Lecture 06: Modals (Could, Should, Would) & Eliminating Common Indianisms",
        "description": "Polite corporate requests using modal verbs, fixing prepositions of time/place, and replacing outdated expressions ('do the needful', 'prepone', 'pass out').",
        "teacher_name": "Ananya Sharma (Senior English Faculty)",
        "teacher_title": "Communication & Soft Skills Coach",
        "teacher_avatar": "/static/img/teacher_ananya.svg",
        "scheduled_at": "2026-11-29T20:30:00Z",
        "scheduled_display": "Sunday, Nov 29 • 8:30 PM",
        "duration_minutes": 60,
        "status": "scheduled",
        "google_meet_url": "https://meet.google.com/new",
        "recording_url": "",
        "notes_url": "",
        "notes_content": """### Indianisms vs Global Corporate English
| Common Indianism | Standard Global Alternative |
| --- | --- |
| I passed out of college in 2024 | I graduated from college in 2024 |
| Can we prepone the standup? | Can we reschedule the standup earlier? |
| Please do the needful | Please take appropriate action / look into this |
| I will revert back | I will get back to you / I will reply |
| Myself Tanishk | My name is Tanishk / I am Tanishk |""",
        "starter_code": """# Indianism Filter Tool
bad_phrases = ["passed out of college", "do the needful", "revert back"]
good_phrases = ["graduated from college", "take required action", "revert / reply"]
print("Always replace outdated phrasing with crisp modern alternatives!")
""",
        "dpp_list": [
            {
                "id": "eng-dpp-6-1",
                "question": "Which option correctly replaces: 'Myself Rahul from Computer Science'?",
                "options": ["Myself is Rahul from CS.", "I am Rahul from Computer Science.", "Mine Rahul from CS.", "Me Rahul."],
                "answer_index": 1,
                "explanation": "'Myself' is a reflexive pronoun and cannot stand as a sentence subject. Use 'I am Rahul' or 'My name is Rahul'."
            },
            {
                "id": "eng-dpp-6-2",
                "question": "What is the proper expression for finishing university?",
                "options": ["I passed out from IIT in 2024.", "I graduated from IIT in 2024.", "I retired from IIT in 2024.", "I dropped off from IIT in 2024."],
                "answer_index": 1,
                "explanation": "In standard English, 'passed out' means fainted or lost consciousness. 'Graduated' is the correct term for college completion."
            },
            {
                "id": "eng-dpp-6-3",
                "question": "Select the most polite request for assistance:",
                "options": ["You must give me access right now.", "Could you please grant me read access to the GitHub repository?", "Give access.", "I want access immediately."],
                "answer_index": 1,
                "explanation": "Modal verb 'Could' with 'please' forms the quintessential professional polite request."
            }
        ]
    },

    # --------------------------------------------------------------------------
    # MODULE 4: Professional Workplace Communication
    # --------------------------------------------------------------------------
    {
        "lecture_id": "eng-live-07",
        "batch_id": "bhavishya-1-0",
        "subject_slug": "english",
        "module_number": 4,
        "module_name": "Module 4: Professional Workplace Communication",
        "lecture_number": 7,
        "order": 7,
        "title": "Live Lecture 07: High-Impact Corporate Email Writing & Message Etiquette",
        "description": "Master subject lines that get opened, concise 3-paragraph email structures, polite follow-ups, and professional email sign-offs.",
        "teacher_name": "Ananya Sharma (Senior English Faculty)",
        "teacher_title": "Communication & Soft Skills Coach",
        "teacher_avatar": "/static/img/teacher_ananya.svg",
        "scheduled_at": "2026-12-02T20:30:00Z",
        "scheduled_display": "Wednesday, Dec 2 • 8:30 PM",
        "duration_minutes": 60,
        "status": "scheduled",
        "google_meet_url": "https://meet.google.com/new",
        "recording_url": "",
        "notes_url": "",
        "notes_content": """### The 3-Paragraph Email Architecture
1. **Paragraph 1 (The Hook/Context)**: State purpose in sentence one ('I am writing to share the updated API schema...').
2. **Paragraph 2 (Details/Actionables)**: Bullet points of core metrics or tasks.
3. **Paragraph 3 (Call-to-Action & Sign-off)**: Next step + deadline ('Kindly review by Thursday 4 PM. Best regards, [Name]').""",
        "starter_code": """# Email Template Generator
def generate_email(subject, recipient, context, cta):
    return f"Subject: {subject}\n\nHi {recipient},\n\nHope you are having a productive week.\n\n{context}\n\n{cta}\n\nBest regards,\nSkillRock Fellow"

print(generate_email("[Update] Sprint 3 Deployment", "Ananya", "The payment gateway integration is tested.", "Please test and confirm."))
""",
        "dpp_list": [
            {
                "id": "eng-dpp-7-1",
                "question": "Which email subject line is most effective and professional?",
                "options": ["URGENT PLEASE READ!!!", "Hey check this", "[Action Required] Code Review for Payment Gateway Pull Request #42", "Meeting."],
                "answer_index": 2,
                "explanation": "Clear prefix tag, specific topic, and pull request identifier provide immediate context."
            },
            {
                "id": "eng-dpp-7-2",
                "question": "Which sign-off is best suited for external clients or senior executives?",
                "options": ["Cheers bro,", "Warm regards,", "Later,", "Yours faithfully,"],
                "answer_index": 1,
                "explanation": "'Warm regards' or 'Best regards' strikes the ideal balance of warmth, respect, and modern corporate professionalism."
            },
            {
                "id": "eng-dpp-7-3",
                "question": "What is the recommended maximum paragraph length in professional email communication?",
                "options": ["10-15 lines", "2-4 concise lines", "1 single endless block", "50 words per letter"],
                "answer_index": 1,
                "explanation": "Short 2-4 line paragraphs enhance scannability on mobile screens and laptop clients."
            }
        ]
    },
    {
        "lecture_id": "eng-live-08",
        "batch_id": "bhavishya-1-0",
        "subject_slug": "english",
        "module_number": 4,
        "module_name": "Module 4: Professional Workplace Communication",
        "lecture_number": 8,
        "order": 8,
        "title": "Live Lecture 08: Daily Standups, Sprint Demos & Slack/Teams Etiquette",
        "description": "Speak with crisp clarity in Agile daily scrums: 'What I achieved yesterday, what I'm executing today, and my blockers'.",
        "teacher_name": "Ananya Sharma (Senior English Faculty)",
        "teacher_title": "Communication & Soft Skills Coach",
        "teacher_avatar": "/static/img/teacher_ananya.svg",
        "scheduled_at": "2026-12-04T20:30:00Z",
        "scheduled_display": "Friday, Dec 4 • 8:30 PM",
        "duration_minutes": 60,
        "status": "scheduled",
        "google_meet_url": "https://meet.google.com/new",
        "recording_url": "",
        "notes_url": "",
        "notes_content": """### Agile Standup Delivery Script
- 'Good morning team. Yesterday I completed the unit test coverage for the authentication middleware.'
- 'Today my goal is to implement the Redis caching layer.'
- 'Currently I have no blockers, but I might sync with Tanishk later on Docker deployment.'""",
        "starter_code": """# Scrum Standup Formatter
yesterday = "Implemented Google OAuth login bridge"
today = "Designing Physics Wallah-style batch UI"
blockers = "None currently"

print(f"Standup Update:\n- Yesterday: {yesterday}\n- Today: {today}\n- Blockers: {blockers}")
""",
        "dpp_list": [
            {
                "id": "eng-dpp-8-1",
                "question": "What is the primary objective of an Agile daily standup update?",
                "options": ["To boast about hours worked", "To share concise progress, commitments, and blockers", "To debate company politics", "To read code line by line"],
                "answer_index": 1,
                "explanation": "Standups are brief synchronizations focusing on yesterday's output, today's targets, and active blockers."
            },
            {
                "id": "eng-dpp-8-2",
                "question": "How long should an individual's standup update typically take?",
                "options": ["1 to 2 minutes", "15 to 20 minutes", "1 hour", "30 seconds total for entire team"],
                "answer_index": 0,
                "explanation": "A crisp, prepared developer update takes approximately 60 to 90 seconds."
            },
            {
                "id": "eng-dpp-8-3",
                "question": "When you have a technical blocker requiring deep discussion with a teammate, what should you say?",
                "options": ["Start arguing right away in the meeting", "I have a blocker on Redis; let's take that offline right after standup", "Ignore the blocker", "Blame the teammate publicly"],
                "answer_index": 1,
                "explanation": "'Taking it offline' preserves everyone's time while prioritizing targeted resolution."
            }
        ]
    },

    # --------------------------------------------------------------------------
    # MODULE 5: Interview Mastery & Group Discussions (GD)
    # --------------------------------------------------------------------------
    {
        "lecture_id": "eng-live-09",
        "batch_id": "bhavishya-1-0",
        "subject_slug": "english",
        "module_number": 5,
        "module_name": "Module 5: Interview Mastery & Group Discussions (GD)",
        "lecture_number": 9,
        "order": 9,
        "title": "Live Lecture 09: Cracking 'Tell Me About Yourself' with the STAR Method",
        "description": "Craft an irresistible 90-second elevator pitch and answer behavioral questions using Situation, Task, Action, and Result.",
        "teacher_name": "Ananya Sharma (Senior English Faculty)",
        "teacher_title": "Communication & Soft Skills Coach",
        "teacher_avatar": "/static/img/teacher_ananya.svg",
        "scheduled_at": "2026-12-07T20:30:00Z",
        "scheduled_display": "Monday, Dec 7 • 8:30 PM",
        "duration_minutes": 60,
        "status": "scheduled",
        "google_meet_url": "https://meet.google.com/new",
        "recording_url": "",
        "notes_url": "",
        "notes_content": """### STAR Framework for Tech Interviews
- **S (Situation)**: Set the scene (e.g., 'In my college final year project...').
- **T (Task)**: What challenge or goal did you need to accomplish?
- **A (Action)**: What specific Python/engineering action did YOU take?
- **R (Result)**: Quantifiable outcome ('Reduced query latency by 40% and published an open-source tool').""",
        "starter_code": """# STAR Story Builder
situation = "High database latency on user query page"
task = "Optimize queries and prevent 500 timeouts"
action = "Replaced N+1 loop with bulk MongoDB $in aggregation"
result = "Decreased response time from 61.8s to 0.56s (108x speedup)"

print(f"STAR Summary:\nWhen faced with {situation}, I was tasked to {task}. I {action}, which resulted in {result}!")
""",
        "dpp_list": [
            {
                "id": "eng-dpp-9-1",
                "question": "What does the 'R' in the STAR behavioral interview method represent?",
                "options": ["Reasoning", "Result", "Rebuttal", "Reflection"],
                "answer_index": 1,
                "explanation": "'R' stands for Result, emphasizing measurable outcomes and lessons learned."
            },
            {
                "id": "eng-dpp-9-2",
                "question": "When asked 'What is your greatest weakness?', what is the best strategy?",
                "options": ["Say 'I have no weaknesses, I am perfect'", "Mention an authentic area of growth and the concrete steps you are actively taking to improve it", "Say 'I hate waking up early'", "Refuse to answer"],
                "answer_index": 1,
                "explanation": "Self-awareness and proactive learning demonstrate maturity, coachability, and emotional intelligence."
            },
            {
                "id": "eng-dpp-9-3",
                "question": "How long should your initial answer to 'Tell me about yourself' ideally last?",
                "options": ["10 seconds", "60 to 90 seconds", "15 minutes", "Half an hour"],
                "answer_index": 1,
                "explanation": "60 to 90 seconds provides ample depth without rambling or overwhelming the interviewer."
            }
        ]
    },
    {
        "lecture_id": "eng-live-10",
        "batch_id": "bhavishya-1-0",
        "subject_slug": "english",
        "module_number": 5,
        "module_name": "Module 5: Interview Mastery & Group Discussions (GD)",
        "lecture_number": 10,
        "order": 10,
        "title": "Live Lecture 10: Group Discussion (GD) Tactics: Entering, Asserting & Summarizing",
        "description": "How to command respect without shouting in GD rounds: conversational entry strategies, bridging opinions, and delivering winning summaries.",
        "teacher_name": "Ananya Sharma (Senior English Faculty)",
        "teacher_title": "Communication & Soft Skills Coach",
        "teacher_avatar": "/static/img/teacher_ananya.svg",
        "scheduled_at": "2026-12-09T20:30:00Z",
        "scheduled_display": "Wednesday, Dec 9 • 8:30 PM",
        "duration_minutes": 60,
        "status": "scheduled",
        "google_meet_url": "https://meet.google.com/new",
        "recording_url": "",
        "notes_url": "",
        "notes_content": """### GD Round Golden Rules
1. **Entry Strategy**: Jump in on the pause, not during someone's mid-sentence ('Building upon what Priya mentioned...').
2. **Moderator Role**: If the group goes off-track, gently guide them: 'Friends, we have 5 minutes left; let us converge on the key solutions.'
3. **Neutral Summary**: Include both perspectives and tie with a constructive conclusion.""",
        "starter_code": """# GD Phrase Bank
entry = "I would like to add an important dimension to this point..."
agreement = "That is a valid insight, and extending that further..."
conclusion = "To synthesize our discussion today..."
print("Ready for GD live practice!")
""",
        "dpp_list": [
            {
                "id": "eng-dpp-10-1",
                "question": "If two participants are aggressively shouting in a GD, what is the best way to earn high marks?",
                "options": ["Shout louder than both of them", "Remain completely silent until the round ends", "Politely intervene: 'Friends, let us maintain decorum so everyone gets a chance to articulate'", "Walk out of the room"],
                "answer_index": 2,
                "explanation": "Demonstrating group leadership and composure in high-pressure moments is highly scored by evaluators."
            },
            {
                "id": "eng-dpp-10-2",
                "question": "When summarizing a Group Discussion, you should:",
                "options": ["Only repeat your own personal points", "Fairly represent both the pros and cons discussed by the group and state the consensus", "Declare yourself the winner", "Introduce completely new points never raised before"],
                "answer_index": 1,
                "explanation": "A summary must be an objective consolidation of the entire group's insights."
            },
            {
                "id": "eng-dpp-10-3",
                "question": "Which transition phrase allows you to interject politely during a group discussion?",
                "options": ["Shut up everyone", "Allow me to build on that fascinating point...", "You guys know nothing", "Listen to me only"],
                "answer_index": 1,
                "explanation": "'Allow me to build on that fascinating point...' shows active listening and constructive collaboration."
            }
        ]
    },

    # --------------------------------------------------------------------------
    # MODULE 6: Public Speaking, Impromptu Talks & Storytelling
    # --------------------------------------------------------------------------
    {
        "lecture_id": "eng-live-11",
        "batch_id": "bhavishya-1-0",
        "subject_slug": "english",
        "module_number": 6,
        "module_name": "Module 6: Public Speaking, Impromptu Talks & Storytelling",
        "lecture_number": 11,
        "order": 11,
        "title": "Live Lecture 11: JAM (Just A Minute) Impromptu Speaking & Overcoming Hesitation",
        "description": "Live 60-second speaking challenges on Google Meet: eradicate filler sounds ('um', 'ah', 'like', 'you know'), control pacing, and think on your feet.",
        "teacher_name": "Ananya Sharma (Senior English Faculty)",
        "teacher_title": "Communication & Soft Skills Coach",
        "teacher_avatar": "/static/img/teacher_ananya.svg",
        "scheduled_at": "2026-12-12T20:30:00Z",
        "scheduled_display": "Saturday, Dec 12 • 8:30 PM",
        "duration_minutes": 60,
        "status": "scheduled",
        "google_meet_url": "https://meet.google.com/new",
        "recording_url": "",
        "notes_url": "",
        "notes_content": """### JAM Rules & Delivery Framework
- **Rule**: Speak for 60 seconds without repetition, hesitation, or deviation.
- **PPF Formula**: Past, Present, Future (e.g. 'How computing was, how it is now, where it will go').
- **Pause Power**: Whenever you feel like saying 'ummm', take a deliberate 1-second breath. Silence radiates confidence.""",
        "starter_code": """# JAM Random Topic Selector
import random
topics = ["Artificial Intelligence in Education", "Remote Work vs Office", "The Book That Changed My Mindset", "Open Source Software"]
selected = random.choice(topics)
print(f"Your 60-second JAM topic is: {selected}\nTake 10 seconds to think, then speak!")
""",
        "dpp_list": [
            {
                "id": "eng-dpp-11-1",
                "question": "What is the most effective replacement for filler words like 'um', 'uh', and 'basically'?",
                "options": ["Saying 'like' repeatedly", "A deliberate, confident 1-second pause", "Talking twice as fast", "Coughing"],
                "answer_index": 1,
                "explanation": "Pausing gives you time to think while projecting poise and control to listeners."
            },
            {
                "id": "eng-dpp-11-2",
                "question": "What is the Past-Present-Future (PPF) formula in impromptu speaking?",
                "options": ["Reciting grammar charts", "Structuring a talk by examining how things began, where they stand today, and future potential", "Predicting horoscopes", "Speaking in three accents"],
                "answer_index": 1,
                "explanation": "The PPF framework ensures a seamless, logical story arc when given any impromptu topic."
            },
            {
                "id": "eng-dpp-11-3",
                "question": "Which element most captivates an audience during an impromptu tech talk?",
                "options": ["Monotone reading from a slide", "A brief relatable story or personal anecdote", "Using the longest possible dictionary words", "Never making eye contact"],
                "answer_index": 1,
                "explanation": "Stories and analogies humanize abstract technical concepts and keep audiences hooked."
            }
        ]
    },
    {
        "lecture_id": "eng-live-12",
        "batch_id": "bhavishya-1-0",
        "subject_slug": "english",
        "module_number": 6,
        "module_name": "Module 6: Public Speaking, Impromptu Talks & Storytelling",
        "lecture_number": 12,
        "order": 12,
        "title": "Live Lecture 12: Capstone Speaking Arena: Live Student Talks & Feedback",
        "description": "Graduation ceremony of the English Live Batch! Students present 3-minute capstone tech talks on Google Meet and receive personalized faculty critique.",
        "teacher_name": "Ananya Sharma (Senior English Faculty)",
        "teacher_title": "Communication & Soft Skills Coach",
        "teacher_avatar": "/static/img/teacher_ananya.svg",
        "scheduled_at": "2026-12-15T20:30:00Z",
        "scheduled_display": "Tuesday, Dec 15 • 8:30 PM",
        "duration_minutes": 90,
        "status": "scheduled",
        "google_meet_url": "https://meet.google.com/new",
        "recording_url": "",
        "notes_url": "",
        "notes_content": """### Capstone Presentation Rubric
1. **Introduction & Hook (20%)**: Grab attention with a surprising statistic or rhetorical question.
2. **Core Message & Logic (40%)**: Structured key insights with clear transitions.
3. **Delivery & Body Language (25%)**: Steady eye contact with camera, open posture, vocal variety.
4. **Conclusion & Q&A (15%)**: Crisp summary and gracious response to peer questions.""",
        "starter_code": """# Capstone Presentation Timer & Outline
print("=== SKILLROCK CAPSTONE SPEAKING ARENA ===")
print("Outline Check:")
print("1. Hook: 'Did you know that 85% of job success comes from communication skills?'")
print("2. Tech Insight: 'How Python microservices communicate.'")
print("3. Takeaway: 'Clarity in code, clarity in speech.'")
""",
        "dpp_list": [
            {
                "id": "eng-dpp-12-1",
                "question": "What is the best way to handle an audience question you do not know the answer to?",
                "options": ["Guess wildly and pretend you know", "Acknowledge honestly: 'That is a great question. I don't have the exact data offhand, but let me research that and follow up with you after this session'", "Insult the questioner", "Ignore the question completely"],
                "answer_index": 1,
                "explanation": "Honesty combined with a commitment to follow up demonstrates integrity and executive presence."
            },
            {
                "id": "eng-dpp-12-2",
                "question": "What is the recommended focal point when presenting in virtual Google Meet meetings?",
                "options": ["Look directly at the webcam lens intermittently to create perceived eye contact", "Look only at your keyboard", "Stare at your own video thumbnail the entire time", "Look out the window"],
                "answer_index": 0,
                "explanation": "Looking directly into the camera lens creates direct personal connection for virtual viewers."
            },
            {
                "id": "eng-dpp-12-3",
                "question": "Congratulations on completing the Bhavishya 1.0 English Academy! What is the primary key to maintaining lifelong fluency?",
                "options": ["Never speaking again", "Consistent daily immersion: reading, listening to podcasts, and conversing in English", "Memorizing the dictionary front to back", "Waiting 5 years before speaking"],
                "answer_index": 1,
                "explanation": "Continuous exposure and active practice solidify fluency for a lifetime."
            }
        ]
    }
]


def ensure_default_bhavishya_live_batch():
    """
    Seeds and ensures the Bhavishya 1.0 Physics Wallah-style Live Batches
    (both Python Mastery and English Communication) and all live lectures exist in MongoDB.
    Safe and idempotent.
    """
    from models.bhavishya import BhavishyaBatchConfig, BhavishyaLiveLecture

    try:
        # 1. Seed or refresh Batch Config
        config = BhavishyaBatchConfig.get_config("bhavishya-1-0")
        config.title = "Bhavishya 1.0 — Free Live & Masterclass Batch"
        config.tagline = "Interactive Live Lectures on Google Meet with Teachers (Python & English), Daily Practice Problems (DPP), Handwritten Notes, and 24/7 AI Doubt Solving"
        config.teacher_name = "Tanishk Pal & Ananya Sharma"
        config.teacher_title = "Lead Faculty Team"
        config.price = 0.0
        config.original_price = 0.0
        config.global_meet_url = config.global_meet_url or "https://meet.google.com/new"
        config.save()

        # 2. Seed or update each of the Python & English live lectures
        db = get_db()
        seeded = 0
        updated = 0
        all_lectures = DEFAULT_LIVE_LECTURES + DEFAULT_ENGLISH_LIVE_LECTURES
        for data in all_lectures:
            lid = data["lecture_id"]
            existing = db.bhavishya_live_lectures.find_one({"lecture_id": lid})
            if not existing:
                lec = BhavishyaLiveLecture(data)
                lec.save()
                seeded += 1
            else:
                # Update content, notes, DPPs while preserving custom status/meet URL if set by admin
                update_fields = {
                    "subject_slug": data.get("subject_slug", "python"),
                    "module_number": data["module_number"],
                    "module_name": data["module_name"],
                    "lecture_number": data["lecture_number"],
                    "order": data["order"],
                    "title": data["title"],
                    "description": data["description"],
                    "teacher_name": data["teacher_name"],
                    "teacher_title": data.get("teacher_title", ""),
                    "teacher_avatar": data.get("teacher_avatar", ""),
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
