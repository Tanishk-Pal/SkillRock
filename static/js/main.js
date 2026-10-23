// SkillSwap Campus - Main UI JavaScript

/* ==========================================================================
   PAGE SKELETON REVEAL & ACTION WHEEL LOADER ENGINE
   ========================================================================== */

(function initActionAndSkeletonEngine() {
    let safetyTimeout = null;

    const getActionElements = () => ({
        loader: document.getElementById("actionWheelLoader"),
        text: document.getElementById("actionWheelText"),
        skeleton: document.getElementById("youtubeSkeleton") || document.getElementById("pageSkeletonWrapper"),
        liveContent: document.getElementById("livePageContent")
    });

    // Immediately reveal page content when data/DOM is ready (no artificial delays)
    const revealPageContent = () => {
        const { skeleton, liveContent } = getActionElements();
        if (skeleton) {
            skeleton.classList.add("fade-out");
            skeleton.style.display = "none";
        }
        if (liveContent) {
            liveContent.classList.remove("is-loading");
            liveContent.style.display = "";
        }
    };

    // Show Small Centered Blue Wheel Loader for Functions / Actions (Icon only, no text words)
    window.showActionLoader = () => {
        const { loader, text } = getActionElements();
        if (loader) {
            if (text) {
                text.textContent = "";
                text.style.display = "none";
            }
            loader.style.display = "flex";
        }
        clearTimeout(safetyTimeout);
        safetyTimeout = setTimeout(() => {
            window.hideActionLoader();
        }, 9000);
    };

    // Hide Small Blue Action Wheel Loader
    window.hideActionLoader = () => {
        clearTimeout(safetyTimeout);
        const { loader } = getActionElements();
        if (loader) {
            loader.style.display = "none";
        }
    };

    // Compatibility aliases
    window.showRedirectLoader = window.showActionLoader;
    window.hideRedirectLoader = window.hideActionLoader;

    // Attach load / ready listeners
    if (document.readyState === "complete") {
        revealPageContent();
        window.hideActionLoader();
    } else {
        window.addEventListener("DOMContentLoaded", revealPageContent);
        window.addEventListener("load", () => {
            revealPageContent();
            window.hideActionLoader();
        });
    }

    window.addEventListener("pageshow", () => {
        window.hideActionLoader();
        revealPageContent();
    });

    // Automatically trigger Small Blue Wheel Loader on functional actions
    document.addEventListener("submit", (e) => {
        const form = e.target;
        if (!form) return;
        // Don't intercept live AI chat, study interests auto-save, live chat, or search inputs
        if (
            form.id === "chatForm" ||
            form.id === "aiChatForm" ||
            form.id === "interestsForm" ||
            form.id === "courseFilterForm" ||
            form.id === "liveDiscoverForm"
        ) return;

        window.showActionLoader();
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
