# SkillRock Automated Test Infrastructure Specification (TEST_INFRA.md)

## 1. Executive Summary & Test Architecture

This document establishes the official End-to-End (E2E) and integration test infrastructure for the SkillRock platform enhancements. The test harness provides opaque-box verification across all functional, boundary, interaction, and real-world acceptance criteria defined in `ORIGINAL_REQUEST.md` and `PROJECT.md`.

### Core Technology Stack
- **Framework**: Python `unittest` standard library with Flask Test Client (`app.test_client()`).
- **Database Engine**: In-memory `mongomock` instance activated when `$env:MONGODB_URI = ""` or `os.environ["MONGODB_URI"] = ""`.
- **Session & Security**: Mock session transactions for simulated student and administrator authentication states; CSRF disabled in test configuration (`WTF_CSRF_ENABLED = False`).
- **Test File Location**: `tests/test_e2e_skillrock_suite.py`.

---

## 2. Environment Configuration & Test Isolation

All tests execute in strict isolation:
1. **Zero External Dependencies**: By setting `os.environ["MONGODB_URI"] = ""` and resetting the `models.mongo` database handle in `setUpClass()`, all database operations target an ephemeral, in-memory MongoDB mock collection.
2. **State Hygiene**: Every test suite and individual test case manages its own test fixtures (courses, users, assignments, enrollments, certificates) and cleans up its data in `setUp()` and `tearDown()`.
3. **Deterministic Execution**: Tests do not rely on execution order and can run in any sequence or in parallel.

### Execution Command
```powershell
cd "C:\Users\Tanishk Pal\OneDrive\Desktop\SkillRock"
$env:MONGODB_URI = ""
.\venv\Scripts\python.exe -m unittest tests/test_e2e_skillrock_suite.py
```

---

## 3. 4-Tier Test Methodology

The test suite is structured around a rigorous 4-tier testing hierarchy:

```
+-----------------------------------------------------------------------+
|  Tier 4: Real-World Workload / End-to-End User Journeys (Multi-step)  |
+-----------------------------------------------------------------------+
|  Tier 3: Cross-Feature Interactions (Auth <-> UI <-> Admin Panel)     |
+-----------------------------------------------------------------------+
|  Tier 2: Boundary, Corner & Resiliency Stress (Empty, Malformed, Edge) |
+-----------------------------------------------------------------------+
|  Tier 1: Feature Coverage (R1 Auth/Enroll, R2 UI Relocation, R3 Admin)|
+-----------------------------------------------------------------------+
```

### 3.1. Tier 1: Feature Coverage (>=5 tests per feature)

#### Feature R1: Automatic Course Enrollment & Registration Flow
- **R1.1**: Unauthenticated visitor clicking "Start Learning" on course card or detail page receives HTTP 302 redirecting to `/register?next=<target_course_url>`.
- **R1.2**: `/register` endpoint preserves and forwards the `next` query parameter across GET and POST.
- **R1.3**: New student registration with a course `next` parameter automatically creates an `Enrollment` document and redirects the user directly to the course player.
- **R1.4**: Existing student login with a course `next` parameter automatically enrolls the student (if not enrolled) and redirects directly to the course player.
- **R1.5**: Authenticated user clicking "Start Learning" (`/learning/courses/<slug>/start`) automatically enrolls immediately without a separate confirmation step and navigates to the player.
- **R1.6**: Unauthenticated requests to course learning content do not stream video lessons and display a locked/restricted learning overlay.

#### Feature R2: Responsive Course Credential Preview Relocation
- **R2.1**: Sample certificate preview card (`#certSampleSection`) is present on the course learning detail page.
- **R2.2**: Certificate preview card is located in the right sidebar column (`.course-sidebar-column` or `col-lg-4`), rather than below the video player in the left column.
- **R2.3**: Certificate preview card is positioned directly beneath the desktop course action/enrollment card.
- **R2.4**: Desktop layout grid specifies `2fr 1fr` or `col-lg-8` / `col-lg-4` with appropriate layout classes.
- **R2.5**: Mobile and tablet styles (< 992px) stack cleanly with the preview card positioned directly beneath the mobile action card with zero sticky element overlap.

#### Feature R3: Admin Panel User Progress and Enrollment Tracking
- **R3.1**: `/admin/users` user table contains an "Enrolled Courses" count summary column.
- **R3.2**: `/admin/users` user table contains an "Overall Progress" percentage summary column.
- **R3.3**: `/admin/users/<user_id>` displays all enrolled course titles along with enrollment dates.
- **R3.4**: `/admin/users/<user_id>` displays video lecture progress metrics (watch percentage, completion status, current watch time).
- **R3.5**: `/admin/users/<user_id>` displays capstone project submission status and review scores.
- **R3.6**: `/admin/users/<user_id>` displays issued certificate credentials (Certificate ID, issue date, SHA-256 verification hash).

---

### 3.2. Tier 2: Boundary & Corner Cases (>=5 tests per feature)

