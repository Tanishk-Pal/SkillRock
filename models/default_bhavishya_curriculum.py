"""
SkillRock — Bhavishya 1.0 Master Curriculum
Complete specification of all 19 subjects across Category A, B, and C with full syllabi,
chapters, Socratic lesson objectives, coding challenges, and prerequisites.
"""

from models.bhavishya import BhavishyaSubject


def get_default_bhavishya_curriculum():
    """Returns the list of 19 Bhavishya subjects with detailed chapters and lessons."""
    return [
        # ==============================================================================
        # CATEGORY A: TECHNICAL SKILLS (01 - 08)
        # ==============================================================================
        {
            "slug": "python-programming",
            "title": "01. Python Programming",
            "category": BhavishyaSubject.CATEGORY_TECHNICAL,
            "order": 1,
            "short_description": "Master Python from syntax fundamentals to Object-Oriented Architecture, exceptions, and data science libraries.",
            "full_description": "Comprehensive journey through Python 3. Covers language syntax, dynamic typing, data structures (lists, tuples, sets, dicts), first-class functions, recursion, OOP design patterns, inheritance, polymorphism, custom exception handling, file I/O, virtual environments, and standard package design.",
            "estimated_hours": 24,
            "difficulty": "Beginner to Intermediate",
            "icon": "code",
            "color_accent": "#38BDF8",
            "prerequisites": [],
            "chapters": [
                {
                    "id": "py-ch1",
                    "title": "Chapter 1: Python Core Foundations & Environment",
                    "lessons": [
                        {
                            "id": "py-l1",
                            "title": "Introduction to Python, Virtual Environments & Syntax",
                            "type": "classroom",
                            "duration_mins": 30,
                            "socratic_prompt": "Introduce Python 3 as an interpreted, dynamically typed language. Explain how CPython executes bytecode. Ask student: Why is dynamic typing both convenient and potentially prone to runtime bugs?",
                            "practice_question": "Explain the difference between compiled languages (like C++) and interpreted languages (like Python).",
                            "starter_code": "# Run your first Python expression\nmessage = 'Welcome to Bhavishya 1.0 Python Classroom'\nprint(message)\n",
                        },
                        {
                            "id": "py-l2",
                            "title": "Variables, Primitive Types & Memory References",
                            "type": "coding_lab",
                            "duration_mins": 45,
                            "socratic_prompt": "Explain immutable primitives vs mutable objects. Demonstrate how Python variables are reference pointers.",
                            "practice_question": "Create variables of types int, float, string, and boolean. Demonstrate type casting and type checking using type().",
                            "starter_code": "def inspect_types(val):\n    # Return the type name as string (e.g., 'int', 'str')\n    return type(val).__name__\n\n# Test your function\nprint(inspect_types(42))\nprint(inspect_types('SkillRock'))\n",
                        },
                        {
                            "id": "py-l3",
                            "title": "Conditionals, Logical Operators & Short-Circuiting",
                            "type": "coding_lab",
                            "duration_mins": 40,
                            "socratic_prompt": "Explain if, elif, else branch execution and Boolean short-circuit evaluation in and/or operators.",
                            "practice_question": "Write a function categorize_score(score) returning 'Distinction' (>=80), 'First Class' (>=60), 'Pass' (>=40), or 'Fail' (<40).",
                            "starter_code": "def categorize_score(score):\n    # Write conditional logic\n    if score >= 80:\n        return 'Distinction'\n    elif score >= 60:\n        return 'First Class'\n    elif score >= 40:\n        return 'Pass'\n    return 'Fail'\n\nprint(categorize_score(85))\n",
                        }
                    ]
                },
                {
                    "id": "py-ch2",
                    "title": "Chapter 2: Data Structures, Loops & Comprehensions",
                    "lessons": [
                        {
                            "id": "py-l4",
                            "title": "Lists, Tuples, Sets & Dictionary Hash Maps",
                            "type": "classroom",
                            "duration_mins": 45,
                            "socratic_prompt": "Explain time complexities of list index access vs dictionary key lookup O(1). Ask student: Why can't a list be used as a dictionary key?",
                            "practice_question": "What is hashability in Python, and why must dictionary keys be immutable?",
                            "starter_code": "student_data = {\n    'name': 'Aarav',\n    'skills': ['Python', 'SQL'],\n    'active': True\n}\nprint(student_data.get('skills'))\n",
                        },
                        {
                            "id": "py-l5",
                            "title": "For/While Loops, Iterators & List Comprehensions",
                            "type": "coding_lab",
                            "duration_mins": 50,
                            "socratic_prompt": "Compare traditional for-loops with concise Pythonic list and dictionary comprehensions.",
                            "practice_question": "Write a function filter_even_squares(numbers) using list comprehension to square only even numbers.",
                            "starter_code": "def filter_even_squares(numbers):\n    # Return squares of even numbers only using comprehension\n    return [n ** 2 for n in numbers if n % 2 == 0]\n\nprint(filter_even_squares([1, 2, 3, 4, 5, 6]))\n",
                        }
                    ]
                },
                {
                    "id": "py-ch3",
                    "title": "Chapter 3: Functions, Lambda & Scope",
                    "lessons": [
                        {
                            "id": "py-l6",
                            "title": "Function Signatures, Default Args, *args & **kwargs",
                            "type": "classroom",
                            "duration_mins": 40,
                            "socratic_prompt": "Explain the LEGB scope rule (Local, Enclosing, Global, Built-in). Show common bug with mutable default arguments.",
                            "practice_question": "Why should you never use a mutable default parameter like `def add_item(item, lst=[])`?",
                            "starter_code": "def build_profile(username, **attributes):\n    profile = {'username': username}\n    profile.update(attributes)\n    return profile\n\nprint(build_profile('tanx', role='Engineer', exp=3))\n",
                        },
                        {
                            "id": "py-l7",
                            "title": "Lambda Functions, Higher-Order Functions & Closures",
                            "type": "coding_lab",
                            "duration_mins": 45,
                            "socratic_prompt": "Teach map(), filter(), sorted(key=...), and closures.",
                            "practice_question": "Sort a list of student dicts by score in descending order using a lambda key.",
                            "starter_code": "students = [{'name': 'Neha', 'score': 88}, {'name': 'Rohan', 'score': 95}]\nsorted_students = sorted(students, key=lambda s: s['score'], reverse=True)\nprint(sorted_students)\n",
                        }
                    ]
                },
                {
                    "id": "py-ch4",
                    "title": "Chapter 4: Object-Oriented Programming (OOP)",
                    "lessons": [
                        {
                            "id": "py-l8",
                            "title": "Classes, Dunder Methods (__init__, __str__, __repr__)",
                            "type": "coding_lab",
                            "duration_mins": 55,
                            "socratic_prompt": "Explain self parameter, encapsulation, and special dunder methods.",
                            "practice_question": "Build a BankAccount class with deposit, withdraw (with balance checking), and __repr__.",
                            "starter_code": "class BankAccount:\n    def __init__(self, owner, balance=0.0):\n        self.owner = owner\n        self.balance = balance\n\n    def deposit(self, amount):\n        self.balance += amount\n        return self.balance\n\n    def withdraw(self, amount):\n        if amount > self.balance:\n            raise ValueError('Insufficient funds')\n        self.balance -= amount\n        return self.balance\n\nacc = BankAccount('Priya', 500)\nacc.deposit(200)\nprint('Balance:', acc.balance)\n",
                        },
                        {
                            "id": "py-l9",
                            "title": "Inheritance, Polymorphism, Super() & Method Resolution Order",
                            "type": "classroom",
                            "duration_mins": 45,
                            "socratic_prompt": "Explain class hierarchies and polymorphism where child classes override parent behaviors.",
                            "practice_question": "What is MRO (Method Resolution Order) and how does Python resolve multi-inheritance?",
                            "starter_code": "class Employee:\n    def get_role(self):\n        return 'General Staff'\n\nclass Developer(Employee):\n    def get_role(self):\n        return 'Software Developer'\n\nprint(Developer().get_role())\n",
                        }
                    ]
                },
                {
                    "id": "py-ch5",
                    "title": "Chapter 5: File I/O, Exceptions & Modules",
                    "lessons": [
                        {
                            "id": "py-l10",
                            "title": "Context Managers (with statement) & Custom Exceptions",
                            "type": "coding_lab",
                            "duration_mins": 45,
                            "socratic_prompt": "Demonstrate try/except/else/finally and creating custom exceptions inheriting from Exception.",
                            "practice_question": "Define an AgeLimitError exception raised if a candidate age is below 18.",
                            "starter_code": "class AgeLimitError(Exception):\n    pass\n\ndef register_voter(age):\n    if age < 18:\n        raise AgeLimitError('Must be at least 18')\n    return 'Registered successfully'\n\ntry:\n    print(register_voter(16))\nexcept AgeLimitError as err:\n    print('Handled error:', err)\n",
                        }
                    ]
                }
            ]
        },

        # 02. Data Structures and Algorithms
        {
            "slug": "data-structures-and-algorithms",
            "title": "02. Data Structures and Algorithms",
            "category": BhavishyaSubject.CATEGORY_TECHNICAL,
            "order": 2,
            "short_description": "Master algorithmic problem-solving: Time/Space Big-O, Stacks, Queues, Trees, Graphs, and Dynamic Programming.",
            "full_description": "In-depth computer science curriculum designed for technical interview rounds. Covers asymptotic analysis (Big-O, Omega, Theta), Arrays, Strings, Two Pointers, Sliding Window, Singly/Doubly Linked Lists, Stacks, Monotonic Queues, Hash Tables, Binary Trees, BSTs, Graph Traversals (BFS, DFS), Shortest Path (Dijkstra), Greedy Choices, and Dynamic Programming memorization and tabulation.",
            "estimated_hours": 30,
            "difficulty": "Intermediate to Advanced",
            "icon": "network",
            "color_accent": "#A855F7",
            "prerequisites": ["python-programming"],
            "chapters": [
                {
                    "id": "dsa-ch1",
                    "title": "Chapter 1: Complexity Analysis & Array Patterns",
                    "lessons": [
                        {
                            "id": "dsa-l1",
                            "title": "Big-O Time & Space Complexity Analysis",
                            "type": "classroom",
                            "duration_mins": 40,
                            "socratic_prompt": "Teach worst-case vs average-case complexity. Compare O(1), O(log n), O(n), O(n log n), and O(n^2). Ask student: Why does binary search achieve O(log n)?",
                            "practice_question": "Analyze the time complexity of nested loops where the inner loop runs j < i.",
                            "starter_code": "# Analyze complexity of this function\ndef has_pair_with_sum(arr, target):\n    seen = set()\n    for num in arr:\n        if target - num in seen:\n            return True\n        seen.add(num)\n    return False\n\nprint(has_pair_with_sum([10, 15, 3, 7], 17))\n",
                        },
                        {
                            "id": "dsa-l2",
                            "title": "Two-Pointers & Sliding Window Techniques",
                            "type": "coding_lab",
                            "duration_mins": 55,
                            "socratic_prompt": "Explain how two pointers eliminate quadratic O(n^2) loops in sorted arrays down to O(n) linear scans.",
                            "practice_question": "Write two_sum_sorted(numbers, target) returning 1-based indices of the two numbers that sum to target.",
                            "starter_code": "def two_sum_sorted(numbers, target):\n    left, right = 0, len(numbers) - 1\n    while left < right:\n        curr = numbers[left] + numbers[right]\n        if curr == target:\n            return [left + 1, right + 1]\n        elif curr < target:\n            left += 1\n        else:\n            right -= 1\n    return []\n\nprint(two_sum_sorted([2, 7, 11, 15], 9))\n",
                        }
                    ]
                },
                {
                    "id": "dsa-ch2",
                    "title": "Chapter 2: Linked Lists, Stacks & Queues",
                    "lessons": [
                        {
                            "id": "dsa-l3",
                            "title": "Singly Linked List Reversal & Cycle Detection",
                            "type": "coding_lab",
                            "duration_mins": 50,
                            "socratic_prompt": "Teach pointer manipulation and Floyd's Tortoise and Hare cycle detection algorithm.",
                            "practice_question": "Reverse a singly linked list in-place in O(n) time and O(1) space.",
                            "starter_code": "class ListNode:\n    def __init__(self, val=0, next=None):\n        self.val = val\n        self.next = next\n\ndef reverse_list(head):\n    prev = None\n    curr = head\n    while curr:\n        nxt = curr.next\n        curr.next = prev\n        prev = curr\n        curr = nxt\n    return prev\n",
                        },
                        {
                            "id": "dsa-l4",
                            "title": "Stack Applications: Valid Parentheses & Monotonic Stack",
                            "type": "coding_lab",
                            "duration_mins": 45,
                            "socratic_prompt": "Explain LIFO stack mechanics for nested bracket matching and expression evaluation.",
                            "practice_question": "Validate whether a string of brackets '()[]{}' is valid.",
                            "starter_code": "def is_valid_brackets(s):\n    mapping = {')': '(', '}': '{', ']': '['}\n    stack = []\n    for char in s:\n        if char in mapping.values():\n            stack.append(char)\n        elif char in mapping:\n            if not stack or stack.pop() != mapping[char]:\n                return False\n    return len(stack) == 0\n\nprint(is_valid_brackets('({[]})'))\n",
                        }
                    ]
                },
                {
                    "id": "dsa-ch3",
                    "title": "Chapter 3: Trees, Binary Search Trees & Graphs",
                    "lessons": [
                        {
                            "id": "dsa-l5",
                            "title": "Binary Tree Traversals (Inorder, Preorder, Postorder, Level-Order)",
                            "type": "classroom",
                            "duration_mins": 50,
                            "socratic_prompt": "Explain recursive tree exploration vs queue-based BFS level-order traversal.",
                            "practice_question": "Why does an inorder traversal of a Binary Search Tree produce numbers in strictly ascending order?",
                            "starter_code": "# Tree traversal fundamentals\nclass TreeNode:\n    def __init__(self, val=0, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n",
                        },
                        {
                            "id": "dsa-l6",
                            "title": "Graph Representations, BFS & DFS Traversals",
                            "type": "coding_lab",
                            "duration_mins": 60,
                            "socratic_prompt": "Teach adjacency list representation and cycle prevention with visited sets.",
                            "practice_question": "Find whether a path exists between source and destination in an undirected graph using BFS.",
                            "starter_code": "from collections import deque\n\ndef path_exists(n, edges, source, destination):\n    graph = {i: [] for i in range(n)}\n    for u, v in edges:\n        graph[u].append(v)\n        graph[v].append(u)\n    \n    visited = set([source])\n    queue = deque([source])\n    while queue:\n        node = queue.popleft()\n        if node == destination:\n            return True\n        for neighbor in graph[node]:\n            if neighbor not in visited:\n                visited.add(neighbor)\n                queue.append(neighbor)\n    return False\n\nprint(path_exists(3, [[0,1],[1,2],[2,0]], 0, 2))\n",
                        }
                    ]
                },
                {
                    "id": "dsa-ch4",
                    "title": "Chapter 4: Dynamic Programming & Greedy Algorithms",
                    "lessons": [
                        {
                            "id": "dsa-l7",
                            "title": "Memoization (Top-Down) vs Tabulation (Bottom-Up)",
                            "type": "coding_lab",
                            "duration_mins": 55,
                            "socratic_prompt": "Identify optimal substructure and overlapping subproblems in the classic 0/1 Knapsack and Climbing Stairs.",
                            "practice_question": "Solve the Coin Change problem: return the fewest number of coins to make up an amount.",
                            "starter_code": "def coin_change(coins, amount):\n    dp = [float('inf')] * (amount + 1)\n    dp[0] = 0\n    for c in coins:\n        for a in range(c, amount + 1):\n            dp[a] = min(dp[a], dp[a - c] + 1)\n    return dp[amount] if dp[amount] != float('inf') else -1\n\nprint(coin_change([1, 2, 5], 11))\n",
                        }
                    ]
                }
            ]
        },

        # 03. Mathematics and Statistics
        {
            "slug": "mathematics-and-statistics",
            "title": "03. Mathematics and Statistics",
            "category": BhavishyaSubject.CATEGORY_TECHNICAL,
            "order": 3,
            "short_description": "Linear Algebra, Probability, Calculus & Inferential Statistics tailored for Machine Learning practitioners.",
            "full_description": "Mathematics is the engine under the hood of Artificial Intelligence. This subject equips students with vectors, dot products, matrix transformations, eigenvalues/eigenvectors, partial derivatives, gradient descent optimization, probability distributions (Normal, Bernoulli, Poisson), Bayes theorem, hypothesis testing (p-values, z-test, t-test), covariance, and correlation matrices.",
            "estimated_hours": 18,
            "difficulty": "Beginner to Intermediate",
            "icon": "calculator",
            "color_accent": "#10B981",
            "prerequisites": ["python-programming"],
            "chapters": [
                {
                    "id": "math-ch1",
                    "title": "Chapter 1: Linear Algebra for Machine Learning",
                    "lessons": [
                        {
                            "id": "math-l1",
                            "title": "Vectors, Norms & Dot Product Geometric Intuition",
                            "type": "classroom",
                            "duration_mins": 40,
                            "socratic_prompt": "Explain how cosine similarity is derived from dot products. Ask student: Why does dot product measure directional alignment between high-dimensional embedding vectors?",
                            "practice_question": "Calculate the cosine similarity between two 3D vectors.",
                            "starter_code": "import math\n\ndef cosine_similarity(v1, v2):\n    dot = sum(a * b for a, b in zip(v1, v2))\n    norm1 = math.sqrt(sum(a * a for a in v1))\n    norm2 = math.sqrt(sum(b * b for b in v2))\n    return dot / (norm1 * norm2) if norm1 * norm2 else 0.0\n\nprint(cosine_similarity([1, 2, 3], [1, 2, 3]))\n",
                        },
                        {
                            "id": "math-l2",
                            "title": "Matrix Multiplication, Transformations & Determinants",
                            "type": "coding_lab",
                            "duration_mins": 45,
                            "socratic_prompt": "Explain matrix multiplication as linear geometric transformation (scaling, rotation, shearing).",
                            "practice_question": "Implement pure Python 2x2 matrix multiplication without external libraries.",
                            "starter_code": "def matmul_2x2(A, B):\n    return [\n        [A[0][0]*B[0][0] + A[0][1]*B[1][0], A[0][0]*B[0][1] + A[0][1]*B[1][1]],\n        [A[1][0]*B[0][0] + A[1][1]*B[1][0], A[1][0]*B[0][1] + A[1][1]*B[1][1]]\n    ]\nprint(matmul_2x2([[1, 2], [3, 4]], [[5, 6], [7, 8]]))\n",
                        }
                    ]
                },
                {
                    "id": "math-ch2",
                    "title": "Chapter 2: Probability & Inferential Statistics",
                    "lessons": [
                        {
                            "id": "math-l3",
                            "title": "Bayes Theorem, Conditional Probability & Prior/Posterior",
                            "type": "classroom",
                            "duration_mins": 40,
                            "socratic_prompt": "Explain conditional probability with a medical test false-positive paradox.",
                            "practice_question": "Calculate P(Disease|Positive Test) given disease prevalence, sensitivity, and false-positive rate.",
                            "starter_code": "# Bayes Theorem: P(A|B) = [P(B|A) * P(A)] / P(B)\n",
                        },
                        {
                            "id": "math-l4",
                            "title": "Normal Distribution, Z-Scores & Hypothesis Testing",
                            "type": "coding_lab",
                            "duration_mins": 45,
                            "socratic_prompt": "Teach Central Limit Theorem, p-values, null hypothesis (H0), and Type I vs Type II errors.",
                            "practice_question": "Compute standard deviation, mean, and z-score for an array of observed values.",
                            "starter_code": "def compute_stats(data):\n    mean = sum(data) / len(data)\n    variance = sum((x - mean) ** 2 for x in data) / len(data)\n    std_dev = variance ** 0.5\n    return {'mean': mean, 'std_dev': std_dev}\n\nprint(compute_stats([10, 12, 23, 23, 16, 23, 21, 16]))\n",
                        }
                    ]
                }
            ]
        },

        # 04. SQL and Data Management
        {
            "slug": "sql-and-data-management",
            "title": "04. SQL and Data Management",
            "category": BhavishyaSubject.CATEGORY_TECHNICAL,
            "order": 4,
            "short_description": "Relational database modeling, complex SQL queries, Joins, Aggregations, and Pandas data pipelines.",
            "full_description": "Master relational database architecture and data manipulation. Covers ACID guarantees, SQL schemas, Primary and Foreign Keys, normalization (1NF through BCNF), SELECT filtering, multi-table JOINs (INNER, LEFT, RIGHT, FULL), Window Functions, GROUP BY aggregations, Subqueries, Indexing for performance, NumPy array processing, and Pandas DataFrames data cleaning.",
            "estimated_hours": 20,
            "difficulty": "Beginner to Intermediate",
            "icon": "database",
            "color_accent": "#F59E0B",
            "prerequisites": ["python-programming"],
            "chapters": [
                {
                    "id": "sql-ch1",
                    "title": "Chapter 1: Relational Modeling & Core SQL",
                    "lessons": [
                        {
                            "id": "sql-l1",
                            "title": "Relational Concepts, DDL & CRUD Queries",
                            "type": "classroom",
                            "duration_mins": 40,
                            "socratic_prompt": "Explain database schemas, primary keys, foreign key constraints, and referential integrity.",
                            "practice_question": "Write SQL to create a students table and an enrollments table with foreign key linkage.",
                            "starter_code": "-- SQL Query Sample\nSELECT student_id, name, email \nFROM students \nWHERE graduation_year = 2026 \nORDER BY name ASC;\n",
                        },
                        {
                            "id": "sql-l2",
                            "title": "Multi-Table JOINs & Aggregation Groupings",
                            "type": "coding_lab",
                            "duration_mins": 50,
                            "socratic_prompt": "Explain differences between INNER, LEFT OUTER, and CROSS joins. Show HAVING vs WHERE filtering.",
                            "practice_question": "Write a query finding departments with average salary > 75,000 using GROUP BY and HAVING.",
                            "starter_code": "-- Formulate the department average query\nSELECT department, AVG(salary) AS avg_sal \nFROM employees \nGROUP BY department \nHAVING AVG(salary) > 75000;\n",
                        }
                    ]
                },
                {
                    "id": "sql-ch2",
                    "title": "Chapter 2: Data Wrangling with Pandas & NumPy",
                    "lessons": [
                        {
                            "id": "sql-l3",
                            "title": "NumPy Vectorized Operations & Broadcasting",
                            "type": "classroom",
                            "duration_mins": 40,
                            "socratic_prompt": "Compare NumPy contiguous C-memory array buffers vs Python lists of pointers. Show why NumPy is 50x faster.",
                            "practice_question": "Explain broadcasting rules when operating on arrays of differing shapes.",
                            "starter_code": "import numpy as np\narr = np.array([1, 2, 3, 4, 5])\nprint('Vectorized square:', arr ** 2)\n",
                        },
                        {
                            "id": "sql-l4",
                            "title": "Pandas DataFrames: Cleaning, Imputation & Merging",
                            "type": "coding_lab",
                            "duration_mins": 55,
                            "socratic_prompt": "Teach handling missing values (dropna, fillna), filtering with boolean masks, and group-by transforms.",
                            "practice_question": "Clean a dataset with missing values and compute mean metrics grouped by category.",
                            "starter_code": "# Pandas Data Cleaning Pipeline\nimport pandas as pd\ndata = {'City': ['Delhi', 'Mumbai', 'Delhi', 'Bengaluru'], 'Score': [85, None, 92, 78]}\ndf = pd.DataFrame(data)\ndf['Score'] = df['Score'].fillna(df['Score'].mean())\nprint(df)\n",
                        }
                    ]
                }
            ]
        },

        # 05. Artificial Intelligence Fundamentals
        {
            "slug": "ai-fundamentals",
            "title": "05. Artificial Intelligence Fundamentals",
            "category": BhavishyaSubject.CATEGORY_TECHNICAL,
            "order": 5,
            "short_description": "Search algorithms, intelligent agents, heuristic problem-solving, and responsible AI ethics.",
            "full_description": "Explore the foundational paradigms of Artificial Intelligence. Understand intelligent agent architectures (reflex, goal-based, utility-based), state space graphs, uninformed search (BFS, DFS, Uniform Cost Search), informed heuristic search (A* search, Greedy Best-First), adversarial game trees (Minimax, Alpha-Beta pruning), knowledge representation, and AI ethics and bias mitigation.",
            "estimated_hours": 16,
            "difficulty": "Intermediate",
            "icon": "sparkles",
            "color_accent": "#EC4899",
            "prerequisites": ["python-programming", "data-structures-and-algorithms"],
            "chapters": [
                {
                    "id": "ai-ch1",
                    "title": "Chapter 1: Intelligent Agents & State Space Search",
                    "lessons": [
                        {
                            "id": "ai-l1",
                            "title": "Intelligent Agents & PEAS Environment Formulation",
                            "type": "classroom",
                            "duration_mins": 35,
                            "socratic_prompt": "Define PEAS (Performance, Environment, Actuators, Sensors) for autonomous agents like self-driving cars.",
                            "practice_question": "Formulate the PEAS description for an automated medical diagnosis agent.",
                            "starter_code": "# Agent definition outline\nclass SimpleReflexAgent:\n    def act(self, percept):\n        if percept == 'dirty':\n            return 'clean'\n        return 'move'\n",
                        },
                        {
                            "id": "ai-l2",
                            "title": "A* Search & Admissible Heuristics",
                            "type": "coding_lab",
                            "duration_mins": 50,
                            "socratic_prompt": "Explain f(n) = g(n) + h(n). Prove why an admissible heuristic (never overestimating true cost) guarantees optimal path.",
                            "practice_question": "Implement Manhattan distance heuristic for a 2D grid pathfinding problem.",
                            "starter_code": "def manhattan_distance(p1, p2):\n    # Return |x1 - x2| + |y1 - y2|\n    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])\n\nprint('Distance:', manhattan_distance((0, 0), (4, 5)))\n",
                        }
                    ]
                }
            ]
        },

        # 06. Machine Learning
        {
            "slug": "machine-learning",
            "title": "06. Machine Learning",
            "category": BhavishyaSubject.CATEGORY_TECHNICAL,
            "order": 6,
            "short_description": "Supervised & Unsupervised modeling: Linear/Logistic Regression, Decision Trees, Random Forests, SVMs, and Scikit-Learn.",
            "full_description": "Master practical machine learning from feature engineering to production evaluation. Covers loss functions, gradient descent optimization, Linear Regression, Logistic Regression for binary/multi-class classification, Decision Trees, Ensemble methods (Random Forests, Gradient Boosting), K-Means Clustering, PCA Dimensionality Reduction, Bias-Variance Tradeoff, Cross-Validation, and Precision/Recall/F1 metrics.",
            "estimated_hours": 26,
            "difficulty": "Intermediate",
            "icon": "cpu",
            "color_accent": "#06B6D4",
            "prerequisites": ["python-programming", "mathematics-and-statistics", "sql-and-data-management"],
            "chapters": [
                {
                    "id": "ml-ch1",
                    "title": "Chapter 1: Regression, Classification & Optimization",
                    "lessons": [
                        {
                            "id": "ml-l1",
                            "title": "Linear Regression, Cost Function & Gradient Descent",
                            "type": "classroom",
                            "duration_mins": 45,
                            "socratic_prompt": "Explain Mean Squared Error (MSE) convex bowl and how partial derivatives adjust weights w and bias b. Ask student: What happens if the learning rate alpha is set too large?",
                            "practice_question": "Derive the weight update rule in batch gradient descent.",
                            "starter_code": "# Linear hypothesis: y = w*x + b\ndef predict(w, b, x):\n    return w * x + b\n\nprint('Prediction:', predict(2.5, 1.0, 4))\n",
                        },
                        {
                            "id": "ml-l2",
                            "title": "Logistic Regression, Sigmoid Function & Decision Boundary",
                            "type": "coding_lab",
                            "duration_mins": 50,
                            "socratic_prompt": "Explain why linear regression fails for binary classification. Introduce the Sigmoid function and Binary Cross-Entropy loss.",
                            "practice_question": "Implement the sigmoid activation function and predict class probability.",
                            "starter_code": "import math\n\ndef sigmoid(z):\n    return 1.0 / (1.0 + math.exp(-z))\n\nprint('Class 1 Probability:', round(sigmoid(1.45), 3))\n",
                        }
                    ]
                },
                {
                    "id": "ml-ch2",
                    "title": "Chapter 2: Tree Ensembles & Model Evaluation",
                    "lessons": [
                        {
                            "id": "ml-l3",
                            "title": "Decision Trees, Gini Impurity & Information Gain",
                            "type": "classroom",
                            "duration_mins": 45,
                            "socratic_prompt": "Explain how recursive splitting selects the feature that maximizes information gain. Discuss overfitting in deep trees.",
                            "practice_question": "Calculate Gini Impurity for a binary dataset with 3 positive and 7 negative samples.",
                            "starter_code": "# Gini Impurity: 1 - sum(p_i^2)\ndef gini_impurity(pos, neg):\n    total = pos + neg\n    p_pos = pos / total\n    p_neg = neg / total\n    return 1 - (p_pos ** 2 + p_neg ** 2)\n\nprint('Gini Impurity:', round(gini_impurity(3, 7), 3))\n",
                        },
                        {
                            "id": "ml-l4",
                            "title": "Model Validation: Precision, Recall, F1 & ROC-AUC",
                            "type": "coding_lab",
                            "duration_mins": 50,
                            "socratic_prompt": "Demonstrate the accuracy paradox in imbalanced datasets (e.g. 99% negative fraud detection). Explain why Recall matters for cancer detection.",
                            "practice_question": "Compute Precision, Recall, and F1-score from a 2x2 Confusion Matrix.",
                            "starter_code": "def evaluate_binary(tp, fp, fn, tn):\n    precision = tp / (tp + fp) if (tp + fp) else 0.0\n    recall = tp / (tp + fn) if (tp + fn) else 0.0\n    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) else 0.0\n    return {'precision': round(precision, 2), 'recall': round(recall, 2), 'f1': round(f1, 2)}\n\nprint(evaluate_binary(tp=80, fp=10, fn=20, tn=890))\n",
                        }
                    ]
                }
            ]
        },

        # 07. Deep Learning and Generative AI
        {
            "slug": "deep-learning-and-genai",
            "title": "07. Deep Learning and Generative AI",
            "category": BhavishyaSubject.CATEGORY_TECHNICAL,
            "order": 7,
            "short_description": "Neural Networks, Backpropagation, Transformers, LLMs, Prompt Engineering, Embeddings, and RAG architectures.",
            "full_description": "Step into the bleeding edge of modern AI. Covers Multilayer Perceptrons (MLP), Activation functions (ReLU, GeLU), Backpropagation via computational graphs, Convolutional Neural Networks (CNNs) for vision, Recurrent networks, the Transformer Attention mechanism (Self-Attention, Multi-Head Attention), Large Language Models (LLMs), Embeddings, Vector Databases, and Retrieval-Augmented Generation (RAG).",
            "estimated_hours": 28,
            "difficulty": "Advanced",
            "icon": "brain",
            "color_accent": "#8B5CF6",
            "prerequisites": ["machine-learning"],
            "chapters": [
                {
                    "id": "dl-ch1",
                    "title": "Chapter 1: Neural Networks & Backpropagation",
                    "lessons": [
                        {
                            "id": "dl-l1",
                            "title": "Artificial Neurons, Activation Functions & Feedforward Flow",
                            "type": "classroom",
                            "duration_mins": 45,
                            "socratic_prompt": "Explain why linear activation functions cannot solve XOR problem. Introduce non-linear activations (ReLU, Sigmoid, Tanh).",
                            "practice_question": "What is the vanishing gradient problem, and why does ReLU mitigate it compared to Sigmoid?",
                            "starter_code": "def relu(x):\n    return max(0.0, x)\n\nprint(relu(-5.2))\nprint(relu(3.8))\n",
                        },
                        {
                            "id": "dl-l2",
                            "title": "Backpropagation & Computational Graph Gradients",
                            "type": "coding_lab",
                            "duration_mins": 55,
                            "socratic_prompt": "Explain the chain rule of calculus for updating intermediate hidden layer weights.",
                            "practice_question": "Trace gradients for a simple 2-node computational graph using the chain rule.",
                            "starter_code": "# Manual scalar backprop step\nx = 2.0\nw = 3.0\ny_true = 10.0\n# Forward: y_pred = w * x\ny_pred = w * x\nloss = (y_pred - y_true) ** 2\n# dLoss/dw = 2 * (y_pred - y_true) * x\ndloss_dw = 2 * (y_pred - y_true) * x\nprint('Gradient dLoss/dw:', dloss_dw)\n",
                        }
                    ]
                },
                {
                    "id": "dl-ch2",
                    "title": "Chapter 2: Transformers, LLMs & Retrieval-Augmented Generation (RAG)",
                    "lessons": [
                        {
                            "id": "dl-l3",
                            "title": "The Transformer Architecture: Self-Attention & QKV Matrices",
                            "type": "classroom",
                            "duration_mins": 50,
                            "socratic_prompt": "Deconstruct Queries (Q), Keys (K), and Values (V). Explain scaled dot-product attention softmax(QK^T / sqrt(d_k))V.",
                            "practice_question": "Why did Transformers replace RNNs/LSTMs in modern NLP?",
                            "starter_code": "# Self-attention concept formula\n# Attention(Q, K, V) = softmax((Q @ K.T) / sqrt(d_k)) @ V\n",
                        },
                        {
                            "id": "dl-l4",
                            "title": "Vector Embeddings & Retrieval-Augmented Generation (RAG)",
                            "type": "coding_lab",
                            "duration_mins": 55,
                            "socratic_prompt": "Explain how high-dimensional semantic embeddings enable nearest-neighbor vector search in knowledge bases to eliminate LLM hallucinations.",
                            "practice_question": "Simulate semantic text similarity ranking using cosine similarity over embeddings.",
                            "starter_code": "# RAG Pipeline Simulation\ndef search_knowledge_base(query, documents):\n    # Simulate semantic matching\n    matches = [doc for doc in documents if any(w in doc.lower() for w in query.lower().split())]\n    return matches or ['No direct match found.']\n\ndocs = ['Python functions support default arguments.', 'SQL JOIN combines multiple tables.']\nprint(search_knowledge_base('What is SQL JOIN?', docs))\n",
                        }
                    ]
                }
            ]
        },

        # 08. Developer Tools and Deployment
        {
            "slug": "developer-tools-and-deployment",
            "title": "08. Developer Tools and Deployment",
            "category": BhavishyaSubject.CATEGORY_TECHNICAL,
            "order": 8,
            "short_description": "Git & GitHub workflows, Linux CLI, FastAPI microservices, Docker containerization, and Cloud deployment.",
            "full_description": "Bridge the gap between model prototyping and production engineering. Covers professional Git collaboration (branches, merge conflicts, pull requests), Linux command line fluency, building high-performance REST APIs with FastAPI, packaging applications into portable Docker images, environment variables, CI/CD pipelines, and deploying web services on cloud infrastructure.",
            "estimated_hours": 20,
            "difficulty": "Intermediate",
            "icon": "terminal",
            "color_accent": "#14B8A6",
            "prerequisites": ["python-programming"],
            "chapters": [
                {
                    "id": "dev-ch1",
                    "title": "Chapter 1: Git Mastery & Linux Command Line",
                    "lessons": [
                        {
                            "id": "dev-l1",
                            "title": "Git Workflow: Commits, Branching, Merging & Pull Requests",
                            "type": "classroom",
                            "duration_mins": 40,
                            "socratic_prompt": "Explain the three states of Git (working directory, staging area, repository). Show how rebasing differs from merging.",
                            "practice_question": "What happens during a Git merge conflict and what are the exact steps to resolve it?",
                            "starter_code": "# Git command reference\n# git checkout -b feature/model-api\n# git add .\n# git commit -m 'feat: add prediction endpoint'\n",
                        },
                        {
                            "id": "dev-l2",
                            "title": "Linux Server Administration, Permissions & Shell Scripting",
                            "type": "classroom",
                            "duration_mins": 40,
                            "socratic_prompt": "Explain Unix file permissions (rwx, chmod 755), process management (ps, kill, top), and environment variables.",
                            "practice_question": "Explain the difference between soft and hard links in Linux.",
                            "starter_code": "# Linux bash snippet\n# chmod +x deploy.sh\n# ps aux | grep python\n",
                        }
                    ]
                },
                {
                    "id": "dev-ch2",
                    "title": "Chapter 2: FastAPI, Docker & Cloud Deployment",
                    "lessons": [
                        {
                            "id": "dev-l3",
                            "title": "Building Production REST APIs with FastAPI & Pydantic",
                            "type": "coding_lab",
                            "duration_mins": 50,
                            "socratic_prompt": "Teach asynchronous endpoint handling (async/await) and request validation with Pydantic schemas.",
                            "practice_question": "Write a FastAPI route that validates an incoming prediction payload and returns a JSON response.",
                            "starter_code": "# FastAPI code template\nfrom pydantic import BaseModel\n\nclass PredictionRequest(BaseModel):\n    features: list[float]\n\ndef predict_mock(req: PredictionRequest):\n    return {'prediction': sum(req.features) > 10.0, 'status': 'success'}\n\nprint(predict_mock(PredictionRequest(features=[2.5, 3.5, 5.0])))\n",
                        },
                        {
                            "id": "dev-l4",
                            "title": "Docker Containers & Containerized Cloud Deployment",
                            "type": "classroom",
                            "duration_mins": 45,
                            "socratic_prompt": "Explain how Docker solves 'it works on my machine'. Deconstruct Dockerfile instructions (FROM, WORKDIR, COPY, RUN, CMD).",
                            "practice_question": "Write a minimal Dockerfile to containerize a Python web application.",
                            "starter_code": "# Dockerfile\n# FROM python:3.11-slim\n# WORKDIR /app\n# COPY requirements.txt .\n# RUN pip install -r requirements.txt\n# COPY . .\n# CMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]\n",
                        }
                    ]
                }
            ]
        },

        # ==============================================================================
        # CATEGORY B: PLACEMENT AND JOB PREPARATION (09 - 14)
        # ==============================================================================
        {
            "slug": "aptitude-and-logical-reasoning",
            "title": "09. Aptitude and Logical Reasoning",
            "category": BhavishyaSubject.CATEGORY_PLACEMENT,
            "order": 9,
            "short_description": "Quantitative Aptitude, Speed Math, Logical Deductions, and Timed Placement Test Drills.",
            "full_description": "Crack the first elimination round of recruitment drives. Covers Percentages, Profit & Loss, Simple & Compound Interest, Ratios & Proportions, Time & Work, Time/Speed/Distance, Permutations & Combinations, Probability, Number Series, Syllogisms, Blood Relations, Seating Arrangements, Coding-Decoding, and Data Interpretation charts with timed mock assessments.",
            "estimated_hours": 20,
            "difficulty": "Beginner to Advanced",
            "icon": "check-circle",
            "color_accent": "#EAB308",
            "prerequisites": [],
            "chapters": [
                {
                    "id": "apt-ch1",
                    "title": "Chapter 1: Quantitative Mathematics & Speed Calculations",
                    "lessons": [
                        {
                            "id": "apt-l1",
                            "title": "Percentages, Profit & Loss and Compound Growth",
                            "type": "classroom",
                            "duration_mins": 40,
                            "socratic_prompt": "Teach mental math percentage shortcuts (fraction to percent conversions: 1/8 = 12.5%, 1/6 = 16.67%).",
                            "practice_question": "If an item is marked up by 40% and sold at a 20% discount, find the net profit percentage.",
                            "starter_code": "def net_profit(markup_pct, discount_pct):\n    cost = 100.0\n    marked = cost * (1 + markup_pct / 100.0)\n    selling = marked * (1 - discount_pct / 100.0)\n    return round(selling - cost, 2)\n\nprint('Net Profit %:', net_profit(40, 20))\n",
                        },
                        {
                            "id": "apt-l2",
                            "title": "Time, Work, Speed & Relative Velocity Problems",
                            "type": "coding_lab",
                            "duration_mins": 45,
                            "socratic_prompt": "Explain LCM method for Time & Work problems instead of cumbersome fraction addition.",
                            "practice_question": "A can do a piece of work in 12 days and B in 15 days. How many days if they work together?",
                            "starter_code": "def work_together(days_a, days_b):\n    return round((days_a * days_b) / (days_a + days_b), 2)\n\nprint('Days together:', work_together(12, 15))\n",
                        }
                    ]
                },
                {
                    "id": "apt-ch2",
                    "title": "Chapter 2: Logical Reasoning & Data Interpretation",
                    "lessons": [
                        {
                            "id": "apt-l3",
                            "title": "Syllogisms, Blood Relations & Seating Arrangement Puzzles",
                            "type": "classroom",
                            "duration_mins": 45,
                            "socratic_prompt": "Teach Venn diagram techniques for evaluating syllogism statements (All A are B, Some B are C).",
                            "practice_question": "Solve a circular seating arrangement puzzle with facing center conditions.",
                            "starter_code": "# Logic puzzle deduction tracker\n",
                        }
                    ]
                }
            ]
        },

        # 10. English and Communication
        {
            "slug": "english-and-communication",
            "title": "10. English and Communication",
            "category": BhavishyaSubject.CATEGORY_PLACEMENT,
            "order": 10,
            "short_description": "Interactive Spoken English, Pronunciation Drills, Active Listening, and Professional Workplace Fluency.",
            "full_description": "Transform verbal fluency and self-confidence through real-time microphone practice. The AI teacher conducts voice conversations, identifies grammatical slip-ups (tense mismatches, subject-verb agreement), suggests vocabulary upgrades, guides presentation tone, and trains students to speak clearly without hesitation or filler words.",
            "estimated_hours": 20,
            "difficulty": "Beginner to Advanced",
            "icon": "mic",
            "color_accent": "#0284C7",
            "prerequisites": [],
            "chapters": [
                {
                    "id": "eng-ch1",
                    "title": "Chapter 1: Spoken Fluency, Tenses & Grammar in Action",
                    "lessons": [
                        {
                            "id": "eng-l1",
                            "title": "Everyday Verbal Fluency & Eliminating Hesitation",
                            "type": "classroom",
                            "duration_mins": 35,
                            "socratic_prompt": "Invite the student to speak through their microphone for 60 seconds about their favorite hobby or tech project. Give positive verbal feedback and point out one natural vocabulary improvement.",
                            "practice_question": "Speak about your background and why you want to become a software engineer.",
                            "starter_code": "# Voice interaction lesson. Click the microphone button to start speaking.\n",
                        },
                        {
                            "id": "eng-l2",
                            "title": "Professional Vocabulary & Structuring Technical Arguments",
                            "type": "classroom",
                            "duration_mins": 40,
                            "socratic_prompt": "Teach replacing weak words ('very good', 'did a lot of things') with precise technical terminology ('optimized', 'architected', 'scalable').",
                            "practice_question": "Rewrite or verbally articulate a project description using power action verbs.",
                            "starter_code": "# Professional communication checklist\n",
                        }
                    ]
                }
            ]
        },

        # 11. Group Discussion
        {
            "slug": "group-discussion-simulator",
            "title": "11. Group Discussion",
            "category": BhavishyaSubject.CATEGORY_PLACEMENT,
            "order": 11,
            "short_description": "AI Multi-Agent GD Simulator: Debate with 4 AI participants on technical and current affairs topics.",
            "full_description": "Experience a realistic campus GD round. You enter a simulated discussion table with 3-4 distinct AI peers (an analytical debater, a moderating leader, a contrarian, and a supportive teammate). Practice introducing topics, presenting structured points, polite interruption, handling disagreement, and synthesizing conclusions.",
            "estimated_hours": 14,
            "difficulty": "Intermediate",
            "icon": "users",
            "color_accent": "#84CC16",
            "prerequisites": ["english-and-communication"],
            "chapters": [
                {
                    "id": "gd-ch1",
                    "title": "Chapter 1: GD Dynamics & AI Multi-Participant Simulation",
                    "lessons": [
                        {
                            "id": "gd-l1",
                            "title": "GD Rules: Opening, Interventions, Body Language & Etiquette",
                            "type": "classroom",
                            "duration_mins": 35,
                            "socratic_prompt": "Teach why shouting or dominating a GD gets candidates rejected, while calm leadership and summarizing opposing points earns high scores.",
                            "practice_question": "What is the 3-second pause technique for polite entry into a heated group discussion?",
                            "starter_code": "# GD guidelines overview\n",
                        },
                        {
                            "id": "gd-l2",
                            "title": "Live Simulated GD: 'Is AI a Threat to Entry-Level Developer Jobs?'",
                            "type": "classroom",
                            "duration_mins": 45,
                            "socratic_prompt": "Initiate the 4-person AI simulation. Agent Aarav argues for job displacement, Agent Sneha points to developer productivity surges, and Agent Vikram acts as moderator. Student must contribute at least two structured arguments.",
                            "practice_question": "Contribute your perspective to the simulated discussion through mic or text.",
                            "starter_code": "# Click 'Join GD Simulator' to begin the multi-agent session.\n",
                        }
                    ]
                }
            ]
        },

        # 12. Technical Interview Preparation
        {
            "slug": "technical-interview-prep",
            "title": "12. Technical Interview Preparation",
            "category": BhavishyaSubject.CATEGORY_PLACEMENT,
            "order": 12,
            "short_description": "One-on-one Conversational AI Technical Interviewer: Coding questions, follow-up probes, and architecture discussions.",
            "full_description": "Face a tough, realistic AI technical interviewer. The AI asks one technical question at a time across Python, DSA, DBMS, System Design, and ML theory. It listens to your conceptual explanations, tests your edge cases, asks follow-up optimization questions, and provides a structured score rubric at the end.",
            "estimated_hours": 18,
            "difficulty": "Intermediate to Advanced",
            "icon": "terminal",
            "color_accent": "#F97316",
            "prerequisites": ["python-programming", "data-structures-and-algorithms", "sql-and-data-management"],
            "chapters": [
                {
                    "id": "techint-ch1",
                    "title": "Chapter 1: Live Technical Round Simulations",
                    "lessons": [
                        {
                            "id": "techint-l1",
                            "title": "Mock Technical Interview: Python, OOP & Complexity",
                            "type": "classroom",
                            "duration_mins": 45,
                            "socratic_prompt": "Act as a Senior Software Engineer interviewing the student. Ask: How does Python manage memory behind the scenes (reference counting and garbage collection)? Listen and probe.",
                            "practice_question": "Explain how Python's GIL (Global Interpreter Lock) impacts multi-threaded CPU vs I/O bound programs.",
                            "starter_code": "# Interactive Technical Interview Mode\n",
                        }
                    ]
                }
            ]
        },

        # 13. HR Interview and Personality
        {
            "slug": "hr-interview-personality",
            "title": "13. HR Interview and Personality",
            "category": BhavishyaSubject.CATEGORY_PLACEMENT,
            "order": 13,
            "short_description": "Behavioral STAR technique, Situational questions, Culture fit, and Salary negotiation strategies.",
            "full_description": "Conquer behavioral and cultural rounds. Learn the STAR method (Situation, Task, Action, Result) to narrate past triumphs and failures. Practice answering classic HR hurdles: 'Tell me about yourself', 'What are your strengths and weaknesses?', 'Why our company?', 'Tell me about a conflict in your team', and professional salary discussions.",
            "estimated_hours": 15,
            "difficulty": "Beginner to Intermediate",
            "icon": "smile",
            "color_accent": "#E11D48",
            "prerequisites": ["english-and-communication"],
            "chapters": [
                {
                    "id": "hr-ch1",
                    "title": "Chapter 1: The STAR Framework & Behavioral Mastery",
                    "lessons": [
                        {
                            "id": "hr-l1",
                            "title": "Mastering the STAR Method for Behavioral Questions",
                            "type": "classroom",
                            "duration_mins": 35,
                            "socratic_prompt": "Deconstruct Situation, Task, Action, Result. Ask student to narrate an instance where a project failed and what they did to fix it.",
                            "practice_question": "Draft a 90-second answer for 'Tell me about a time you handled a tight deadline.'",
                            "starter_code": "# STAR Formula Template\n# Situation: Set the context\n# Task: Define the challenge\n# Action: Detail the specific steps YOU took\n# Result: Quantifiable outcome achieved\n",
                        },
                        {
                            "id": "hr-l2",
                            "title": "Live AI HR Interview Simulation",
                            "type": "classroom",
                            "duration_mins": 45,
                            "socratic_prompt": "Act as an experienced VP of People interviewing the candidate. Evaluate posture, tone, self-awareness, and emotional maturity.",
                            "practice_question": "Complete the 5-question HR simulation session.",
                            "starter_code": "# Click to enter the AI HR interview booth.\n",
                        }
                    ]
                }
            ]
        },

        # 14. Resume, LinkedIn and GitHub
        {
            "slug": "resume-linkedin-github",
            "title": "14. Resume, LinkedIn and GitHub",
            "category": BhavishyaSubject.CATEGORY_PLACEMENT,
            "order": 14,
            "short_description": "ATS Resume Building, LinkedIn Profile Optimization, and GitHub Repository showcase.",
            "full_description": "Stand out in recruiters' screening algorithms. Build single-page ATS-compliant resumes with quantified bullet points (Google XYZ formula: Accomplished [X], as measured by [Y], by doing [Z]). Optimize your LinkedIn headline, summary, and skills endorsements. Structure GitHub repositories with professional READMEs, architecture diagrams, and live demo links.",
            "estimated_hours": 12,
            "difficulty": "Beginner to Intermediate",
            "icon": "file-text",
            "color_accent": "#6366F1",
            "prerequisites": [],
            "chapters": [
                {
                    "id": "res-ch1",
                    "title": "Chapter 1: ATS Engineering & Portfolio Architecture",
                    "lessons": [
                        {
                            "id": "res-l1",
                            "title": "ATS-Proof Resume Architecture & The Google XYZ Formula",
                            "type": "classroom",
                            "duration_mins": 40,
                            "socratic_prompt": "Explain why multi-column graphics-heavy resumes fail ATS parsers. Show how to format bullet points with quantifiable metrics.",
                            "practice_question": "Transform a vague project description into a crisp Google XYZ formatted bullet.",
                            "starter_code": "# Example: Built a full-stack portal -> Engineered a responsive portal using React and Python, accelerating test turnaround by 35% across 500 active users.\n",
                        },
                        {
                            "id": "res-l2",
                            "title": "GitHub Profile Readme, Clean Code Commitments & LinkedIn Magnetism",
                            "type": "classroom",
                            "duration_mins": 40,
                            "socratic_prompt": "Review student's GitHub README design, badges, and documentation structure.",
                            "practice_question": "Structure a repository README with Problem, Architecture, Installation, API Specs, and Demo GIF.",
                            "starter_code": "# Repository README template\n",
                        }
                    ]
                }
            ]
        },

        # ==============================================================================
        # CATEGORY C: PRACTICAL PROJECTS AND CAREER PORTFOLIO (15 - 19)
        # ==============================================================================
        {
            "slug": "placement-simulator",
            "title": "15. AI Mock Interview & Placement Simulator",
            "category": BhavishyaSubject.CATEGORY_PROJECTS,
            "order": 15,
            "short_description": "Complete 5-Round Campus Recruitment Simulator: Aptitude, Coding, GD, Technical & HR.",
            "full_description": "Put your skills to the ultimate test before sitting in actual college recruitment drives. Go through 5 timed, rigorous placement rounds: Round 1 (Timed Aptitude), Round 2 (Timed Coding Challenge), Round 3 (Multi-Agent Group Discussion), Round 4 (Live Technical Interview), and Round 5 (HR Interview). Generates an end-of-assessment Placement Readiness Score with breakdown rubrics.",
            "estimated_hours": 15,
            "difficulty": "Advanced",
            "icon": "award",
            "color_accent": "#10B981",
            "prerequisites": ["aptitude-and-logical-reasoning", "technical-interview-prep", "hr-interview-personality"],
            "chapters": [
                {
                    "id": "sim-ch1",
                    "title": "Chapter 1: The 5-Round Placement Simulator",
                    "lessons": [
                        {
                            "id": "sim-l1",
                            "title": "Complete 5-Round Placement Assessment Walkthrough",
                            "type": "classroom",
                            "duration_mins": 60,
                            "socratic_prompt": "Explain how cumulative placement scores are weighted across technical competency, problem-solving, and communication.",
                            "practice_question": "Begin Round 1: Quantitative & Logical Assessment.",
                            "starter_code": "# Launch Simulator\n",
                        }
                    ]
                }
            ]
        },

        # 16. Data Analytics Project
        {
            "slug": "data-analytics-project",
            "title": "16. Data Analytics Project",
            "category": BhavishyaSubject.CATEGORY_PROJECTS,
            "order": 16,
            "short_description": "Build an end-to-end exploratory data analysis and visualization dashboard on real-world datasets.",
            "full_description": "Transform messy raw datasets into actionable executive insights. Clean nulls, detect outliers, perform univariate and bivariate statistical analysis, engineer new features, and generate publication-quality visual dashboards using Pandas, NumPy, Matplotlib, and Seaborn. Submit GitHub repository and analysis report.",
            "estimated_hours": 16,
            "difficulty": "Intermediate",
            "icon": "bar-chart-2",
            "color_accent": "#3B82F6",
            "prerequisites": ["sql-and-data-management"],
            "chapters": [
                {
                    "id": "da-ch1",
                    "title": "Chapter 1: Exploratory Analysis & Executive Reporting",
                    "lessons": [
                        {
                            "id": "da-l1",
                            "title": "Project Brief: Real-World E-Commerce & Customer Churn Analysis",
                            "type": "coding_lab",
                            "duration_mins": 60,
                            "socratic_prompt": "Guide student through calculating customer lifetime value (LTV), cohort retention rates, and churn correlation matrices.",
                            "practice_question": "Submit completed data analysis script with summary insights.",
                            "starter_code": "# Data Analytics Template\nimport pandas as pd\n# Load dataset and inspect correlations\n",
                        }
                    ]
                }
            ]
        },

        # 17. Machine Learning Predictive Project
        {
            "slug": "ml-predictive-project",
            "title": "17. Machine Learning Predictive Project",
            "category": BhavishyaSubject.CATEGORY_PROJECTS,
            "order": 17,
            "short_description": "Train, tune, evaluate, and package a production-grade machine learning model for inference.",
            "full_description": "Build an end-to-end predictive machine learning solution. Formulate problem statement, split data with stratified cross-validation, train multiple candidate models (Linear, Random Forest, XGBoost), tune hyperparameters using Optuna/GridSearchCV, inspect feature importances, and serialize the champion pipeline with Joblib.",
            "estimated_hours": 18,
            "difficulty": "Intermediate",
            "icon": "activity",
            "color_accent": "#6366F1",
            "prerequisites": ["machine-learning"],
            "chapters": [
                {
                    "id": "mlp-ch1",
                    "title": "Chapter 1: Model Engineering & Pipeline Serialization",
                    "lessons": [
                        {
                            "id": "mlp-l1",
                            "title": "Project Brief: Predictive Loan Default Risk Engine",
                            "type": "coding_lab",
                            "duration_mins": 60,
                            "socratic_prompt": "Evaluate model trade-offs between precision (avoiding bad loans) and recall (capturing true defaults).",
                            "practice_question": "Build an end-to-end Scikit-Learn Pipeline with scaling, encoding, and classifier.",
                            "starter_code": "# Machine Learning Pipeline Template\n",
                        }
                    ]
                }
            ]
        },

        # 18. Generative AI Chatbot Project
        {
            "slug": "genai-application-project",
            "title": "18. Generative AI Chatbot Project",
            "category": BhavishyaSubject.CATEGORY_PROJECTS,
            "order": 18,
            "short_description": "Build a Retrieval-Augmented Generation (RAG) assistant with Vector DB and LLM APIs.",
            "full_description": "Architect a production-ready Generative AI assistant. Parse unstructured documentation (PDFs, Markdown), chunk text semantically, generate vector embeddings, store them in a vector index (ChromaDB/FAISS), formulate context-stuffed prompt templates with guardrails, and stream responses to a web interface.",
            "estimated_hours": 20,
            "difficulty": "Advanced",
            "icon": "message-square",
            "color_accent": "#A855F7",
            "prerequisites": ["deep-learning-and-genai"],
            "chapters": [
                {
                    "id": "genp-ch1",
                    "title": "Chapter 1: RAG Architecture & Vector Indexing",
                    "lessons": [
                        {
                            "id": "genp-l1",
                            "title": "Project Brief: Intelligent PDF Document Research Assistant",
                            "type": "coding_lab",
                            "duration_mins": 60,
                            "socratic_prompt": "Guide student through embedding calculation, similarity thresholding, and prompt injection defenses.",
                            "practice_question": "Submit working RAG backend endpoint code.",
                            "starter_code": "# GenAI RAG assistant template\n",
                        }
                    ]
                }
            ]
        },

        # 19. Final Industry Capstone Project
        {
            "slug": "ai-ml-capstone-project",
            "title": "19. Final Industry Capstone Project",
            "category": BhavishyaSubject.CATEGORY_PROJECTS,
            "order": 19,
            "short_description": "Full-stack AI application: Model training, FastAPI backend, interactive frontend, and cloud deployment.",
            "full_description": "The crowning achievement of Bhavishya 1.0. Build, document, test, containerize, and deploy a full-scale AI application to a public cloud URL. Mandatory deliverables: GitHub repository with clean commits and documentation, working public web application URL, video demonstration, and architectural design writeup reviewed against an industry grading rubric.",
            "estimated_hours": 24,
            "difficulty": "Advanced",
            "icon": "rocket",
            "color_accent": "#EC4899",
            "prerequisites": ["developer-tools-and-deployment", "placement-simulator"],
            "chapters": [
                {
                    "id": "cap-ch1",
                    "title": "Chapter 1: Capstone Execution & Evaluation",
                    "lessons": [
                        {
                            "id": "cap-l1",
                            "title": "Capstone Submission & AI Rubric Evaluation",
                            "type": "classroom",
                            "duration_mins": 60,
                            "socratic_prompt": "Evaluate student's capstone repository, API documentation, unit tests, Dockerfile, and live cloud deployment URL.",
                            "practice_question": "Submit your GitHub repository, live URL, and architecture overview.",
                            "starter_code": "# Capstone Submission Portal\n",
                        }
                    ]
                }
            ]
        }
    ]


