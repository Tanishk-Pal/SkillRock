# Project: SkillRock Platform Enhancements

## Architecture
- **Framework & Runtime**: Python 3.12, Flask, Jinja2 templates, Flask-Login authentication.
- **Database**: MongoDB via pymongo (`models/mongo.py`), with in-memory `mongomock` fallback for local unit testing when `MONGODB_URI` is empty.
- **Modules**:
  - `routes/auth.py`: Authentication, login, registration, password reset, OAuth.
  - `routes/learning.py`: Course listings, course detail, lesson playback, enrollment, capstone submissions.
  - `routes/admin.py`: Administrative dashboard, user management, course management, analytics.
  - `models/mongo.py`: Data models including `User`, `Course`, `Enrollment`, `Assignment`, `Submission`, `Review`, `Certificate`.
  - `templates/`: Jinja2 HTML templates partitioned into `learning/`, `admin/`, and root layouts.
  - `static/css/`: Custom stylesheets `style.css` and `mobile.css`.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Unauthenticated "Start Learning" Redirect | Clicking "Start Learning" while logged out redirects to `/register?next=<course_path>`. | M1 | ORIGINAL_REQUEST § R1 |
| 2 | Registration & Login `next` Parameter Retention | Retain and forward `next` redirect target through `/register` and `login.html`. | M1 | ORIGINAL_REQUEST § R1 |
| 3 | Auto-Enrollment Post-Auth | Auto-redirect back to course and immediately enroll user in course upon login/register. | M1 | ORIGINAL_REQUEST § R1 |
| 4 | Authenticated Direct "Start Learning" Auto-Enroll | Authenticated click on "Start Learning" auto-enrolls and navigates directly to course player. | M1 | ORIGINAL_REQUEST § R1 |
| 5 | Course Learning Content Protection | Unauthenticated users prevented from viewing/streaming restricted course lessons. | M1 | ORIGINAL_REQUEST § R1 |
| 6 | Certificate Preview Relocation | Move certificate preview card from beneath video area to right sidebar. | M2 | ORIGINAL_REQUEST § R2 |
| 7 | Desktop (>= 992px) Sidebar Positioning | Position preview card in `col-lg-4` right column directly below action/enrollment card. | M2 | ORIGINAL_REQUEST § R2 |
| 8 | Mobile (< 992px) Clean Stacking | Stack certificate preview card cleanly directly beneath course action card. | M2 | ORIGINAL_REQUEST § R2 |
| 9 | Fluid Responsiveness & Zero Overflow | Full responsiveness with no horizontal overflow, clipping, or sticky collisions. | M2 | ORIGINAL_REQUEST § R2 |
| 10 | Admin Users Table Summary Columns | `/admin/users` displays "Enrolled Courses" count and "Overall Progress" per user. | M3 | ORIGINAL_REQUEST § R3 |
| 11 | Admin User Detail Enrolled Courses & Dates | `/admin/users/<user_id>` displays enrolled course titles and enrollment dates. | M3 | ORIGINAL_REQUEST § R3 |
| 12 | Admin User Detail Video Lecture Progress | `/admin/users/<user_id>` displays watch percentage, completion status, and watch time. | M3 | ORIGINAL_REQUEST § R3 |
| 13 | Admin User Detail Capstone Status & Scores | `/admin/users/<user_id>` displays capstone submission status and review scores. | M3 | ORIGINAL_REQUEST § R3 |
| 14 | Admin User Detail Certificate Credentials | `/admin/users/<user_id>` displays Certificate ID, issue date, and SHA-256 hash. | M3 | ORIGINAL_REQUEST § R3 |
| 15 | Admin Views Mobile & Desktop Responsiveness | Ensure all admin views adapt cleanly on `< 992px` and `>= 992px`. | M3 | ORIGINAL_REQUEST § R3 |
| 16 | Comprehensive E2E Test Suite & Audit | Full verification test suite and forensic audit ensuring all criteria pass without regression. | M4 | ORIGINAL_REQUEST § Acceptance Criteria |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | M1: Automatic Course Enrollment & Auth Flow | Routes & templates for R1: `routes/auth.py`, `routes/learning.py`, `_course_card.html`, `course_detail.html` | None | DONE |
| 2 | M2: Responsive Course Credential Preview Relocation | Layout & styling for R2: `templates/learning/course_detail.html`, `static/css/style.css`, `static/css/mobile.css` | M1 | IN_PROGRESS |
| 3 | M3: Admin Panel User Progress and Enrollment Tracking | Routes & templates for R3: `routes/admin.py`, `templates/admin/users.html`, `templates/admin/user_detail.html` | None | PLANNED |
| 4 | M4: Final Verification, E2E Testing & Audit | End-to-end regression tests across all features, test tier execution, forensic integrity audit | M1, M2, M3 | PLANNED |

