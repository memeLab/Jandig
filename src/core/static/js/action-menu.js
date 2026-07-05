function closeAllMenus() {
    document.querySelectorAll(".action-menu-dropdown.open").forEach(function (d) {
        d.classList.remove("open");
        d.parentElement.classList.remove("menu-active");
    });
}

function createOverlay() {
    const overlay = document.createElement("div");
    overlay.className = "action-modal-overlay";
    overlay.addEventListener("click", function (e) {
        if (e.target === overlay) {
            destroyOverlay(overlay);
        }
    });
    document.body.appendChild(overlay);
    // Force reflow then show
    overlay.offsetHeight;
    overlay.classList.add("visible");
    return overlay;
}

function destroyOverlay(overlay) {
    overlay.classList.remove("visible");
    setTimeout(function () {
        overlay.remove();
    }, 200);
}

function showInfoModal(reason) {
    const overlay = createOverlay();
    const box = document.createElement("div");
    box.className = "action-modal-box";
    box.innerHTML =
        '<p>' + escapeHtml(reason) + '</p>' +
        '<div class="action-modal-buttons">' +
        '<button class="action-modal-btn action-modal-btn-ok">OK</button>' +
        '</div>';
    overlay.appendChild(box);
    box.querySelector(".action-modal-btn-ok").addEventListener("click", function () {
        destroyOverlay(overlay);
    });
}

function showConfirmModal(message, href) {
    const overlay = createOverlay();
    const box = document.createElement("div");
    box.className = "action-modal-box";
    box.innerHTML =
        '<p>' + escapeHtml(message) + '</p>' +
        '<div class="action-modal-buttons">' +
        '<button class="action-modal-btn action-modal-btn-cancel">Cancel</button>' +
        '<button class="action-modal-btn action-modal-btn-confirm">Delete</button>' +
        '</div>';
    overlay.appendChild(box);
    box.querySelector(".action-modal-btn-cancel").addEventListener("click", function () {
        destroyOverlay(overlay);
    });
    box.querySelector(".action-modal-btn-confirm").addEventListener("click", function () {
        globalThis.location.href = href;
    });
}

function escapeHtml(str) {
    const div = document.createElement("div");
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
}

document.addEventListener("DOMContentLoaded", function () {
    // Use capturing phase so this fires BEFORE htmx/jQuery handlers on parent elements
    document.addEventListener("click", function (e) {
        const menuContainer = e.target.closest(".action-menu-container");

        // Any click inside the menu container: stop propagation to prevent
        // parent handlers (HTMX modal trigger, jQuery toggleModal) from firing
        if (menuContainer) {
            e.stopPropagation();

            const trigger = e.target.closest(".action-menu-trigger");
            if (trigger) {
                e.preventDefault();
                const dropdown = trigger.nextElementSibling;
                const container = trigger.parentElement;
                // Close any other open menus first
                document.querySelectorAll(".action-menu-dropdown.open").forEach(function (d) {
                    if (d !== dropdown) {
                        d.classList.remove("open");
                        d.parentElement.classList.remove("menu-active");
                    }
                });
                dropdown.classList.toggle("open");
                container.classList.toggle("menu-active");
                return;
            }

            // Handle disabled menu item click
            const disabledItem = e.target.closest(".action-menu-item[data-disabled]");
            if (disabledItem) {
                e.preventDefault();
                closeAllMenus();
                showInfoModal(disabledItem.dataset.reason);
                return;
            }

            // Handle delete confirmation
            const deleteItem = e.target.closest(".action-menu-item.action-menu-delete:not(.disabled)");
            if (deleteItem) {
                e.preventDefault();
                closeAllMenus();
                const message = deleteItem.dataset.confirm;
                const href = deleteItem.getAttribute("href");
                showConfirmModal(message, href);
                return;
            }

            // For enabled Edit/Preview links: allow normal navigation (no preventDefault)
            return;
        }

        // Click outside any menu: close all menus
        closeAllMenus();
    }, true);  // true = capturing phase
});
