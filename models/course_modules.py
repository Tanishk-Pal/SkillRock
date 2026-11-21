"""
SkillRock — Six-Module Course Architecture & Learning Resources
Powers the 6 Educational Modules across all SkillRock Courses:
  MODULE 01: LEARN (Syllabus, Chapters, Notes, Video Player & Watch Tracking)
  MODULE 02: PRACTICE & TEST (Topic Tests, MCQs, Output Prediction, Coding Sandbox)
  MODULE 03: BUILD (Milestone Practical Project, Rubrics, GitHub & Deployment Review)
  MODULE 04: INTERVIEW PREPARATION (50+ Domain Technical Questions + HR Interview Toolkit)
  MODULE 05: CAREER & COMMUNICATION (English Academy 10 Lessons, ATS Resume, Opportunities)
  MODULE 06: CERTIFICATION & VERIFICATION (SHA-256 Hash, QR Online Verification)
"""

import re
from typing import Dict, List, Any

# ==============================================================================
# MODULE 04: TECHNICAL & HR INTERVIEW QUESTION BANKS
# ==============================================================================

PYTHON_INTERVIEW_QUESTIONS = [
    {
        "id": "py-q1",
        "question": "What is the difference between mutable and immutable types in Python? Give examples.",
        "difficulty": "Beginner",
        "category": "Core Python",
        "short_answer": "Immutable objects cannot be modified after creation (int, float, str, tuple, frozenset), whereas mutable objects can be modified in-place without changing memory address (list, dict, set).",
        "detailed_explanation": "In Python, every variable is a reference to an object in memory. When you reassign or modify an immutable object (e.g. string concatenation `s += '!'`), Python allocates a new object in memory. In contrast, mutable objects like lists support in-place mutations (e.g. `.append()`, `.extend()`) without changing `id(obj)`.",
        "code_example": "# Immutable example:\ns = 'Skill'\nprint(id(s))\ns += 'Rock'  # Creates new object\nprint(id(s))  # Different memory address\n\n# Mutable example:\nlst = [1, 2]\nprint(id(lst))\nlst.append(3)  # Modifies in-place\nprint(id(lst))  # Same memory address",
        "related_topic": "Memory Management & Object Model"
    },
    {
        "id": "py-q2",
        "question": "How does Python manage memory, and what role does Garbage Collection play?",
        "difficulty": "Intermediate",
        "category": "Architecture & Internals",
        "short_answer": "Python uses reference counting as its primary memory management mechanism, supplemented by a cyclic generational garbage collector (gc module) to detect and resolve circular references.",
        "detailed_explanation": "Every Python object contains an internal reference counter (`ob_refcnt`). When this count drops to zero, memory is freed immediately. However, circular references (where object A points to B, and B points to A) prevent reference counts from ever reaching 0. To fix this, Python runs a generational garbage collector (Generations 0, 1, and 2) using threshold heuristics to detect isolated reference cycles.",
        "code_example": "import sys, gc\na = []\nprint(sys.getrefcount(a))  # Reference count tracker\n\n# Circular reference:\nb = []\na.append(b)\nb.append(a)\ndel a, b  # Cyclic GC reclaims this memory",
        "related_topic": "Garbage Collection & CPython Runtime"
    },
    {
        "id": "py-q3",
        "question": "What is the Global Interpreter Lock (GIL), and how does it impact multi-threaded programs?",
        "difficulty": "Advanced",
        "category": "Concurrency & Performance",
        "short_answer": "The GIL is a mutex in CPython that prevents multiple native threads from executing Python bytecode simultaneously, ensuring thread-safe CPython memory management.",
        "detailed_explanation": "Because CPython's memory management is not thread-safe, the GIL restricts thread execution to one thread per process at a time. For CPU-bound tasks (e.g. mathematical calculations, image rendering), multi-threading in Python does not provide parallel speedup. Instead, developers use the `multiprocessing` module (spawning distinct OS processes with individual memory spaces) or asynchronous I/O (`asyncio`) for I/O-bound concurrency.",
        "code_example": "from multiprocessing import Pool\n\ndef heavy_calculation(n):\n    return sum(i * i for i in range(n))\n\nif __name__ == '__main__':\n    # Bypasses the GIL by leveraging multi-core parallelism:\n    with Pool(4) as p:\n        results = p.map(heavy_calculation, [1000000, 2000000, 3000000])",
        "related_topic": "CPython GIL & Concurrency"
    },
    {
        "id": "py-q4",
        "question": "Explain Python Generators, the `yield` statement, and memory advantages over Lists.",
        "difficulty": "Beginner",
        "category": "Functional Python",
        "short_answer": "Generators are lazy iterators that produce values one at a time using the `yield` keyword instead of computing and storing entire sequences in memory.",
        "detailed_explanation": "A standard function executes completely and returns a single value via `return`. A generator function yields values lazily on-demand. When `yield` is encountered, the function's execution state, local variables, and instruction pointer are frozen and yielded to the caller. Calling `next()` resumes execution immediately after `yield`.",
        "code_example": "# List comprehension stores 10 million ints in RAM (~80MB):\n# numbers = [i for i in range(10_000_000)]\n\n# Generator expression uses ~112 bytes of RAM:\nnumbers_gen = (i for i in range(10_000_000))\nprint(next(numbers_gen))  # 0\nprint(next(numbers_gen))  # 1",
        "related_topic": "Iterators & Lazy Evaluation"
    },
    {
        "id": "py-q5",
        "question": "What are Python Decorators, and how do you write a custom function execution timer?",
        "difficulty": "Intermediate",
        "category": "Meta-programming",
        "short_answer": "Decorators are callable functions that accept another function as an argument, extend or modify its behavior without modifying the original source code, and return a callable wrapper.",
        "detailed_explanation": "Decorators utilize first-class functions and closures in Python. When you annotate `@my_decorator` above a function definition `def f()`, Python translates this to `f = my_decorator(f)`. Custom wrappers typically use `functools.wraps` to preserve the original function's name and docstrings.",
        "code_example": "import time\nfrom functools import wraps\n\ndef execution_timer(func):\n    @wraps(func)\n    def wrapper(*args, **kwargs):\n        start = time.perf_counter()\n        result = func(*args, **kwargs)\n        elapsed = time.perf_counter() - start\n        print(f'{func.__name__} executed in {elapsed:.4f}s')\n        return result\n    return wrapper\n\n@execution_timer\ndef calculate_primes(limit):\n    return [n for n in range(2, limit) if all(n % d != 0 for d in range(2, int(n**0.5) + 1))]",
        "related_topic": "Decorators & Closures"
    },
    {
        "id": "py-q6",
        "question": "What is the difference between `__init__` and `__new__` in Python classes?",
        "difficulty": "Advanced",
        "category": "OOP & Metaclasses",
        "short_answer": "`__new__` is the actual constructor that creates and returns a new object instance, while `__init__` is the initializer that configures attributes on the already-created instance.",
        "detailed_explanation": "`__new__` is a static method called before `__init__`. It receives `cls` as its first parameter and must return a new instance of that class (typically via `super().__new__(cls)`). It is primarily used when subclassing immutable types (like `str` or `int`) or implementing the Singleton design pattern.",
        "code_example": "class Singleton:\n    _instance = None\n    def __new__(cls, *args, **kwargs):\n        if cls._instance is None:\n            cls._instance = super().__new__(cls)\n        return cls._instance",
        "related_topic": "Object Instantiation & Design Patterns"
    },
    {
        "id": "py-q7",
        "question": "Explain the difference between `deepcopy` and `copy` (shallow copy) in Python.",
        "difficulty": "Beginner",
        "category": "Core Python",
        "short_answer": "A shallow copy creates a new collection object but copies references to child elements; a deep copy recursively clones the collection and all nested objects contained within it.",
        "detailed_explanation": "If a list contains mutable nested objects (like a list of lists or dicts), modifying a child object inside a shallow copy will unintentionally modify the original parent's child object as well. `copy.deepcopy()` creates completely independent memory allocations for all nested children.",
        "code_example": "import copy\norig = [[1, 2], [3, 4]]\nshallow = copy.copy(orig)\ndeep = copy.deepcopy(orig)\n\nshallow[0][0] = 999\nprint(orig[0][0])  # 999 (Mutated!)\n\ndeep[1][0] = 777\nprint(orig[1][0])  # 3 (Safe!)",
        "related_topic": "Object References & Deep Cloning"
    },
    {
        "id": "py-q8",
        "question": "What are Python Context Managers, and how does the `with` statement work internally?",
        "difficulty": "Intermediate",
        "category": "Resource Management",
        "short_answer": "Context managers guarantee deterministic resource setup and teardown (e.g. closing file handles, releasing locks) using the `__enter__` and `__exit__` magic protocols.",
        "detailed_explanation": "When a `with` block begins, the context manager's `__enter__()` method executes and its return value is bound to the target variable (`as f`). When the block exits (either normally or via an unhandled exception), `__exit__(exc_type, exc_val, exc_tb)` is guaranteed to run, ensuring cleanup.",
        "code_example": "class DatabaseConnection:\n    def __enter__(self):\n        print('Acquiring database connection from pool...')\n        return self\n    def __exit__(self, exc_type, exc_val, exc_tb):\n        print('Safely closing connection and returning to pool.')\n        return False  # Do not suppress exceptions",
        "related_topic": "Context Protocols & Exception Handling"
    }
]

