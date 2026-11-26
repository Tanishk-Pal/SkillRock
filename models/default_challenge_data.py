"""
SkillRock — Default Monthly Challenge Curriculum Seeder
Provides default production data for:
- "Python Programming — 30-Day Challenge" (₹499 | 30 Days | 100% Refund Guarantee)
- 6 Structured Modules with curated YouTube course content
- Practice Arena Topic-wise MCQs
- Placement Interview Preparation Questions
- Inbuilt Coding Arena Algorithmic Problems with Sample & Hidden Test Cases
- 50-MCQ Final Assessment Question Bank
- Final Practical Capstone Assignment with 4-part Evaluation Rubric
"""

import logging
from datetime import datetime, timezone, timedelta
from models.challenge import (
    MonthlyChallenge,
    PracticeQuestion,
    InterviewQuestion,
    CodingProblem,
    AssessmentQuestion,
    PracticalAssignment
)

logger = logging.getLogger(__name__)

DEFAULT_PYTHON_CHALLENGE = {
    "challenge_id": "python-28-day-challenge",
    "slug": "python-28-day-challenge",
    "title": "Python Programming — 30-Day Challenge",
    "tagline": "Learn. Practice. Complete. Get Certified.",
    "promotional_message": "Complete your learning challenge within 30 days and get 100% of your eligible enrolment fee back!",
    "short_description": "Learn Python through a curated YouTube course, solve practical problems, prepare for technical interviews, and earn your SkillRock certificate.",
    "full_description": """Welcome to the SkillRock Monthly Challenge! Over the next 30 days, you will embark on an intensive, structured curriculum covering foundational and advanced Python programming. 

You will study curated YouTube lessons, solve module-wise practice questions, master frequently asked placement interview problems, write code inside our interactive Coding Arena, complete an evaluated practical project, and prove your mastery in a comprehensive 50-question final assessment.

Meet all graduation requirements within 30 days and receive a 100% refund of your eligible ₹499 enrolment fee!""",
    "badge_text": "MONTHLY CHALLENGE",
    "month_display": "November 2026",
    "instructor": "Programming with Mosh & SkillRock Faculty",
    "thumbnail_url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&auto=format&fit=crop&q=80",
    "banner_url": "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=1600&auto=format&fit=crop&q=80",
    "price": 499.0,
    "original_price": 1999.0,
    "currency": "INR",
    "duration_days": 30,
    "difficulty": "Beginner to Placement Ready",
    "skills_covered": ["Python 3", "Data Structures", "Control Flow", "Object-Oriented Programming", "File I/O", "Exception Handling", "Algorithmic Thinking"],
    "learning_outcomes": [
        "Master Python syntax, variables, expressions, and primitive/composite data types.",
        "Gain command over conditional logic, loops, iterators, and comprehension syntax.",
        "Write robust, reusable code with functions, decorators, and lambda expressions.",
        "Design modular object-oriented software with classes, encapsulation, and inheritance.",
        "Solve classic placement coding problems with optimized time and space complexity.",
        "Confidently answer technical interview questions asked by top tech employers.",
        "Build a persistent practical project evaluated by SkillRock faculty against a rubric.",
        "Earn a tamper-proof verified SkillRock Certificate and claim a 100% refund upon completion."
    ],
    "youtube_course_url": "https://www.youtube.com/watch?v=_uQrJ0TkZlc",
    "youtube_video_id": "_uQrJ0TkZlc",
    "is_published": True,
    "is_programming": True,
    "supported_languages": ["python"],
    "refund_terms": "Complete all mandatory modules, solve practical exercises, submit and pass the practical assignment rubric (>=70%), pass the 50-MCQ final assessment (>=80%), and receive your SkillRock certificate within 30 days of enrolment to qualify for a 100% refund of your ₹499 fee.",
    "modules": [
        {
            "module_id": "mod-1",
            "module_number": 1,
            "title": "Module 1 — Introduction & Environment Setup",
            "description": "Understand Python architecture, install VS Code/Python, understand interpreters vs compilers, and write your first clean Python script.",
            "duration": "4 Hours",
            "youtube_url": "https://www.youtube.com/watch?v=_uQrJ0TkZlc",
            "youtube_video_id": "_uQrJ0TkZlc",
            "video_start_time": 0,
            "objectives": [
                "Install Python 3 and configure VS Code development environment",
                "Understand Python bytecode and CPython execution model",
                "Learn variables, dynamic typing, and standard input/output"
            ],
            "notes": "Python is an interpreted, high-level, dynamically-typed programming language created by Guido van Rossum. CPython converts source code into intermediate bytecode (.pyc) which is executed by the Python Virtual Machine (PVM)."
        },
        {
            "module_id": "mod-2",
            "module_number": 2,
            "title": "Module 2 — Fundamentals: Data Types & Control Flow",
            "description": "Master integers, floats, strings, booleans, arithmetic operators, if-elif-else statements, while loops, and for-in range iteration.",
            "duration": "6 Hours",
            "youtube_url": "https://www.youtube.com/watch?v=_uQrJ0TkZlc",
            "youtube_video_id": "_uQrJ0TkZlc",
            "video_start_time": 1800,
            "objectives": [
                "Perform string slicing, formatting with f-strings, and string methods",
                "Implement conditional logic using boolean expressions and logical operators",
                "Master loops: while loops, for loops with range(), break, and continue"
            ],
            "notes": "Strings in Python are immutable sequences of Unicode characters. Slicing syntax `string[start:stop:step]` allows rapid extraction. Control flow supports `pass` as a no-op placeholder."
        },
        {
            "module_id": "mod-3",
            "module_number": 3,
            "title": "Module 3 — Core Concepts: Data Structures & Collections",
            "description": "Deep dive into lists, tuples, dictionaries, sets, list comprehensions, unpacking, and dictionary transformations.",
            "duration": "7 Hours",
            "youtube_url": "https://www.youtube.com/watch?v=_uQrJ0TkZlc",
            "youtube_video_id": "_uQrJ0TkZlc",
            "video_start_time": 4200,
            "objectives": [
                "Utilize lists (mutable dynamic arrays) and tuples (immutable sequences)",
                "Master dictionaries (hash maps) with key-value lookups, get(), and items()",
                "Write concise, high-speed list, set, and dictionary comprehensions"
            ],
            "notes": "Dictionaries in Python 3.7+ maintain insertion order. Average time complexity for dict key lookup, insertion, and deletion is O(1). Tuples are hashable and can be used as dictionary keys."
        },
        {
            "module_id": "mod-4",
            "module_number": 4,
            "title": "Module 4 — Functions, Scope & Exception Handling",
            "description": "Learn clean modular architecture: defining functions, *args, **kwargs, default parameters, variable scope (LEGB rule), and try-except-finally blocks.",
            "duration": "6 Hours",
            "youtube_url": "https://www.youtube.com/watch?v=_uQrJ0TkZlc",
            "youtube_video_id": "_uQrJ0TkZlc",
            "video_start_time": 7200,
            "objectives": [
                "Write functions with positional, keyword, and arbitrary arguments (*args, **kwargs)",
                "Understand variable resolution via LEGB (Local, Enclosing, Global, Built-in)",
                "Safely handle exceptions using try, except, else, and finally"
            ],
            "notes": "Functions in Python are first-class citizens: they can be passed as arguments, assigned to variables, and returned from other functions. Exception hierarchy inherits from BaseException -> Exception."
        },
        {
            "module_id": "mod-5",
            "module_number": 5,
            "title": "Module 5 — Object-Oriented Programming (OOP) & Files",
            "description": "Master OOP principles: Classes, __init__, instance vs class attributes, inheritance, polymorphism, encapsulation, and reading/writing files with context managers.",
            "duration": "8 Hours",
            "youtube_url": "https://www.youtube.com/watch?v=_uQrJ0TkZlc",
            "youtube_video_id": "_uQrJ0TkZlc",
            "video_start_time": 10800,
            "objectives": [
                "Define custom classes with constructors (__init__) and methods",
                "Implement single and multi-level inheritance with super()",
                "Read and write files safely with the `with open(...)` context manager"
            ],
            "notes": "Encapsulation in Python uses naming conventions: a single leading underscore `_protected` indicates internal use, while a double leading underscore `__private` triggers name mangling."
        },
        {
            "module_id": "mod-6",
            "module_number": 6,
            "title": "Module 6 — Practical Implementation & Final Revision",
            "description": "Consolidate your knowledge by architecting complete CLI programs, refactoring code, optimizing algorithms, and reviewing key placement questions.",
            "duration": "5 Hours",
            "youtube_url": "https://www.youtube.com/watch?v=_uQrJ0TkZlc",
            "youtube_video_id": "_uQrJ0TkZlc",
            "video_start_time": 14400,
            "objectives": [
                "Integrate modular architecture, JSON persistence, and OOP design",
                "Review time and space complexity (Big-O notation) for core operations",
                "Prepare for the practical assignment submission and 50-MCQ final assessment"
            ],
            "notes": "Code readability counts (PEP 8). Keep functions single-purpose (SRP). Document complex algorithms with clear docstrings and meaningful variable names."
        }
    ]
}