#### R1 Boundary & Corner Cases
- **R1-B1**: Malformed or non-existent course slug in `next` redirect target gracefully falls back without server 500 error.
- **R1-B2**: Double click / repeated invocation of `/learning/courses/<slug>/start` is idempotent and does not create duplicate enrollments.
- **R1-B3**: Re-clicking "Start Learning" on an already in-progress or completed course preserves existing watch progress and completion status.
- **R1-B4**: URL-encoded special characters, query strings, and fragments in `next` parameter are safely decoded and handled.
- **R1-B5**: Unauthenticated POST attempt to `/learning/save-progress` or `/learning/enrol/<course_id>` is rejected with 401 or redirect to login.

#### R2 Boundary & Corner Cases
- **R2-B1**: Extremely long course titles and student names fit inside the miniature certificate canvas without text clipping or horizontal overflow.
- **R2-B2**: Unauthenticated visitor state in relocated certificate preview card displays motivating registration CTA.
- **R2-B3**: Enrolled student state in relocated certificate preview card displays dynamic progress callout.
- **R2-B4**: Certified student state in relocated certificate preview card displays earned certificate verification badges.
- **R2-B5**: Mobile viewport breakpoint (`@media (max-width: 991.98px)`) stacks columns cleanly without horizontal scrollbars.

#### R3 Boundary & Corner Cases
- **R3-B1**: User with zero enrollments displays 0 enrolled courses and 0% overall progress without division-by-zero errors.
- **R3-B2**: User enrolled in multiple courses with varying watch percentages correctly computes the arithmetic average progress.
- **R3-B3**: User with submitted capstone pending review displays "Under Review" / "Pending" status with graceful empty/none score indicator.
- **R3-B4**: Completed course without certificate issued displays completion status while gracefully omitting or indicating unissued certificate credentials.
- **R3-B5**: Request to `/admin/users/<invalid_id>` with non-existent or invalid ObjectId returns 404 or redirect, never an unhandled 500 crash.

---

### 3.3. Tier 3: Cross-Feature Interactions

- **T3.1 (Full Student Lifecycle to Admin Audit)**: Anonymous user clicks "Start Learning" -> redirects to `/register?next=...` -> completes registration -> auto-enrolled -> redirected to course detail -> views relocated certificate preview card in sidebar -> streams lecture -> sends watch progress -> submits capstone -> admin reviews submission -> admin views `/admin/users` and `/admin/users/<user_id>` with exact matching metrics.
- **T3.2 (Multi-Course Cross-Enrollment & Aggregate Tracking)**: Student enrolls in Course A (0% watched) and Course B (80% watched) -> `/admin/users` reflects 2 courses and 40% aggregate progress -> `/admin/users/<user_id>` displays separate per-course cards.
- **T3.3 (Auth State Transitions & Viewport Integrity)**: State transitions from anonymous (locked player, sidebar preview) to authenticated (live player, enrolled sidebar) preserve DOM layout without breaking CSS grid structures.
- **T3.4 (Security & Privilege Isolation)**: Non-admin student accounts attempting to access `/admin/users` or `/admin/users/<user_id>` receive HTTP 403 or redirect to login.

---

### 3.4. Tier 4: Real-World Workload / End-to-End User Scenarios

- **T4.1 (Scenario A: Fast-Track Student Certification Pipeline)**: Complete simulation from initial enrollment through unskippable video milestone to capstone review and certificate generation.
- **T4.2 (Scenario B: Multi-User Administrator Cohort Monitoring)**: Cohort of multiple students with diverse academic states (unregistered, newly enrolled, halfway through lecture, pending capstone review, fully certified) simultaneously audited via admin user list and user detail endpoints.
- **T4.3 (Scenario C: Adversarial Stress & Resiliency)**: Simulated injection attempts in `next` parameters (e.g. `javascript:`, external URLs, SQL-like syntax), extreme watch timestamps, and concurrent session interactions.

---

## 4. Traceability Matrix

