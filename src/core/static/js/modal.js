// this external function is used to wait the DOM to be loaded before adding the event listeners
$(function() {
    const modal = document.querySelector("#modal");
    const triggers = $(".trigger-modal");

    function toggleModal() {
        const toggle_result = modal.classList.toggle("show-modal");
        // Remove the content when the modal is closed
        if (!toggle_result) {
            modal.innerHTML = "";
        }
    }

    function windowOnClick(event) {
        if (event.target === modal) {
            toggleModal();
        }
    }

    triggers.click(toggleModal);
    globalThis.addEventListener("click", windowOnClick);
});