DEFAULT_PRACTICE_QUESTIONS = [
    {
        "question_id": "pq-1-1",
        "module_id": "mod-1",
        "topic": "Python Basics",
        "difficulty": "Easy",
        "question": "Which of the following is an invalid variable name in Python?",
        "options": ["_user_age", "user_age_2", "2nd_user", "userAge"],
        "correct_answer_index": 2,
        "explanation": "Variable names in Python cannot begin with a number. '2nd_user' starts with '2', violating variable naming rules.",
        "hint": "Check which identifier begins with a numeric character."
    },
    {
        "question_id": "pq-1-2",
        "module_id": "mod-1",
        "topic": "Data Types",
        "difficulty": "Easy",
        "question": "What is the output of `type(3.14)` in Python 3?",
        "options": ["<class 'int'>", "<class 'float'>", "<class 'double'>", "<class 'decimal'>"],
        "correct_answer_index": 1,
        "explanation": "Python represents real numbers with floating-point precision as `<class 'float'>`. There is no separate 'double' primitive type in Python.",
        "hint": "Python handles decimal numbers using IEEE 754 floating point standard."
    },
    {
        "question_id": "pq-2-1",
        "module_id": "mod-2",
        "topic": "Control Flow",
        "difficulty": "Medium",
        "question": "What is the output of the following code?\n```python\nx = [1, 2, 3]\nfor i in x:\n    if i == 2:\n        continue\n    print(i, end=' ')\n```",
        "options": ["1 2 3", "1 3", "1 2", "2 3"],
        "correct_answer_index": 1,
        "explanation": "The `continue` statement skips the rest of the current loop iteration when `i == 2`. Thus, only 1 and 3 are printed.",
        "hint": "The continue keyword jumps immediately to the next iteration."
    },
    {
        "question_id": "pq-2-2",
        "module_id": "mod-2",
        "topic": "String Operations",
        "difficulty": "Medium",
        "question": "What does `'SkillRock'[::-1]` evaluate to in Python?",
        "options": ["'kcoRllikS'", "'SkillRock'", "'kcoR'", "Error: Step negative not allowed"],
        "correct_answer_index": 0,
        "explanation": "A slice with step `-1` traverses the sequence backwards from end to start, reversing the string to 'kcoRllikS'.",
        "hint": "A negative step index reverses the string."
    },
    {
        "question_id": "pq-3-1",
        "module_id": "mod-3",
        "topic": "Data Structures",
        "difficulty": "Medium",
        "question": "What is the primary difference between a List and a Tuple in Python?",
        "options": [
            "Lists can contain integers; Tuples can only contain strings",
            "Lists are mutable; Tuples are immutable",
            "Tuples are mutable; Lists are immutable",
            "Lists use parentheses (); Tuples use square brackets []"
        ],
        "correct_answer_index": 1,
        "explanation": "Lists can be modified after creation (append, pop, assign), whereas Tuples cannot have their elements altered once defined.",
        "hint": "Consider mutability and memory safety."
    },
    {
        "question_id": "pq-3-2",
        "module_id": "mod-3",
        "topic": "Dictionaries",
        "difficulty": "Hard",
        "question": "What is the average time complexity for key lookups in a Python dictionary?",
        "options": ["O(N)", "O(log N)", "O(1)", "O(N^2)"],
        "correct_answer_index": 2,
        "explanation": "Python dictionaries are implemented using hash tables with open addressing, yielding an average time complexity of O(1) for lookups.",
        "hint": "Think about hash maps and constant time access."
    },
    {
        "question_id": "pq-4-1",
        "module_id": "mod-4",
        "topic": "Functions & Scope",
        "difficulty": "Medium",
        "question": "What does `*args` and `**kwargs` allow in a Python function definition?",
        "options": [
            "Pointers and memory references",
            "Arbitrary number of positional arguments and keyword arguments",
            "Only integer arguments and string arguments",
            "Mandatory return types"
        ],
        "correct_answer_index": 1,
        "explanation": "`*args` unpacks variable positional arguments into a tuple, while `**kwargs` unpacks keyword arguments into a dictionary.",
        "hint": "Look for variable-length argument handling."
    },
    {
        "question_id": "pq-5-1",
        "module_id": "mod-5",
        "topic": "OOP",
        "difficulty": "Hard",
        "question": "In Python class inheritance, what is the purpose of `super().__init__()`?",
        "options": [
            "It creates a superuser instance",
            "It calls the constructor of the parent/base class",
            "It destroys the child instance",
            "It converts the class into a singleton"
        ],
        "correct_answer_index": 1,
        "explanation": "`super().__init__()` delegates initialization to the superclass according to the Method Resolution Order (MRO).",
        "hint": "It invokes parent class initialization."
    }
]