| Requirement | Acceptance Criteria | Test Method Name in `test_e2e_skillrock_suite.py` | Tier |
|---|---|---|---|
| R1 | Unauthenticated "Start Learning" redirect | `test_tier1_r1_unauthenticated_start_learning_redirects_to_register_with_next` | Tier 1 |
| R1 | Register form retains `next` parameter | `test_tier1_r1_register_page_preserves_and_forwards_next_param` | Tier 1 |
| R1 | Post-registration auto-enrollment | `test_tier1_r1_post_registration_auto_enrolls_and_navigates_to_player` | Tier 1 |
| R1 | Post-login auto-enrollment | `test_tier1_r1_post_login_auto_enrolls_with_next_param` | Tier 1 |
| R1 | Authenticated "Start Learning" auto-enroll | `test_tier1_r1_authenticated_direct_start_learning_auto_enrolls` | Tier 1 |
| R1 | Unauthenticated streaming protection | `test_tier1_r1_unauthenticated_user_cannot_stream_restricted_lessons` | Tier 1 |
| R1 | Invalid slug in next parameter | `test_tier2_r1_invalid_or_malicious_slug_in_next_param` | Tier 2 |
| R1 | Enrollment idempotency | `test_tier2_r1_double_start_learning_enrollment_idempotency` | Tier 2 |
| R1 | Retain existing progress on re-enroll | `test_tier2_r1_existing_progress_retained_on_re_start` | Tier 2 |
| R1 | URL encoding & query strings in `next` | `test_tier2_r1_encoded_next_url_with_query_params_and_hash` | Tier 2 |
| R1 | Unauthenticated progress update rejection | `test_tier2_r1_unauthenticated_api_save_progress_rejected` | Tier 2 |
| R2 | Certificate preview card present | `test_tier1_r2_cert_preview_present_in_course_detail` | Tier 1 |
| R2 | Preview card in sidebar column | `test_tier1_r2_cert_preview_located_in_sidebar_column` | Tier 1 |
| R2 | Preview card below action card | `test_tier1_r2_cert_preview_positioned_below_action_card` | Tier 1 |
| R2 | Desktop grid columns `col-lg-4` | `test_tier1_r2_desktop_grid_structure_and_col_width` | Tier 1 |
| R2 | Mobile stacking and zero sticky overlap | `test_tier1_r2_mobile_stacking_order_and_zero_sticky_overlap` | Tier 1 |
| R2 | Long course title handling | `test_tier2_r2_long_course_title_no_overflow_in_sidebar_cert` | Tier 2 |
| R2 | Unauthenticated visitor preview card CTA | `test_tier2_r2_unauthenticated_visitor_preview_card_cta` | Tier 2 |
| R2 | Enrolled student dynamic preview state | `test_tier2_r2_enrolled_student_preview_card_dynamic_state` | Tier 2 |
| R2 | Certified student preview state | `test_tier2_r2_completed_certified_student_preview_card_state` | Tier 2 |
| R2 | Mobile breakpoint CSS definition | `test_tier2_r2_css_mobile_breakpoint_at_991_98px_stacks_cleanly` | Tier 2 |
| R3 | `/admin/users` enrolled count column | `test_tier1_r3_admin_users_displays_enrolled_courses_count_column` | Tier 1 |
| R3 | `/admin/users` overall progress column | `test_tier1_r3_admin_users_displays_overall_progress_column` | Tier 1 |
| R3 | `/admin/users/<id>` enrolled course titles & dates | `test_tier1_r3_admin_user_detail_displays_enrolled_course_titles_and_dates` | Tier 1 |
| R3 | `/admin/users/<id>` video progress metrics | `test_tier1_r3_admin_user_detail_displays_video_progress_metrics` | Tier 1 |
| R3 | `/admin/users/<id>` capstone status & score | `test_tier1_r3_admin_user_detail_displays_capstone_status_and_scores` | Tier 1 |
| R3 | `/admin/users/<id>` certificate credentials | `test_tier1_r3_admin_user_detail_displays_certificate_credentials` | Tier 1 |
| R3 | Zero enrollments edge case | `test_tier2_r3_user_with_zero_enrollments_displays_clean_empty_state` | Tier 2 |
| R3 | Multi-course average progress computation | `test_tier2_r3_user_with_multiple_courses_calculates_accurate_average_progress` | Tier 2 |
| R3 | Pending capstone status display | `test_tier2_r3_user_with_pending_capstone_shows_pending_status_without_score` | Tier 2 |
| R3 | Unissued certificate graceful display | `test_tier2_r3_user_without_certificate_gracefully_handled` | Tier 2 |
| R3 | Invalid user ID handling (404/redirect) | `test_tier2_r3_invalid_user_id_returns_404_or_redirect_not_500` | Tier 2 |
| Cross | Full student lifecycle to admin audit | `test_tier3_e2e_student_lifecycle_registration_enrollment_preview_admin_visibility` | Tier 3 |
| Cross | Multi-course aggregate tracking | `test_tier3_multi_course_auto_enrollment_cross_tracking` | Tier 3 |
| Cross | Auth transitions & DOM integrity | `test_tier3_unauthenticated_redirect_to_auth_to_learning_layout_integrity` | Tier 3 |
| Cross | Admin route privilege enforcement | `test_tier3_security_privilege_isolation_for_admin_views` | Tier 3 |
| E2E | Fast-track student certification | `test_tier4_scenario_complete_student_certification_journey` | Tier 4 |
| E2E | Multi-user cohort monitoring | `test_tier4_scenario_admin_audit_and_student_monitoring_dashboard` | Tier 4 |
| E2E | Adversarial stress & tampering | `test_tier4_scenario_adversarial_tampering_and_privilege_isolation` | Tier 4 |

---

## 5. Verification & Acceptance Gate

A milestone or platform enhancement is considered **VERIFIED & READY** only when:
1. All 38 test cases in `tests/test_e2e_skillrock_suite.py` execute cleanly.
2. 0 failures and 0 errors are reported by `python -m unittest tests/test_e2e_skillrock_suite.py`.
3. Test execution time is under 10 seconds due to in-memory `mongomock` optimization.
