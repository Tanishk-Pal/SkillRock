// SkillSwap Campus - Main UI JavaScript

/* ==========================================================================
   YOUTUBE-STYLE SKELETON REVEAL & NAVIGATION WHEEL LOADER ENGINE
   ========================================================================== */

(function initPageTransitionEngine() {
    let progressTimer = null;
    let safetyTimeout = null;

    const getElements = () => ({
        skeleton: document.getElementById("youtubeSkeleton"),
        liveContent: document.getElementById("livePageContent"),
        progressBar: document.getElementById("pageProgressBar"),
        redirectLoader: document.getElementById("pageRedirectLoader"),
        loaderText: document.getElementById("wheelLoaderText")
    });

    // Gracefully reveal live page content and fade out YouTube skeleton
    const revealPageContent = () => {
        const { skeleton, liveContent } = getElements();
        if (skeleton && liveContent) {
            // Smooth 150ms shimmer preview so user sees reassuring feedback
            setTimeout(() => {
                skeleton.classList.add("fade-out");
                liveContent.classList.remove("is-loading");
                setTimeout(() => {
                    skeleton.style.display = "none";
                }, 260);
            }, 150);
        } else if (liveContent) {
            liveContent.classList.remove("is-loading");
        }
    };

    // Animate top YouTube glowing progress bar
    const startProgressBar = () => {
        const { progressBar } = getElements();
        if (!progressBar) return;
        clearInterval(progressTimer);
        progressBar.classList.add("active");
        progressBar.style.width = "0%";

        let currentWidth = 12;
        progressBar.style.width = currentWidth + "%";

        progressTimer = setInterval(() => {
            if (currentWidth < 65) {
                currentWidth += Math.random() * 12 + 6;
            } else if (currentWidth < 88) {
                currentWidth += Math.random() * 3 + 1;
            }
            if (currentWidth > 90) currentWidth = 90;
            progressBar.style.width = currentWidth + "%";
        }, 160);
    };

    // Complete top progress bar
    const completeProgressBar = () => {
        const { progressBar } = getElements();
        if (!progressBar) return;
        clearInterval(progressTimer);
        progressBar.style.width = "100%";
        setTimeout(() => {
            progressBar.classList.remove("active");
            setTimeout(() => {
                progressBar.style.width = "0%";
            }, 200);
        }, 220);
    };

    // Show Small Diameter Wheel Loader floating pill & top progress bar
    window.showRedirectLoader = (message = "Loading...") => {
        const { redirectLoader, loaderText, liveContent } = getElements();
        if (redirectLoader) {
            if (loaderText) loaderText.textContent = message;
            redirectLoader.classList.add("active");
        }
        startProgressBar();
        if (liveContent) {
            liveContent.classList.add("is-redirecting");
        }

        // Safety reset if navigation takes too long or cancels
        clearTimeout(safetyTimeout);
        safetyTimeout = setTimeout(() => {
            window.hideRedirectLoader();
        }, 9000);
    };

    // Hide loader and restore live content state
    window.hideRedirectLoader = () => {
        clearTimeout(safetyTimeout);
        completeProgressBar();
        const { redirectLoader, liveContent } = getElements();
        if (redirectLoader) {
            redirectLoader.classList.remove("active");
        }
        if (liveContent) {
            liveContent.classList.remove("is-redirecting");
        }
    };

    // Attach load / ready listeners
    if (document.readyState === "complete") {
        revealPageContent();
        window.hideRedirectLoader();
    } else {
        window.addEventListener("DOMContentLoaded", revealPageContent);
        window.addEventListener("load", () => {
            revealPageContent();
            window.hideRedirectLoader();
        });
    }

    // Reset when navigating using browser history (Back / Forward cache)
    window.addEventListener("pageshow", () => {
        window.hideRedirectLoader();
        revealPageContent();
    });

    // Intercept clicks on links for instant redirect feedback
    document.addEventListener("click", (e) => {
        const link = e.target.closest("a");
        if (!link) return;

        const href = link.getAttribute("href");
        const target = link.getAttribute("target");
        const isDownload = link.hasAttribute("download");

        // Skip non-navigating links or new tabs
        if (!href || href.startsWith("#") || href.startsWith("javascript:") || href.startsWith("mailto:") || href.startsWith("tel:") || isDownload) {
            return;
        }
        if (target === "_blank" || e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) {
            return;
        }
        // Skip modal open/close buttons
        if (link.classList.contains("modal-close") || link.hasAttribute("data-modal-close") ||
            link.classList.contains("btn-request-swap") || link.classList.contains("btn-schedule-session") ||
            link.classList.contains("btn-open-rate-modal") || link.classList.contains("btn-open-link-modal")) {
            return;
        }

        // Contextual message
        let msg = "Loading...";
        const lowerHref = href.toLowerCase();
        const linkText = (link.textContent || "").trim();

        if (lowerHref.includes("chat")) {
            msg = "Opening Messages...";
        } else if (lowerHref.includes("discover")) {
            msg = "Finding Students...";
        } else if (lowerHref.includes("dashboard")) {
            msg = "Opening Dashboard...";
        } else if (lowerHref.includes("sessions")) {
            msg = "Loading Sessions...";
        } else if (lowerHref.includes("requests") || lowerHref.includes("swap")) {
            msg = "Loading Requests...";
        } else if (lowerHref.includes("profile")) {
            msg = "Opening Profile...";
        } else if (lowerHref.includes("google")) {
            msg = "Connecting to Google...";
        } else if (lowerHref.includes("assistant") || lowerHref.includes("ai")) {
            msg = "Launching SkillBot...";
        } else if (lowerHref.includes("login") || lowerHref.includes("logout")) {
            msg = "Please wait...";
        } else if (linkText.length > 0 && linkText.length < 24) {
            msg = `Loading ${linkText}...`;
        }

        window.showRedirectLoader(msg);
    });

    // Form submission listener
    document.addEventListener("submit", (e) => {
        const form = e.target;
        // Don't intercept chat messages (already live dynamic)
        if (form.id === "chatForm") return;

        let msg = "Submitting...";
        const action = (form.getAttribute("action") || "").toLowerCase();
        if (action.includes("login")) {
            msg = "Signing in...";
        } else if (action.includes("register")) {
            msg = "Creating account...";
        } else if (action.includes("discover")) {
            msg = "Searching matches...";
        } else if (action.includes("profile")) {
            msg = "Saving profile...";
        } else if (action.includes("request")) {
            msg = "Sending request...";
        } else if (action.includes("rate")) {
            msg = "Submitting rating...";
        }

        window.showRedirectLoader(msg);
    });
})();

