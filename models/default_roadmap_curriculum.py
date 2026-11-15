"""
SkillRock — Full Stack Developer Launchpad Curriculum Definition
20 Weeks, 5 Phases, Verified YouTube Video Resources, Weekly Milestones,
Projects, and Capstone Rubrics.
"""

def get_fullstack_roadmap_curriculum():
    return {
        "slug": "full-stack-developer-launchpad",
        "title": "Full Stack Developer Launchpad",
        "short_description": "A comprehensive 20-week, 5-phase career roadmap taking beginners from foundational web development to production-grade full-stack engineering with a 50% Completion Cashback incentive.",
        "full_description": """The Full Stack Developer Launchpad is SkillRock's flagship career preparation package. Spanning 20 intensive weeks across 5 distinct architectural phases, this roadmap is engineered for college students, self-taught coders, and aspiring developers who want to build real software.

Rather than watching passive tutorials, students follow a disciplined weekly milestone workflow: mastering HTML/CSS, modern JavaScript (ES6+), Git workflows, React component architecture, Node.js and Express backend design, PostgreSQL database modeling, TypeScript, and cloud deployment. 

Students complete 5 production-grade phase projects and an evaluated Capstone project (Job Application Tracker) evaluated by senior engineering rubrics. Upon verified completion of all modules, projects, and the capstone within 180 days, students receive a verified completion certificate and an instant 50% Completion Cashback reward.""",
        "duration": "20 Weeks",
        "level": "Beginner to Intermediate",
        "language": "Hinglish & English (Concepts in Hinglish, Industry Tech Standards in English)",
        "price": 999.0,
        "original_price": 2999.0,
        "currency": "INR",
        "cashback_enabled": True,
        "cashback_percentage": 50.0,
        "completion_deadline_days": 180,
        "is_published": True,
        "thumbnail_url": "https://img.youtube.com/vi/LzMnsfqjzkA/maxresdefault.jpg",
        "tech_stack": [
            "HTML5",
            "CSS3",
            "JavaScript ES6+",
            "Git & GitHub",
            "React",
            "Vite",
            "Node.js",
            "Express.js",
            "PostgreSQL",
            "SQL",
            "TypeScript",
            "REST APIs",
            "Testing & Deployment"
        ],
        "career_outcomes": [
            "Junior Full Stack Developer",
            "Junior React Developer",
            "Junior Frontend Developer",
            "Junior Node.js Developer"
        ],
        "phases": [
            # ==================================================================
            # PHASE 1: WEB DEVELOPMENT FOUNDATIONS (Weeks 1-4)
            # ==================================================================
            {
                "phase_number": 1,
                "title": "Phase 1: Web Development Foundations",
                "tagline": "Semantic Web, Modern CSS Architecture & Core JavaScript Problem Solving",
                "weeks_range": "Weeks 1–4",
                "summary": "Master the core building blocks of the web: semantic HTML5, accessible form architecture, modern CSS Flexbox and Grid layouts, responsive mobile-first styling, and algorithmic JavaScript DOM manipulation.",
                "weeks": [
                    {
                        "week_number": 1,
                        "title": "Week 1: Web Fundamentals, HTML5 & Semantic Web",
                        "objective": "Understand how the internet, HTTP, and browser rendering engines work; write clean semantic HTML5 documents, accessible forms, and structured layouts.",
                        "checklist": [
                            "Understand DNS, HTTP/HTTPS request-response cycles, and client-server architecture",
                            "Build structured HTML5 documents utilizing header, nav, main, section, article, and footer",
                            "Construct accessible web forms with inputs, labels, selects, and client validations",
                            "Incorporate images, audio, video with proper alt attributes and semantic markup"
                        ],
                        "lessons": [
                            {
                                "id": "w1_l1",
                                "title": "Internet, Browser Engine & Client-Server Architecture",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 87,
                                "duration_text": "35 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Learn how browsers fetch, parse, and render HTML, understand client vs server roles, and set up your local development environment with VS Code.",
                                "reading_urls": [
                                    {"title": "MDN: How the Web Works", "url": "https://developer.mozilla.org/en-US/docs/Learn/Common_questions/Web_mechanisms/How_does_the_Internet_work"},
                                    {"title": "Roadmap.sh: Internet Architecture", "url": "https://roadmap.sh/guides/what-is-internet"}
                                ]
                            },
                            {
                                "id": "w1_l2",
                                "title": "HTML5 Document Structure & Semantic Tags",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 1200,
                                "duration_text": "45 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Structure web pages with modern HTML5 semantic elements rather than div soup for SEO and screen-reader accessibility.",
                                "reading_urls": [
                                    {"title": "MDN: Semantic HTML", "url": "https://developer.mozilla.org/en-US/docs/Glossary/Semantics#semantics_in_html"},
                                    {"title": "The Odin Project: Introduction to HTML", "url": "https://www.theodinproject.com/lessons/foundations-introduction-to-html-and-css"}
                                ]
                            },
                            {
                                "id": "w1_l3",
                                "title": "Accessible Forms, Tables & Input Validation",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 4500,
                                "duration_text": "50 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Construct robust interactive forms using labels, required fields, pattern validation, radio/checkbox groups, and accessible tables.",
                                "reading_urls": [
                                    {"title": "MDN: Web Forms Guide", "url": "https://developer.mozilla.org/en-US/docs/Learn/Forms"}
                                ]
                            }
                        ]
                    },
                    {
                        "week_number": 2,
                        "title": "Week 2: CSS3 Mastery, Flexbox & Responsive Grid",
                        "objective": "Understand the CSS box model, cascade specificity, modern Flexbox alignment, CSS Grid 2D layouts, and media queries for responsive devices.",
                        "checklist": [
                            "Master margin, padding, border, content, and box-sizing: border-box",
                            "Implement 1D alignment with Flexbox (justify-content, align-items, flex-wrap)",
                            "Design 2D responsive magazine and dashboard grids with CSS Grid",
                            "Apply fluid typography and mobile-first media queries"
                        ],
                        "lessons": [
                            {
                                "id": "w2_l1",
                                "title": "The CSS Box Model, Selectors & Cascade Specificity",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 8200,
                                "duration_text": "55 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Learn how the browser computes dimensions, margin collapsing, inheritance, and selector specificity hierarchy.",
                                "reading_urls": [
                                    {"title": "MDN: The Box Model", "url": "https://developer.mozilla.org/en-US/docs/Learn/CSS/Building_blocks/The_box_model"}
                                ]
                            },
                            {
                                "id": "w2_l2",
                                "title": "Modern Flexbox Layouts & Directional Alignment",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 13400,
                                "duration_text": "60 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Build navigation bars, hero layouts, card grids, and vertical centering with Flexbox.",
                                "reading_urls": [
                                    {"title": "CSS-Tricks: Complete Guide to Flexbox", "url": "https://css-tricks.com/snippets/css/a-guide-to-flexbox/"}
                                ]
                            },
                            {
                                "id": "w2_l3",
                                "title": "CSS Grid & Mobile-First Media Queries",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 18200,
                                "duration_text": "65 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Design 2D layouts using grid-template-columns, fr units, minmax(), and responsive breakpoints for mobile screens.",
                                "reading_urls": [
                                    {"title": "MDN: CSS Grid Layout", "url": "https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Grids"}
                                ]
                            }
                        ]
                    },
                    {
                        "week_number": 3,
                        "title": "Week 3: JavaScript Core Fundamentals & Logic",
                        "objective": "Master JavaScript variables, data types, function scope, arrow functions, arrays, objects, control flow, and algorithmic problem solving.",
                        "checklist": [
                            "Understand let, const, var, primitive vs reference types",
                            "Write reusable functions, default parameters, and arrow syntax",
                            "Iterate and manipulate arrays with push, pop, slice, splice",
                            "Build structured objects, nested keys, and understand JSON data structures"
                        ],
                        "lessons": [
                            {
                                "id": "w3_l1",
                                "title": "JavaScript Variables, Data Types & Scope",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 24369,
                                "duration_text": "50 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Understand execution context, block scope vs function scope, string interpolation, and boolean comparison truthiness.",
                                "reading_urls": [
                                    {"title": "javascript.info: Variables & Types", "url": "https://javascript.info/variables"}
                                ]
                            },
                            {
                                "id": "w3_l2",
                                "title": "Functions, Arrow Functions & Execution Flow",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 24800,
                                "duration_text": "45 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Write pure functions, return statements, arrow functions, and solve algorithmic logic puzzles.",
                                "reading_urls": [
                                    {"title": "MDN: Functions Guide", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Functions"}
                                ]
                            },
                            {
                                "id": "w3_l3",
                                "title": "Arrays, Object Literals & Practical Challenges",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 25200,
                                "duration_text": "60 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Manipulate lists and key-value records, build search filters, and handle structured student data.",
                                "reading_urls": [
                                    {"title": "javascript.info: Array methods", "url": "https://javascript.info/array-methods"}
                                ]
                            }
                        ]
                    },
                    {
                        "week_number": 4,
                        "title": "Week 4: DOM Manipulation, Events & Async Fetch API",
                        "objective": "Select DOM elements, listen to events, dynamically manipulate styles/classes, handle promises, and fetch data from external REST APIs.",
                        "checklist": [
                            "Query elements with querySelector and querySelectorAll",
                            "Attach click, submit, input, and keydown event listeners",
                            "Understand async/await, Promises, and fetch requests",
                            "Build Phase 1 Project: Responsive Personal Developer Portfolio"
                        ],
                        "lessons": [
                            {
                                "id": "w4_l1",
                                "title": "DOM Selection, Class Manipulation & Dynamic Nodes",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 66417,
                                "duration_text": "55 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Read and modify innerText, classList, createElement, and appendChild to render dynamic UI components.",
                                "reading_urls": [
                                    {"title": "MDN: Introduction to the DOM", "url": "https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model/Introduction"}
                                ]
                            },
                            {
                                "id": "w4_l2",
                                "title": "Asynchronous JavaScript, Promises & Fetch API",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 68500,
                                "duration_text": "60 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Consume public REST endpoints with async/await, parse JSON payloads, and handle network error states gracefully.",
                                "reading_urls": [
                                    {"title": "javascript.info: Async/await", "url": "https://javascript.info/async-await"}
                                ]
                            }
                        ]
                    }
                ]
            },

            # ==================================================================
            # PHASE 2: DEVELOPER TOOLS & FRONTEND (Weeks 5-8)
            # ==================================================================
            {
                "phase_number": 2,
                "title": "Phase 2: Developer Tools & Frontend Architecture",
                "tagline": "Professional Git Workflows & React Component State Systems",
                "weeks_range": "Weeks 5–8",
                "summary": "Step into modern frontend engineering: learn essential Git and GitHub collaboration flows (commits, branches, pull requests), build single-page applications with React and Vite, manage component props, state hooks, side effects, and client-side routing.",
                "weeks": [
                    {
                        "week_number": 5,
                        "title": "Week 5: Git & GitHub Collaboration Workflows",
                        "objective": "Initialize repositories, stage commits with clean messages, branch, resolve merge conflicts, and collaborate with GitHub pull requests.",
                        "checklist": [
                            "Configure Git name, email, and SSH keys",
                            "Master git init, add, commit, status, log, and diff",
                            "Create feature branches, push to remote GitHub, and open Pull Requests",
                            "Write professional README.md documentation with markdown formatting"
                        ],
                        "lessons": [
                            {
                                "id": "w5_l1",
                                "title": "Git Basics: Init, Staging & Commit Architecture",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 25679,
                                "duration_text": "50 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Understand Git tracking vs working directory, commit hash trees, and status inspection.",
                                "reading_urls": [
                                    {"title": "Git Book: Getting Started", "url": "https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control"}
                                ]
                            },
                            {
                                "id": "w5_l2",
                                "title": "Branching, Pull Requests & Remote GitHub Repositories",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 53187,
                                "duration_text": "65 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Push code to GitHub, manage branches, merge features, and collaborate via open source pull requests.",
                                "reading_urls": [
                                    {"title": "GitHub Docs: About Pull Requests", "url": "https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests"}
                                ]
                            },
                            {
                                "id": "w5_l3",
                                "title": "Supplementary: Git & GitHub Complete Deep Dive",
                                "video_id": "mAFoROnOfHs",
                                "start_seconds": 0,
                                "duration_text": "40 Mins",
                                "instructor": "freeCodeCamp Community",
                                "objectives": "Master stash, reset vs revert, rebase basics, and .gitignore configuration.",
                                "reading_urls": [
                                    {"title": "Roadmap.sh: Git Best Practices", "url": "https://roadmap.sh/guides/git-best-practices"}
                                ]
                            }
                        ]
                    },
                    {
                        "week_number": 6,
                        "title": "Week 6: React Introduction, JSX & Component Hierarchy",
                        "objective": "Understand declarative UI, scaffold a Vite React project, write JSX, decompose user interfaces into components, and pass immutable props.",
                        "checklist": [
                            "Scaffold a blazing-fast React project using Vite and npm",
                            "Understand JSX syntax, expressions, and fragments",
                            "Deconstruct UI designs into modular reusable components",
                            "Pass props, default values, and render lists with key attributes"
                        ],
                        "lessons": [
                            {
                                "id": "w6_l1",
                                "title": "Why React? Vite Project Setup & JSX Essentials",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 111780,
                                "duration_text": "55 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Understand the Virtual DOM, Vite build tooling, and JSX syntax rules.",
                                "reading_urls": [
                                    {"title": "React Docs: Describing the UI", "url": "https://react.dev/learn/describing-the-ui"}
                                ]
                            },
                            {
                                "id": "w6_l2",
                                "title": "Component Architecture, Props & List Rendering",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 114500,
                                "duration_text": "50 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Pass data downwards with props, use children props, and map arrays with stable keys.",
                                "reading_urls": [
                                    {"title": "React Docs: Passing Props to a Component", "url": "https://react.dev/learn/passing-props-to-a-component"}
                                ]
                            }
                        ]
                    },
                    {
                        "week_number": 7,
                        "title": "Week 7: React State, useState & Side Effects with useEffect",
                        "objective": "Manage dynamic component state with useState, handle controlled forms, synchronize with browser APIs, and fetch external data with useEffect.",
                        "checklist": [
                            "Implement useState for interactive counters, toggles, and form inputs",
                            "Manage controlled form elements and multi-input state objects",
                            "Execute side effects, API requests, and cleanup functions with useEffect",
                            "Prevent infinite rendering loops and understand dependency arrays"
                        ],
                        "lessons": [
                            {
                                "id": "w7_l1",
                                "title": "useState Hook & Controlled Form State",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 118200,
                                "duration_text": "60 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Manage local state, updater functions, immutable object updates, and controlled text/select inputs.",
                                "reading_urls": [
                                    {"title": "React Docs: State a Component's Memory", "url": "https://react.dev/learn/state-a-components-memory"}
                                ]
                            },
                            {
                                "id": "w7_l2",
                                "title": "useEffect Hook, Lifecycle & API Integration",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 130622,
                                "duration_text": "65 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Fetch data on mount, synchronize with localStorage, and execute cleanups.",
                                "reading_urls": [
                                    {"title": "React Docs: Synchronizing with Effects", "url": "https://react.dev/learn/synchronizing-with-effects"}
                                ]
                            },
                            {
                                "id": "w7_l3",
                                "title": "Supplementary: Full React 18 Crash Course",
                                "video_id": "x4rFhThSX04",
                                "start_seconds": 0,
                                "duration_text": "45 Mins",
                                "instructor": "freeCodeCamp Community",
                                "objectives": "Consolidate React core mental models with real project walkthroughs.",
                                "reading_urls": [
                                    {"title": "The Odin Project: React Course", "url": "https://www.theodinproject.com/paths/full-stack-javascript/courses/react"}
                                ]
                            }
                        ]
                    },
                    {
                        "week_number": 8,
                        "title": "Week 8: Routing, Architecture & Phase 2 Project",
                        "objective": "Set up client-side page navigation with React Router, handle loading/error skeletons, and build the React Task Manager application.",
                        "checklist": [
                            "Install and configure React Router DOM (BrowserRouter, Routes, Route, Link)",
                            "Implement URL route parameters and 404 Not Found fallback pages",
                            "Create reusable UI component library (Buttons, Modals, Cards, Badges)",
                            "Build Phase 2 Project: React Task Manager & API Dashboard"
                        ],
                        "lessons": [
                            {
                                "id": "w8_l1",
                                "title": "Client-Side Routing with React Router",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 134500,
                                "duration_text": "55 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Build multi-page Single Page Applications without page reloads using React Router.",
                                "reading_urls": [
                                    {"title": "React Router Official Tutorial", "url": "https://reactrouter.com/en/main/start/tutorial"}
                                ]
                            },
                            {
                                "id": "w8_l2",
                                "title": "Frontend Error Boundaries, Loading States & Toast Notifications",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 136200,
                                "duration_text": "45 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Design production-ready user experiences with optimistic UI, spinner states, and toast alerts.",
                                "reading_urls": [
                                    {"title": "MDN: Handling Errors", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Control_flow_and_error_handling"}
                                ]
                            }
                        ]
                    }
                ]
            },

            # ==================================================================
            # PHASE 3: BACKEND DEVELOPMENT (Weeks 9-12)
            # ==================================================================
            {
                "phase_number": 3,
                "title": "Phase 3: Backend Development with Node & Express",
                "tagline": "Scalable REST APIs, Server Architecture & Authentication Security",
                "weeks_range": "Weeks 9–12",
                "summary": "Transition to backend engineering: understand the V8 JavaScript runtime in Node.js, organize modular server code, build RESTful microservices with Express.js, handle JSON requests/responses, implement middleware pipelines, and secure endpoints with password hashing (bcrypt) and JWT tokens.",
                "weeks": [
                    {
                        "week_number": 9,
                        "title": "Week 9: Node.js Runtime, NPM & Modular Architecture",
                        "objective": "Understand the event loop, non-blocking I/O, npm package management, and write modular backend utilities.",
                        "checklist": [
                            "Understand Node.js single-threaded event loop and asynchronous architecture",
                            "Manage project dependencies with package.json, npm scripts, and semver",
                            "Import and export modules with CommonJS and ES Modules",
                            "Read/write files with Node.js fs module and inspect process.env"
                        ],
                        "lessons": [
                            {
                                "id": "w9_l1",
                                "title": "Node.js Runtime Architecture & Non-Blocking Event Loop",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 76782,
                                "duration_text": "55 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Learn how Node executes JavaScript on the server, global objects, and asynchronous callbacks.",
                                "reading_urls": [
                                    {"title": "Node.js Official About Guide", "url": "https://nodejs.org/en/about/"}
                                ]
                            },
                            {
                                "id": "w9_l2",
                                "title": "NPM Package Management & Modern ES Modules",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 78500,
                                "duration_text": "45 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Structure backend projects, configure package.json scripts, nodemon auto-restart, and environment variables.",
                                "reading_urls": [
                                    {"title": "Node.js Docs: ES Modules", "url": "https://nodejs.org/api/esm.html"}
                                ]
                            }
                        ]
                    },
                    {
                        "week_number": 10,
                        "title": "Week 10: Express.js Server Setup, Routing & Middleware",
                        "objective": "Build HTTP web servers with Express, structure clean controller routes, and implement request logging and validation middleware.",
                        "checklist": [
                            "Initialize an Express server listening on configurable PORT",
                            "Define GET, POST, PUT, DELETE endpoints with express.Router",
                            "Parse JSON request bodies using express.json() middleware",
                            "Write custom middleware for logging, rate limiting, and error handling"
                        ],
                        "lessons": [
                            {
                                "id": "w10_l1",
                                "title": "Express.js Fundamentals: App, Request & Response Objects",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 80000,
                                "duration_text": "50 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Understand req.params, req.query, req.body, and res.status().json() methods.",
                                "reading_urls": [
                                    {"title": "Express.js Guide: Basic Routing", "url": "https://expressjs.com/en/starter/basic-routing.html"}
                                ]
                            },
                            {
                                "id": "w10_l2",
                                "title": "Middleware Pipeline & Centralized Error Handlers",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 81771,
                                "duration_text": "60 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Master the next() middleware chain and catch unexpected backend exceptions safely.",
                                "reading_urls": [
                                    {"title": "Express.js Guide: Using Middleware", "url": "https://expressjs.com/en/guide/using-middleware.html"}
                                ]
                            }
                        ]
                    },
                    {
                        "week_number": 11,
                        "title": "Week 11: RESTful API Design, CRUD Operations & Validation",
                        "objective": "Design standard REST APIs adhering to HTTP status codes, implement CRUD logic, and validate client inputs.",
                        "checklist": [
                            "Design idempotent REST resource endpoints (/api/v1/resources)",
                            "Use proper HTTP status codes (200, 201, 400, 401, 403, 404, 500)",
                            "Validate client payloads with Joi or Zod schemas",
                            "Test and document APIs with Postman or Thunder Client"
                        ],
                        "lessons": [
                            {
                                "id": "w11_l1",
                                "title": "REST Architecture Principles & Resource Naming",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 83500,
                                "duration_text": "50 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Follow industry standard API conventions, plural nouns, and semantic status codes.",
                                "reading_urls": [
                                    {"title": "Roadmap.sh: REST API Guide", "url": "https://roadmap.sh/guides/rest-api"}
                                ]
                            },
                            {
                                "id": "w11_l2",
                                "title": "Building Complete In-Memory CRUD Endpoints",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 85000,
                                "duration_text": "55 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Implement create, read, update, delete operations with comprehensive input validation.",
                                "reading_urls": [
                                    {"title": "MDN: HTTP Status Codes", "url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status"}
                                ]
                            }
                        ]
                    },
                    {
                        "week_number": 12,
                        "title": "Week 12: Authentication, Password Hashing & JWT Security",
                        "objective": "Implement secure user registration, hash passwords with bcrypt, sign and verify JSON Web Tokens (JWT), and protect private routes.",
                        "checklist": [
                            "Never store plain-text passwords: hash with bcrypt salt rounds",
                            "Issue signed JWT tokens upon verified user credentials",
                            "Implement authMiddleware to decode Bearer tokens and attach req.user",
                            "Build Phase 3 Project: Secure Auth REST API"
                        ],
                        "lessons": [
                            {
                                "id": "w12_l1",
                                "title": "Password Hashing with Bcrypt & Salt Rounds",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 86800,
                                "duration_text": "50 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Understand one-way cryptographic hashing, timing attacks, and salt generation.",
                                "reading_urls": [
                                    {"title": "OWASP: Password Storage Cheat Sheet", "url": "https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html"}
                                ]
                            },
                            {
                                "id": "w12_l2",
                                "title": "JSON Web Tokens (JWT) & Protected Route Middleware",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 88200,
                                "duration_text": "60 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Sign stateless auth tokens, configure expiration, and guard private endpoints.",
                                "reading_urls": [
                                    {"title": "jwt.io: Introduction to JSON Web Tokens", "url": "https://jwt.io/introduction"}
                                ]
                            }
                        ]
                    }
                ]
            },

            # ==================================================================
            # PHASE 4: DATABASE & FULL STACK INTEGRATION (Weeks 13-15)
            # ==================================================================
            {
                "phase_number": 4,
                "title": "Phase 4: Database & Full Stack Integration",
                "tagline": "Relational Data Modeling with PostgreSQL & End-to-End Connectivity",
                "weeks_range": "Weeks 13–15",
                "summary": "Master enterprise persistence: understand relational database architecture, relational normalization, SQL queries (SELECT, INSERT, UPDATE, DELETE, JOINs), connect Node.js to PostgreSQL using pg/Prisma/Knex, and connect your React frontend to your Express backend into a unified full-stack application.",
                "weeks": [
                    {
                        "week_number": 13,
                        "title": "Week 13: Database Fundamentals, Relational Modeling & SQL",
                        "objective": "Understand relational database tables, primary/foreign keys, one-to-many & many-to-many schemas, and fundamental SQL syntax.",
                        "checklist": [
                            "Understand relational vs document database trade-offs",
                            "Design normalized schemas with primary keys and foreign key constraints",
                            "Execute CREATE TABLE, DROP TABLE, ALTER TABLE statements",
                            "Write foundational queries: SELECT, WHERE, ORDER BY, LIMIT"
                        ],
                        "lessons": [
                            {
                                "id": "w13_l1",
                                "title": "Relational Database Concepts & Schema Normalization",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 89571,
                                "duration_text": "55 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Learn table relations, normalization rules (1NF, 2NF, 3NF), and entity-relationship diagrams.",
                                "reading_urls": [
                                    {"title": "PostgreSQL Tutorial: What is PostgreSQL", "url": "https://www.postgresqltutorial.com/postgresql-getting-started/what-is-postgresql/"}
                                ]
                            },
                            {
                                "id": "w13_l2",
                                "title": "Core SQL Queries: SELECT, Filter, Insert & Update",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 90805,
                                "duration_text": "60 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Query records, filter with AND/OR/LIKE, insert new rows, and execute safe updates.",
                                "reading_urls": [
                                    {"title": "PostgreSQL Tutorial: Basic SQL Queries", "url": "https://www.postgresqltutorial.com/postgresql-tutorial/postgresql-select/"}
                                ]
                            }
                        ]
                    },
                    {
                        "week_number": 14,
                        "title": "Week 14: PostgreSQL Deep Dive, Joins, Indexes & Transactions",
                        "objective": "Master multi-table INNER and LEFT JOINs, aggregate functions (COUNT, SUM, AVG), indexing for high performance, and transactions.",
                        "checklist": [
                            "Write multi-table INNER JOIN and LEFT JOIN queries",
                            "Group records with GROUP BY and filter aggregates with HAVING",
                            "Create B-tree indexes on foreign keys and frequently queried columns",
                            "Understand ACID properties and write BEGIN...COMMIT transactions"
                        ],
                        "lessons": [
                            {
                                "id": "w14_l1",
                                "title": "SQL Multi-Table Joins (INNER, LEFT, RIGHT) & Aggregations",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 95000,
                                "duration_text": "65 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Link tables seamlessly, calculate summary statistics, and avoid Cartesian products.",
                                "reading_urls": [
                                    {"title": "PostgreSQL Tutorial: Joins", "url": "https://www.postgresqltutorial.com/postgresql-tutorial/postgresql-joins/"}
                                ]
                            },
                            {
                                "id": "w14_l2",
                                "title": "Database Indexing, Constraints & ACID Transactions",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 100000,
                                "duration_text": "55 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Optimize query execution plans with indexes and protect data integrity with transactions.",
                                "reading_urls": [
                                    {"title": "PostgreSQL Tutorial: Indexes", "url": "https://www.postgresqltutorial.com/postgresql-indexes/"}
                                ]
                            }
                        ]
                    },
                    {
                        "week_number": 15,
                        "title": "Week 15: Full Stack Integration (React + Express + PostgreSQL)",
                        "objective": "Connect your React client to your Express REST API, query PostgreSQL, manage CORS, and implement authenticated full-stack workflows.",
                        "checklist": [
                            "Connect Node to PostgreSQL with connection pooling (pg Pool)",
                            "Configure CORS headers to allow React client communication",
                            "Store JWT tokens in client state / secure cookies",
                            "Build Phase 4 Project: Full Stack Database-Connected CRUD Application"
                        ],
                        "lessons": [
                            {
                                "id": "w15_l1",
                                "title": "Connecting Node.js & Express to PostgreSQL with Connection Pools",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 105000,
                                "duration_text": "60 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Use node-postgres (pg) pool to execute parameterized queries safely against SQL injections.",
                                "reading_urls": [
                                    {"title": "node-postgres Official Documentation", "url": "https://node-postgres.com/"}
                                ]
                            },
                            {
                                "id": "w15_l2",
                                "title": "Bridging React Frontend with Backend API & CORS",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 108000,
                                "duration_text": "55 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Consume authenticated backend endpoints from React with Axios or Fetch, handling loading and error states.",
                                "reading_urls": [
                                    {"title": "MDN: Cross-Origin Resource Sharing (CORS)", "url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS"}
                                ]
                            }
                        ]
                    }
                ]
            },

            # ==================================================================
            # PHASE 5: PRODUCTION & CAREER PREPARATION (Weeks 16-20)
            # ==================================================================
            {
                "phase_number": 5,
                "title": "Phase 5: Production & Career Preparation",
                "tagline": "TypeScript, Automated Testing, Cloud Deployment & Capstone Evaluation",
                "weeks_range": "Weeks 16–20",
                "summary": "Elevate your code to production standards: write type-safe code with TypeScript in React and Node, implement automated unit and integration tests, secure applications against OWASP top vulnerabilities, deploy to cloud providers (Render/Vercel/Supabase), prepare tech resumes, and submit the evaluated Job Application Tracker Capstone project.",
                "weeks": [
                    {
                        "week_number": 16,
                        "title": "Week 16: TypeScript Fundamentals & Type Safety in React",
                        "objective": "Understand static typing, interfaces, generics, and add TypeScript to React components and Node backend utilities.",
                        "checklist": [
                            "Configure tsconfig.json for modern full-stack development",
                            "Define interfaces, types, union types, and optional properties",
                            "Type React component props, state hooks, and DOM events",
                            "Type Express request handlers and database entity interfaces"
                        ],
                        "lessons": [
                            {
                                "id": "w16_l1",
                                "title": "TypeScript Fundamentals: Types, Interfaces & Unions",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 144746,
                                "duration_text": "60 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Learn type inference, primitive types, object interfaces, and enum/union patterns.",
                                "reading_urls": [
                                    {"title": "TypeScript Official Handbook", "url": "https://www.typescriptlang.org/docs/handbook/intro.html"}
                                ]
                            },
                            {
                                "id": "w16_l2",
                                "title": "TypeScript in React Components & Hooks",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 152121,
                                "duration_text": "60 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Type useState, useEffect, custom props, and form submission events safely.",
                                "reading_urls": [
                                    {"title": "React TypeScript Cheatsheet", "url": "https://react-typescript-cheatsheet.netlify.app/"}
                                ]
                            }
                        ]
                    },
                    {
                        "week_number": 17,
                        "title": "Week 17: Testing, Debugging & Web Security Fundamentals",
                        "objective": "Write unit and API tests with Jest / Vitest, debug network failures, and protect applications against common security vulnerabilities.",
                        "checklist": [
                            "Write unit tests for utility functions with Vitest or Jest",
                            "Test Express API endpoints with Supertest",
                            "Defend against OWASP vulnerabilities: SQL injection, XSS, CSRF, and CORS leaks",
                            "Use Chrome DevTools performance profiler and network waterfall tabs"
                        ],
                        "lessons": [
                            {
                                "id": "w17_l1",
                                "title": "Automated Testing for APIs & Frontend Components",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 153500,
                                "duration_text": "55 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Understand test assertions, mocking external APIs, and test-driven development basics.",
                                "reading_urls": [
                                    {"title": "Vitest Getting Started", "url": "https://vitest.dev/guide/"}
                                ]
                            },
                            {
                                "id": "w17_l2",
                                "title": "Web Security Essentials: OWASP Top 10 & Defenses",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 154200,
                                "duration_text": "50 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Sanitize inputs, implement security headers with Helmet, and manage sensitive secrets.",
                                "reading_urls": [
                                    {"title": "OWASP Top 10 Web Application Security Risks", "url": "https://owasp.org/www-project-top-ten/"}
                                ]
                            }
                        ]
                    },
                    {
                        "week_number": 18,
                        "title": "Week 18: Cloud Deployment, Environment Config & Monitoring",
                        "objective": "Deploy PostgreSQL to managed clouds (Supabase/Neon), deploy Express API to Render, deploy React frontend to Vercel/Netlify, and manage production env secrets.",
                        "checklist": [
                            "Provision hosted PostgreSQL databases with SSL connection strings",
                            "Deploy Node Express backends to Render / Railway with environment variables",
                            "Deploy React frontends to Vercel / Netlify with custom domain DNS",
                            "Implement health-check endpoints (/healthz) and basic uptime monitoring"
                        ],
                        "lessons": [
                            {
                                "id": "w18_l1",
                                "title": "Cloud Production Deployment: Frontend, Backend & Database",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 155181,
                                "duration_text": "65 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Deploy full-stack applications with production builds, environment variables, and zero CORS errors.",
                                "reading_urls": [
                                    {"title": "Render Web Services Deployment Guide", "url": "https://render.com/docs/web-services"}
                                ]
                            }
                        ]
                    },
                    {
                        "week_number": 19,
                        "title": "Week 19: Technical Interview Preparation (DSA, OOP, DBMS)",
                        "objective": "Review essential Data Structures & Algorithms, Object-Oriented Principles, Database indexing concepts, and common technical interview questions.",
                        "checklist": [
                            "Review time & space complexity (Big O) and core arrays/hashmaps patterns",
                            "Master OOP principles: Encapsulation, Abstraction, Inheritance, Polymorphism",
                            "Review DBMS fundamentals: Normalization, Indexing, Transactions, and ACID",
                            "Practice live technical whiteboard problems and behavioral STAR stories"
                        ],
                        "lessons": [
                            {
                                "id": "w19_l1",
                                "title": "Full Stack Tech Interview Roadmap: DSA, System Design & DBMS",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 137149,
                                "duration_text": "60 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Master technical interview questions frequently asked at tech startups and product companies.",
                                "reading_urls": [
                                    {"title": "Roadmap.sh: Backend & Frontend Interview Questions", "url": "https://roadmap.sh/questions"}
                                ]
                            }
                        ]
                    },
                    {
                        "week_number": 20,
                        "title": "Week 20: Capstone Project Evaluation, GitHub Portfolio & Certification",
                        "objective": "Complete and submit your Job Application Tracker Capstone project, optimize your GitHub portfolio, and earn your verified certificate and 50% Cashback reward.",
                        "checklist": [
                            "Complete all mandatory features of the Job Application Tracker Capstone",
                            "Verify live deployment accessibility and clean GitHub README with architecture diagram",
                            "Submit project links for senior engineering rubric evaluation",
                            "Request 50% Completion Cashback upon passing review and verified milestone completion"
                        ],
                        "lessons": [
                            {
                                "id": "w20_l1",
                                "title": "Capstone Submission Walkthrough & Code Quality Standards",
                                "video_id": "LzMnsfqjzkA",
                                "start_seconds": 138500,
                                "duration_text": "45 Mins",
                                "instructor": "freeCodeCamp / Scrimba",
                                "objectives": "Review the evaluation criteria for the Job Application Tracker capstone project.",
                                "reading_urls": [
                                    {"title": "SkillRock: Capstone Rubrics & Guidelines", "url": "#rubrics"}
                                ]
                            }
                        ]
                    }
                ]
            }
        ],
        "projects": [
            {
                "id": "proj_p1",
                "phase_number": 1,
                "title": "Phase 1 Project: Personal Developer Portfolio Website",
                "tagline": "Build a responsive, modern personal developer website showcasing projects, skills, and contact form.",
                "problem_statement": "Aspiring engineers need a clean, responsive personal portfolio to establish their identity and showcase coursework.",
                "required_features": [
                    "Semantic HTML5 document structure with navigation, about, skills, projects, and contact sections",
                    "Modern responsive CSS using Flexbox and Grid without relying on heavy UI libraries",
                    "Interactive JavaScript features (theme toggle, mobile menu, or project filter buttons)",
                    "Working contact form with client-side field validation",
                    "Clean code, organized CSS/JS files, and public GitHub repository with README"
                ],
                "tech_requirements": "HTML5, CSS3, Vanilla JavaScript, Git & GitHub.",
                "bonus_challenges": [
                    "Add subtle CSS keyframe animations or micro-interactions",
                    "Deploy live on GitHub Pages or Vercel and include the live URL in your submission"
                ],
                "rubric": [
                    {"criterion": "Semantic Markup & Accessibility", "max_points": 25, "description": "Proper HTML5 semantic tags, alt tags, and accessible contrast."},
                    {"criterion": "Responsive Design & Visual Quality", "max_points": 35, "description": "Flawless mobile, tablet, and desktop layout using modern CSS."},
                    {"criterion": "JavaScript Functionality & Interactivity", "max_points": 25, "description": "Working DOM manipulation, event listeners, and clean code."},
                    {"criterion": "Repository Quality & README", "max_points": 15, "description": "Meaningful Git commit history and well-documented README."}
                ],
                "passing_score": 70
            },
            {
                "id": "proj_p2",
                "phase_number": 2,
                "title": "Phase 2 Project: React Task Manager & API Dashboard",
                "tagline": "Build an interactive single-page React productivity application with external API integration.",
                "problem_statement": "Students must demonstrate mastery of React component trees, props, useState, useEffect, and API communication.",
                "required_features": [
                    "Scaffolded with Vite + React",
                    "Task creation, editing, deletion, priority tagging, and completion status toggles",
                    "Persistent state stored in browser localStorage or fetched from a public REST API",
                    "Search and filtering by category or completion state",
                    "Responsive UI with loading indicators and error banners"
                ],
                "tech_requirements": "React 18+, Vite, JavaScript ES6+, CSS/Tailwind, Git & GitHub.",
                "bonus_challenges": [
                    "Incorporate React Router for multi-view navigation",
                    "Deploy live to Vercel or Netlify"
                ],
                "rubric": [
                    {"criterion": "Component Architecture & State Management", "max_points": 35, "description": "Proper hook usage (useState, useEffect) and clean component decomposition."},
                    {"criterion": "Feature Completeness & UX", "max_points": 30, "description": "All task management, search, and filtering features functional."},
                    {"criterion": "Code Quality & Organization", "max_points": 20, "description": "Modular folder structure, clean imports, and readable code."},
                    {"criterion": "Documentation & Deployment", "max_points": 15, "description": "Live working URL and well-documented repository."}
                ],
                "passing_score": 70
            },
            {
                "id": "proj_p3",
                "phase_number": 3,
                "title": "Phase 3 Project: Secure Authentication REST API with Express",
                "tagline": "Build a modular Node.js Express backend service with bcrypt password hashing and JWT authentication.",
                "problem_statement": "Backend engineers must be capable of architecting secure REST services with authentication and input validation.",
                "required_features": [
                    "Express server with modular router and controller architecture",
                    "User registration with email validation and bcrypt password hashing",
                    "User login generating signed JSON Web Tokens (JWT)",
                    "Protected endpoints requiring Authorization: Bearer <token>",
                    "Centralized error handling middleware and structured JSON responses"
                ],
                "tech_requirements": "Node.js, Express.js, bcrypt, jsonwebtoken, Joi/Zod, Git & GitHub.",
                "bonus_challenges": [
                    "Implement refresh token rotation or password reset workflow",
                    "Include an automated Postman test collection"
                ],
                "rubric": [
                    {"criterion": "Security & Cryptographic Standards", "max_points": 35, "description": "Safe password hashing, salt rounds, and proper JWT verification."},
                    {"criterion": "RESTful API Design & Status Codes", "max_points": 30, "description": "Accurate HTTP status codes, error payloads, and controller patterns."},
                    {"criterion": "Middleware Pipeline & Validation", "max_points": 20, "description": "Robust input sanitation and centralized exception catching."},
                    {"criterion": "Repository Quality & Testing", "max_points": 15, "description": "Clean Git history, environment variable templates (.env.example), and README."}
                ],
                "passing_score": 70
            },
            {
                "id": "proj_p4",
                "phase_number": 4,
                "title": "Phase 4 Project: Full Stack Database-Connected CRUD Application",
                "tagline": "Connect React frontend, Express backend, and PostgreSQL database into an integrated system.",
                "problem_statement": "Full stack engineers must integrate all layers: user interface, server API, and relational database persistence.",
                "required_features": [
                    "PostgreSQL relational schema with foreign key relationships",
                    "Express backend executing parameterized SQL queries preventing SQL injections",
                    "React client consuming backend endpoints with loading and error states",
                    "Full CRUD functionality (Create, Read, Update, Delete) persisting to PostgreSQL",
                    "CORS configuration allowing secure cross-origin communication"
                ],
                "tech_requirements": "React, Node.js, Express.js, PostgreSQL (pg / Knex / Prisma), Git & GitHub.",
                "bonus_challenges": [
                    "Implement multi-table JOINs and search indexing",
                    "Deploy backend and PostgreSQL database to Render/Supabase"
                ],
                "rubric": [
                    {"criterion": "Full Stack Architecture & End-to-End Integration", "max_points": 35, "description": "Smooth data flow between React UI, Express server, and PostgreSQL database."},
                    {"criterion": "Database Modeling & Query Safety", "max_points": 30, "description": "Normalized schema, foreign keys, and parameterized query safety."},
                    {"criterion": "Error Handling & User Feedback", "max_points": 20, "description": "Graceful handling of server downtime, validation errors, and loading states."},
                    {"criterion": "Documentation & Deployment", "max_points": 15, "description": "Comprehensive README setup instructions and deployed application."}
                ],
                "passing_score": 70
            }
        ],
        "capstone": {
            "id": "capstone_job_tracker",
            "title": "Capstone Project: Job Application Tracker",
            "tagline": "The culminating full-stack production application evaluated for graduation, verified certification, and 50% Completion Cashback.",
            "problem_statement": """Job seekers often struggle to track job applications across dozens of companies, deadlines, interview stages, and technical interview notes.

Build an end-to-end, production-ready Full Stack Job Application Tracker that allows users to manage their career search with authentication, database persistence, status workflows, and visual analytics.

This project is the comprehensive evaluation requirement for the Full Stack Developer Launchpad.""",
            "required_features": [
                "User Authentication: Secure user registration and login with encrypted passwords and JWT/session management",
                "Job Application CRUD: Add, view, edit, and delete job applications (Company, Job Title, Salary, Job URL, Location, Status, Notes)",
                "Status Tracking: Categorize applications through stages: Applied, Interviewing, Offer, Rejected, Bookmarked",
                "Search & Filtering: Real-time search by company name, job role, and filter by application status and date",
                "Dashboard Statistics: Visual overview cards displaying total applications, active interviews, offer count, and rejection rate",
                "Relational Persistence: PostgreSQL database with user-to-application foreign key relationship and timestamps",
                "Responsive UI: Polished, modern frontend that adapts seamlessly to desktop and mobile devices",
                "Live Cloud Deployment: Fully deployed application with frontend and backend accessible over the public web",
                "Professional GitHub Repository: Clean Git commit history, architecture diagram, setup instructions, and tech stack details"
            ],
            "tech_requirements": """Frontend: React + Vite + CSS/Tailwind
Backend: Node.js + Express.js
Database: PostgreSQL
Authentication: JWT or secure sessions with bcrypt password hashing
Deployment: Render, Vercel, Supabase, or Railway
Version Control: Git + GitHub""",
            "bonus_challenges": [
                "Include TypeScript across frontend and backend codebases",
                "Add automated unit or integration tests (Vitest / Supertest)",
                "Add an interview calendar or reminder email feature"
            ],
            "rubric": [
                {"criterion": "Frontend Architecture & Responsive UX", "max_points": 20, "description": "Polished, intuitive UI, responsive on mobile & desktop, with loading/error states."},
                {"criterion": "Backend API Robustness & Security", "max_points": 20, "description": "Clean REST controllers, JWT middleware, input validation, and password encryption."},
                {"criterion": "PostgreSQL Modeling & Data Integrity", "max_points": 20, "description": "Proper relational constraints, parameterized queries, and safe operations."},
                {"criterion": "Feature Completeness & Dashboard Analytics", "max_points": 20, "description": "All mandatory features functional: search, filtering, statistics, and status transitions."},
                {"criterion": "Cloud Deployment & Documentation Quality", "max_points": 20, "description": "Active live deployment URL, well-structured GitHub README, and clean commit history."}
            ],
            "passing_score": 75
        }
    }