DEFAULT_INTERVIEW_QUESTIONS = [
    {
        "question_id": "iq-1",
        "topic": "Python Internals",
        "level": "Intermediate",
        "category": "Conceptual",
        "question": "Explain Python's Global Interpreter Lock (GIL) and its implications for multithreading.",
        "sample_answer": "The Global Interpreter Lock (GIL) is a mutex in CPython that prevents multiple native threads from executing Python bytecode simultaneously. It was introduced to simplify CPython's memory management and ensure thread-safety for reference counting. However, it means CPU-bound Python tasks cannot leverage multiple CPU cores using multithreading alone. For true parallel processing of CPU-bound workloads, developers use the `multiprocessing` module or native C extensions.",
        "explanation": "Candidates must clearly distinguish between CPU-bound tasks (which are restricted by the GIL) and I/O-bound tasks (network, disk, database) where threads release the GIL during I/O wait times.",
        "interviewer_tips": "Ask how they would speed up an image processing pipeline vs a web scraper to test practical knowledge of multiprocessing vs asyncio/threading."
    },
    {
        "question_id": "iq-2",
        "topic": "Data Structures",
        "level": "Beginner",
        "category": "Technical",
        "question": "What is the difference between shallow copy and deep copy in Python?",
        "sample_answer": "A shallow copy (`copy.copy()`) creates a new collection object but populates it with references to the original nested child objects. If an inner mutable object is altered, both copies reflect the change. A deep copy (`copy.deepcopy()`) recursively duplicates the outer object and all nested child objects independently, creating completely disconnected memory structures.",
        "explanation": "Illustrate with a nested list: `a = [[1, 2], [3, 4]]`. A shallow copy will share the inner lists `[1, 2]`, whereas deep copy clones them.",
        "interviewer_tips": "Look for mention of mutable nested elements and the `copy` standard library module."
    },
    {
        "question_id": "iq-3",
        "topic": "Object-Oriented Programming",
        "level": "Intermediate",
        "category": "Scenario",
        "question": "How do `@classmethod`, `@staticmethod`, and instance methods differ in Python?",
        "sample_answer": "- **Instance Method**: Takes `self` as the first argument; has access to and can modify instance state and class state.\n- **Class Method (`@classmethod`)**: Takes `cls` as the first argument; can access and modify class-level state, often used as alternative constructors (e.g. `User.from_dict()`).\n- **Static Method (`@staticmethod`)**: Takes neither `self` nor `cls`; behaves like a plain utility function scoped inside the class namespace for logical grouping.",
        "explanation": "Demonstrates clear understanding of method binding and decorators in Python OOP.",
        "interviewer_tips": "Ask for an example of a factory method or alternative constructor using @classmethod."
    },
    {
        "question_id": "iq-4",
        "topic": "Memory & Performance",
        "level": "Advanced",
        "category": "Technical",
        "question": "How does Python's memory management work under the hood?",
        "sample_answer": "Python manages memory via two main subsystems:\n1. **Reference Counting**: Every object tracks the number of references pointing to it. When the count hits zero, memory is deallocated immediately.\n2. **Generational Garbage Collector (cyclic GC)**: Handles reference cycles (e.g. Object A refers to B, and B refers to A). Objects are categorized into 3 generations (Gen 0, 1, 2) based on how many GC collection cycles they survive.\n3. **PyMalloc**: An internal small-object memory allocator that manages pools and arenas to avoid fragmentation from OS-level malloc/free calls.",
        "explanation": "Understanding cycles and why reference counting alone is insufficient is a key indicator of a strong senior candidate.",
        "interviewer_tips": "Ask what causes memory leaks in Python even with automatic garbage collection."
    }
]

