Trix.config.blockAttributes.heading2 = {
    tagName: "h2",
    breakOnReturn: true,
    group: false,
    terminal: true
}

Trix.config.blockAttributes.heading3 = {
    tagName: "h3",
    breakOnReturn: true,
    group: false,
    terminal: true
}

Trix.config.blockAttributes.heading4 = {
    tagName: "h4",
    breakOnReturn: true,
    group: false,
    terminal: true
}

Trix.config.blockAttributes.p = {
    tagName: "p",
    breakOnReturn: true,
    terminal: true
}

Trix.config.textAttributes.underlined = {
    tagName: "u",
    inheritable: true,
    parser(element) {
        const style = window.getComputedStyle(element);
        return style.textDecoration === "underline";
    },
}

document.addEventListener("trix-before-initialize", () => {
    Trix.config.toolbar.getDefaultHTML = () => document.getElementById("trix-toolbar").innerHTML
})


document.addEventListener("trix-initialize", function (event) {
  function insertToolbarButton(event) {
    const { toolbar, attachment } = event;

    // Add custom link button
    const linkButtonHTML = `
      <button 
        type="button" 
        title="Link" 
        class="trix-button trix-button--link" 
        data-attachment-id="${attachment.id}"
      >
        Link
      </button>
    `;

    toolbar
      .querySelector(".trix-button-group")
      .insertAdjacentHTML("beforeend", linkButtonHTML);

    // Add event listener for the custom link button
    toolbar
      .querySelector(`.trix-button--link[data-attachment-id="${attachment.id}"]`)
      .addEventListener("click", function () {
        handleLinkAttachment(attachment);
      });
  }

  function handleLinkAttachment(attachment) {
    const url = prompt("Enter the URL: (blank to remove)", attachment.getAttributes().href || "media/post_images/");

    // Explicitly set href to null if the URL is empty or only whitespace
    attachment.setAttributes({ href: url.trim() === "" ? null : url.trim() });

    const editor = document.querySelector("trix-editor").editor;
    editor.insertAttachment(attachment); // Reinsert attachment to update it
  }

  event.target.addEventListener("trix-attachment-before-toolbar", insertToolbarButton, { once: false });
});