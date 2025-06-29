// this external function is used to wait the DOM to be loaded before adding the event listeners
$(function() {
    var modal = document.querySelector("#modal");
    var triggers = $(".trigger-modal");

    function toggleModal() {
        var toggle_result = modal.classList.toggle("show-modal");
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
    window.addEventListener("click", windowOnClick);
});