DEFAULT_CODING_PROBLEMS = [
    {
        "problem_id": "cp-1",
        "slug": "sum-of-two-numbers",
        "title": "Sum of Two Numbers",
        "difficulty": "Easy",
        "order": 1,
        "description": "Given two space-separated integers `a` and `b` from standard input, calculate and print their sum.",
        "input_format": "Two space-separated or newline-separated integers `a` and `b`",
        "output_format": "An integer representing the sum a + b",
        "constraints": "-10^9 <= a, b <= 10^9",
        "examples": [
            {"input": "3 5", "output": "8", "explanation": "3 + 5 = 8"}
        ],
        "starter_code": {
            "python": "import sys\n\ndef solve():\n    lines = sys.stdin.read().split()\n    if lines:\n        a = int(lines[0])\n        b = int(lines[1])\n        print(a + b)\n\nif __name__ == '__main__':\n    solve()\n"
        },
        "sample_test_cases": [
            {"input": "3 5\n", "expected_output": "8"},
            {"input": "10 20\n", "expected_output": "30"}
        ],
        "hidden_test_cases": [
            {"input": "100 250\n", "expected_output": "350"},
            {"input": "-5 15\n", "expected_output": "10"}
        ]
    },
    {
        "problem_id": "cp-2",
        "slug": "two-sum",
        "title": "Two Sum Problem",
        "difficulty": "Easy",
        "order": 2,
        "description": "Given an array of integers `nums` and an integer `target`, return the indices of the two numbers such that they add up to `target`. You may assume each input has exactly one solution, and you may not use the same element twice.",
        "input_format": "A list of integers `nums` and an integer `target`",
        "output_format": "A list of two integer indices [i, j]",
        "constraints": "2 <= len(nums) <= 10^4, -10^9 <= nums[i] <= 10^9",
        "examples": [
            {"input": "nums = [2, 7, 11, 15], target = 9", "output": "[0, 1]", "explanation": "nums[0] + nums[1] = 2 + 7 = 9"}
        ],
        "starter_code": {
            "python": "def two_sum(nums, target):\n    # Write your solution here\n    # Return [index1, index2]\n    seen = {}\n    for i, n in enumerate(nums):\n        comp = target - n\n        if comp in seen:\n            return [seen[comp], i]\n        seen[n] = i\n    return []\n"
        },
        "sample_test_cases": [
            {"input": "nums = [2, 7, 11, 15], target = 9", "expected_output": "[0, 1]"},
            {"input": "nums = [3, 2, 4], target = 6", "expected_output": "[1, 2]"}
        ],
        "hidden_test_cases": [
            {"input": "nums = [3, 3], target = 6", "expected_output": "[0, 1]"},
            {"input": "nums = [-1, -2, -3, -4, -5], target = -8", "expected_output": "[2, 4]"}
        ]
    },
    {
        "problem_id": "cp-2",
        "slug": "valid-palindrome",
        "title": "Valid Palindrome",
        "difficulty": "Easy",
        "order": 2,
        "description": "A phrase is a palindrome if, after converting all uppercase letters into lowercase letters and removing all non-alphanumeric characters, it reads the same forward and backward. Alphanumeric characters include letters and numbers. Given a string `s`, return `True` if it is a palindrome, or `False` otherwise.",
        "input_format": "A string `s`",
        "output_format": "Boolean (True or False)",
        "constraints": "1 <= len(s) <= 2 * 10^5",
        "examples": [
            {"input": "s = 'A man, a plan, a canal: Panama'", "output": "True", "explanation": "'amanaplanacanalpanama' is a palindrome."}
        ],
        "starter_code": {
            "python": "def is_palindrome(s):\n    # Write your solution here\n    cleaned = [c.lower() for c in s if c.isalnum()]\n    return cleaned == cleaned[::-1]\n"
        },
        "sample_test_cases": [
            {"input": "s = 'A man, a plan, a canal: Panama'", "expected_output": "True"},
            {"input": "s = 'race a car'", "expected_output": "False"}
        ],
        "hidden_test_cases": [
            {"input": "s = ' '", "expected_output": "True"},
            {"input": "s = '0P'", "expected_output": "False"}
        ]
    },
    {
        "problem_id": "cp-3",
        "slug": "reverse-string",
        "title": "Reverse String In-Place",
        "difficulty": "Easy",
        "order": 3,
        "description": "Write a function that reverses a list of characters `s` in-place with O(1) extra memory.",
        "input_format": "List of characters `s`",
        "output_format": "Reversed list `s`",
        "constraints": "1 <= len(s) <= 10^5",
        "examples": [
            {"input": "s = ['h', 'e', 'l', 'l', 'o']", "output": "['o', 'l', 'l', 'e', 'h']", "explanation": "The list is reversed in-place."}
        ],
        "starter_code": {
            "python": "def reverse_string(s):\n    # Modify s in-place and return it\n    left, right = 0, len(s) - 1\n    while left < right:\n        s[left], s[right] = s[right], s[left]\n        left += 1\n        right -= 1\n    return s\n"
        },
        "sample_test_cases": [
            {"input": "s = ['h', 'e', 'l', 'l', 'o']", "expected_output": "['o', 'l', 'l', 'e', 'h']"}
        ],
        "hidden_test_cases": [
            {"input": "s = ['H', 'a', 'n', 'n', 'a', 'h']", "expected_output": "['h', 'a', 'n', 'n', 'a', 'H']"}
        ]
    },
    {
        "problem_id": "cp-4",
        "slug": "fizz-buzz",
        "title": "FizzBuzz Generator",
        "difficulty": "Easy",
        "order": 4,
        "description": "Given an integer `n`, return a string array `answer` (1-indexed) where:\n- `answer[i] == 'FizzBuzz'` if `i` is divisible by 3 and 5.\n- `answer[i] == 'Fizz'` if `i` is divisible by 3.\n- `answer[i] == 'Buzz'` if `i` is divisible by 5.\n- `answer[i] == str(i)` if none of the above conditions are true.",
        "input_format": "An integer `n`",
        "output_format": "List of strings",
        "constraints": "1 <= n <= 10^4",
        "examples": [
            {"input": "n = 5", "output": "['1', '2', 'Fizz', '4', 'Buzz']", "explanation": "Standard FizzBuzz for 1..5"}
        ],
        "starter_code": {
            "python": "def fizz_buzz(n):\n    res = []\n    for i in range(1, n + 1):\n        if i % 15 == 0:\n            res.append('FizzBuzz')\n        elif i % 3 == 0:\n            res.append('Fizz')\n        elif i % 5 == 0:\n            res.append('Buzz')\n        else:\n            res.append(str(i))\n    return res\n"
        },
        "sample_test_cases": [
            {"input": "n = 3", "expected_output": "['1', '2', 'Fizz']"},
            {"input": "n = 5", "expected_output": "['1', '2', 'Fizz', '4', 'Buzz']"}
        ],
        "hidden_test_cases": [
            {"input": "n = 15", "expected_output": "['1', '2', 'Fizz', '4', 'Buzz', 'Fizz', '7', '8', 'Fizz', 'Buzz', '11', 'Fizz', '13', '14', 'FizzBuzz']"}
        ]
    }
]