WEBDEV_INTERVIEW_QUESTIONS = [
    {
        "id": "web-q1",
        "question": "What happens in the browser from the moment you type a URL and hit Enter until the page renders?",
        "difficulty": "Intermediate",
        "category": "Web Architecture & Networking",
        "short_answer": "DNS resolution converts domain to IP -> TCP 3-way handshake -> TLS handshake -> HTTP/HTTPS request -> Server processes & sends HTTP response -> Browser parses HTML/CSS to build DOM & CSSOM -> Render Tree -> Layout -> Painting.",
        "detailed_explanation": "1. DNS lookup (Browser cache -> OS cache -> Router cache -> ISP DNS Resolver -> Root/TLD/Authoritative nameservers).\n2. TCP Handshake (SYN, SYN-ACK, ACK) and TLS 1.3 cryptographic key exchange.\n3. Server returns HTML response. Browser streams bytes, decodes characters, tokenizes, and builds Document Object Model (DOM).\n4. CSS is parsed into CSS Object Model (CSSOM). DOM + CSSOM combine into the Render Tree.\n5. Layout computes geometry and coordinates. Paint rasterizes pixels onto composite layers for GPU rendering.",
        "code_example": "// Critical Rendering Path:\n// HTML -> DOM\n// CSS -> CSSOM\n// DOM + CSSOM -> Render Tree -> Layout -> Paint -> Composite",
        "related_topic": "Networking, DNS & Browser Rendering Engine"
    },
    {
        "id": "web-q2",
        "question": "Explain the difference between Cookies, LocalStorage, SessionStorage, and IndexedDB.",
        "difficulty": "Beginner",
        "category": "Client Storage & Security",
        "short_answer": "Cookies (~4KB) are sent with every HTTP request and support HttpOnly/Secure flags; LocalStorage (~5-10MB) persists across browser tabs/restarts; SessionStorage (~5MB) dies when the tab closes; IndexedDB is a full client-side NoSQL database.",
        "detailed_explanation": "For sensitive authentication session tokens, always use `HttpOnly; Secure; SameSite=Lax` cookies to prevent XSS (Cross-Site Scripting) token theft. LocalStorage is synchronous and accessible via JavaScript (`window.localStorage`), making it vulnerable to XSS. IndexedDB is asynchronous, transactional, and ideal for storing large offline datasets in Progressive Web Apps (PWAs).",
        "code_example": "// Storing non-sensitive UI preferences in LocalStorage:\nlocalStorage.setItem('skillrock_theme', 'dark');\nconst theme = localStorage.getItem('skillrock_theme');",
        "related_topic": "Web Storage & Application Security"
    },
    {
        "id": "web-q3",
        "question": "What are CORS (Cross-Origin Resource Sharing) errors, and how are they properly resolved on the backend?",
        "difficulty": "Intermediate",
        "category": "APIs & Security",
        "short_answer": "CORS is a browser security mechanism that blocks web pages from making AJAX requests to a different domain/port unless the target server explicitly permits it via `Access-Control-Allow-Origin` HTTP headers.",
        "detailed_explanation": "When an origin (`https://skillrock.in`) makes a cross-origin fetch request with custom headers or non-GET/POST methods, the browser sends an HTTP `OPTIONS` preflight request. The server must respond with `Access-Control-Allow-Origin`, `Access-Control-Allow-Methods`, and `Access-Control-Allow-Headers`. CORS cannot be disabled on the frontend; it is strictly a server-configured policy.",
        "code_example": "# Flask backend CORS configuration:\n@app.after_request\ndef add_cors_headers(response):\n    response.headers['Access-Control-Allow-Origin'] = 'https://skillrock.in'\n    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'\n    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'\n    return response",
        "related_topic": "HTTP Protocols, Preflights & API Security"
    },
    {
        "id": "web-q4",
        "question": "What is the JavaScript Event Loop, Call Stack, Microtask Queue, and Callback Queue?",
        "difficulty": "Advanced",
        "category": "JavaScript Runtime",
        "short_answer": "The Event Loop continuously checks if the Call Stack is empty. If empty, it processes all jobs in the Microtask Queue (Promises, queueMicrotask) before processing the oldest task in the Callback/Macrotask Queue (setTimeout, setInterval).",
        "detailed_explanation": "JavaScript is single-threaded. Synchronous code executes immediately on the Call Stack. Asynchronous operations are delegated to browser Web APIs. When completed, callbacks are queued. Microtasks (Promise `.then()`, `async/await`) have strict priority over Macrotasks (`setTimeout`, `setInterval`). The entire microtask queue must be completely drained before the next macrotask is dequeued.",
        "code_example": "console.log('1'); // Synchronous\nsetTimeout(() => console.log('2'), 0); // Macrotask\nPromise.resolve().then(() => console.log('3')); // Microtask\nconsole.log('4'); // Synchronous\n\n// Output Order: 1 -> 4 -> 3 -> 2",
        "related_topic": "V8 Engine, Event Loop & Asynchronous JS"
    }
]

