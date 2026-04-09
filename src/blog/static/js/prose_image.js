import { Node, updateAttrsDialog } from "django-prose-editor/editor";

const imageDialogImpl = (editor, attrs, options) => {
  const properties = {
    src: {
      type: "string",
      title: gettext("Source"),
      required: true,
    },
    alt: {
      type: "string",
      title: gettext("Alt Text"),
      required: true,
    },
    title: {
      type: "string",
      title: gettext("Title"),
    },
    width: {
      type: "number",
      title: gettext("Width"),
    },
    height: {
      type: "number",
      title: gettext("Height"),
    },
  };

  return updateAttrsDialog(properties, {
    title: gettext("Add or edit image"),
  })(editor, attrs);
};

const ImageDialog = async (editor, attrs, options) => {
  attrs = attrs || {};
  attrs = await imageDialogImpl(editor, attrs, options);
  if (attrs) {
    return attrs;
  }
};

export const AddImage = Node.create({
  name: "image",
  content: "inline*",
  group: "block",
  isolating: true,

  addAttributes() {
    return {
      src: {
        default: null,
      },
      alt: {
        default: null,
      },
      title: {
        default: null,
      },
      width: {
        default: null,
      },
      height: {
        default: null,
      },
    };
  },
  parseHTML() {
    return [
      {
        tag: "img[src]",
        getAttrs: (dom) => ({
          src: dom.getAttribute("src"),
          alt: dom.getAttribute("alt"),
          title: dom.getAttribute("title"),
          width: dom.getAttribute("width"),
          height: dom.getAttribute("height"),
        }),
      },
    ];
  },
  renderHTML({ HTMLAttributes }) {
    return ["img", HTMLAttributes];
  },
  addMenuItems({ editor, buttons, menu }) {
    menu.defineItem({
      name: "addImage",
      groups: "link",
      command: (editor) => editor.chain().addImage().focus().run(),
      button: buttons.material("image", "Add image"),
      enabled: (editor) => true,
      active: (editor) => editor.isActive("image"),
    });
  },
  addCommands() {
    return {
      ...this.parent?.(),
      addImage:
        () =>
        ({ editor }) => {
          const attrs = editor.getAttributes(this.name);

          ImageDialog(editor, attrs, this.options).then((attrs) => {
            if (attrs) {
              editor
                .chain()
                .focus()
                .insertContent({
                  type: "image",
                  attrs: attrs,
                })
                .run();
            }
          });
        },
    };
  },
});