## Interface Contracts
### Auth ↔ Learning (Course Enrollment & Navigation)
- Endpoint: `GET /learning/courses/<slug>/start`
  - Unauthenticated: Redirects to `url_for('auth.register', next=url_for('learning.course_detail', slug=slug))`
  - Authenticated: Auto-enrolls student via `Enrollment.create(user_id, course.id)` if not already enrolled, redirects to `url_for('learning.course_detail', slug=slug, player=1, _anchor='skillrockPlayerFrame')`.
- Endpoint: `GET /register` & `POST /auth/login`
  - Retains `next` query parameter across GET and POST.
  - Upon successful registration or login: If `next` contains `/learning/courses/<slug>`, parse slug or course, automatically enroll user, and redirect to the course player.

### Learning View ↔ Layout & CSS
- Template: `templates/learning/course_detail.html`
  - Container classes: `.course-layout-grid`, `.course-main-column` (left), `.course-sidebar-column` with `col-lg-4` (right).
  - Certificate Preview Card (`#certSampleSection` / `.cert-sample-wrapper-card`) located inside `.course-sidebar-column` directly below `.course-action-card`.
  - CSS breakpoints: `@media (max-width: 991.98px)` stacks columns vertically so `#certSampleSection` appears immediately below the action card.

### Admin Controller ↔ Templates
- Route: `GET /admin/users`
  - Context dictionary `enriched_users` includes:
    - `"enrolled_courses_count"`: integer (count of user's enrollments)
    - `"overall_progress"`: integer (average `watch_percent` across enrolled courses, or 0 if none)
- Route: `GET /admin/users/<user_id>`
  - Context passed to `admin/user_detail.html` includes `enrollments_data`:
    - List of dicts, each with:
      - `"course_title"`: str
      - `"enrolled_at"`: datetime or formatted str
      - `"watch_percent"`: int (0–100)
      - `"video_completed"`: bool
      - `"current_watch_time"`: formatted str (e.g. "12:45")
      - `"capstone_status"`: str / status label
      - `"capstone_score"`: float/int or None
      - `"certificate"`: dict with `certificate_id`, `issued_at`, `verification_hash` (or None)

## Code Layout
- `routes/auth.py`: Exclusive write ownership for Milestone 1
- `routes/learning.py`: Exclusive write ownership for Milestone 1
- `templates/learning/_course_card.html`: Exclusive write ownership for Milestone 1
- `templates/learning/course_detail.html`: Write ownership M1 (player gating & CTA), then M2 (relocate `#certSampleSection`)
- `static/css/style.css` & `static/css/mobile.css`: Exclusive write ownership for Milestone 2
- `routes/admin.py`: Exclusive write ownership for Milestone 3
- `templates/admin/users.html`: Exclusive write ownership for Milestone 3
- `templates/admin/user_detail.html`: Exclusive write ownership for Milestone 3
- `tests/test_r1_enrollment_auth_flow.py`: Milestone 1 tests
- `tests/test_r2_responsive_cert_preview.py`: Milestone 2 tests
- `tests/test_r3_admin_progress_tracking.py`: Milestone 3 tests
- `tests/`: Final E2E test runs for Milestone 4