SQL_INTERVIEW_QUESTIONS = [
    {
        "id": "sql-q1",
        "question": "What is the difference between WHERE and HAVING clauses in SQL?",
        "difficulty": "Beginner",
        "category": "SQL Fundamentals",
        "short_answer": "`WHERE` filters individual rows before grouping (`GROUP BY`) takes place; `HAVING` filters aggregated groups after grouping and aggregate calculations (`COUNT`, `AVG`, `SUM`) occur.",
        "detailed_explanation": "You cannot use aggregate functions like `COUNT(*)` or `AVG(salary)` inside a `WHERE` clause because aggregation has not yet happened when row-level filtering occurs. `HAVING` operates strictly on the grouped records.",
        "code_example": "SELECT department_id, COUNT(*) as employee_count\nFROM employees\nWHERE status = 'ACTIVE'               -- Filters rows first\nGROUP BY department_id\nHAVING COUNT(*) > 5;                  -- Filters aggregated groups",
        "related_topic": "Query Execution Order & Aggregations"
    },
    {
        "id": "sql-q2",
        "question": "Explain Database Normalization (1NF, 2NF, 3NF, BCNF) and when to Denormalize.",
        "difficulty": "Intermediate",
        "category": "Database Design & Architecture",
        "short_answer": "Normalization organizes database schemas to reduce data redundancy and eliminate insert/update/delete anomalies. Denormalization intentionally adds redundant data to eliminate expensive multi-table JOINs in high-read analytical workloads.",
        "detailed_explanation": "1NF: Atomic values (no repeating groups/arrays).\n2NF: In 1NF + no partial dependency (every non-key column depends on the whole primary key).\n3NF: In 2NF + no transitive dependency (non-key columns do not depend on other non-key columns).\nBCNF: In 3NF + for every functional dependency X -> Y, X must be a super key.\nIn OLAP data warehouses (like BigQuery or reporting tables), denormalization is often preferred to optimize read query latency.",
        "code_example": "-- 3NF: Users table separate from Colleges table\nCREATE TABLE colleges (id INT PRIMARY KEY, name VARCHAR(100));\nCREATE TABLE students (\n    id INT PRIMARY KEY, \n    name VARCHAR(100), \n    college_id INT REFERENCES colleges(id)\n);",
        "related_topic": "Relational Schema Design & Normal Forms"
    },
    {
        "id": "sql-q3",
        "question": "What is a Database Index (B-Tree vs Hash), and why do too many indexes degrade write performance?",
        "difficulty": "Advanced",
        "category": "Performance & Storage Internals",
        "short_answer": "An index is a balanced auxiliary data structure (typically a B+Tree) that provides O(log N) lookup time for query searches. However, every `INSERT`, `UPDATE`, and `DELETE` must rebalance the tree and write to index files, degrading write throughput.",
        "detailed_explanation": "B+Trees maintain sorted keys with pointers to data pages, allowing efficient equality searches (`=` ) and range scans (`BETWEEN`, `>`, `<`). Hash indexes provide O(1) equality lookups but cannot perform range scans. When you add 10 indexes to a table, a single row insertion requires writing to the base storage plus updating all 10 index trees.",
        "code_example": "-- Index on foreign key and frequently searched columns:\nCREATE INDEX idx_enrollment_user_course ON enrollments(user_id, course_id);\n\n-- Inspect query execution plan in MySQL / PostgreSQL:\nEXPLAIN ANALYZE SELECT * FROM enrollments WHERE user_id = '123';",
        "related_topic": "B+Tree Data Structures & Query Optimization"
    }
]

# Combined Master Technical Interview Question Bank
TECHNICAL_INTERVIEW_QUESTIONS = PYTHON_INTERVIEW_QUESTIONS + WEBDEV_INTERVIEW_QUESTIONS + SQL_INTERVIEW_QUESTIONS