document.addEventListener("DOMContentLoaded", () => {
    // 1. Modal Triggers
    const modalOverlays = document.querySelectorAll(".modal-overlay");
    const closeButtons = document.querySelectorAll(".modal-close, [data-modal-close]");

    closeButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            modalOverlays.forEach(m => m.classList.remove("active"));
        });
    });

    modalOverlays.forEach(overlay => {
        overlay.addEventListener("click", (e) => {
            if (e.target === overlay) {
                overlay.classList.remove("active");
            }
        });
    });

    // 2. Open Request Swap Modal with dynamic pre-fill
    const requestButtons = document.querySelectorAll(".btn-request-swap");
    const swapModal = document.getElementById("requestSwapModal");

    requestButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const receiverId = btn.getAttribute("data-user-id");
            const receiverName = btn.getAttribute("data-user-name");
            const partnerTeaches = JSON.parse(btn.getAttribute("data-teaches") || "[]");

            if (swapModal) {
                document.getElementById("modalReceiverId").value = receiverId;
                document.getElementById("modalReceiverName").textContent = receiverName;

                // Populate what the partner teaches (which current user wants to learn)
                const learnSelect = document.getElementById("modalLearnSkill");
                if (learnSelect) {
                    learnSelect.innerHTML = '<option value="">-- Choose what to learn --</option>';
                    partnerTeaches.forEach(skill => {
                        const opt = document.createElement("option");
                        opt.value = skill.id;
                        opt.textContent = skill.name;
                        learnSelect.appendChild(opt);
                    });
                }

                swapModal.classList.add("active");
            }
        });
    });

    // 3. Open Schedule Session Modal
    const scheduleButtons = document.querySelectorAll(".btn-schedule-session");
    const sessionModal = document.getElementById("scheduleSessionModal");

    scheduleButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const connectionId = btn.getAttribute("data-connection-id");
            const partnerId = btn.getAttribute("data-partner-id");
            const partnerName = btn.getAttribute("data-partner-name");
            const partnerTeaches = JSON.parse(btn.getAttribute("data-partner-teaches") || "[]");
            const myTeaches = JSON.parse(btn.getAttribute("data-my-teaches") || "[]");

            if (sessionModal) {
                document.getElementById("sessionConnectionId").value = connectionId;
                document.getElementById("sessionPartnerId").value = partnerId;
                document.getElementById("sessionPartnerName").textContent = partnerName;

                // Populate skill choices
                const skillSelect = document.getElementById("sessionSkillSelect");
                const roleSelect = document.getElementById("sessionRoleSelect");

                const updateSkillDropdown = () => {
                    const role = roleSelect.value;
                    const skillsList = role === "teach" ? myTeaches : partnerTeaches;
                    skillSelect.innerHTML = '<option value="">-- Select Skill --</option>';
                    skillsList.forEach(s => {
                        const opt = document.createElement("option");
                        opt.value = s.id;
                        opt.textContent = s.name;
                        skillSelect.appendChild(opt);
                    });
                };

                if (roleSelect && skillSelect) {
                    roleSelect.onchange = updateSkillDropdown;
                    updateSkillDropdown();
                }

                // Default date to tomorrow
                const tomorrow = new Date();
                tomorrow.setDate(tomorrow.getDate() + 1);
                const dateInput = document.getElementById("sessionDateInput");
                if (dateInput) {
                    dateInput.value = tomorrow.toISOString().split("T")[0];
                }

                sessionModal.classList.add("active");
            }
        });
    });

    // 4. Open Rating Modal
    const rateButtons = document.querySelectorAll(".btn-open-rate-modal");
    const rateModal = document.getElementById("rateSessionModal");

    rateButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const sessionId = btn.getAttribute("data-session-id");
            const partnerName = btn.getAttribute("data-partner-name");
            const skillName = btn.getAttribute("data-skill-name");

            if (rateModal) {
                const form = document.getElementById("rateSessionForm");
                form.action = `/sessions/${sessionId}/rate`;
                document.getElementById("ratePartnerName").textContent = partnerName;
                document.getElementById("rateSkillName").textContent = skillName;
                rateModal.classList.add("active");
            }
        });
    });

    // 5. Star Rating Selector in Rating Modal
    const starInputs = document.querySelectorAll(".star-input-group input[type='radio']");
    const starLabels = document.querySelectorAll(".star-input-group label");

    starInputs.forEach(input => {
        input.addEventListener("change", (e) => {
            const val = parseInt(e.target.value);
            starLabels.forEach((label, idx) => {
                if (idx < val) {
                    label.style.color = "#f59e0b";
                } else {
                    label.style.color = "#475569";
                }
            });
        });
    });

    // 6. Flash Alert Dismissal
    const alertDismissButtons = document.querySelectorAll(".alert-dismiss");
    alertDismissButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const alert = btn.closest(".alert");
            if (alert) {
                alert.style.opacity = "0";
                setTimeout(() => alert.remove(), 200);
            }
        });
    });

    // 7. Mobile Menu Toggle
    const mobileMenuBtn = document.getElementById("mobileMenuBtn");
    const navLinks = document.getElementById("navLinks");
    if (mobileMenuBtn && navLinks) {
        mobileMenuBtn.addEventListener("click", () => {
            navLinks.classList.toggle("mobile-open");
        });
    }

    // 8. Open Set Meeting Link Modal
    const setLinkButtons = document.querySelectorAll(".btn-open-link-modal");
    const setLinkModal = document.getElementById("setLinkModal");

    setLinkButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const sessionId = btn.getAttribute("data-session-id");
            const currentLink = btn.getAttribute("data-current-link") || "";
            if (setLinkModal) {
                const form = document.getElementById("setLinkForm");
                const input = document.getElementById("modalLinkInput");
                if (form) form.action = `/sessions/${sessionId}/set-link`;
                if (input) input.value = currentLink;
                setLinkModal.classList.add("active");
            }
        });
    });
});
