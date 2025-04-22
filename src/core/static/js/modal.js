// this external function is used to wait the DOM to be loaded before adding the event listeners
$(function() {
    var modal = document.querySelector("#modal");
    var triggers = $(".trigger-modal");

    function toggleModal() {
        modal.classList.toggle("show-modal");
    }

    function windowOnClick(event) {
        if (event.target === modal) {
            toggleModal();
        }
    }

    triggers.click(toggleModal);
    window.addEventListener("click", windowOnClick);
});