HR_INTERVIEW_QUESTIONS = [
    {
        "id": "hr-q1",
        "question": "Tell me about yourself (Professional Student Framework).",
        "difficulty": "General",
        "framework": "Past -> Present -> Future",
        "model_answer": "Good morning/afternoon. I'm currently completing my degree in Computer Science/Engineering. Over the past couple of years, I've developed a strong passion for full-stack software development and practical problem-solving. Through platforms like SkillRock, I've built end-to-end applications including a real-world student portal with database persistence, authentication, and REST APIs. I'm skilled in Python, JavaScript, and SQL, and I'm eager to bring my hands-on project experience, fast learning ability, and dedication to your engineering team as a Software Engineering Intern.",
        "key_tips": "Keep it under 90 seconds. Focus 70% on technical skills, projects, and learning achievements, and 30% on academic background. Avoid reciting your high school marks."
    },
    {
        "id": "hr-q2",
        "question": "What are your greatest strengths and weaknesses?",
        "difficulty": "General",
        "framework": "Strength + Evidence | Weakness + Active Improvement",
        "model_answer": "My greatest strength is my disciplined, self-directed learning ability. When building my course capstone, I encountered unfamiliar deployment configurations, but I debugged the logs systematically and deployed the live project within 48 hours. As for a weakness, I used to struggle with delegating tasks because I wanted to ensure perfection in every line of code. However, while working on team projects, I learned that clear communication and trust improve overall speed and quality, and I now use structured task boards to collaborate effectively.",
        "key_tips": "Never choose a fake weakness like 'I work too hard'. Pick a genuine, non-fatal professional skill and immediately explain the concrete steps you are actively taking to overcome it."
    },
    {
        "id": "hr-q3",
        "question": "Why should we hire you over other candidates?",
        "difficulty": "General",
        "framework": "Skills + Proof of Work + Cultural Drive",
        "model_answer": "You should hire me because unlike candidates who only memorize theoretical concepts, I have proven hands-on capability by building, testing, and deploying real applications from scratch. I understand code quality, Git workflows, and API architectures. More importantly, I have a relentless curiosity to learn your stack, take ownership of tasks, and contribute productive code from day one.",
        "key_tips": "Highlight your practical project deliverables and your agility to adapt and deliver value."
    },
    {
        "id": "hr-q4",
        "question": "Explain a difficult bug or challenge you faced in your project and how you resolved it.",
        "difficulty": "General",
        "framework": "STAR (Situation, Task, Action, Result)",
        "model_answer": "In my web application project, I encountered an issue where user watch progress was not persisting reliably when students switched tabs or navigated away. The task was to ensure zero data loss without overloading the server with requests. I analyzed the networking lifecycle and implemented an auto-save watchdog using the `navigator.sendBeacon` and `visibilitychange` APIs alongside a debounced 10-second sync timer. As a result, progress tracking accuracy reached 99.8% with zero noticeable browser lag.",
        "key_tips": "Structure your story clearly with the STAR method: Situation, Task, Action, and measurable Result."
    },
    {
        "id": "hr-q5",
        "question": "Where do you see yourself in five years?",
        "difficulty": "General",
        "framework": "Competency -> Impact -> Leadership",
        "model_answer": "In five years, I see myself as a seasoned Senior Software Engineer who has deeply mastered distributed system architectures and cloud infrastructure. I want to have contributed to core production features that impact thousands of users and mentor junior developers who join the organization, helping maintain high standards of code excellence and team velocity.",
        "key_tips": "Show realistic career ambition, technical depth, and organizational commitment."
    }
]

# ==============================================================================
# MODULE 05: CAREER & COMMUNICATION ACADEMY
# ==============================================================================