DEFAULT_ASSESSMENT_QUESTIONS = [
    # 50 MCQs across all Python modules
    {"question_id": "aq-1", "topic": "Basics", "question": "Who created Python and in what year was it first released?", "options": ["Guido van Rossum (1991)", "Dennis Ritchie (1972)", "Bjarne Stroustrup (1985)", "James Gosling (1995)"], "correct_answer_index": 0, "explanation": "Python was conceived in the late 1980s by Guido van Rossum and first released in 1991."},
    {"question_id": "aq-2", "topic": "Syntax", "question": "How are code blocks demarcated in Python?", "options": ["Curly braces {}", "Indentation (whitespace)", "Begin and End keywords", "Parentheses ()"], "correct_answer_index": 1, "explanation": "Python uses indentation (standard 4 spaces) rather than curly braces to group code blocks."},
    {"question_id": "aq-3", "topic": "Data Types", "question": "Which of the following data types in Python is mutable?", "options": ["tuple", "str", "list", "frozenset"], "correct_answer_index": 2, "explanation": "Lists are mutable and can have elements appended, removed, or reassigned."},
    {"question_id": "aq-4", "topic": "Data Types", "question": "What is the boolean evaluation of an empty list `[]` in Python?", "options": ["True", "False", "None", "Error"], "correct_answer_index": 1, "explanation": "Empty collections (lists, tuples, dicts, sets, strings) evaluate to `False` in boolean contexts."},
    {"question_id": "aq-5", "topic": "Operators", "question": "What is the result of `7 // 2` in Python 3?", "options": ["3.5", "3", "4", "3.0"], "correct_answer_index": 1, "explanation": "The `//` operator performs floor division, truncating towards negative infinity to return an integer 3."},
    {"question_id": "aq-6", "topic": "Operators", "question": "What is the result of `2 ** 3` in Python?", "options": ["6", "8", "9", "5"], "correct_answer_index": 1, "explanation": "The `**` operator represents exponentiation ($2^3 = 8$)."},
    {"question_id": "aq-7", "topic": "Strings", "question": "What does `'hello'.upper()` return?", "options": ["'HELLO'", "'Hello'", "None", "'hello'"], "correct_answer_index": 0, "explanation": "The `.upper()` method returns a new string with all lowercase characters converted to uppercase."},
    {"question_id": "aq-8", "topic": "Strings", "question": "What is the output of `'python'[1:4]`?", "options": ["'pyt'", "'yth'", "'ytho'", "'tho'"], "correct_answer_index": 1, "explanation": "Slicing `[1:4]` takes characters at indices 1, 2, and 3: 'y', 't', 'h'."},
    {"question_id": "aq-9", "topic": "Lists", "question": "Which method removes and returns the last element of a list?", "options": ["pop()", "remove()", "discard()", "delete()"], "correct_answer_index": 0, "explanation": "`list.pop()` removes and returns the element at the given index (defaults to the last item)."},
    {"question_id": "aq-10", "topic": "Lists", "question": "What is the output of `[x * 2 for x in range(3)]`?", "options": ["[0, 2, 4]", "[2, 4, 6]", "[0, 1, 2]", "[1, 2, 3]"], "correct_answer_index": 0, "explanation": "The list comprehension multiplies 0, 1, and 2 by 2, resulting in `[0, 2, 4]`."},
    {"question_id": "aq-11", "topic": "Tuples", "question": "How do you create a single-element tuple in Python containing the number 5?", "options": ["(5)", "(5,)", "tuple(5)", "[5]"], "correct_answer_index": 1, "explanation": "A trailing comma `(5,)` is required; `(5)` is interpreted as an integer in parentheses."},
    {"question_id": "aq-12", "topic": "Sets", "question": "What is true about elements in a Python `set`?", "options": ["They maintain insertion order and allow duplicates", "They are unique and unordered/hashable", "They can be indexed like `my_set[0]`", "They are mutable inside nested sets"], "correct_answer_index": 1, "explanation": "Sets contain unique, hashable elements with no duplicate values allowed."},
    {"question_id": "aq-13", "topic": "Dictionaries", "question": "Which method retrieves a dictionary value without raising a KeyError if the key is absent?", "options": ["dict.fetch()", "dict.get()", "dict.find()", "dict.lookup()"], "correct_answer_index": 1, "explanation": "`dict.get(key, default)` returns the default value (or None) without throwing an exception."},
    {"question_id": "aq-14", "topic": "Dictionaries", "question": "What are dictionary keys required to be in Python?", "options": ["Mutable objects", "Hashable objects", "Integers only", "Strings only"], "correct_answer_index": 1, "explanation": "Dictionary keys must implement `__hash__()` and `__eq__()` (i.e. be hashable)."},
    {"question_id": "aq-15", "topic": "Control Flow", "question": "Which statement terminates the entire enclosing loop prematurely?", "options": ["continue", "break", "pass", "exit"], "correct_answer_index": 1, "explanation": "`break` terminates execution of the innermost enclosing loop immediately."},
    {"question_id": "aq-16", "topic": "Control Flow", "question": "What does the `pass` statement do?", "options": ["Skips to next iteration", "Exits the program", "Acts as a null operation / placeholder", "Raises an error"], "correct_answer_index": 2, "explanation": "`pass` is a syntactic placeholder where code is required but no action should be executed."},
    {"question_id": "aq-17", "topic": "Functions", "question": "What does a Python function return if no explicit `return` statement is executed?", "options": ["0", "False", "None", "undefined"], "correct_answer_index": 2, "explanation": "Python functions implicitly return `None` when control reaches the end without a return."},
    {"question_id": "aq-18", "topic": "Functions", "question": "What is a lambda function in Python?", "options": ["A multi-threaded function", "An anonymous inline function", "A built-in class method", "A function with no arguments"], "correct_answer_index": 1, "explanation": "`lambda` creates small, anonymous inline functions restricted to a single expression."},
    {"question_id": "aq-19", "topic": "Scope", "question": "What order does Python follow when resolving variable names?", "options": ["LEGB: Local, Enclosing, Global, Built-in", "GLBE: Global, Local, Built-in, Enclosing", "BGL: Built-in, Global, Local", "LIFO: Last in first out"], "correct_answer_index": 0, "explanation": "Python checks the Local scope first, then Enclosing functions, then Global, then Built-ins (LEGB rule)."},
    {"question_id": "aq-20", "topic": "Exceptions", "question": "Which block in a try-except structure executes only when NO exception occurs?", "options": ["finally", "else", "except", "catch"], "correct_answer_index": 1, "explanation": "The `else` block executes after `try` only if no exceptions were raised."},
    {"question_id": "aq-21", "topic": "Exceptions", "question": "Which block in a try-except structure ALWAYS executes regardless of exceptions?", "options": ["finally", "else", "except", "always"], "correct_answer_index": 0, "explanation": "The `finally` block always executes, commonly used for cleanup and closing resource handles."},
    {"question_id": "aq-22", "topic": "File I/O", "question": "What is the recommended statement to open a file and ensure it is closed automatically?", "options": ["with open(...) as f:", "try open(...) as f:", "file.auto_close()", "using f = open(...):"], "correct_answer_index": 0, "explanation": "The `with` statement utilizes context management to invoke `__enter__` and guaranteed `__exit__`."},
    {"question_id": "aq-23", "topic": "File I/O", "question": "What does the file open mode `'a'` represent?", "options": ["Read only", "Write from beginning (truncate)", "Append to end of file", "Binary read"], "correct_answer_index": 2, "explanation": "Mode `'a'` opens the file for appending, placing the write pointer at the end of the file."},
    {"question_id": "aq-24", "topic": "OOP", "question": "What is the first parameter typically passed to instance methods in Python classes?", "options": ["this", "self", "cls", "base"], "correct_answer_index": 1, "explanation": "`self` references the specific instance invoking the method."},
    {"question_id": "aq-25", "topic": "OOP", "question": "What special method functions as the constructor in Python classes?", "options": ["__construct__", "__init__", "__new__", "__start__"], "correct_answer_index": 1, "explanation": "`__init__` initializes the instance attributes after creation."},
    {"question_id": "aq-26", "topic": "OOP", "question": "How do you achieve private attribute name mangling in a Python class?", "options": ["Prefix with single underscore `_attr`", "Prefix with double underscore `__attr`", "Use the `private` keyword", "Suffix with `_private`"], "correct_answer_index": 1, "explanation": "Attributes with at least two leading underscores (and at most one trailing) are name-mangled to `_ClassName__attr`."},
    {"question_id": "aq-27", "topic": "OOP", "question": "What built-in function checks whether an object is an instance of a specific class or tuple of classes?", "options": ["typeof()", "isinstance()", "issubclass()", "hasattr()"], "correct_answer_index": 1, "explanation": "`isinstance(obj, class_or_tuple)` verifies inheritance and type relationships."},
    {"question_id": "aq-28", "topic": "OOP", "question": "What method is called when `print(obj)` or `str(obj)` is called on a custom class?", "options": ["__repr__", "__str__", "__print__", "__display__"], "correct_answer_index": 1, "explanation": "`__str__` returns an informal, user-readable string representation of the object."},
    {"question_id": "aq-29", "topic": "Modules", "question": "What is the name of the special variable that holds `'__main__'` when a script is executed directly?", "options": ["__file__", "__name__", "__doc__", "__module__"], "correct_answer_index": 1, "explanation": "`__name__` equals `'__main__'` when the script is run directly from the CLI."},
    {"question_id": "aq-30", "topic": "Modules", "question": "Which built-in module provides functions for interacting with the operating system?", "options": ["sys", "os", "math", "platform"], "correct_answer_index": 1, "explanation": "The `os` module provides OS-dependent functionality such as directory scanning and path manipulation."},
    {"question_id": "aq-31", "topic": "Algorithms", "question": "What is the time complexity of searching for an element in an unsorted list of length N?", "options": ["O(1)", "O(log N)", "O(N)", "O(N^2)"], "correct_answer_index": 2, "explanation": "Linear search inspects elements one by one from beginning to end, taking O(N) comparisons."},
    {"question_id": "aq-32", "topic": "Algorithms", "question": "What is the time complexity of binary search on a sorted list?", "options": ["O(1)", "O(log N)", "O(N)", "O(N log N)"], "correct_answer_index": 1, "explanation": "Binary search halves the search space at each step, running in O(log N) time."},
    {"question_id": "aq-33", "topic": "Built-ins", "question": "What does `zip([1, 2], ['a', 'b'])` produce when converted to a list?", "options": ["[(1, 'a'), (2, 'b')]", "[1, 'a', 2, 'b']", "[(1, 2), ('a', 'b')]", "{1: 'a', 2: 'b'}"], "correct_answer_index": 0, "explanation": "`zip()` aggregates elements from each of the iterables in parallel tuples."},
    {"question_id": "aq-34", "topic": "Built-ins", "question": "What built-in function returns an enumerate object yielding `(index, item)` pairs?", "options": ["counter()", "enumerate()", "indexer()", "range()"], "correct_answer_index": 1, "explanation": "`enumerate(iterable, start=0)` generates tuple pairs of `(index, element)`."},
    {"question_id": "aq-35", "topic": "Built-ins", "question": "What does `any([False, 0, 'Hello', None])` return?", "options": ["False", "True", "None", "Error"], "correct_answer_index": 1, "explanation": "`any()` returns `True` if at least one element is truthy. 'Hello' is non-empty and truthy."},
    {"question_id": "aq-36", "topic": "Built-ins", "question": "What does `all([True, 1, 'world'])` return?", "options": ["True", "False", "None", "Error"], "correct_answer_index": 0, "explanation": "`all()` returns `True` because every single element in the iterable is truthy."},
    {"question_id": "aq-37", "topic": "Memory", "question": "What is the primary mechanism Python uses for automatic memory reclamation?", "options": ["Mark and Sweep only", "Reference counting combined with cyclic garbage collection", "Manual free() calls", "Deterministic stack unrolling"], "correct_answer_index": 1, "explanation": "Python uses immediate reference counting, supported by a generational cyclic garbage collector."},
    {"question_id": "aq-38", "topic": "Functions", "question": "What is a decorator in Python?", "options": ["A CSS styling utility", "A function that takes another function and extends its behavior without modifying it", "A class destructor", "A package manager"], "correct_answer_index": 1, "explanation": "Decorators use the `@decorator` syntax to wrap and augment functions dynamically."},
    {"question_id": "aq-39", "topic": "Data Types", "question": "What is the result of `type(None)`?", "options": ["<class 'None'>", "<class 'NoneType'>", "<class 'null'>", "<class 'void'>"], "correct_answer_index": 1, "explanation": "`None` is the singleton instance of `<class 'NoneType'>`."},
    {"question_id": "aq-40", "topic": "Strings", "question": "What does `'   hello   '.strip()` return?", "options": ["'hello'", "'   hello'", "'hello   '", "'h e l l o'"], "correct_answer_index": 0, "explanation": "`.strip()` removes leading and trailing whitespace characters."},
    {"question_id": "aq-41", "topic": "Lists", "question": "What is the result of `[1, 2] + [3, 4]`?", "options": ["[4, 6]", "[1, 2, 3, 4]", "[[1, 2], [3, 4]]", "Error"], "correct_answer_index": 1, "explanation": "The `+` operator on lists concatenates them into a single new list."},
    {"question_id": "aq-42", "topic": "Data Structures", "question": "Which collection type is ideal for Fast First-In-First-Out (FIFO) queue operations?", "options": ["list", "collections.deque", "set", "dict"], "correct_answer_index": 1, "explanation": "`collections.deque` provides O(1) pops and appends from both ends, whereas `list.pop(0)` is O(N)."},
    {"question_id": "aq-43", "topic": "OOP", "question": "What is Method Resolution Order (MRO) in Python?", "options": ["The compilation order of methods in a file", "The order in which Python searches classes in multiple inheritance hierarchies", "The execution order of constructors", "The alphabetical sorting of functions"], "correct_answer_index": 1, "explanation": "MRO (computed via C3 Linearization) dictates the attribute lookup order across base classes."},
    {"question_id": "aq-44", "topic": "Built-ins", "question": "What does `map(func, iterable)` return in Python 3?", "options": ["A new list", "An iterator yielding transformed values", "A tuple", "None"], "correct_answer_index": 1, "explanation": "`map()` returns an iterator (generator-like) that applies the function lazily on request."},
    {"question_id": "aq-45", "topic": "Built-ins", "question": "What does `filter(func, iterable)` do?", "options": ["Sorts the iterable", "Constructs an iterator from elements for which `func` returns True", "Removes duplicate values", "Finds the maximum value"], "correct_answer_index": 1, "explanation": "`filter()` filters elements from an iterable based on a boolean predicate function."},
    {"question_id": "aq-46", "topic": "Formatting", "question": "Which string formatting syntax was introduced in Python 3.6 for direct expression interpolation?", "options": ["% formatting", "str.format()", "f-strings (Formatted string literals)", "template strings"], "correct_answer_index": 2, "explanation": "f-strings (`f'{expression}'`) offer fast, clean, and readable inline interpolation."},
    {"question_id": "aq-47", "topic": "Advanced", "question": "What is a generator function in Python?", "options": ["A function that creates instances of classes", "A function that uses `yield` to return an iterator producing a stream of values lazily", "A function that generates random numbers", "A C++ compiler wrapper"], "correct_answer_index": 1, "explanation": "Generator functions use `yield` to produce values one by one on-demand, saving memory."},
    {"question_id": "aq-48", "topic": "Exceptions", "question": "Which exception is raised when trying to access a dictionary key that does not exist?", "options": ["IndexError", "KeyError", "ValueError", "AttributeError"], "correct_answer_index": 1, "explanation": "Direct indexing `dict[missing_key]` raises a `KeyError`."},
    {"question_id": "aq-49", "topic": "Exceptions", "question": "Which exception is raised when trying to access an index beyond a list's length?", "options": ["KeyError", "IndexError", "OverflowError", "RangeError"], "correct_answer_index": 1, "explanation": "`list[999]` raises an `IndexError: list index out of range`."},
    {"question_id": "aq-50", "topic": "Best Practices", "question": "What is PEP 8 in the Python ecosystem?", "options": ["The official Python packaging protocol", "The official Style Guide for Python Code", "The Python Security Vulnerability database", "The Python virtual environment spec"], "correct_answer_index": 1, "explanation": "PEP 8 is the official Style Guide for Python Code, detailing conventions for indentation, naming, and structure."}
]

