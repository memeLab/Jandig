// Paging for the HTMX repository lists in the selection modals.
// Each list carries its current page and page count as data attributes,
// so the buttons stay right when a search changes how many pages there are.

function next_page(element_type, increment) {
    let list = document.getElementById("repo-" + element_type);
    return Math.max(1, Number(list.dataset.page) + increment);
}

function update_page_buttons() {
    document.querySelectorAll(".repository-list[data-num-pages]").forEach(function (list) {
        let element_type = list.id.replace("repo-", "");
        let page = Number(list.dataset.page);
        let previous_button = document.getElementById("previous-button-" + element_type);
        let next_button = document.getElementById("next-button-" + element_type);
        if (previous_button) {
            previous_button.disabled = page <= 1;
        }
        if (next_button) {
            next_button.disabled = page >= Number(list.dataset.numPages);
        }
    });
}

document.addEventListener("DOMContentLoaded", update_page_buttons);
document.addEventListener("htmx:afterSwap", update_page_buttons);