ENGLISH_ACADEMY_LESSONS = [
    {
        "lesson_num": 1,
        "title": "Introducing Yourself in English",
        "subtitle": "Clear, confident personal introductions in casual and academic settings",
        "hindi_explanation": "Apna introduction dena interview ka pehla aur sabse important step hota hai. Isme aapko simple English me apna naam, qualification, aur interests batane hote hain bina ghabraye.",
        "key_phrases": [
            {"phrase": "Hello everyone, my name is [Name].", "usage": "Clear opening greeting"},
            {"phrase": "I am currently pursuing my degree in [Field] from [College].", "usage": "Stating educational background"},
            {"phrase": "I am passionate about software development and solving algorithmic problems.", "usage": "Expressing professional interests"},
            {"phrase": "I'm excited to connect with all of you today.", "usage": "Warm closing"}
        ],
        "practical_dialogue": "Interviewer: 'Welcome to the interview! Could you please introduce yourself?'\nCandidate: 'Good morning! Thank you for this opportunity. My name is Rahul Sharma. I am in my final year of Computer Science Engineering at XYZ Institute. I have a strong interest in backend programming with Python and building database-driven applications. In my free time, I love building open-source tools and exploring cloud technologies.'",
        "exercise": "Write down a 3-sentence self-introduction covering: 1) Your name and current college, 2) Your main technical skill, and 3) What excites you about engineering."
    },
    {
        "lesson_num": 2,
        "title": "Self-Introduction for Technical Interviews",
        "subtitle": "Laser-focused professional pitch tailored for tech recruiters & hiring managers",
        "hindi_explanation": "Technical interview me introduction me school ke marks ya family background nahi batana hota. Seedha apne skills, projects aur coding passion par focus karein.",
        "key_phrases": [
            {"phrase": "Over the past two years, I have focused extensively on [Tech Stack].", "usage": "Highlighting focus area"},
            {"phrase": "One of my flagship projects is [Project Name], which solves [Problem].", "usage": "Spotlighting proof of work"},
            {"phrase": "I enjoy writing clean, modular code with thorough test coverage.", "usage": "Demonstrating engineering maturity"}
        ],
        "practical_dialogue": "Interviewer: 'Take 2 minutes to walk me through your technical profile.'\nCandidate: 'Certainly! I'm a full-stack developer specializing in Python, JavaScript, and SQL. Recently, I built and deployed an automated learning platform with JWT authentication and video progress tracking. I'm comfortable with Git collaboration, RESTful API design, and writing clean, scalable code. I'm eager to apply these skills to your backend infrastructure.'",
        "exercise": "Record yourself on your phone delivering a 60-second technical pitch. Check that you clearly mentioned at least 2 technologies and 1 project."
    },
    {
        "lesson_num": 3,
        "title": "Explaining Your College and Education",
        "subtitle": "Describing academic coursework, electives, and GPA with poise",
        "hindi_explanation": "Apne college aur degree ko explain karte waqt relevant subjects (jaise Data Structures, Operating Systems, DBMS) ka zikr karein jo software roles ke liye zaroori hain.",
        "key_phrases": [
            {"phrase": "I am in my final semester at [University].", "usage": "Academic status"},
            {"phrase": "My coursework has given me a solid grounding in core CS subjects like DSA and OS.", "usage": "Connecting coursework to job requirements"},
            {"phrase": "Alongside academics, I consistently dedicated time to hands-on programming labs.", "usage": "Showing self-motivation"}
        ],
        "practical_dialogue": "Interviewer: 'What subjects in college did you enjoy the most?'\nCandidate: 'I particularly enjoyed Database Management Systems and Algorithms because they taught me how data is indexed and retrieved efficiently at scale. I took those theoretical lessons and built actual database schemas in my project.'",
        "exercise": "Identify 3 computer science subjects you studied in college and write one sentence explaining how each subject relates to software development."
    },
    {
        "lesson_num": 4,
        "title": "Explaining Your Projects with the STAR Method",
        "subtitle": "How to structure and articulate technical project walkthroughs seamlessly",
        "hindi_explanation": "Project samjhate waqt hamesha STAR framework use karein: Situation (kya problem thi), Task (aapko kya karna tha), Action (aapne kaunsa code/technology use kiya), Result (kya result nikla).",
        "key_phrases": [
            {"phrase": "The objective of this project was to address [Problem Statement].", "usage": "Defining the problem"},
            {"phrase": "I architected the backend using [Technology] and configured [Database].", "usage": "Technical implementation"},
            {"phrase": "A key challenge I resolved was [Technical Obstacle], which I solved by [Solution].", "usage": "Highlighting problem-solving"},
            {"phrase": "The application achieved [Metric: e.g. sub-100ms response time / 100% test pass rate].", "usage": "Demonstrating measurable results"}
        ],
        "practical_dialogue": "Candidate: 'For my capstone project, I noticed students struggled to find study partners on campus. I built a real-time matching application using Flask, MongoDB, and WebSockets. I implemented session scheduling with Google Calendar APIs, which reduced scheduling friction by over 70% during our campus test run.'",
        "exercise": "Pick one project on your resume and write down: Situation (1 line), Task (1 line), Action (2 lines), and Result (1 line with a number or percentage)."
    },
    {
        "lesson_num": 5,
        "title": "Daily Professional English Sentences in Tech",
        "subtitle": "Common idioms, stand-up meeting vocabulary, and peer collaboration phrases",
        "hindi_explanation": "Software company me daily standup meeting hoti hai jahan aapko batana hota hai ki kal kya kiya, aaj kya karenge, aur koi blocker toh nahi hai.",
        "key_phrases": [
            {"phrase": "Yesterday, I pushed the PR for the authentication bug fix.", "usage": "Status update"},
            {"phrase": "Today, I'll be working on writing unit tests for the payment module.", "usage": "Daily objective"},
            {"phrase": "I'm currently blocked on the third-party API credentials.", "usage": "Communicating an obstacle"},
            {"phrase": "Let's take this discussion offline to avoid holding up the meeting.", "usage": "Professional meeting etiquette"}
        ],
        "practical_dialogue": "Scrum Master: 'Any blockers from your end?'\nDeveloper: 'No hard blockers right now. I just need a quick code review on PR #42 before merging into staging. Once approved, I'll deploy the build.'",
        "exercise": "Practice saying aloud: 'Yesterday I finished the database migration, today I am integrating the payment webhook, and I have no blockers.'"
    },
    {
        "lesson_num": 6,
        "title": "HR Interview Communication & Behavioral Questions",
        "subtitle": "Expressing workplace ethics, handling pressure, and cultural alignment",
        "hindi_explanation": "HR interview me aapki honesty, teamwork aur professional attitude dekha jata hai. Kabhi bhi purane college ya company ki burai na karein.",
        "key_phrases": [
            {"phrase": "I believe in open communication and constructive feedback.", "usage": "Team alignment"},
            {"phrase": "When faced with tight deadlines, I prioritize high-impact tasks first.", "usage": "Handling pressure"},
            {"phrase": "I am adaptable and always eager to learn whatever tech stack the team needs.", "usage": "Demonstrating agility"}
        ],
        "practical_dialogue": "HR: 'How do you handle conflict with a teammate?'\nCandidate: 'I focus on the code and the user requirement rather than personal viewpoints. I prefer hopping on a quick call, listening to their architectural reasoning, and evaluating the pros and cons objectively with data.'",
        "exercise": "Write down how you would respond if an interviewer asks: 'What would you do if your project deadline was moved up by two days?'"
    },
    {
        "lesson_num": 7,
        "title": "Group Discussion (GD) Preparation & Interventions",
        "subtitle": "Politely agreeing, disagreeing, and adding constructive insights in team rounds",
        "hindi_explanation": "Group Discussion me doosro ko cut nahi karna chahiye. Hamesha polite tareeke se enter karein jaise 'I would like to add a point here...'",
        "key_phrases": [
            {"phrase": "I see your point, and I'd like to build upon what you mentioned about [Topic].", "usage": "Agreeing and adding value"},
            {"phrase": "While I understand that perspective, we should also consider [Alternative].", "usage": "Polite disagreement"},
            {"phrase": "To summarize the key consensus points of our group discussion...", "usage": "Taking leadership to conclude"}
        ],
        "practical_dialogue": "Participant 1: 'AI will completely eliminate software jobs!'\nCandidate: 'While AI will certainly automate repetitive boilerplate code, I believe it will elevate engineers to focus on architecture, system design, and complex problem-solving rather than eliminate the craft entirely.'",
        "exercise": "Practice 3 transition phrases: 'Adding to that point...', 'From an architectural perspective...', 'In conclusion, our group agrees that...'"
    },
    {
        "lesson_num": 8,
        "title": "Professional Email Writing for Engineers",
        "subtitle": "Cold emails, follow-ups, interview confirmations, and leave applications",
        "hindi_explanation": "Professional email me clear Subject line honi chahiye, polite opening ('Dear Hiring Team'), brief context, aur professional closing ('Warm regards').",
        "key_phrases": [
            {"phrase": "I am writing to express my strong interest in the [Role] position.", "usage": "Email opening"},
            {"phrase": "Please find attached my resume and links to my deployed GitHub projects.", "usage": "Attaching portfolio"},
            {"phrase": "Thank you for your time and consideration. I look forward to hearing from you.", "usage": "Email closing"}
        ],
        "practical_dialogue": "Subject: Software Engineering Intern Application — [Your Name]\n\nDear Hiring Team,\n\nI am writing to express my strong interest in the Software Engineering Internship at [Company]. I recently completed a 12-week intensive project-based curriculum on SkillRock, where I built full-stack Python and web applications.\n\nMy GitHub portfolio: https://github.com/[username]\nMy Live Project: https://[project].skillrock.in\n\nI would welcome the opportunity to discuss how my hands-on coding skills can contribute to your team.\n\nWarm regards,\n[Your Name] | [Phone Number]",
        "exercise": "Draft a 5-sentence professional follow-up email to a recruiter 5 days after your interview."
    },
    {
        "lesson_num": 9,
        "title": "Speaking Confidence & Overcoming Hesitation",
        "subtitle": "Voice modulation, posture, eye contact on video calls, and pacing",
        "hindi_explanation": "English bolte waqt jaldi-jaldi bolne ki zaroorat nahi hai. Thoda pause leke, aaram se clear aawaz me boleinge toh samne wale par behtar impression padega.",
        "key_phrases": [
            {"phrase": "That's an interesting question. Let me take a moment to structure my thoughts.", "usage": "Buying 3-5 seconds to think gracefully"},
            {"phrase": "Could you please elaborate or clarify that requirement slightly?", "usage": "Asking for clarification with confidence"}
        ],
        "practical_dialogue": "Interviewer: 'Can you design a distributed cache with custom eviction?'\nCandidate: 'That's a great systems question. May I take 5 seconds to write down the constraints? Specifically, are we optimizing for read latency or memory footprints first?'",
        "exercise": "Practice the pause technique: Count '1, 2' in your mind before answering a mock question aloud."
    },
    {
        "lesson_num": 10,
        "title": "Common Interview Conversations & Asking Great Questions",
        "subtitle": "Smart questions to ask the interviewer at the end of the round",
        "hindi_explanation": "Interview ke end me jab interviewer bole 'Do you have any questions for me?', toh kabhi 'No' mat bolo! Hamesha unki team aur engineering practices ke baare me pucho.",
        "key_phrases": [
            {"phrase": "What does a typical day look like for an engineer in this team?", "usage": "Inquiring about daily workflow"},
            {"phrase": "What are the biggest technical challenges the team is currently tackling?", "usage": "Showing deep engineering curiosity"},
            {"phrase": "What CI/CD and automated testing standards does the team follow?", "usage": "Demonstrating professionalism"}
        ],
        "practical_dialogue": "Interviewer: 'Do you have any questions for us?'\nCandidate: 'Yes, thank you! I noticed your recent blog post on moving to microservices. What has been the most interesting architectural challenge the team faced during that transition?'",
        "exercise": "Memorize 2 smart questions you will ask in your next technical interview."
    }
]

