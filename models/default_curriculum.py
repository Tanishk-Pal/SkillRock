"""
SkillRock — Production Course Catalog & Milestone Curriculum
Curated from top community recommendations on Reddit (r/learnprogramming, r/webdev, r/cybersecurity)
and YouTube (Bro Code, Kunal Kushwaha, Striver take U forward, Programming with Mosh, freeCodeCamp,
The Net Ninja, Traversy Media, CodeWithHarry, NetworkChuck, Gary Simon DesignCourse).
"""

def get_default_curriculum():
    return [
        # ==============================================================================
        # 1. Java Programming & Object-Oriented Design (Bro Code)
        # ==============================================================================
        {
            "slug": "java-core-oops-masterclass",
            "title": "Java Programming & Object-Oriented Design Masterclass",
            "category": "Programming",
            "language": "English",
            "difficulty": "Beginner",
            "estimated_duration": "12 Hours",
            "instructor": "Bro Code",
            "youtube_url": "https://www.youtube.com/watch?v=xk4_1vDrzzo",
            "thumbnail_url": "https://img.youtube.com/vi/xk4_1vDrzzo/maxresdefault.jpg",
            "description": "Master core Java from first principles: variables, operators, loops, arrays, methods, object-oriented programming (inheritance, polymorphism, abstraction, encapsulation), Java Collections, and file operations.",
            "learning_objectives": [
                "Understand JVM mechanics, memory allocation, and Java syntax",
                "Implement clean OOP design principles and modular classes",
                "Master the Java Collections Framework (ArrayList, HashMap, HashSet)",
                "Safely handle exceptions and persist records with file streams"
            ],
            "milestone_assignments": [
                {
                    "step_number": 1,
                    "total_steps": 3,
                    "evaluation_type": "algorithmic",
                    "title": "Milestone 1: String Palindrome & Word Reverser",
                    "short_description": "Implement efficient string manipulation and palindrome verification in Python/Java logic.",
                    "problem_statement": "Write a function `is_palindrome(text)` that returns True if a given string is a palindrome (ignoring casing and non-alphanumeric characters) and False otherwise. Additionally, write `reverse_words(sentence)` that reverses word order.",
                    "target_function_name": "is_palindrome",
                    "starter_code": "def is_palindrome(text):\n    # Write clean logic here\n    cleaned = ''.join(c.lower() for c in str(text) if c.isalnum())\n    return cleaned == cleaned[::-1]\n",
                    "test_cases": [
                        {"name": "Simple Palindrome", "input": "racecar", "expected": True},
                        {"name": "Phrase with Punctuation", "input": "A man, a plan, a canal: Panama", "expected": True},
                        {"name": "Non-palindrome", "input": "skillrock", "expected": False},
                        {"name": "Empty string", "input": "", "expected": True}
                    ],
                    "required_keywords": ["def", "return"],
                    "tech_requirements": "Python 3.10+ or Java logical syntax",
                    "is_deployment_required": False
                },
                {
                    "step_number": 2,
                    "total_steps": 3,
                    "evaluation_type": "ai_dual",
                    "title": "Milestone 2: Bank Account Class & Transaction Ledger",
                    "short_description": "Implement an encapsulated BankAccount class with balance invariants and audit history.",
                    "problem_statement": "Implement a `BankAccount` class with `deposit(amount)`, `withdraw(amount)`, and `get_balance()`. Overdrafts must be rejected (return False or raise error). All transactions must be logged in an internal list.",
                    "target_function_name": "create_account",
                    "starter_code": "class BankAccount:\n    def __init__(self, owner, initial_balance=0):\n        self.owner = owner\n        self.balance = max(0, initial_balance)\n        self.transactions = []\n\n    def deposit(self, amount):\n        if amount <= 0: return False\n        self.balance += amount\n        self.transactions.append(('DEPOSIT', amount))\n        return True\n\n    def withdraw(self, amount):\n        if amount <= 0 or amount > self.balance: return False\n        self.balance -= amount\n        self.transactions.append(('WITHDRAW', amount))\n        return True\n\n    def get_balance(self):\n        return self.balance\n\ndef create_account(owner, balance):\n    acc = BankAccount(owner, balance)\n    acc.deposit(50)\n    acc.withdraw(20)\n    return acc.get_balance()\n",
                    "test_cases": [
                        {"name": "Initial Balance with Transactions", "input": ("Alex", 100), "expected": 130},
                        {"name": "Zero Initial Balance", "input": ("Sara", 0), "expected": 30}
                    ],
                    "required_keywords": ["class", "def", "return"],
                    "tech_requirements": "Clean OOP, encapsulation, transactions",
                    "is_deployment_required": False
                },
                {
                    "step_number": 3,
                    "total_steps": 3,
                    "evaluation_type": "human",
                    "title": "Capstone Project: Campus Student Banking & Records System",
                    "short_description": "Full end-to-end multi-class Java/Python application with persistent storage, CLI, and public GitHub repository.",
                    "problem_statement": "Build an end-to-end banking or library management system with user accounts, interest calculators, transaction history export, and persistent data storage (SQLite, JSON, or CSV).",
                    "required_features": [
                        "Complete OOP architecture with classes, inheritance, and interfaces",
                        "File or database persistence that preserves state across program restarts",
                        "Robust validation preventing invalid deposits, overdrafts, and corrupted records",
                        "Clean command-line or interactive web/GUI interface",
                        "Public GitHub repository with comprehensive README, setup instructions, and architecture diagrams"
                    ],
                    "optional_features": [
                        "Export monthly account statements to CSV",
                        "Automated unit test suite using JUnit or pytest"
                    ],
                    "tech_requirements": "Java or Python, Git, SQLite/File Persistence",
                    "is_deployment_required": False
                }
            ]
        },

        # ==============================================================================
        # 2. Java & Data Structures Masterclass (Kunal Kushwaha)
        # ==============================================================================
        {
            "slug": "java-dsa-enterprise-architecture",
            "title": "Java & Data Structures Masterclass with Enterprise Patterns",
            "category": "Programming",
            "language": "English",
            "difficulty": "Intermediate",
            "estimated_duration": "25 Hours",
            "instructor": "Kunal Kushwaha",
            "youtube_url": "https://www.youtube.com/watch?v=rZ41y93P2Qo",
            "thumbnail_url": "https://img.youtube.com/vi/rZ41y93P2Qo/maxresdefault.jpg",
            "description": "Comprehensive journey from foundational Java mechanics to advanced bitwise algorithms, recursive problem solving, tree traversals, graph algorithms, and enterprise architectural design.",
            "learning_objectives": [
                "Understand JVM internal memory model, garbage collection, and bitwise math",
                "Implement divide-and-conquer and backtracking algorithms",
                "Build custom linked lists, binary search trees, and heaps",
                "Apply clean enterprise design patterns to solve high-throughput data problems"
            ],
            "milestone_assignments": [
                {
                    "step_number": 1,
                    "total_steps": 3,
                    "evaluation_type": "algorithmic",
                    "title": "Milestone 1: Binary Search with Rotated Array & Peak Element",
                    "short_description": "Implement optimal O(log n) search on rotated sorted arrays.",
                    "problem_statement": "Implement `search_rotated(nums, target)` that finds target in a rotated sorted array in O(log n) time. Return its index or -1 if not found.",
                    "target_function_name": "search_rotated",
                    "starter_code": "def search_rotated(nums, target):\n    left, right = 0, len(nums) - 1\n    while left <= right:\n        mid = (left + right) // 2\n        if nums[mid] == target: return mid\n        if nums[left] <= nums[mid]:\n            if nums[left] <= target < nums[mid]: right = mid - 1\n            else: left = mid + 1\n        else:\n            if nums[mid] < target <= nums[right]: left = mid + 1\n            else: right = mid - 1\n    return -1\n",
                    "test_cases": [
                        {"name": "Found in Rotated", "input": ([4, 5, 6, 7, 0, 1, 2], 0), "expected": 4},
                        {"name": "Target at Start", "input": ([4, 5, 6, 7, 0, 1, 2], 4), "expected": 0},
                        {"name": "Not Found", "input": ([4, 5, 6, 7, 0, 1, 2], 3), "expected": -1},
                        {"name": "Single Element", "input": ([1], 1), "expected": 0}
                    ],
                    "required_keywords": ["def", "while", "return"],
                    "tech_requirements": "O(log n) time complexity, O(1) space",
                    "is_deployment_required": False
                },
                {
                    "step_number": 2,
                    "total_steps": 3,
                    "evaluation_type": "ai_dual",
                    "title": "Milestone 2: Custom Linked List Reversal & Cycle Detection",
                    "short_description": "Implement a custom Singly Linked List with in-place reversal and Floyd's cycle detection.",
                    "problem_statement": "Implement `reverse_linked_list(head)` that reverses a linked list in O(n) time and O(1) space. Function takes a Python list representing nodes and returns the reversed list.",
                    "target_function_name": "reverse_linked_list",
                    "starter_code": "def reverse_linked_list(values):\n    if not values: return []\n    # Simulate linked list node reversal\n    res = []\n    for v in reversed(values):\n        res.append(v)\n    return res\n",
                    "test_cases": [
                        {"name": "Multi-node list", "input": [1, 2, 3, 4, 5], "expected": [5, 4, 3, 2, 1]},
                        {"name": "Two nodes", "input": [10, 20], "expected": [20, 10]},
                        {"name": "Empty list", "input": [], "expected": []}
                    ],
                    "required_keywords": ["def", "return"],
                    "tech_requirements": "Linear time, clean pointer manipulation",
                    "is_deployment_required": False
                },
                {
                    "step_number": 3,
                    "total_steps": 3,
                    "evaluation_type": "human",
                    "title": "Capstone Project: High-Performance In-Memory LRU Cache & Graph Search Engine",
                    "short_description": "Production-grade in-memory cache supporting O(1) get/put operations and BFS/DFS graph indexing.",
                    "problem_statement": "Build an in-memory caching engine using doubly-linked lists and hash maps. Include TTL expiration, thread-safety, eviction policies, and a benchmark CLI.",
                    "required_features": [
                        "O(1) time complexity for get and put operations via Doubly Linked List + HashMap",
                        "Capacity enforcement with Least Recently Used (LRU) automatic eviction",
                        "Time-To-Live (TTL) automatic key expiration mechanism",
                        "Concurrent safety or thread-safe locking architecture",
                        "Public GitHub repo with benchmark metrics, unit tests, and comprehensive README"
                    ],
                    "optional_features": [
                        "Persist cache snapshot to disk on shutdown",
                        "Interactive CLI dashboard displaying hit/miss rates"
                    ],
                    "tech_requirements": "Java or Python, Git, Concurrency/Threading",
                    "is_deployment_required": False
                }
            ]
        },

        # ==============================================================================
        # 3. Striver's A2Z DSA Complete Roadmap
        # ==============================================================================
        {
            "slug": "strivers-a2z-dsa-roadmap",
            "title": "Striver's A2Z DSA Complete Roadmap for Tech Interviews",
            "category": "Data Structures & Algorithms",
            "language": "English",
            "difficulty": "Intermediate",
            "estimated_duration": "30 Hours",
            "instructor": "take U forward (Striver)",
            "youtube_url": "https://www.youtube.com/watch?v=EAR7De6Goz4",
            "thumbnail_url": "https://img.youtube.com/vi/EAR7De6Goz4/maxresdefault.jpg",
            "description": "The gold standard interview curriculum covering step-by-step problem solving patterns: Two Pointers, Sliding Window, Prefix Sums, Binary Trees, Graphs, Disjoint Sets, and Dynamic Programming.",
            "learning_objectives": [
                "Deconstruct LeetCode Medium & Hard patterns methodically",
                "Optimize space and time complexity using hash maps and two pointers",
                "Solve tree and graph problems using BFS, DFS, and topological sort",
                "Master dynamic programming: memoization, tabulation, and space optimization"
            ],
            "milestone_assignments": [
                {
                    "step_number": 1,
                    "total_steps": 3,
                    "evaluation_type": "algorithmic",
                    "title": "Milestone 1: Two Sum & Subarray Sum Equals K",
                    "short_description": "Implement optimal O(n) solutions using prefix sums and hash tables.",
                    "problem_statement": "Implement `two_sum(nums, target)` that returns the 0-based indices of two numbers that add up to target in O(n) time.",
                    "target_function_name": "two_sum",
                    "starter_code": "def two_sum(nums, target):\n    lookup = {}\n    for i, n in enumerate(nums):\n        complement = target - n\n        if complement in lookup:\n            return [lookup[complement], i]\n        lookup[n] = i\n    return []\n",
                    "test_cases": [
                        {"name": "Standard array", "input": ([2, 7, 11, 15], 9), "expected": [0, 1]},
                        {"name": "Unsorted numbers", "input": ([3, 2, 4], 6), "expected": [1, 2]},
                        {"name": "Identical numbers", "input": ([3, 3], 6), "expected": [0, 1]}
                    ],
                    "required_keywords": ["def", "return"],
                    "tech_requirements": "O(n) time complexity, single-pass hashmap",
                    "is_deployment_required": False
                },
                {
                    "step_number": 2,
                    "total_steps": 3,
                    "evaluation_type": "ai_dual",
                    "title": "Milestone 2: Valid Parentheses & Monotonic Stack",
                    "short_description": "Implement expression matching and Next Greater Element using a monotonic stack.",
                    "problem_statement": "Write `is_valid_parentheses(s)` to determine if brackets '()[]{}' are closed in correct order.",
                    "target_function_name": "is_valid_parentheses",
                    "starter_code": "def is_valid_parentheses(s):\n    stack = []\n    mapping = {')': '(', '}': '{', ']': '['}\n    for char in s:\n        if char in mapping:\n            top = stack.pop() if stack else '#'\n            if mapping[char] != top: return False\n        else:\n            stack.append(char)\n    return not stack\n",
                    "test_cases": [
                        {"name": "Simple valid", "input": "()[]{}", "expected": True},
                        {"name": "Nested valid", "input": "{[()]}", "expected": True},
                        {"name": "Mismatched", "input": "(]", "expected": False},
                        {"name": "Single open bracket", "input": "(", "expected": False}
                    ],
                    "required_keywords": ["def", "return"],
                    "tech_requirements": "Stack data structure, O(n) time",
                    "is_deployment_required": False
                },
                {
                    "step_number": 3,
                    "total_steps": 3,
                    "evaluation_type": "human",
                    "title": "Capstone Project: Algorithm Visualizer & Benchmarking Dashboard",
                    "short_description": "Interactive web application visualizing sorting, pathfinding (Dijkstra/A*), and algorithm benchmarking.",
                    "problem_statement": "Create a fully deployed interactive web app that visualizes sorting algorithms (Merge, Quick, Heap) and graph pathfinding (BFS, DFS, Dijkstra). Include real-time step counters and speed controls.",
                    "required_features": [
                        "Visual interactive canvas/DOM rendering algorithm step animations",
                        "Support for at least 3 distinct sorting and 2 graph search algorithms",
                        "Speed controller, array size sliders, and custom input dataset generators",
                        "Performance comparison metrics (operations count, time taken)",
                        "Public GitHub repo with clean architecture and live deployment on Vercel/Render/Netlify"
                    ],
                    "optional_features": [
                        "Sound synthesis on comparison steps",
                        "Maze generator for pathfinding visualization"
                    ],
                    "tech_requirements": "React / HTML5 Canvas / Modern JS / Python, Git, Live Deployment",
                    "is_deployment_required": True
                }
            ]
        },

        # ==============================================================================
        # 4. Data Structures & Algorithms in Python (Abdul Bari / Curated)
        # ==============================================================================
        {
            "slug": "python-dsa-masterclass",
            "title": "Data Structures & Algorithms in Python: Problem Solving Masterclass",
            "category": "Data Structures & Algorithms",
            "language": "English",
            "difficulty": "Intermediate",
            "estimated_duration": "18 Hours",
            "instructor": "Abdul Bari / Curated",
            "youtube_url": "https://www.youtube.com/watch?v=8hly31xKli0",
            "thumbnail_url": "https://img.youtube.com/vi/8hly31xKli0/maxresdefault.jpg",
            "description": "Master algorithmic complexity, asymptotic analysis, recursive trees, dynamic programming memoization, and custom data structure implementations using idiomatic Python.",
            "learning_objectives": [
                "Analyze time & space complexity with mathematical rigor",
                "Implement priority queues, heaps, and binary search trees from scratch",
                "Solve DP optimization problems with top-down and bottom-up paradigms",
                "Build production-grade algorithmic utilities in Python"
            ],
            "milestone_assignments": [
                {
                    "step_number": 1,
                    "total_steps": 3,
                    "evaluation_type": "algorithmic",
                    "title": "Milestone 1: Maximum Subarray Sum (Kadane's Algorithm)",
                    "short_description": "Implement Kadane's algorithm to solve maximum contiguous subarray sum in O(n) time.",
                    "problem_statement": "Implement `max_subarray(nums)` that finds the contiguous subarray with the largest sum and returns that sum in O(n) time.",
                    "target_function_name": "max_subarray",
                    "starter_code": "def max_subarray(nums):\n    if not nums: return 0\n    max_so_far = current_max = nums[0]\n    for n in nums[1:]:\n        current_max = max(n, current_max + n)\n        max_so_far = max(max_so_far, current_max)\n    return max_so_far\n",
                    "test_cases": [
                        {"name": "Standard Mixed Array", "input": [-2, 1, -3, 4, -1, 2, 1, -5, 4], "expected": 6},
                        {"name": "Single Element", "input": [1], "expected": 1},
                        {"name": "All Negative Numbers", "input": [-5, -2, -8, -1], "expected": -1}
                    ],
                    "required_keywords": ["def", "return"],
                    "tech_requirements": "O(n) time complexity, O(1) space",
                    "is_deployment_required": False
                },
                {
                    "step_number": 2,
                    "total_steps": 3,
                    "evaluation_type": "ai_dual",
                    "title": "Milestone 2: Coin Change Problem (Dynamic Programming)",
                    "short_description": "Find the minimum number of coins needed to make up a given amount.",
                    "problem_statement": "Implement `coin_change(coins, amount)` that computes the fewest number of coins needed to make up that amount. Return -1 if impossible.",
                    "target_function_name": "coin_change",
                    "starter_code": "def coin_change(coins, amount):\n    dp = [float('inf')] * (amount + 1)\n    dp[0] = 0\n    for c in coins:\n        for i in range(c, amount + 1):\n            dp[i] = min(dp[i], dp[i - c] + 1)\n    return dp[amount] if dp[amount] != float('inf') else -1\n",
                    "test_cases": [
                        {"name": "Normal Coins", "input": ([1, 2, 5], 11), "expected": 3},
                        {"name": "Impossible Amount", "input": ([2], 3), "expected": -1},
                        {"name": "Zero Amount", "input": ([1], 0), "expected": 0}
                    ],
                    "required_keywords": ["def", "return"],
                    "tech_requirements": "Dynamic programming tabulation or memoization",
                    "is_deployment_required": False
                },
                {
                    "step_number": 3,
                    "total_steps": 3,
                    "evaluation_type": "human",
                    "title": "Capstone Project: Competitive DSA Problem Solver & Benchmarking Web App",
                    "short_description": "Full-stack algorithmic playground with automated test suite, time complexity profiler, and code runner.",
                    "problem_statement": "Build an algorithmic playground web app where users can benchmark custom sorting and search implementations against varying dataset sizes.",
                    "required_features": [
                        "Modular Python backend benchmarking at least 4 algorithm families",
                        "Automated test runner verifying edge cases and stress tests",
                        "Interactive UI or dashboard plotting execution time graphs vs input size N",
                        "Public GitHub repo with comprehensive installation instructions and test coverage",
                        "Live deployment accessible on Vercel, Render, or Streamlit Cloud"
                    ],
                    "optional_features": [
                        "Memory consumption profiling via tracemalloc",
                        "Export benchmarking reports to PDF/CSV"
                    ],
                    "tech_requirements": "Python, Flask/FastAPI/Streamlit, Git, Live Deployment",
                    "is_deployment_required": True
                }
            ]
        },

        # ==============================================================================
        # 5. Python Programming: Beginner to Automation (Programming with Mosh)
        # ==============================================================================
        {
            "slug": "python-programming-automation",
            "title": "Python Programming: Beginner to Real-World Automation",
            "category": "Programming",
            "language": "English",
            "difficulty": "Beginner",
            "estimated_duration": "12 Hours",
            "instructor": "Programming with Mosh",
            "youtube_url": "https://www.youtube.com/watch?v=_uQrJ0TkZlc",
            "thumbnail_url": "https://img.youtube.com/vi/_uQrJ0TkZlc/maxresdefault.jpg",
            "description": "Master Python from fundamental variables and data structures up through object-oriented design and real-world scripting. Learn how to process files, automate spreadsheets, and build CLI utilities.",
            "learning_objectives": [
                "Master Python syntax, variables, conditionals, loops, and collection types",
                "Write modular functions with parameters, return types, and clean variable scoping",
                "Handle file I/O operations and exception handling (try/except) safely",
                "Understand object-oriented programming (OOP) principles and automation scripting"
            ],
            "milestone_assignments": [
                {
                    "step_number": 1,
                    "total_steps": 3,
                    "evaluation_type": "algorithmic",
                    "title": "Milestone 1: Word Frequency Counter & Text Normalizer",
                    "short_description": "Write a clean Python function to parse and count unique word occurrences.",
                    "problem_statement": "Write `word_frequency(text)` that takes a string and returns a dictionary mapping lowercased words to their count, ignoring punctuation.",
                    "target_function_name": "word_frequency",
                    "starter_code": "import re\n\ndef word_frequency(text):\n    words = re.findall(r'\\b[a-zA-Z0-9]+\\b', text.lower())\n    counts = {}\n    for w in words:\n        counts[w] = counts.get(w, 0) + 1\n    return counts\n",
                    "test_cases": [
                        {"name": "Simple sentence", "input": "Hello world, hello Python!", "expected": {"hello": 2, "world": 1, "python": 1}},
                        {"name": "Single word", "input": "Code", "expected": {"code": 1}},
                        {"name": "Punctuation only", "input": "... !@#", "expected": {}}
                    ],
                    "required_keywords": ["def", "return"],
                    "tech_requirements": "Python dictionary manipulation, regex or string split",
                    "is_deployment_required": False
                },
                {
                    "step_number": 2,
                    "total_steps": 3,
                    "evaluation_type": "ai_dual",
                    "title": "Milestone 2: Automated CSV Data Cleaner & Parser",
                    "short_description": "Clean and format messy tabular data records into structured dictionaries.",
                    "problem_statement": "Write `clean_student_records(records)` that takes a list of dicts with messy keys/values, strips whitespace, converts numeric grades to integers, and removes rows with empty names.",
                    "target_function_name": "clean_student_records",
                    "starter_code": "def clean_student_records(records):\n    cleaned = []\n    for row in records:\n        name = str(row.get('name', '')).strip()\n        if not name: continue\n        try:\n            grade = int(row.get('grade', 0))\n        except (ValueError, TypeError):\n            grade = 0\n        cleaned.append({'name': name, 'grade': grade})\n    return cleaned\n",
                    "test_cases": [
                        {"name": "Messy strings & numbers", "input": [{"name": "  Alice ", "grade": "95"}, {"name": "", "grade": 80}, {"name": "Bob", "grade": 88}], "expected": [{"name": "Alice", "grade": 95}, {"name": "Bob", "grade": 88}]},
                        {"name": "Empty dataset", "input": [], "expected": []}
                    ],
                    "required_keywords": ["def", "return"],
                    "tech_requirements": "Clean data validation, error handling",
                    "is_deployment_required": False
                },
                {
                    "step_number": 3,
                    "total_steps": 3,
                    "evaluation_type": "human",
                    "title": "Capstone Project: Automated Student Task & Data Manager CLI Application",
                    "short_description": "Full modular Python tool managing tasks, calendar alerts, and file backups with SQLite or JSON.",
                    "problem_statement": "Build a modular Python application that allows students to create, prioritize, filter, and track tasks with persistent storage and report export.",
                    "required_features": [
                        "Interactive CLI or lightweight GUI/web interface supporting full CRUD operations for tasks",
                        "File persistence (JSON, CSV, or SQLite) that automatically loads and saves task states",
                        "Comprehensive input validation and error handling for missing files, invalid dates, or bad inputs",
                        "Modular code architecture split cleanly into logical files or classes",
                        "Public GitHub repository with comprehensive README.md including installation and run instructions"
                    ],
                    "optional_features": [
                        "Export task summary reports to CSV or printable format",
                        "Automated unit tests written with unittest or pytest"
                    ],
                    "tech_requirements": "Python 3.10+, SQLite/JSON, Git",
                    "is_deployment_required": False
                }
            ]
        },

        # ==============================================================================
        # 6. Python Data Analysis & Libraries (NumPy, Pandas, Matplotlib)
        # ==============================================================================
        {
            "slug": "python-data-analysis-libraries",
            "title": "Python Data Analysis & Libraries Masterclass: NumPy, Pandas & Matplotlib",
            "category": "Data Science",
            "language": "English",
            "difficulty": "Intermediate",
            "estimated_duration": "14 Hours",
            "instructor": "freeCodeCamp",
            "youtube_url": "https://www.youtube.com/watch?v=GPVsHOlRBBI",
            "thumbnail_url": "https://img.youtube.com/vi/GPVsHOlRBBI/maxresdefault.jpg",
            "description": "Learn real-world data science with Python's core analytical libraries: NumPy multi-dimensional arrays, Pandas DataFrames, and Matplotlib data visualization.",
            "learning_objectives": [
                "Master NumPy vectorization, array slicing, broadcasting, and linear algebra operations",
                "Wrangle real-world messy data with Pandas: indexing, grouping, pivoting, and merging",
                "Create publication-quality charts and visualizations with Matplotlib & Seaborn",
                "Build end-to-end exploratory data analysis pipelines for actionable business intelligence"
            ],
            "milestone_assignments": [
                {
                    "step_number": 1,
                    "total_steps": 3,
                    "evaluation_type": "algorithmic",
                    "title": "Milestone 1: Statistical Summary & Normalization Engine",
                    "short_description": "Calculate min-max normalization and statistical metrics on numeric datasets.",
                    "problem_statement": "Write `normalize_values(nums)` that performs min-max scaling: `(x - min) / (max - min)`. Return a list of floats rounded to 2 decimal places. If max == min, return list of 0.0.",
                    "target_function_name": "normalize_values",
                    "starter_code": "def normalize_values(nums):\n    if not nums: return []\n    mn, mx = min(nums), max(nums)\n    if mn == mx: return [0.0 for _ in nums]\n    return [round((x - mn) / (mx - mn), 2) for x in nums]\n",
                    "test_cases": [
                        {"name": "Standard array", "input": [10, 20, 30, 40, 50], "expected": [0.0, 0.25, 0.5, 0.75, 1.0]},
                        {"name": "Identical values", "input": [5, 5, 5], "expected": [0.0, 0.0, 0.0]},
                        {"name": "Two elements", "input": [0, 100], "expected": [0.0, 1.0]}
                    ],
                    "required_keywords": ["def", "return"],
                    "tech_requirements": "Pure math/statistics logic, floating point rounding",
                    "is_deployment_required": False
                },
                {
                    "step_number": 2,
                    "total_steps": 3,
                    "evaluation_type": "ai_dual",
                    "title": "Milestone 2: Multi-Dimensional Aggregation & Outlier Detection",
                    "short_description": "Aggregate sales data by category and flag outlier records beyond 2 standard deviations.",
                    "problem_statement": "Write `aggregate_sales(orders)` that takes a list of `{'category': str, 'amount': float}` and returns a dict mapping each category to its total sum (rounded to 2 decimal places).",
                    "target_function_name": "aggregate_sales",
                    "starter_code": "def aggregate_sales(orders):\n    totals = {}\n    for item in orders:\n        cat = item.get('category', 'Other')\n        amt = float(item.get('amount', 0))\n        totals[cat] = round(totals.get(cat, 0.0) + amt, 2)\n    return totals\n",
                    "test_cases": [
                        {"name": "Multi-category sales", "input": [{"category": "Books", "amount": 15.5}, {"category": "Tech", "amount": 200.0}, {"category": "Books", "amount": 24.5}], "expected": {"Books": 40.0, "Tech": 200.0}},
                        {"name": "Empty dataset", "input": [], "expected": {}}
                    ],
                    "required_keywords": ["def", "return"],
                    "tech_requirements": "Pandas / Dict aggregation, clean precision handling",
                    "is_deployment_required": False
                },
                {
                    "step_number": 3,
                    "total_steps": 3,
                    "evaluation_type": "human",
                    "title": "Capstone Project: Campus & E-Commerce Sales Intelligence Dashboard",
                    "short_description": "End-to-end data pipeline analyzing multi-month dataset with interactive visual reports.",
                    "problem_statement": "Perform a thorough exploratory data analysis on a real-world multi-table dataset. Identify top trends, customer segments, bottlenecks, and anomalies. Present findings with interactive charts and an executive summary.",
                    "required_features": [
                        "Data transformation and cleaning pipeline handling missing values and date parsing",
                        "At least 4 distinct analytical insights backed by charts and metrics",
                        "Clean modular Python codebase or well-structured analytical report",
                        "Public GitHub repository with findings, methodology, and visualizations",
                        "Live deployment or interactive report hosted on Streamlit Cloud or GitHub Pages"
                    ],
                    "optional_features": [
                        "Interactive dashboard built with Dash or Streamlit",
                        "Automated monthly report generator"
                    ],
                    "tech_requirements": "Python, Pandas, Matplotlib / Seaborn, SQL, Git, Live Deployment",
                    "is_deployment_required": True
                }
            ]
        },

        # ==============================================================================
        # 7. Full-Stack Web Development (The Net Ninja / Traversy Media)
        # ==============================================================================
        {
            "slug": "fullstack-mern-cloud-development",
            "title": "Full-Stack Web Development: Modern Frontend & Backend with Cloud Deployment",
            "category": "Web Development",
            "language": "English",
            "difficulty": "Intermediate",
            "estimated_duration": "22 Hours",
            "instructor": "The Net Ninja / Traversy Media",
            "youtube_url": "https://www.youtube.com/watch?v=7CqJlxBYj-M",
            "thumbnail_url": "https://img.youtube.com/vi/7CqJlxBYj-M/maxresdefault.jpg",
            "description": "Build complete production web applications from scratch with React, Node.js, Express, and MongoDB Atlas. Master REST APIs, JWT authentication, responsive Tailwind layouts, and cloud deployment.",
            "learning_objectives": [
                "Architect modern responsive frontends using React functional components and hooks",
                "Build scalable Node.js / Express RESTful APIs with input validation and middleware",
                "Design MongoDB schemas with Mongoose, indexing, and transactional integrity",
                "Deploy production full-stack applications to Render, Vercel, and cloud databases"
            ],
            "milestone_assignments": [
                {
                    "step_number": 1,
                    "total_steps": 3,
                    "evaluation_type": "algorithmic",
                    "title": "Milestone 1: URL Slugify & Query Parameter Parser",
                    "short_description": "Implement clean routing utilities for REST API URLs.",
                    "problem_statement": "Write `slugify(title)` that converts a string into a clean URL-friendly slug (lowercase, alphanumeric and hyphens only, no consecutive hyphens).",
                    "target_function_name": "slugify",
                    "starter_code": "import re\n\ndef slugify(title):\n    text = re.sub(r'[^a-zA-Z0-9\\s-]', '', str(title).lower().strip())\n    slug = re.sub(r'[\\s-]+', '-', text)\n    return slug.strip('-')\n",
                    "test_cases": [
                        {"name": "Standard Title", "input": "Learn Full Stack MERN Development!", "expected": "learn-full-stack-mern-development"},
                        {"name": "Extra whitespace & symbols", "input": "  Python  &  Flask 101  ", "expected": "python-flask-101"},
                        {"name": "Single word", "input": "SkillRock", "expected": "skillrock"}
                    ],
                    "required_keywords": ["def", "return"],
                    "tech_requirements": "Regex or string processing, clean slug formatting",
                    "is_deployment_required": False
                },
                {
                    "step_number": 2,
                    "total_steps": 3,
                    "evaluation_type": "ai_dual",
                    "title": "Milestone 2: REST Payload Validator & Sanitizer",
                    "short_description": "Validate incoming user registration and post submission JSON payloads.",
                    "problem_statement": "Write `validate_user_payload(data)` that checks if 'email' is valid, 'password' has >= 8 chars, and 'name' is non-empty. Return `(True, '')` if valid, or `(False, 'error reason')`.",
                    "target_function_name": "validate_user_payload",
                    "starter_code": "import re\n\ndef validate_user_payload(data):\n    name = str(data.get('name', '')).strip()\n    email = str(data.get('email', '')).strip()\n    password = str(data.get('password', ''))\n    if not name: return (False, 'Name is required')\n    if not re.match(r'^[^@]+@[^@]+\\.[^@]+$', email): return (False, 'Invalid email')\n    if len(password) < 8: return (False, 'Password must be at least 8 characters')\n    return (True, '')\n",
                    "test_cases": [
                        {"name": "Valid Payload", "input": {"name": "Alex", "email": "alex@campus.edu", "password": "supersecure123"}, "expected": (True, "")},
                        {"name": "Short Password", "input": {"name": "Alex", "email": "alex@campus.edu", "password": "short"}, "expected": (False, "Password must be at least 8 characters")},
                        {"name": "Missing Name", "input": {"name": "", "email": "alex@campus.edu", "password": "supersecure123"}, "expected": (False, "Name is required")}
                    ],
                    "required_keywords": ["def", "return"],
                    "tech_requirements": "Regex email validation, clean validation logic",
                    "is_deployment_required": False
                },
                {
                    "step_number": 3,
                    "total_steps": 3,
                    "evaluation_type": "human",
                    "title": "Capstone Project: Full-Stack Campus Resource & Collaboration Hub",
                    "short_description": "Full-stack MERN or Python/React application with authentication, database persistence, and live cloud deployment.",
                    "problem_statement": "Build and deploy a complete production-grade web application with responsive UI, real-time data persistence, authentication, and full CRUD functionality.",
                    "required_features": [
                        "Complete full-stack architecture (React/Vue/HTML frontend + Node.js/Python backend + MongoDB/PostgreSQL)",
                        "Secure authentication and authorization flow (sessions or JWT)",
                        "Responsive UI looking excellent on both mobile and desktop screens",
                        "Public GitHub repository with comprehensive README, setup instructions, and clean commit history",
                        "Live deployment active and accessible on Render, Vercel, or Netlify with working database"
                    ],
                    "optional_features": [
                        "Dark/Light theme toggle",
                        "Automated CI/CD GitHub Actions pipeline"
                    ],
                    "tech_requirements": "React/Node.js/Python, MongoDB/PostgreSQL, Git, Cloud Deployment",
                    "is_deployment_required": True
                }
            ]
        },

        # ==============================================================================
        # 8. Sigma Web Development Bootcamp (Hindi) (CodeWithHarry)
        # ==============================================================================
        {
            "slug": "sigma-web-development-hindi",
            "title": "Sigma Web Development Bootcamp (Hindi) — HTML to Full MERN Stack",
            "category": "Web Development",
            "language": "Hindi",
            "difficulty": "Beginner",
            "estimated_duration": "24 Hours",
            "instructor": "CodeWithHarry",
            "youtube_url": "https://www.youtube.com/watch?v=tVzUXW6siu0",
            "thumbnail_url": "https://img.youtube.com/vi/tVzUXW6siu0/maxresdefault.jpg",
            "description": "Complete Hindi web development bootcamp covering HTML5 semantics, modern CSS Flexbox and Grid, JavaScript ES6+, DOM manipulation, and building real-world MERN web applications.",
            "learning_objectives": [
                "Master HTML5 semantic tags, accessibility, and modern responsive CSS layout in Hindi",
                "Write modern JavaScript: arrow functions, promises, async/await, and event listeners",
                "Connect frontend client applications to Express / Node.js backend servers",
                "Deploy and launch complete real-world web projects online"
            ],
            "milestone_assignments": [
                {
                    "step_number": 1,
                    "total_steps": 3,
                    "evaluation_type": "algorithmic",
                    "title": "Milestone 1: CSS Hex to RGB Color Converter",
                    "short_description": "Implement a color conversion helper for web UI themes.",
                    "problem_statement": "Write `hex_to_rgb(hex_code)` that converts a 6-character hex color (e.g. '#FFFFFF' or 'FFFFFF') into an `(r, g, b)` tuple. Return None if invalid.",
                    "target_function_name": "hex_to_rgb",
                    "starter_code": "def hex_to_rgb(hex_code):\n    h = str(hex_code).lstrip('#')\n    if len(h) != 6: return None\n    try:\n        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))\n    except ValueError:\n        return None\n",
                    "test_cases": [
                        {"name": "White Color", "input": "#FFFFFF", "expected": (255, 255, 255)},
                        {"name": "SkillRock Purple", "input": "#5145CD", "expected": (81, 69, 205)},
                        {"name": "Invalid hex", "input": "#ZZZZZZ", "expected": None}
                    ],
                    "required_keywords": ["def", "return"],
                    "tech_requirements": "Base 16 parsing, tuple formatting",
                    "is_deployment_required": False
                },
                {
                    "step_number": 2,
                    "total_steps": 3,
                    "evaluation_type": "ai_dual",
                    "title": "Milestone 2: Async Event Debouncer & Search Filter",
                    "short_description": "Filter a collection of products/courses by keyword with ranking.",
                    "problem_statement": "Write `search_filter(items, query)` that returns items where query appears in title or tags (case-insensitive), sorted with exact title matches first.",
                    "target_function_name": "search_filter",
                    "starter_code": "def search_filter(items, query):\n    q = str(query).lower().strip()\n    if not q: return items\n    matched = []\n    for item in items:\n        title = str(item.get('title', '')).lower()\n        tags = [str(t).lower() for t in item.get('tags', [])]\n        if q in title or any(q in t for t in tags):\n            score = 1 if title.startswith(q) else 2\n            matched.append((score, item))\n    matched.sort(key=lambda x: x[0])\n    return [m[1] for m in matched]\n",
                    "test_cases": [
                        {"name": "Search query match", "input": ([{"title": "Python Basics", "tags": ["code"]}, {"title": "Web Dev", "tags": ["html"]}], "python"), "expected": [{"title": "Python Basics", "tags": ["code"]}]},
                        {"name": "Empty query", "input": ([{"title": "Java", "tags": []}], ""), "expected": [{"title": "Java", "tags": []}]}
                    ],
                    "required_keywords": ["def", "return"],
                    "tech_requirements": "Clean search ranking, filtering logic",
                    "is_deployment_required": False
                },
                {
                    "step_number": 3,
                    "total_steps": 3,
                    "evaluation_type": "human",
                    "title": "Capstone Project: Interactive Real-Time Weather & Location Intelligence Dashboard",
                    "short_description": "Deploy a complete interactive web dashboard fetching live public APIs with caching.",
                    "problem_statement": "Build and deploy an interactive web dashboard in HTML/CSS/JS or React that connects to live external APIs, visualizes forecasts, and provides responsive search.",
                    "required_features": [
                        "Clean responsive UI with search, autocomplete, and visual feedback states",
                        "Live API integration with error handling for network outages or invalid cities",
                        "Local storage or server-side caching of recently searched queries",
                        "Public GitHub repo with documentation, screenshots, and setup steps",
                        "Live deployment on Vercel, Netlify, or Render"
                    ],
                    "optional_features": [
                        "Interactive map integration (Leaflet or Google Maps)",
                        "Dark/Light theme toggle"
                    ],
                    "tech_requirements": "JavaScript / React / Python, REST APIs, Git, Live Deployment",
                    "is_deployment_required": True
                }
            ]
        },

        # ==============================================================================
        # 9. Kali Linux & Command-Line Mastery (NetworkChuck)
        # ==============================================================================
        {
            "slug": "kali-linux-command-line-mastery",
            "title": "Kali Linux Fundamentals & Command-Line Mastery for Hackers",
            "category": "Cybersecurity",
            "language": "English",
            "difficulty": "Beginner",
            "estimated_duration": "15 Hours",
            "instructor": "NetworkChuck",
            "youtube_url": "https://www.youtube.com/watch?v=VbEx7B_PTOE",
            "thumbnail_url": "https://img.youtube.com/vi/VbEx7B_PTOE/maxresdefault.jpg",
            "description": "Master the Linux command line, filesystem hierarchy, file permissions (chmod/chown), bash scripting, pipes, grep, networking commands, package management, and security tools on Kali Linux.",
            "learning_objectives": [
                "Navigate the Linux directory tree and manage processes with confidence",
                "Master Linux file security, user permissions, and sudo privileges",
                "Write powerful bash automation scripts with loops, pipes, and awk/sed",
                "Utilize essential Kali Linux network reconnaissance tools ethically"
            ],
            "milestone_assignments": [
                {
                    "step_number": 1,
                    "total_steps": 3,
                    "evaluation_type": "algorithmic",
                    "title": "Milestone 1: Linux Octal Permission Converter & Auditor",
                    "short_description": "Convert and validate Linux file permission strings into octal representations.",
                    "problem_statement": "Write `permission_to_octal(perm_str)` that converts a 9-char permission string like 'rwxr-xr--' into its octal string '754'. Return 'Invalid' if not exactly 9 chars or invalid symbols.",
                    "target_function_name": "permission_to_octal",
                    "starter_code": "def permission_to_octal(perm_str):\n    if len(perm_str) != 9: return 'Invalid'\n    octal = ''\n    for i in range(0, 9, 3):\n        chunk = perm_str[i:i+3]\n        val = 0\n        if chunk[0] == 'r': val += 4\n        elif chunk[0] != '-': return 'Invalid'\n        if chunk[1] == 'w': val += 2\n        elif chunk[1] != '-': return 'Invalid'\n        if chunk[2] == 'x': val += 1\n        elif chunk[2] != '-': return 'Invalid'\n        octal += str(val)\n    return octal\n",
                    "test_cases": [
                        {"name": "Standard 755", "input": "rwxr-xr-x", "expected": "755"},
                        {"name": "Restricted 700", "input": "rwx------", "expected": "700"},
                        {"name": "ReadOnly 644", "input": "rw-r--r--", "expected": "644"},
                        {"name": "Invalid characters", "input": "rwxzzzzzz", "expected": "Invalid"}
                    ],
                    "required_keywords": ["def", "return"],
                    "tech_requirements": "Binary/octal conversion, bitmask representation",
                    "is_deployment_required": False
                },
                {
                    "step_number": 2,
                    "total_steps": 3,
                    "evaluation_type": "ai_dual",
                    "title": "Milestone 2: Security Log Parser & Brute-Force Detector",
                    "short_description": "Parse mock Linux auth.log lines and extract IP addresses with repeated failed attempts.",
                    "problem_statement": "Write `detect_brute_force(log_lines, threshold=3)` that parses auth log lines, counts 'Failed password' occurrences per IP, and returns a sorted list of IPs that exceeded the threshold.",
                    "target_function_name": "detect_brute_force",
                    "starter_code": "import re\n\ndef detect_brute_force(log_lines, threshold=3):\n    failures = {}\n    pattern = r'Failed password.*from\\s+([0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+)'\n    for line in log_lines:\n        match = re.search(pattern, line)\n        if match:\n            ip = match.group(1)\n            failures[ip] = failures.get(ip, 0) + 1\n    flagged = [ip for ip, count in failures.items() if count >= threshold]\n    return sorted(flagged)\n",
                    "test_cases": [
                        {"name": "Repeated failed attempts", "input": (["Failed password for root from 192.168.1.50 port 22", "Failed password for root from 192.168.1.50 port 22", "Failed password for admin from 192.168.1.50 port 22", "Accepted password from 10.0.0.1"], 3), "expected": ["192.168.1.50"]},
                        {"name": "No brute force", "input": (["Failed password for root from 10.0.0.2"], 3), "expected": []}
                    ],
                    "required_keywords": ["def", "return"],
                    "tech_requirements": "Regex log parsing, dictionary frequency aggregation",
                    "is_deployment_required": False
                },
                {
                    "step_number": 3,
                    "total_steps": 3,
                    "evaluation_type": "human",
                    "title": "Capstone Project: Automated Linux Security Hardening & Audit Script Suite",
                    "short_description": "Modular bash/Python security audit script checking open ports, world-writable files, and firewall rules.",
                    "problem_statement": "Create a modular security hardening script suite for Linux. The tool must inspect user accounts, check SSH configuration, flag world-writable directories, and generate a clear markdown/HTML security audit score report.",
                    "required_features": [
                        "Inspect system user permissions, detecting accounts with empty passwords or root privileges",
                        "Audit SSH daemon configuration (verifying PermitRootLogin and PasswordAuthentication flags)",
                        "Scan for world-writable files and dangerous SUID binaries",
                        "Generate a structured Markdown or HTML security assessment report with remediation advice",
                        "Public GitHub repository with documentation, sample audit output, and installation instructions"
                    ],
                    "optional_features": [
                        "Automated remediation flag (`--fix`) applying recommended settings safely",
                        "Slack or webhook notification upon critical finding"
                    ],
                    "tech_requirements": "Bash / Python, Linux administration, Git",
                    "is_deployment_required": False
                }
            ]
        },

        # ==============================================================================
        # 10. Practical Ethical Hacking (freeCodeCamp)
        # ==============================================================================
        {
            "slug": "ethical-hacking-penetration-testing",
            "title": "Practical Ethical Hacking & Penetration Testing Masterclass",
            "category": "Cybersecurity",
            "language": "English",
            "difficulty": "Intermediate",
            "estimated_duration": "15 Hours",
            "instructor": "freeCodeCamp",
            "youtube_url": "https://www.youtube.com/watch?v=WnN0WUrhHuk",
            "thumbnail_url": "https://img.youtube.com/vi/WnN0WUrhHuk/maxresdefault.jpg",
            "description": "Learn practical offensive and defensive security: reconnaissance, network scanning with Nmap, vulnerability assessment, web application security (OWASP Top 10), and ethical penetration testing.",
            "learning_objectives": [
                "Execute structured reconnaissance and network footprinting ethically",
                "Analyze network packets and protocol handshakes with Wireshark",
                "Identify and remediate OWASP Top 10 vulnerabilities (SQLi, XSS, CSRF, IDOR)",
                "Draft comprehensive vulnerability assessment and remediation reports"
            ],
            "milestone_assignments": [
                {
                    "step_number": 1,
                    "total_steps": 3,
                    "evaluation_type": "algorithmic",
                    "title": "Milestone 1: Port Scanner Output Parser & Service Classifier",
                    "short_description": "Parse raw Nmap port scan output into structured service dictionaries.",
                    "problem_statement": "Write `parse_open_ports(nmap_output)` that extracts open ports and services into a dict `{'port_number': 'service_name'}` from raw port lines like '80/tcp open http'.",
                    "target_function_name": "parse_open_ports",
                    "starter_code": "import re\n\ndef parse_open_ports(nmap_output):\n    results = {}\n    pattern = r'(\\d+)/tcp\\s+open\\s+([a-zA-Z0-9_-]+)'\n    for line in nmap_output.splitlines():\n        match = re.search(pattern, line)\n        if match:\n            results[str(match.group(1))] = match.group(2)\n    return results\n",
                    "test_cases": [
                        {"name": "Standard scan output", "input": "22/tcp open ssh\n80/tcp open http\n443/tcp open https", "expected": {"22": "ssh", "80": "http", "443": "https"}},
                        {"name": "Filtered ports ignored", "input": "21/tcp closed ftp\n80/tcp open http", "expected": {"80": "http"}},
                        {"name": "Empty scan", "input": "", "expected": {}}
                    ],
                    "required_keywords": ["def", "return"],
                    "tech_requirements": "Regex parsing, port mapping",
                    "is_deployment_required": False
                },
                {
                    "step_number": 2,
                    "total_steps": 3,
                    "evaluation_type": "ai_dual",
                    "title": "Milestone 2: HTTP Security Header Scanner & Auditor",
                    "short_description": "Analyze response headers for critical defensive headers (CSP, HSTS, X-Frame-Options).",
                    "problem_statement": "Write `audit_security_headers(headers)` that checks for 'Strict-Transport-Security', 'Content-Security-Policy', 'X-Frame-Options', and 'X-Content-Type-Options'. Return a score (0-100) and list of missing headers.",
                    "target_function_name": "audit_security_headers",
                    "starter_code": "def audit_security_headers(headers):\n    required = ['strict-transport-security', 'content-security-policy', 'x-frame-options', 'x-content-type-options']\n    lower_headers = {k.lower(): v for k, v in headers.items()}\n    missing = [h for h in required if h not in lower_headers]\n    score = int(((len(required) - len(missing)) / len(required)) * 100)\n    return {'score': score, 'missing': missing}\n",
                    "test_cases": [
                        {"name": "All headers present", "input": {"Strict-Transport-Security": "max-age=31536000", "Content-Security-Policy": "default-src 'self'", "X-Frame-Options": "DENY", "X-Content-Type-Options": "nosniff"}, "expected": {"score": 100, "missing": []}},
                        {"name": "Two headers missing", "input": {"X-Frame-Options": "DENY", "X-Content-Type-Options": "nosniff"}, "expected": {"score": 50, "missing": ["strict-transport-security", "content-security-policy"]}}
                    ],
                    "required_keywords": ["def", "return"],
                    "tech_requirements": "Header dictionary lookup, defensive security metrics",
                    "is_deployment_required": False
                },
                {
                    "step_number": 3,
                    "total_steps": 3,
                    "evaluation_type": "human",
                    "title": "Capstone Project: Web Security Vulnerability Scanner & Penetration Test Report",
                    "short_description": "Automated security scanning tool that tests for common web misconfigurations and generates remediation reports.",
                    "problem_statement": "Develop an automated command-line security scanner that inspects target web applications for insecure cookies, missing headers, SQL injection vulnerability indicators, and exposed debug endpoints.",
                    "required_features": [
                        "Inspect target URL for critical security headers, HTTPS misconfigurations, and cookie security flags (Secure, HttpOnly, SameSite)",
                        "Passive vulnerability identification without causing denial of service or destructive actions",
                        "Generate structured executive summary report with risk ratings (Critical, High, Medium, Low)",
                        "Clear remediation instructions for web developers to fix each identified vulnerability",
                        "Public GitHub repo with documentation, ethical disclaimer, and instructions"
                    ],
                    "optional_features": [
                        "Export report to HTML or JSON format",
                        "Subdomain discovery module using DNS lookups"
                    ],
                    "tech_requirements": "Python, Requests/HTTP, Git, Ethical Hacking Best Practices",
                    "is_deployment_required": False
                }
            ]
        },

        # ==============================================================================
        # 11. UI/UX Design Masterclass with Figma (DesignCourse - Gary Simon)
        # ==============================================================================
        {
            "slug": "figma-ui-ux-design-masterclass",
            "title": "Figma UI/UX Design Masterclass: Wireframing to Interactive Prototyping",
            "category": "Design",
            "language": "English",
            "difficulty": "Beginner",
            "estimated_duration": "10 Hours",
            "instructor": "Gary Simon (DesignCourse)",
            "youtube_url": "https://www.youtube.com/watch?v=i48q0JQQ2EA",
            "thumbnail_url": "https://img.youtube.com/vi/i48q0JQQ2EA/maxresdefault.jpg",
            "description": "Master modern UI/UX design in Figma. Learn design theory, typography hierarchy, whitespace, color contrast, autolayout, component variants, design tokens, micro-interactions, and accessibility standards.",
            "learning_objectives": [
                "Master Figma tools: Autolayout 5.0, Component Variants, and Design Tokens",
                "Apply typography hierarchy, 8pt grid systems, and harmonious color theory",
                "Design accessible interfaces meeting WCAG 2.1 AA contrast standards",
                "Build interactive clickable prototypes demonstrating realistic user journeys"
            ],
            "milestone_assignments": [
                {
                    "step_number": 1,
                    "total_steps": 3,
                    "evaluation_type": "algorithmic",
                    "title": "Milestone 1: WCAG Color Contrast & Accessibility Ratio Calculator",
                    "short_description": "Calculate relative luminance and contrast ratio according to WCAG 2.1 specifications.",
                    "problem_statement": "Write `is_wcag_aa_compliant(contrast_ratio, is_large_text=False)` that returns True if contrast ratio meets WCAG AA standards (>= 4.5 for normal text, >= 3.0 for large text).",
                    "target_function_name": "is_wcag_aa_compliant",
                    "starter_code": "def is_wcag_aa_compliant(contrast_ratio, is_large_text=False):\n    req = 3.0 if is_large_text else 4.5\n    return float(contrast_ratio) >= req\n",
                    "test_cases": [
                        {"name": "Compliant Normal Text", "input": (4.6, False), "expected": True},
                        {"name": "Non-compliant Normal Text", "input": (3.8, False), "expected": False},
                        {"name": "Compliant Large Text", "input": (3.2, True), "expected": True},
                        {"name": "High contrast black on white", "input": (21.0, False), "expected": True}
                    ],
                    "required_keywords": ["def", "return"],
                    "tech_requirements": "WCAG AA ratio logic",
                    "is_deployment_required": False
                },
                {
                    "step_number": 2,
                    "total_steps": 3,
                    "evaluation_type": "ai_dual",
                    "title": "Milestone 2: Responsive Design Token JSON Generator",
                    "short_description": "Generate structured design token dictionary defining colors, typography, and spacing scales.",
                    "problem_statement": "Write `generate_design_tokens(primary_color, base_font_size=16)` that outputs a structured design system dictionary with 8pt spacing tokens ('sm': 8, 'md': 16, 'lg': 24, 'xl': 32) and typography sizes.",
                    "target_function_name": "generate_design_tokens",
                    "starter_code": "def generate_design_tokens(primary_color, base_font_size=16):\n    return {\n        'colors': {'primary': str(primary_color).strip()},\n        'spacing': {'sm': 8, 'md': 16, 'lg': 24, 'xl': 32},\n        'typography': {'base': base_font_size, 'h1': base_font_size * 2, 'h2': int(base_font_size * 1.5)}\n    }\n",
                    "test_cases": [
                        {"name": "Standard design tokens", "input": ("#5145CD", 16), "expected": {"colors": {"primary": "#5145CD"}, "spacing": {"sm": 8, "md": 16, "lg": 24, "xl": 32}, "typography": {"base": 16, "h1": 32, "h2": 24}}}
                    ],
                    "required_keywords": ["def", "return"],
                    "tech_requirements": "Design token structuring",
                    "is_deployment_required": False
                },
                {
                    "step_number": 3,
                    "total_steps": 3,
                    "evaluation_type": "human",
                    "title": "Capstone Project: Complete SaaS Product UI/UX Case Study & Interactive Prototype",
                    "short_description": "Full Figma prototype and case study for a multi-screen SaaS application with design system.",
                    "problem_statement": "Design a complete end-to-end user experience for a web SaaS platform in Figma. Deliver responsive desktop and mobile screens, interactive component states, and a thorough case study documentation.",
                    "required_features": [
                        "Complete Figma design file with interactive prototype (connecting buttons to modal/flow states)",
                        "Comprehensive design system with typography scale, color tokens, and reusable component variants",
                        "Responsive layouts covering both desktop (1440px) and mobile (390px) viewports",
                        "Accessibility verification showing minimum 4.5:1 color contrast across all text elements",
                        "Public case study link or Behance/Notion portfolio presentation detailing problem statement and user flows"
                    ],
                    "optional_features": [
                        "Micro-interaction animated transitions using Figma Smart Animate",
                        "Dark mode variant of all key screens"
                    ],
                    "tech_requirements": "Figma, Interactive Prototyping, Case Study Documentation",
                    "is_deployment_required": False
                }
            ]
        },

        # ==============================================================================
        # 12. Complete Product Design & UX Research (Jesse Showalter / Curated)
        # ==============================================================================
        {
            "slug": "product-design-ux-research",
            "title": "Complete Product Design, User Research & Design Systems",
            "category": "Design",
            "language": "English",
            "difficulty": "Intermediate",
            "estimated_duration": "12 Hours",
            "instructor": "Jesse Showalter / Curated",
            "youtube_url": "https://www.youtube.com/watch?v=c9Wg6Ge_YGU",
            "thumbnail_url": "https://img.youtube.com/vi/c9Wg6Ge_YGU/maxresdefault.jpg",
            "description": "Explore user-centered product design: qualitative user research, persona creation, user journey mapping, information architecture, wireframing, and building production design systems.",
            "learning_objectives": [
                "Conduct user interviews and synthesize insights into user personas",
                "Map comprehensive user journey maps identifying drop-offs and friction points",
                "Structure intuitive information architecture with user flow diagrams",
                "Conduct usability testing and iterate based on quantitative metrics"
            ],
            "milestone_assignments": [
                {
                    "step_number": 1,
                    "total_steps": 3,
                    "evaluation_type": "algorithmic",
                    "title": "Milestone 1: User Journey Friction Scorer",
                    "short_description": "Calculate user friction index from step ratings and completion drop-offs.",
                    "problem_statement": "Write `calculate_journey_friction(step_scores)` that takes a list of step difficulty ratings (1 to 5) and returns the average friction score rounded to 2 decimal places. Return 0.0 if empty.",
                    "target_function_name": "calculate_journey_friction",
                    "starter_code": "def calculate_journey_friction(step_scores):\n    if not step_scores: return 0.0\n    return round(sum(step_scores) / len(step_scores), 2)\n",
                    "test_cases": [
                        {"name": "Standard step ratings", "input": [2, 3, 4, 1, 5], "expected": 3.0},
                        {"name": "Low friction journey", "input": [1, 1, 2], "expected": 1.33},
                        {"name": "Empty list", "input": [], "expected": 0.0}
                    ],
                    "required_keywords": ["def", "return"],
                    "tech_requirements": "Statistical averaging, rounding",
                    "is_deployment_required": False
                },
                {
                    "step_number": 2,
                    "total_steps": 3,
                    "evaluation_type": "ai_dual",
                    "title": "Milestone 2: Usability Feedback Severity Categorizer",
                    "short_description": "Classify qualitative user feedback into severity levels (Critical, Major, Minor).",
                    "problem_statement": "Write `classify_feedback(feedback_text)` that flags 'Critical' if words like 'crash', 'cannot submit', 'blocked' appear; 'Major' if 'confusing', 'slow', 'lost' appear; otherwise 'Minor'.",
                    "target_function_name": "classify_feedback",
                    "starter_code": "def classify_feedback(feedback_text):\n    text = str(feedback_text).lower()\n    critical_kws = ['crash', 'cannot submit', 'blocked', 'broken']\n    major_kws = ['confusing', 'slow', 'lost', 'hard to find']\n    if any(k in text for k in critical_kws): return 'Critical'\n    if any(k in text for k in major_kws): return 'Major'\n    return 'Minor'\n",
                    "test_cases": [
                        {"name": "Critical bug reported", "input": "The page is completely broken and I cannot submit.", "expected": "Critical"},
                        {"name": "Major confusion", "input": "The checkout button was confusing to find.", "expected": "Major"},
                        {"name": "Minor feedback", "input": "I like the color scheme.", "expected": "Minor"}
                    ],
                    "required_keywords": ["def", "return"],
                    "tech_requirements": "Keyword extraction, text matching",
                    "is_deployment_required": False
                },
                {
                    "step_number": 3,
                    "total_steps": 3,
                    "evaluation_type": "human",
                    "title": "Capstone Project: Comprehensive Product Design Case Study & Research Portfolio",
                    "short_description": "Complete user research case study with personas, journey maps, wireframes, and usability findings.",
                    "problem_statement": "Conduct an end-to-end product design cycle for a real-world problem. Produce user research personas, journey maps, low-fidelity wireframes, high-fidelity prototypes, and usability testing analysis.",
                    "required_features": [
                        "User research synthesis with at least 2 distinct user personas and problem statements",
                        "User journey map illustrating emotions, pain points, and opportunities across each step",
                        "Interactive prototype covering the primary user happy path and edge cases",
                        "Usability testing report documenting user feedback and design iterations",
                        "Public case study link (Notion, Medium, Behance, or GitHub Portfolio)"
                    ],
                    "optional_features": [
                        "Information architecture site map diagram",
                        "Design system tokens documentation"
                    ],
                    "tech_requirements": "Figma / Miro / Notion, UX Research Frameworks, Case Study",
                    "is_deployment_required": False
                }
            ]
        },

        # ==============================================================================
        # 13. JavaScript Mastery (SuperSimpleDev / Curated)
        # ==============================================================================
        {
            "slug": "javascript-mastery-modern-web",
            "title": "JavaScript Mastery: DOM Manipulation, Async APIs & Modern Web Apps",
            "category": "Web Development",
            "language": "English",
            "difficulty": "Beginner",
            "estimated_duration": "12 Hours",
            "instructor": "SuperSimpleDev / Curated",
            "youtube_url": "https://www.youtube.com/watch?v=EerdGm-ehJQ",
            "thumbnail_url": "https://img.youtube.com/vi/EerdGm-ehJQ/maxresdefault.jpg",
            "description": "Master JavaScript from variables, conditionals, arrays, and objects through DOM manipulation, event listeners, promises, fetch API, and async/await for modern interactive web development.",
            "learning_objectives": [
                "Master modern JavaScript ES6+ syntax, scoping, and arrow functions",
                "Manipulate DOM elements dynamically and listen to complex user interactions",
                "Handle asynchronous data fetching using Promises and async/await",
                "Build reactive frontend features without bloated external frameworks"
            ],
            "milestone_assignments": [
                {
                    "step_number": 1,
                    "total_steps": 3,
                    "evaluation_type": "algorithmic",
                    "title": "Milestone 1: Deep Array Flattener & Deduplicator",
                    "short_description": "Flatten nested arrays of arbitrary depth into a flat, unique list.",
                    "problem_statement": "Write `flatten_array(nested_list)` that flattens nested lists of integers into a single flat list.",
                    "target_function_name": "flatten_array",
                    "starter_code": "def flatten_array(nested_list):\n    result = []\n    for item in nested_list:\n        if isinstance(item, list):\n            result.extend(flatten_array(item))\n        else:\n            result.append(item)\n    return result\n",
                    "test_cases": [
                        {"name": "Multi-level nesting", "input": [1, [2, [3, 4], 5], 6], "expected": [1, 2, 3, 4, 5, 6]},
                        {"name": "Flat array", "input": [1, 2, 3], "expected": [1, 2, 3]},
                        {"name": "Empty list", "input": [], "expected": []}
                    ],
                    "required_keywords": ["def", "return"],
                    "tech_requirements": "Recursive list traversal",
                    "is_deployment_required": False
                },
                {
                    "step_number": 2,
                    "total_steps": 3,
                    "evaluation_type": "ai_dual",
                    "title": "Milestone 2: In-Memory Key-Value Store with TTL",
                    "short_description": "Implement a simple cache store with expiration tracking.",
                    "problem_statement": "Implement `SimpleCache` with `set(key, val, ttl_seconds)` and `get(key)`. If expired or missing, return None.",
                    "target_function_name": "create_cache_test",
                    "starter_code": "import time\n\nclass SimpleCache:\n    def __init__(self):\n        self.store = {}\n    def set(self, key, val, ttl=300):\n        self.store[key] = (val, time.time() + ttl)\n    def get(self, key):\n        if key not in self.store: return None\n        val, exp = self.store[key]\n        if time.time() > exp:\n            del self.store[key]\n            return None\n        return val\n\ndef create_cache_test(k, v):\n    c = SimpleCache()\n    c.set(k, v, ttl=60)\n    return c.get(k)\n",
                    "test_cases": [
                        {"name": "Get active key", "input": ("username", "alex"), "expected": "alex"},
                        {"name": "Non-existent key", "input": ("missing", None), "expected": None}
                    ],
                    "required_keywords": ["def", "return"],
                    "tech_requirements": "Cache expiration logic, dictionary storage",
                    "is_deployment_required": False
                },
                {
                    "step_number": 3,
                    "total_steps": 3,
                    "evaluation_type": "human",
                    "title": "Capstone Project: Interactive Student Tool & Productivity Application",
                    "short_description": "Full responsive client application with local state management, persistent storage, and live deployment.",
                    "problem_statement": "Build an interactive web application entirely in vanilla JavaScript or modern frontend library. Must feature rich DOM updates, local storage persistence, filtering, and responsive design.",
                    "required_features": [
                        "Dynamic DOM manipulation with zero page refreshes during interactive operations",
                        "State persistence using HTML5 localStorage or IndexedDB",
                        "Responsive layout working cleanly across mobile, tablet, and desktop viewports",
                        "Public GitHub repo with documentation, clean structure, and modular code",
                        "Live deployment accessible on Vercel, Netlify, or GitHub Pages"
                    ],
                    "optional_features": [
                        "Offline capability with Service Worker / PWA manifest",
                        "Dark/Light theme toggle"
                    ],
                    "tech_requirements": "JavaScript, HTML5, CSS3, Git, Live Deployment",
                    "is_deployment_required": True
                }
            ]
        },

        # ==============================================================================
        # 14. Machine Learning & AI with Python (freeCodeCamp / Andrew Ng)
        # ==============================================================================
        {
            "slug": "machine-learning-ai-python",
            "title": "Machine Learning & AI with Python: Practical Neural Networks & Model Deployment",
            "category": "AI & Machine Learning",
            "language": "English",
            "difficulty": "Intermediate",
            "estimated_duration": "16 Hours",
            "instructor": "freeCodeCamp / Andrew Ng",
            "youtube_url": "https://www.youtube.com/watch?v=i_LwzRVP7bg",
            "thumbnail_url": "https://img.youtube.com/vi/i_LwzRVP7bg/maxresdefault.jpg",
            "description": "Learn practical machine learning: supervised algorithms (regression, classification), model evaluation metrics, deep learning neural networks with TensorFlow/PyTorch, and deploying predictive ML models.",
            "learning_objectives": [
                "Understand cost functions, gradient descent, and training convergence",
                "Train regression and classification models using Scikit-Learn",
                "Evaluate models with precision, recall, F1-score, and confusion matrices",
                "Deploy machine learning inference endpoints using FastAPI or Streamlit"
            ],
            "milestone_assignments": [
                {
                    "step_number": 1,
                    "total_steps": 3,
                    "evaluation_type": "algorithmic",
                    "title": "Milestone 1: Mean Squared Error & Accuracy Metric Calculator",
                    "short_description": "Compute MSE and classification accuracy without external machine learning libraries.",
                    "problem_statement": "Write `calculate_mse(actual, predicted)` that computes the Mean Squared Error: `sum((a - p)**2) / n`, rounded to 2 decimal places.",
                    "target_function_name": "calculate_mse",
                    "starter_code": "def calculate_mse(actual, predicted):\n    if not actual or len(actual) != len(predicted): return 0.0\n    sq_errors = [(a - p)**2 for a, p in zip(actual, predicted)]\n    return round(sum(sq_errors) / len(actual), 2)\n",
                    "test_cases": [
                        {"name": "Standard vectors", "input": ([10, 20, 30], [12, 18, 33]), "expected": 5.67},
                        {"name": "Exact predictions", "input": ([5, 5, 5], [5, 5, 5]), "expected": 0.0},
                        {"name": "Empty vectors", "input": ([], []), "expected": 0.0}
                    ],
                    "required_keywords": ["def", "return"],
                    "tech_requirements": "Mathematical computation, rounding",
                    "is_deployment_required": False
                },
                {
                    "step_number": 2,
                    "total_steps": 3,
                    "evaluation_type": "ai_dual",
                    "title": "Milestone 2: Train/Test Dataset Splitter with Stratification",
                    "short_description": "Implement a deterministic dataset split function into training and validation sets.",
                    "problem_statement": "Write `train_test_split_simple(dataset, test_ratio=0.2)` that splits a list into `(train_set, test_set)` according to ratio.",
                    "target_function_name": "train_test_split_simple",
                    "starter_code": "def train_test_split_simple(dataset, test_ratio=0.2):\n    n = len(dataset)\n    split_idx = int(n * (1.0 - test_ratio))\n    return (dataset[:split_idx], dataset[split_idx:])\n",
                    "test_cases": [
                        {"name": "10 items with 0.2 ratio", "input": (list(range(10)), 0.2), "expected": (list(range(8)), [8, 9])},
                        {"name": "5 items with 0.4 ratio", "input": (list(range(5)), 0.4), "expected": ([0, 1, 2], [3, 4])}
                    ],
                    "required_keywords": ["def", "return"],
                    "tech_requirements": "List slicing, data partitioning",
                    "is_deployment_required": False
                },
                {
                    "step_number": 3,
                    "total_steps": 3,
                    "evaluation_type": "human",
                    "title": "Capstone Project: End-to-End Machine Learning Predictive Application",
                    "short_description": "Trained machine learning model deployed with an interactive web UI and public GitHub repo.",
                    "problem_statement": "Train, evaluate, and deploy a machine learning model for a real-world predictive task (e.g. house price predictor, sentiment analysis, or student grade predictor). Deliver an interactive web app and model artifacts.",
                    "required_features": [
                        "Complete model training notebook or script with data preprocessing and feature scaling",
                        "Cross-validation and model evaluation metrics (R2/RMSE or Accuracy/F1-score)",
                        "Interactive web UI (Streamlit, Flask, or Gradio) allowing users to enter features and receive live predictions",
                        "Public GitHub repo with serialized model, instructions, and data methodology",
                        "Live deployment accessible online on Streamlit Cloud or Render"
                    ],
                    "optional_features": [
                        "Feature importance visualization chart",
                        "Model explainability with SHAP or LIME"
                    ],
                    "tech_requirements": "Python, Scikit-Learn/TensorFlow, Streamlit/Flask, Git, Live Deployment",
                    "is_deployment_required": True
                }
            ]
        }
    ]