DEFAULT_PRACTICAL_ASSIGNMENT = {
    "assignment_id": "asg-python-habit-tracker",
    "challenge_id": "python-28-day-challenge",
    "title": "Final Practical Capstone: Task & Habit Tracker CLI",
    "description": """Design, implement, and document a full-featured Command-Line Interface (CLI) application in Python that helps university students manage daily study tasks and habits.

### Core Deliverables:
1. **Task & Habit Management**: Add, view, complete, update, and delete tasks/habits with priority levels and categories (e.g. Study, Exercise, Coding, Reading).
2. **Persistence**: Store all tasks and streak history in a local file (`tasks.json` or SQLite) so state is preserved between program runs.
3. **Streak Calculation**: Automatically calculate and display current streak days and longest streak.
4. **OOP Architecture**: Organize your project into clean, modular classes (e.g. `Task`, `Habit`, `TrackerManager`, `StorageHandler`).
5. **Robust Error Handling**: Handle invalid user input, missing files, or corrupted JSON gracefully without crashing.
6. **Documentation & Video Demo**: A comprehensive `README.md` with usage examples and setup instructions, hosted on a public GitHub repository.""",
    "requirements": [
        "Repository must be publicly accessible on GitHub with a clean commit history.",
        "Code must adhere to PEP 8 standards with descriptive variable and method names.",
        "All data must persist across restarts using JSON or SQLite.",
        "Must include at least 4 classes implementing Object-Oriented principles.",
        "Provide clear instructions and a 1-minute video demo or screenshot proofs in the README."
    ],
    "rubric": [
        {"criterion": "Architecture & Code Quality", "max_points": 25, "desc": "Clean OOP separation, modular functions, PEP 8 styling, type hints."},
        {"criterion": "Functionality & Persistence", "max_points": 35, "desc": "All CRUD features, streak math, and robust file storage work without crashing."},
        {"criterion": "Error Handling & Edge Cases", "max_points": 20, "desc": "Handles corrupted files, invalid menu choices, and empty inputs gracefully."},
        {"criterion": "Documentation & Demo Proof", "max_points": 20, "desc": "Clear README with install steps, screenshots or video demo of working CLI."}
    ],
    "passing_score": 70
}


