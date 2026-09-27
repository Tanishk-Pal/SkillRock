// SkillSwap Campus - Main UI JavaScript

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