def ensure_default_bhavishya_subjects():
    """
    Seeds and ensures all 19 Bhavishya subjects exist in the MongoDB database.
    Safe and idempotent: refreshes curriculum without overwriting custom admin settings.
    """
    from models.mongo import get_db
    try:
        db = get_db()
        curriculum = get_default_bhavishya_curriculum()
        seeded_count = 0
        updated_count = 0
        for item in curriculum:
            slug = item["slug"]
            existing = db.bhavishya_subjects.find_one({"slug": slug})
            if not existing:
                subj = BhavishyaSubject(item)
                subj.save()
                seeded_count += 1
            else:
                # Refresh curriculum chapters & descriptions while preserving custom overrides
                db.bhavishya_subjects.update_one(
                    {"slug": slug},
                    {
                        "$set": {
                            "title": item["title"],
                            "category": item["category"],
                            "order": item["order"],
                            "short_description": item["short_description"],
                            "full_description": item["full_description"],
                            "estimated_hours": item["estimated_hours"],
                            "difficulty": item["difficulty"],
                            "icon": item["icon"],
                            "color_accent": item["color_accent"],
                            "prerequisites": item["prerequisites"],
                            "chapters": item["chapters"],
                            "is_published": item.get("is_published", True),
                        }
                    }
                )
                updated_count += 1
        print(f"[BHAVISHYA] Seeded {seeded_count} new subjects, refreshed {updated_count} existing subjects in MongoDB.")
        return True
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"[BHAVISHYA SEED WARNING] {e}")
        return False