CAREER_DEVELOPMENT_RESOURCES = {
    "ats_resume_guide": {
        "title": "ATS-Friendly Tech Resume Blueprint",
        "key_rules": [
            "Use clean single-column layout without tables, graphics, or text boxes that confuse ATS parsers.",
            "Use standard section headers: 'Education', 'Technical Skills', 'Projects', 'Experience', 'Certifications'.",
            "Use the Google XYZ Formula for project bullet points: 'Accomplished [X] as measured by [Y], by doing [Z]'.",
            "Keep technical skills organized: Languages (Python, C++, JS), Frameworks (Flask, React), Tools (Git, Docker), Databases (MongoDB, SQL).",
            "Save and export as standard PDF format with selectable text (never scanned image PDF)."
        ],
        "sample_bullet_points": [
            "Architected RESTful e-learning backend in Python/Flask serving 500+ requests with sub-80ms response latency.",
            "Engineered automated code execution sandbox using Docker and Python subprocesses with 100% test isolation.",
            "Implemented SHA-256 cryptographic certificate generation with live QR validation verified at skillrock.in."
        ]
    },
    "linkedin_optimization": {
        "title": "LinkedIn Profile Optimization for College Developers",
        "steps": [
            "Headline: '[Aspiring Software Engineer | Python, Web & Algorithms | Student at XYZ College]'.",
            "Featured Section: Pin your live SkillRock certificate and your top 2 GitHub repository links.",
            "About Section: 3 short paragraphs covering your background, passion for building projects, and contact email.",
            "Projects: Add every course project with links to the GitHub repo and live demo URL."
        ]
    },
    "github_portfolio_checklist": {
        "title": "GitHub Profile & Repository Professional Standards",
        "checklist": [
            "Professional GitHub profile README with bio, tech stack badges, and pinned repositories.",
            "Every project repository MUST contain a comprehensive README.md with setup instructions, architecture diagram, and demo GIF.",
            "Include an open-source LICENSE (MIT or Apache 2.0).",
            "Clean commit history with conventional commit messages (feat:, fix:, docs:, test:)."
        ]
    }
}

INTERNSHIP_OPPORTUNITIES = [
    {
        "id": "opp-1",
        "company": "SkillRock Engineering & Campus Partners",
        "title": "Software Development Engineer Intern (Backend / Python)",
        "work_mode": "Remote",
        "type": "Paid Internship",
        "stipend": "₹15,000 – ₹25,000 / month",
        "duration": "3–6 Months",
        "skills_required": ["Python", "Flask", "MongoDB", "REST APIs", "Git"],
        "eligibility": "B.Tech / BCA / MCA students with completed practical capstone projects",
        "verified": True,
        "source": "SkillRock Official Partner Network",
        "apply_url": "https://skillrock.in/learning/courses",
        "deadline": "Open Rolling Applications"
    },
    {
        "id": "opp-2",
        "company": "Google Summer of Code (GSoC)",
        "title": "Open Source Contributor & Fellowship Program",
        "work_mode": "Remote",
        "type": "Fellowship / Open Source",
        "stipend": "$1,500 – $3,000 USD (Stipend based on country)",
        "duration": "12–22 Weeks",
        "skills_required": ["Git", "Python/C++/Java", "Open Source Communication"],
        "eligibility": "Open to all students and beginners worldwide (18+)",
        "verified": True,
        "source": "Official Google Program",
        "apply_url": "https://summerofcode.withgoogle.com",
        "deadline": "Annual Spring Applications"
    },
    {
        "id": "opp-3",
        "company": "Linux Foundation (LFX Mentorship)",
        "title": "Systems & Cloud Infrastructure Engineering Mentorship",
        "work_mode": "Remote",
        "type": "Paid Mentorship",
        "stipend": "$3,000 – $6,600 USD",
        "duration": "12 Weeks (Full-time or Part-time)",
        "skills_required": ["Linux", "Go/Python/C++", "Containerization", "Git"],
        "eligibility": "All enrolled college students with verified project deliverables",
        "verified": True,
        "source": "Linux Foundation Official Portal",
        "apply_url": "https://lfx.linuxfoundation.org/tools/mentorship/",
        "deadline": "Summer & Fall Cohorts"
    },
    {
        "id": "opp-4",
        "company": "Smart India Hackathon (SIH)",
        "title": "National Technical Innovation & Problem Solving Arena",
        "work_mode": "Hybrid / On-site",
        "type": "National Hackathon",
        "stipend": "₹1,00,000 prize per problem statement",
        "duration": "Annual Multi-Stage Event",
        "skills_required": ["Full Stack Web", "Mobile Dev", "AI/ML", "Team Collaboration"],
        "eligibility": "Enrolled undergraduate & postgraduate university teams",
        "verified": True,
        "source": "Government of India / AICTE",
        "apply_url": "https://www.sih.gov.in",
        "deadline": "Annual College Nominations"
    },
    {
        "id": "opp-5",
        "company": "Fast-Growing Tech Startups & Seed Ventures",
        "title": "Frontend & Full Stack Junior Engineer Trainee",
        "work_mode": "Hybrid / Bangalore & Remote",
        "type": "Paid Internship",
        "stipend": "₹18,000 – ₹30,000 / month",
        "duration": "6 Months",
        "skills_required": ["JavaScript", "React / Node.js", "HTML5/CSS3", "Git"],
        "eligibility": "Pre-final and final year students with live portfolio deployment",
        "verified": True,
        "source": "Curated Tech Jobs Portal",
        "apply_url": "https://skillrock.in/learning/courses",
        "deadline": "Ongoing"
    }
]

