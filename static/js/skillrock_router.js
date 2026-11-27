/**
 * SkillRock Instant Client-Side Router & Progressive Rendering Engine
 * ==============================================================================
 * YouTube/GitHub/Turbo-style persistent shell with zero-delay tab switching,
 * speculative hover prefetching, in-memory stale-while-revalidate caching,
 * instant URL & active navigation synchronization, and page-specific skeletons.
 * ==============================================================================
 */

(function initSkillRockRouter() {
    'use strict';

    if (window.SkillRockRouter) return;

    // In-memory LRU Page Cache
    const pageCache = new Map();
    const MAX_CACHE_ENTRIES = 35;
    const CACHE_TTL_MS = 2 * 60 * 1000; // 2 minutes

    // Active in-flight fetch controller
    let currentAbortController = null;
    let isNavigating = false;

    // Top Progress Bar Engine
    const ProgressBar = {
        bar: null,
        progress: 0,
        trickleTimer: null,
        safetyTimer: null,

        init() {
            this.bar = document.getElementById('topProgressBar');
        },

        start() {
            this.init();
            if (!this.bar) return;
            this.reset();
            this.bar.style.transition = 'transform 200ms cubic-bezier(0.1, 0.5, 0.1, 1), opacity 150ms ease';
            this.bar.style.opacity = '1';
            this.setProgress(0.28); // Instant tactile response on click (<10ms)

            this.trickleTimer = setInterval(() => {
                if (this.progress < 0.88) {
                    const remaining = 0.92 - this.progress;
                    this.setProgress(this.progress + remaining * 0.16);
                }
            }, 180);

            this.safetyTimer = setTimeout(() => {
                this.finish();
            }, 9000);
        },

        setProgress(val) {
            this.progress = Math.min(Math.max(val, 0), 1);
            if (this.bar) {
                this.bar.style.transform = `scaleX(${this.progress})`;
            }
        },

        finish() {
            if (this.trickleTimer) { clearInterval(this.trickleTimer); this.trickleTimer = null; }
            if (this.safetyTimer) { clearTimeout(this.safetyTimer); this.safetyTimer = null; }
            if (!this.bar) return;
            this.bar.style.transition = 'transform 100ms ease-out, opacity 200ms ease 80ms';
            this.setProgress(1);
            this.bar.style.opacity = '0';
            setTimeout(() => {
                if (this.progress >= 1) {
                    this.bar.style.transition = 'none';
                    this.setProgress(0);
                }
            }, 300);
        },

        reset() {
            if (this.trickleTimer) { clearInterval(this.trickleTimer); this.trickleTimer = null; }
            if (this.safetyTimer) { clearTimeout(this.safetyTimer); this.safetyTimer = null; }
            if (this.bar) {
                this.bar.style.transition = 'none';
                this.bar.style.opacity = '0';
                this.setProgress(0);
            }
        }
    };

    // =========================================================================
    // Page-Specific Skeleton Templates (Rendered instantly in <10ms)
    // =========================================================================
    const Skeletons = {
        courses() {
            return `
            <div class="learning-container" style="animation: fadeIn 0.15s ease-out;">
                <!-- Hero Banner Skeleton -->
                <div class="learning-hero-card" style="margin-bottom: 24px; position: relative; overflow: hidden; pointer-events: none;">
                    <div style="max-width: 740px;">
                        <div class="sk-pill sk-dark" style="width: 220px; height: 26px; border-radius: 9999px; margin-bottom: 14px;"></div>
                        <div class="sk-line sk-dark" style="width: 80%; height: 32px; border-radius: 8px; margin-bottom: 10px;"></div>
                        <div class="sk-line sk-dark" style="width: 55%; height: 32px; border-radius: 8px; margin-bottom: 16px;"></div>
                        <div class="sk-line sk-dark" style="width: 90%; height: 15px; border-radius: 6px; margin-bottom: 8px;"></div>
                        <div class="sk-line sk-dark" style="width: 70%; height: 15px; border-radius: 6px; margin-bottom: 20px;"></div>
                        <div style="display: flex; gap: 14px; flex-wrap: wrap;">
                            <div class="sk-pill sk-dark" style="width: 130px; height: 24px; border-radius: 9999px;"></div>
                            <div class="sk-pill sk-dark" style="width: 150px; height: 24px; border-radius: 9999px;"></div>
                            <div class="sk-pill sk-dark" style="width: 140px; height: 24px; border-radius: 9999px;"></div>
                        </div>
                    </div>
                </div>

                <!-- Category Chips Skeleton -->
                <div style="display: flex; gap: 8px; overflow-x: auto; padding-bottom: 10px; margin-bottom: 20px;">
                    <div class="sk-pill" style="width: 100px; height: 36px; border-radius: 9999px;"></div>
                    <div class="sk-pill" style="width: 140px; height: 36px; border-radius: 9999px;"></div>
                    <div class="sk-pill" style="width: 110px; height: 36px; border-radius: 9999px;"></div>
                    <div class="sk-pill" style="width: 130px; height: 36px; border-radius: 9999px;"></div>
                    <div class="sk-pill" style="width: 120px; height: 36px; border-radius: 9999px;"></div>
                </div>

                <!-- 6 Course Cards Grid Skeleton -->
                <div class="grid-3" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px;">
                    ${Array(6).fill(0).map(() => `
                        <div class="card course-card-custom" style="padding: 0; overflow: hidden; border-radius: 14px;">
                            <div class="sk-block" style="height: 180px; width: 100%;"></div>
                            <div style="padding: 18px;">
                                <div class="sk-line" style="width: 90px; height: 12px; margin-bottom: 8px;"></div>
                                <div class="sk-line" style="width: 90%; height: 20px; border-radius: 6px; margin-bottom: 6px;"></div>
                                <div class="sk-line" style="width: 70%; height: 20px; border-radius: 6px; margin-bottom: 12px;"></div>
                                <div class="sk-line" style="width: 100%; height: 13px; margin-bottom: 6px;"></div>
                                <div class="sk-line" style="width: 80%; height: 13px; margin-bottom: 14px;"></div>
                                <div class="sk-block" style="height: 38px; border-radius: 8px; margin-bottom: 12px;"></div>
                            </div>
                            <div style="padding: 12px 18px; border-top: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center;">
                                <div class="sk-pill" style="width: 80px; height: 20px;"></div>
                                <div class="sk-btn" style="width: 100px; height: 32px; border-radius: 8px;"></div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>`;
        },

        challenge() {
            return `
            <div class="container py-4" style="max-width: 1200px; animation: fadeIn 0.15s ease-out;">
                <!-- Challenge Hero Skeleton -->
                <div class="challenge-hero-card" style="padding: 34px 24px; text-align: center; border-radius: 18px; margin-bottom: 30px; background: #0F172A; border: 1px solid rgba(245, 158, 11, 0.2);">
                    <div class="sk-pill sk-dark" style="width: 220px; height: 28px; border-radius: 9999px; margin-bottom: 16px;"></div>
                    <div class="sk-line sk-dark" style="width: 60%; height: 34px; border-radius: 8px; margin: 0 auto 12px auto;"></div>
                    <div class="sk-line sk-dark" style="width: 75%; height: 16px; border-radius: 6px; margin: 0 auto 20px auto;"></div>
                    <div style="display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;">
                        <div class="sk-pill sk-dark" style="width: 150px; height: 26px; border-radius: 9999px;"></div>
                        <div class="sk-pill sk-dark" style="width: 160px; height: 26px; border-radius: 9999px;"></div>
                        <div class="sk-pill sk-dark" style="width: 150px; height: 26px; border-radius: 9999px;"></div>
                    </div>
                </div>

                <!-- Challenge Cards Grid Skeleton -->
                <div class="grid-3" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px;">
                    ${Array(3).fill(0).map(() => `
                        <div class="card" style="padding: 0; overflow: hidden; border-radius: 14px; border: 1px solid rgba(245, 158, 11, 0.25);">
                            <div class="sk-block" style="height: 185px; width: 100%;"></div>
                            <div style="padding: 18px;">
                                <div class="sk-line" style="width: 80px; height: 12px; margin-bottom: 8px;"></div>
                                <div class="sk-line" style="width: 85%; height: 20px; border-radius: 6px; margin-bottom: 8px;"></div>
                                <div class="sk-line" style="width: 95%; height: 13px; margin-bottom: 6px;"></div>
                                <div class="sk-line" style="width: 75%; height: 13px; margin-bottom: 14px;"></div>
                                <div class="sk-block" style="height: 34px; border-radius: 8px;"></div>
                            </div>
                            <div style="padding: 12px 18px; border-top: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center;">
                                <div class="sk-line" style="width: 80px; height: 18px;"></div>
                                <div class="sk-btn" style="width: 120px; height: 34px; border-radius: 8px;"></div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>`;
        },

        courseDetail() {
            return `
            <div class="course-detail-container" style="max-width: 1140px; margin: 0 auto; padding-bottom: 48px; animation: fadeIn 0.15s ease-out;">
                <!-- Header Breadcrumb Skeleton -->
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 12px; border-bottom: 1px solid var(--border-color);">
                    <div style="display: flex; gap: 10px; align-items: center;">
                        <div class="sk-btn" style="width: 80px; height: 32px; border-radius: 8px;"></div>
                        <div class="sk-pill" style="width: 90px; height: 24px; border-radius: 9999px;"></div>
                    </div>
                    <div class="sk-line" style="width: 140px; height: 16px;"></div>
                </div>

                <!-- 2-Column Grid Layout -->
                <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 28px;" class="course-layout-grid">
                    <div>
                        <!-- 16:9 Video Player Skeleton -->
                        <div class="sk-block" style="width: 100%; aspect-ratio: 16 / 9; border-radius: 14px; margin-bottom: 20px; background: #000000; position: relative;">
                            <div class="sk-circle" style="width: 60px; height: 60px; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); opacity: 0.7;"></div>
                        </div>

                        <!-- Progress Bar Card Skeleton -->
                        <div class="card" style="padding: 18px; margin-bottom: 20px; border-radius: 14px;">
                            <div class="sk-line" style="width: 180px; height: 18px; margin-bottom: 12px;"></div>
                            <div class="sk-block" style="width: 100%; height: 10px; border-radius: 9999px; margin-bottom: 10px;"></div>
                            <div class="sk-line" style="width: 120px; height: 12px;"></div>
                        </div>

                        <!-- About Skeleton -->
                        <div class="card" style="padding: 20px; border-radius: 14px; margin-bottom: 20px;">
                            <div class="sk-line" style="width: 220px; height: 22px; margin-bottom: 12px;"></div>
                            <div class="sk-line" style="width: 95%; height: 14px; margin-bottom: 8px;"></div>
                            <div class="sk-line" style="width: 85%; height: 14px; margin-bottom: 8px;"></div>
                            <div class="sk-line" style="width: 65%; height: 14px;"></div>
                        </div>
                    </div>

                    <!-- Right Column Sidebar Skeleton -->
                    <div class="course-sidebar-column">
                        <div class="card" style="padding: 20px; border-radius: 14px; margin-bottom: 16px;">
                            <div class="sk-line" style="width: 100px; height: 24px; margin-bottom: 14px;"></div>
                            <div class="sk-block" style="width: 100%; height: 42px; border-radius: 8px; margin-bottom: 14px;"></div>
                            <div class="sk-line" style="width: 90%; height: 12px; margin-bottom: 6px;"></div>
                            <div class="sk-line" style="width: 75%; height: 12px;"></div>
                        </div>
                        <div class="card" style="padding: 16px; border-radius: 14px;">
                            <div class="sk-block" style="width: 100%; aspect-ratio: 1.4; border-radius: 10px; margin-bottom: 12px;"></div>
                            <div class="sk-line" style="width: 120px; height: 14px;"></div>
                        </div>
                    </div>
                </div>
            </div>`;
        },

        dashboard() {
            return `
            <div class="container py-4" style="animation: fadeIn 0.15s ease-out;">
                <!-- Welcome Banner Skeleton -->
                <div class="card" style="padding: 24px; border-radius: 16px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
                    <div>
                        <div class="sk-line" style="width: 200px; height: 26px; border-radius: 6px; margin-bottom: 8px;"></div>
                        <div class="sk-line" style="width: 320px; height: 14px; border-radius: 4px;"></div>
                    </div>
                    <div style="display: flex; gap: 10px;">
                        <div class="sk-pill" style="width: 110px; height: 34px; border-radius: 8px;"></div>
                        <div class="sk-pill" style="width: 110px; height: 34px; border-radius: 8px;"></div>
                    </div>
                </div>

                <!-- Metric Cards Skeleton -->
                <div class="grid-4" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 28px;">
                    ${Array(4).fill(0).map(() => `
                        <div class="card" style="padding: 18px; border-radius: 12px;">
                            <div class="sk-circle" style="width: 38px; height: 38px; border-radius: 10px; margin-bottom: 10px;"></div>
                            <div class="sk-line" style="width: 60px; height: 26px; border-radius: 4px; margin-bottom: 6px;"></div>
                            <div class="sk-line" style="width: 110px; height: 12px; border-radius: 4px;"></div>
                        </div>
                    `).join('')}
                </div>

                <!-- Recent Courses Skeleton -->
                <div style="margin-bottom: 20px;">
                    <div class="sk-line" style="width: 180px; height: 22px; border-radius: 6px; margin-bottom: 16px;"></div>
                    <div class="grid-3" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 18px;">
                        ${Array(3).fill(0).map(() => `
                            <div class="card" style="padding: 16px; border-radius: 12px;">
                                <div class="sk-block" style="height: 140px; border-radius: 8px; margin-bottom: 12px;"></div>
                                <div class="sk-line" style="width: 80%; height: 18px; margin-bottom: 8px;"></div>
                                <div class="sk-block" style="height: 8px; border-radius: 9999px; margin-bottom: 12px;"></div>
                                <div class="sk-btn" style="height: 32px; border-radius: 6px;"></div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>`;
        },

        discover() {
            return `
            <div class="container py-4" style="animation: fadeIn 0.15s ease-out;">
                <!-- Header & Search Filter Skeleton -->
                <div class="page-header" style="margin-bottom: 24px;">
                    <div class="sk-line" style="width: 240px; height: 28px; margin-bottom: 8px;"></div>
                    <div class="sk-line" style="width: 360px; height: 14px; margin-bottom: 20px;"></div>
                    <div class="card" style="padding: 16px; border-radius: 12px; display: flex; gap: 12px; flex-wrap: wrap;">
                        <div class="sk-block" style="flex: 2; min-width: 200px; height: 40px; border-radius: 8px;"></div>
                        <div class="sk-block" style="flex: 1; min-width: 140px; height: 40px; border-radius: 8px;"></div>
                        <div class="sk-block" style="flex: 1; min-width: 140px; height: 40px; border-radius: 8px;"></div>
                    </div>
                </div>

                <!-- User Cards Skeleton -->
                <div class="grid-3" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 18px;">
                    ${Array(6).fill(0).map(() => `
                        <div class="card" style="padding: 18px; border-radius: 12px;">
                            <div style="display: flex; gap: 12px; align-items: center; margin-bottom: 14px;">
                                <div class="sk-circle" style="width: 48px; height: 48px;"></div>
                                <div>
                                    <div class="sk-line" style="width: 120px; height: 16px; margin-bottom: 6px;"></div>
                                    <div class="sk-line" style="width: 90px; height: 12px;"></div>
                                </div>
                            </div>
                            <div class="sk-line" style="width: 100%; height: 12px; margin-bottom: 6px;"></div>
                            <div class="sk-line" style="width: 80%; height: 12px; margin-bottom: 14px;"></div>
                            <div style="display: flex; gap: 6px; margin-bottom: 16px;">
                                <div class="sk-pill" style="width: 60px; height: 22px;"></div>
                                <div class="sk-pill" style="width: 75px; height: 22px;"></div>
                                <div class="sk-pill" style="width: 65px; height: 22px;"></div>
                            </div>
                            <div class="sk-btn" style="height: 36px; border-radius: 8px;"></div>
                        </div>
                    `).join('')}
                </div>
            </div>`;
        },

        profile() {
            return `
            <div class="container py-4" style="max-width: 900px; animation: fadeIn 0.15s ease-out;">
                <div class="card" style="padding: 24px; border-radius: 16px; margin-bottom: 24px;">
                    <div style="display: flex; gap: 18px; align-items: center; flex-wrap: wrap;">
                        <div class="sk-circle" style="width: 80px; height: 80px;"></div>
                        <div style="flex: 1;">
                            <div class="sk-line" style="width: 160px; height: 24px; margin-bottom: 8px;"></div>
                            <div class="sk-line" style="width: 220px; height: 14px; margin-bottom: 12px;"></div>
                            <div style="display: flex; gap: 8px;">
                                <div class="sk-pill" style="width: 90px; height: 24px;"></div>
                                <div class="sk-pill" style="width: 100px; height: 24px;"></div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="card" style="padding: 20px; border-radius: 14px;">
                    <div class="sk-line" style="width: 140px; height: 20px; margin-bottom: 16px;"></div>
                    <div class="grid-2" style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                        <div class="sk-block" style="height: 120px; border-radius: 10px;"></div>
                        <div class="sk-block" style="height: 120px; border-radius: 10px;"></div>
                    </div>
                </div>
            </div>`;
        },

        universal() {
            return `
            <div class="container py-4" style="animation: fadeIn 0.15s ease-out;">
                <div style="margin-bottom: 24px;">
                    <div class="sk-line" style="width: 220px; height: 28px; border-radius: 6px; margin-bottom: 10px;"></div>
                    <div class="sk-line" style="width: 340px; height: 14px; border-radius: 4px;"></div>
                </div>
                <div class="grid-3" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 18px;">
                    ${Array(6).fill(0).map(() => `
                        <div class="card" style="padding: 20px; border-radius: 12px;">
                            <div class="sk-line" style="width: 120px; height: 18px; margin-bottom: 12px;"></div>
                            <div class="sk-line" style="width: 100%; height: 14px; margin-bottom: 8px;"></div>
                            <div class="sk-line" style="width: 75%; height: 14px; margin-bottom: 16px;"></div>
                            <div class="sk-btn" style="height: 36px; border-radius: 8px;"></div>
                        </div>
                    `).join('')}
                </div>
            </div>`;
        },

        getForUrl(url) {
            const path = new URL(url, window.location.origin).pathname;
            if (path.startsWith('/learning/courses/') && path !== '/learning/courses' && path !== '/learning/courses/') {
                return this.courseDetail();
            }
            if (path.startsWith('/learning')) {
                return this.courses();
            }
            if (path.startsWith('/challenge/') && path !== '/challenge' && path !== '/challenge/') {
                return this.challenge();
            }
            if (path.startsWith('/challenge')) {
                return this.challenge();
            }
            if (path.startsWith('/dashboard')) {
                return this.dashboard();
            }
            if (path.startsWith('/discover')) {
                return this.discover();
            }
            if (path.startsWith('/profile')) {
                return this.profile();
            }
            return this.universal();
        }
    };

    // =========================================================================
    // Core Navigation & Router Engine
    // =========================================================================
    const Router = {
        init() {
            ProgressBar.init();

            // Intercept internal link clicks with high priority
            document.addEventListener('click', (e) => this.handleClick(e));

            // Speculative hover prefetch on desktop mouseover (debounced 65ms)
            let hoverTimer = null;
            document.addEventListener('mouseover', (e) => {
                const link = e.target.closest('a');
                if (!link) return;
                clearTimeout(hoverTimer);
                hoverTimer = setTimeout(() => {
                    this.prefetchLink(link);
                }, 65);
            }, { passive: true });

            // High-priority touchstart / pointerdown prefetch for mobile (starts download 120-200ms before touch release!)
            document.addEventListener('pointerdown', (e) => {
                const link = e.target.closest('a');
                if (link) this.prefetchLink(link);
            }, { passive: true });

            // Handle browser back and forward
            window.addEventListener('popstate', (e) => this.handlePopState(e));

            // Cache the initial page load so returning to it is 0ms
            this.cacheCurrentPage();

            // Auto-cleanup on mutations / form submissions
            document.addEventListener('submit', (e) => this.handleFormSubmit(e));

            console.info('[SkillRockRouter] Instant YouTube-style navigation engine active.');
        },

        isEligibleLink(link) {
            if (!link || !link.href) return false;
            if (link.target === '_blank' || link.hasAttribute('download')) return false;
            if (link.hasAttribute('data-no-instant') || link.classList.contains('no-instant')) return false;

            const href = link.getAttribute('href');
            if (!href || href.startsWith('#') || href.startsWith('javascript:') || href.startsWith('mailto:') || href.startsWith('tel:')) return false;

            try {
                const url = new URL(link.href, window.location.origin);
                // Must be same origin
                if (url.origin !== window.location.origin) return false;

                // Exclude hard auth/payment endpoints that require standard browser redirects
                const path = url.pathname;
                if (
                    path.startsWith('/auth/google') ||
                    path.startsWith('/auth/logout') ||
                    path.startsWith('/logout') ||
                    path.startsWith('/payment/process') ||
                    path.startsWith('/api/') ||
                    path.startsWith('/static/')
                ) {
                    return false;
                }

                return true;
            } catch (e) {
                return false;
            }
        },

        handleClick(e) {
            if (e.defaultPrevented || e.button !== 0 || e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) {
                return;
            }

            const link = e.target.closest('a');
            if (!this.isEligibleLink(link)) return;

            const targetUrl = link.href;
            const currentUrl = window.location.href;

            // If clicking the current exact URL with an anchor, allow normal scroll
            if (targetUrl === currentUrl || targetUrl === currentUrl + '#' || (targetUrl.includes('#') && targetUrl.split('#')[0] === currentUrl.split('#')[0])) {
                const hash = new URL(targetUrl).hash;
                if (hash) {
                    const el = document.querySelector(hash);
                    if (el) {
                        e.preventDefault();
                        el.scrollIntoView({ behavior: 'smooth' });
                        return;
                    }
                }
            }

            e.preventDefault();
            this.navigate(targetUrl, { pushState: true });
        },

        // Instant Navigation Execution (<15ms UI response)
        async navigate(targetUrl, options = { pushState: true }) {
            const urlObj = new URL(targetUrl, window.location.origin);
            const cleanUrl = urlObj.pathname + urlObj.search;

            // 1. Immediately update active UI state on sidebar, header, and mobile nav (<5ms)
            this.updateActiveNavState(targetUrl);

            // 2. Immediately update browser URL bar
            if (options.pushState) {
                history.pushState({ url: targetUrl, title: document.title }, '', targetUrl);
            }

            // 3. Start top progress bar
            ProgressBar.start();

            // 4. Check in-memory page cache (0ms instant swap if found!)
            const cached = pageCache.get(cleanUrl);
            const now = Date.now();

            if (cached && (now - cached.timestamp < CACHE_TTL_MS)) {
                this.renderPage(cached.html, cached.title, targetUrl);
                ProgressBar.finish();
                // Stale-while-revalidate background refresh
                this.backgroundRevalidate(cleanUrl, targetUrl);
                return;
            }

            // 5. If not cached, render target page skeleton immediately (<10ms)
            const liveContent = document.getElementById('livePageContent');
            if (liveContent) {
                const skeletonHtml = Skeletons.getForUrl(targetUrl);
                liveContent.innerHTML = skeletonHtml;
                window.scrollTo({ top: 0, behavior: 'instant' });
            }

            // 6. Fetch target page HTML asynchronously
            if (currentAbortController) {
                currentAbortController.abort();
            }
            currentAbortController = new AbortController();

            try {
                const resp = await fetch(targetUrl, {
                    headers: {
                        'X-Requested-With': 'SkillRock-SPA',
                        'Accept': 'text/html,application/xhtml+xml'
                    },
                    signal: currentAbortController.signal
                });

                // If redirected (e.g. to login), follow naturally
                if (resp.redirected && resp.url) {
                    window.location.href = resp.url;
                    return;
                }

                if (!resp.ok) {
                    // Fallback to standard browser navigation on 4xx/5xx
                    window.location.href = targetUrl;
                    return;
                }

                const htmlText = await resp.text();
                const doc = new DOMParser().parseFromString(htmlText, 'text/html');
                const title = doc.querySelector('title') ? doc.querySelector('title').innerText : document.title;

                // Cache page
                this.addToCache(cleanUrl, htmlText, title);

                // Render page content
                this.renderPage(htmlText, title, targetUrl);
                ProgressBar.finish();

            } catch (err) {
                if (err.name === 'AbortError') return;
                console.warn('[SkillRockRouter] Client navigation error, falling back to full reload:', err);
                window.location.href = targetUrl;
            }
        },

        renderPage(fullHtml, title, url) {
            document.title = title;

            const doc = new DOMParser().parseFromString(fullHtml, 'text/html');
            const newContent = doc.getElementById('livePageContent');
            const targetContainer = document.getElementById('livePageContent');

            if (newContent && targetContainer) {
                targetContainer.innerHTML = newContent.innerHTML;
            } else {
                // If structure differs, fallback
                window.location.href = url;
                return;
            }

            // Sync flashed alerts if present
            const newFlashes = doc.querySelector('.flash-container');
            const curFlashes = document.querySelector('.flash-container');
            if (newFlashes && curFlashes) {
                curFlashes.innerHTML = newFlashes.innerHTML;
            }

            // Re-render Lucide icons
            if (window.lucide && typeof window.lucide.createIcons === 'function') {
                try {
                    window.lucide.createIcons();
                } catch (e) {}
            }

            // Re-evaluate page-specific inline scripts
            this.executePageScripts(targetContainer);

            // Scroll to anchor or top
            const hash = new URL(url, window.location.origin).hash;
            if (hash) {
                const anchorEl = document.querySelector(hash);
                if (anchorEl) {
                    setTimeout(() => anchorEl.scrollIntoView({ behavior: 'smooth' }), 50);
                } else {
                    window.scrollTo({ top: 0, behavior: 'instant' });
                }
            } else {
                window.scrollTo({ top: 0, behavior: 'instant' });
            }

            // Dispatch global event for modular listeners
            window.dispatchEvent(new CustomEvent('skillrock:navigated', { detail: { url } }));
        },

        executePageScripts(container) {
            if (!container) return;
            const scripts = container.querySelectorAll('script');
            scripts.forEach((oldScript) => {
                const newScript = document.createElement('script');
                Array.from(oldScript.attributes).forEach((attr) => {
                    newScript.setAttribute(attr.name, attr.value);
                });
                newScript.textContent = oldScript.textContent;
                oldScript.parentNode.replaceChild(newScript, oldScript);
            });
        },

        // Instant UI Tab Sync (<5ms)
        updateActiveNavState(targetUrl) {
            const urlObj = new URL(targetUrl, window.location.origin);
            const path = urlObj.pathname;

            // Update Left Sidebar items
            document.querySelectorAll('.pw-nav-item').forEach((item) => {
                const href = item.getAttribute('href');
                if (!href) return;
                const itemPath = new URL(href, window.location.origin).pathname;

                if (
                    itemPath === path ||
                    (itemPath !== '/' && path.startsWith(itemPath)) ||
                    (itemPath.includes('courses') && path.startsWith('/learning/courses')) ||
                    (itemPath.includes('challenge') && path.startsWith('/challenge')) ||
                    (itemPath.includes('test_series') && path.startsWith('/test-series')) ||
                    (itemPath.includes('discover') && path.startsWith('/discover'))
                ) {
                    item.classList.add('active');
                } else {
                    item.classList.remove('active');
                }
            });

            // Update Mobile Bottom Navigation
            document.querySelectorAll('.mobile-bottom-item').forEach((item) => {
                const href = item.getAttribute('href');
                if (!href) return;
                const itemPath = new URL(href, window.location.origin).pathname;

                if (
                    itemPath === path ||
                    (itemPath !== '/' && path.startsWith(itemPath)) ||
                    (itemPath.includes('courses') && path.startsWith('/learning/courses')) ||
                    (itemPath.includes('challenge') && path.startsWith('/challenge')) ||
                    (itemPath.includes('test_series') && path.startsWith('/test-series'))
                ) {
                    item.classList.add('active');
                    item.style.transform = 'scale(0.94)';
                    setTimeout(() => { item.style.transform = ''; }, 140);
                } else {
                    item.classList.remove('active');
                }
            });
        },

        // Speculative Hover / Touch Prefetching
        async prefetchLink(link) {
            if (!this.isEligibleLink(link)) return;

            // Respect user data saver preference
            if (navigator.connection && navigator.connection.saveData) return;

            const url = new URL(link.href, window.location.origin);
            const cleanUrl = url.pathname + url.search;

            // If already cached and fresh, skip
            const cached = pageCache.get(cleanUrl);
            if (cached && (Date.now() - cached.timestamp < CACHE_TTL_MS)) return;

            try {
                const resp = await fetch(link.href, {
                    headers: {
                        'X-Requested-With': 'SkillRock-SPA',
                        'Accept': 'text/html'
                    },
                    priority: 'low'
                });
                if (resp.ok && !resp.redirected) {
                    const html = await resp.text();
                    const doc = new DOMParser().parseFromString(html, 'text/html');
                    const title = doc.querySelector('title') ? doc.querySelector('title').innerText : document.title;
                    this.addToCache(cleanUrl, html, title);
                }
            } catch (e) {
                // Ignore prefetch failures quietly
            }
        },

        async backgroundRevalidate(cleanUrl, targetUrl) {
            try {
                const resp = await fetch(targetUrl, {
                    headers: { 'X-Requested-With': 'SkillRock-SPA', 'Accept': 'text/html' }
                });
                if (resp.ok && !resp.redirected) {
                    const html = await resp.text();
                    const doc = new DOMParser().parseFromString(html, 'text/html');
                    const title = doc.querySelector('title') ? doc.querySelector('title').innerText : document.title;
                    this.addToCache(cleanUrl, html, title);
                }
            } catch (e) {}
        },

        addToCache(key, html, title) {
            if (pageCache.size >= MAX_CACHE_ENTRIES) {
                const firstKey = pageCache.keys().next().value;
                pageCache.delete(firstKey);
            }
            pageCache.set(key, { html, title, timestamp: Date.now() });
        },

        cacheCurrentPage() {
            const currentUrl = window.location.pathname + window.location.search;
            const liveContent = document.getElementById('livePageContent');
            if (liveContent) {
                // Store serialized shell-compatible representation
                const title = document.title;
                const fullDocHtml = document.documentElement.outerHTML;
                this.addToCache(currentUrl, fullDocHtml, title);
            }
        },

        handlePopState(e) {
            const targetUrl = window.location.href;
            this.navigate(targetUrl, { pushState: false });
        },

        handleFormSubmit(e) {
            // When user submits a form (e.g. login, enroll, rating, profile update),
            // invalidate page cache so fresh data is loaded on subsequent views.
            pageCache.clear();
        }
    };

    // Expose global router instance
    window.SkillRockRouter = Router;

    // Auto-initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => Router.init());
    } else {
        Router.init();
    }
})();