def ensure_default_monthly_challenge():
    """
    Seeds the inaugural Monthly Challenge into MongoDB.
    Safely upserts to preserve existing student enrollment and payment records.
    """
    try:
        # 1. Challenge Document
        challenge = MonthlyChallenge(DEFAULT_PYTHON_CHALLENGE)
        challenge.save()

        # 2. Practice Questions
        for q_data in DEFAULT_PRACTICE_QUESTIONS:
            q_data["challenge_id"] = challenge.challenge_id
            pq = PracticeQuestion(q_data)
            pq.save()

        # 3. Interview Questions
        for i_data in DEFAULT_INTERVIEW_QUESTIONS:
            i_data["challenge_id"] = challenge.challenge_id
            iq = InterviewQuestion(i_data)
            iq.save()

        # 4. Coding Problems
        for cp_data in DEFAULT_CODING_PROBLEMS:
            cp_data["challenge_id"] = challenge.challenge_id
            cp = CodingProblem(cp_data)
            cp.save()

        # 5. Assessment Questions (Exactly 50 MCQs)
        for aq_data in DEFAULT_ASSESSMENT_QUESTIONS:
            aq_data["challenge_id"] = challenge.challenge_id
            aq = AssessmentQuestion(aq_data)
            aq.save()

        # 6. Practical Assignment
        asg = PracticalAssignment(DEFAULT_PRACTICAL_ASSIGNMENT)
        asg.save()

        logger.info(f"[MONTHLY CHALLENGE] Seeded / verified active challenge: {challenge.title} with 50 MCQs & 6 modules.")
        return True
    except Exception as e:
        logger.error(f"[MONTHLY CHALLENGE SEED ERROR] {e}")
        return False