# ==============================================================================
# COURSE CHAPTERS, PLAYLISTS & PRACTICE TESTS REGISTRY
# ==============================================================================

COURSE_METADATA_REGISTRY = {
    "python": {
        "chapters": [
            {"num": 1, "title": "Python Syntax, Variables & Primitive Data Types", "duration": "45 mins", "timestamp": "0:00"},
            {"num": 2, "title": "Conditionals, Loops & Iterators", "duration": "60 mins", "timestamp": "45:00"},
            {"num": 3, "title": "Functions, Scope, *args & **kwargs", "duration": "55 mins", "timestamp": "1:45:00"},
            {"num": 4, "title": "Data Structures: Lists, Tuples, Dictionaries & Sets", "duration": "75 mins", "timestamp": "2:40:00"},
            {"num": 5, "title": "Object-Oriented Programming: Classes, Inheritance & Dunder Methods", "duration": "90 mins", "timestamp": "3:55:00"},
            {"num": 6, "title": "Error Handling, Exceptions & Context Managers", "duration": "50 mins", "timestamp": "5:25:00"},
            {"num": 7, "title": "File I/O, Serialization (JSON & CSV) & Persistent Records", "duration": "65 mins", "timestamp": "6:15:00"},
            {"num": 8, "title": "Capstone Project Architecture & Deployment", "duration": "80 mins", "timestamp": "7:20:00"}
        ],
        "practice_test": {
            "title": "Python Core Proficiency & Output Prediction Test",
            "time_limit_mins": 20,
            "passing_percent": 70,
            "questions": [
                {
                    "q": "What is the output of the following Python snippet?\n\n```python\na = [1, 2, 3]\nb = a\nb.append(4)\nprint(len(a))\n```",
                    "options": ["3", "4", "Error", "None"],
                    "correct": 1,
                    "explanation": "In Python, variable assignment `b = a` creates a reference to the same list in memory. Mutating `b` directly mutates `a`. Hence `len(a)` is 4."
                },
                {
                    "q": "Which of the following data structures is immutable in Python?",
                    "options": ["List", "Dictionary", "Tuple", "Set"],
                    "correct": 2,
                    "explanation": "Tuples are immutable in Python. Once created, elements cannot be appended, removed, or modified."
                },
                {
                    "q": "What is the output of `type(lambda x: x * 2)`?",
                    "options": ["<class 'function'>", "<class 'lambda'>", "<class 'operator'>", "<class 'expression'>"],
                    "correct": 0,
                    "explanation": "A lambda in Python produces an anonymous function object whose type is `<class 'function'>`."
                },
                {
                    "q": "What does the `pass` statement do in Python?",
                    "options": [
                        "Terminates the program immediately",
                        "Acts as a syntactic null statement where code is required",
                        "Skips to the next iteration of a loop like continue",
                        "Returns None from a function"
                    ],
                    "correct": 1,
                    "explanation": "`pass` is a null statement in Python. It is used as a placeholder in empty functions, loops, or classes where syntax requires a statement."
                }
            ],
            "coding_challenge": {
                "title": "Reverse Words in a Sentence",
                "difficulty": "Beginner",
                "problem": "Write a function `reverse_words(s)` that takes a string of words and returns the string with the words reversed in order, separated by a single space.",
                "starter_code": "def reverse_words(s):\n    # Write clean logic here\n    return ' '.join(s.split()[::-1])\n",
                "test_cases": [
                    {"input": "the sky is blue", "expected": "blue is sky the"},
                    {"input": "  hello world  ", "expected": "world hello"},
                    {"input": "Python", "expected": "Python"}
                ]
            }
        }
    },
    "webdev": {
        "chapters": [
            {"num": 1, "title": "Modern HTML5 Semantic Architecture & Accessibility", "duration": "40 mins", "timestamp": "0:00"},
            {"num": 2, "title": "CSS3 Flexbox, CSS Grid & Responsive Design Systems", "duration": "60 mins", "timestamp": "40:00"},
            {"num": 3, "title": "JavaScript DOM Manipulation & Event Handling", "duration": "75 mins", "timestamp": "1:40:00"},
            {"num": 4, "title": "Asynchronous JavaScript: Promises, Async/Await & Fetch API", "duration": "65 mins", "timestamp": "2:55:00"},
            {"num": 5, "title": "Backend Fundamentals with Node.js & Express REST APIs", "duration": "85 mins", "timestamp": "4:00:00"},
            {"num": 6, "title": "Database Integration with MongoDB & CRUD Operations", "duration": "70 mins", "timestamp": "5:25:00"},
            {"num": 7, "title": "Authentication, JWT Tokens & Web Security", "duration": "60 mins", "timestamp": "6:35:00"},
            {"num": 8, "title": "Production Cloud Deployment, HTTPS & CI/CD", "duration": "50 mins", "timestamp": "7:35:00"}
        ],
        "practice_test": {
            "title": "Full Stack Web Architecture & DOM Assessment",
            "time_limit_mins": 20,
            "passing_percent": 70,
            "questions": [
                {
                    "q": "What is the primary difference between `let` and `var` in modern JavaScript?",
                    "options": [
                        "`let` is block-scoped while `var` is function-scoped",
                        "`var` is block-scoped while `let` is function-scoped",
                        "`let` cannot be reassigned while `var` can",
                        "There is no difference in modern browsers"
                    ],
                    "correct": 0,
                    "explanation": "`let` provides block scoping (`{ ... }`) and is not hoisted with initialization, preventing accidental variable leakage that occurs with function-scoped `var`."
                },
                {
                    "q": "What HTTP status code represents a successful resource creation?",
                    "options": ["200 OK", "201 Created", "204 No Content", "301 Moved Permanently"],
                    "correct": 1,
                    "explanation": "HTTP status code 201 indicates that the request succeeded and a new resource was created as a result."
                },
                {
                    "q": "Which CSS property is used to create a 2-dimensional grid layout?",
                    "options": ["display: flex", "display: grid", "display: inline-block", "float: left"],
                    "correct": 1,
                    "explanation": "CSS Grid (`display: grid`) is designed for 2-dimensional layouts (rows and columns simultaneously), whereas Flexbox is primarily 1-dimensional."
                }
            ],
            "coding_challenge": {
                "title": "Array Flattening Utility",
                "difficulty": "Intermediate",
                "problem": "Write a JavaScript/Python function that flattens a nested array of arbitrary depth into a single flat array.",
                "starter_code": "def flatten_array(arr):\n    result = []\n    for item in arr:\n        if isinstance(item, list):\n            result.extend(flatten_array(item))\n        else:\n            result.append(item)\n    return result\n",
                "test_cases": [
                    {"input": [[1, [2, [3, 4]]]], "expected": [1, 2, 3, 4]},
                    {"input": [1, 2, 3], "expected": [1, 2, 3]}
                ]
            }
        }
    },
    "sql": {
        "chapters": [
            {"num": 1, "title": "Relational Database Concepts & Schema Design", "duration": "30 mins", "timestamp": "0:00"},
            {"num": 2, "title": "SQL Data Types, DDL (CREATE, ALTER, DROP) & Constraints", "duration": "45 mins", "timestamp": "30:00"},
            {"num": 3, "title": "DML: INSERT, UPDATE, DELETE & Safe Transactions", "duration": "40 mins", "timestamp": "1:15:00"},
            {"num": 4, "title": "Querying Data: SELECT, WHERE, LIKE & Sorting", "duration": "50 mins", "timestamp": "1:55:00"},
            {"num": 5, "title": "Aggregations: GROUP BY, HAVING, COUNT, SUM & AVG", "duration": "55 mins", "timestamp": "2:45:00"},
            {"num": 6, "title": "Multi-Table JOINs: INNER, LEFT, RIGHT, FULL & Cross JOIN", "duration": "70 mins", "timestamp": "3:40:00"},
            {"num": 7, "title": "Subqueries, CTEs (WITH) & Window Functions", "duration": "65 mins", "timestamp": "4:50:00"},
            {"num": 8, "title": "Indexing, Query Performance & B-Tree Execution Plans", "duration": "60 mins", "timestamp": "5:55:00"}
        ],
        "practice_test": {
            "title": "SQL Query Writing & Optimization Assessment",
            "time_limit_mins": 20,
            "passing_percent": 70,
            "questions": [
                {
                    "q": "Which SQL JOIN returns all rows from the left table even if there are no matches in the right table?",
                    "options": ["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "CROSS JOIN"],
                    "correct": 1,
                    "explanation": "`LEFT JOIN` returns all rows from the left table, and the matched records from the right table. If no match is found, NULL values are returned for the right columns."
                },
                {
                    "q": "What is the result of `SELECT COUNT(*)` on an empty table?",
                    "options": ["NULL", "0", "Error", "False"],
                    "correct": 1,
                    "explanation": "`COUNT(*)` on an empty table evaluates to 0."
                }
            ],
            "coding_challenge": {
                "title": "Second Highest Salary Query Logic",
                "difficulty": "Intermediate",
                "problem": "Write a query or logical function to return the second highest salary from an employee list.",
                "starter_code": "def get_second_highest(salaries):\n    unique = sorted(set(salaries), reverse=True)\n    return unique[1] if len(unique) > 1 else None\n",
                "test_cases": [
                    {"input": [100, 200, 300], "expected": 200},
                    {"input": [100], "expected": None}
                ]
            }
        }
    }
}

# Generic fallback chapters for courses without custom metadata
DEFAULT_CHAPTERS = [
    {"num": 1, "title": "Course Overview, Tooling & Environment Setup", "duration": "30 mins", "timestamp": "0:00"},
    {"num": 2, "title": "Core Syntax, Data Types & Fundamental Building Blocks", "duration": "50 mins", "timestamp": "30:00"},
    {"num": 3, "title": "Control Flow, Logic & Algorithmic Problem Solving", "duration": "60 mins", "timestamp": "1:20:00"},
    {"num": 4, "title": "Modular Architecture, Functions & Code Reusability", "duration": "65 mins", "timestamp": "2:20:00"},
    {"num": 5, "title": "Object-Oriented Design & System Architecture Patterns", "duration": "75 mins", "timestamp": "3:25:00"},
    {"num": 6, "title": "Error Handling, Testing & Defensive Programming", "duration": "45 mins", "timestamp": "4:40:00"},
    {"num": 7, "title": "Database Integration, Persistent Storage & REST APIs", "duration": "70 mins", "timestamp": "5:25:00"},
    {"num": 8, "title": "Capstone Milestone Project Briefing & Code Review", "duration": "80 mins", "timestamp": "6:35:00"}
]


def get_course_modules_data(course_slug: str, course_title: str = "") -> Dict[str, Any]:
    """
    Returns complete data payload covering all 6 educational modules for a given course.
    """
    clean_slug = str(course_slug or "").lower()
    clean_title = str(course_title or "").lower()

    # Determine topic category
    if "python" in clean_slug or "python" in clean_title:
        topic_key = "python"
        tech_questions = PYTHON_INTERVIEW_QUESTIONS
    elif "sql" in clean_slug or "database" in clean_slug or "mysql" in clean_slug:
        topic_key = "sql"
        tech_questions = SQL_INTERVIEW_QUESTIONS
    elif any(k in clean_slug or k in clean_title for k in ["web", "html", "css", "javascript", "react", "node"]):
        topic_key = "webdev"
        tech_questions = WEBDEV_INTERVIEW_QUESTIONS
    else:
        topic_key = "python"
        tech_questions = PYTHON_INTERVIEW_QUESTIONS

    meta = COURSE_METADATA_REGISTRY.get(topic_key, {})
    chapters = meta.get("chapters", DEFAULT_CHAPTERS)
    practice_test = meta.get("practice_test", COURSE_METADATA_REGISTRY["python"]["practice_test"])

    return {
        "topic_key": topic_key,
        "chapters": chapters,
        "practice_test": practice_test,
        "tech_questions": tech_questions,
        "hr_questions": HR_INTERVIEW_QUESTIONS,
        "english_lessons": ENGLISH_ACADEMY_LESSONS,
        "career_resources": CAREER_DEVELOPMENT_RESOURCES,
        "internships": INTERNSHIP_OPPORTUNITIES
    }
