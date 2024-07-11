/**
 * Make main header sections in the sidebar togglable, for a full navigation tree.
 *
 * This function is directly adapted from Godot's own custom RDT code:
 * https://github.com/godotengine/godot-docs/blob/master/_static/css/custom.css
 */
function handleSidebarHeaderToggle() {
  let isCurrent = false;
  let menuHeaders = document.querySelectorAll(
    ".wy-menu-vertical .caption[role=heading]"
  );

  menuHeaders.forEach((header) => {
    let connectedMenu = header.nextElementSibling;

    // Enable toggling.
    header.addEventListener(
      "click",
      () => {
        if (connectedMenu.classList.contains("active")) {
          connectedMenu.classList.remove("active");
          header.classList.remove("active");
        } else {
          connectedMenu.classList.add("active");
          header.classList.add("active");
        }

        // Hide other sections.
        menuHeaders.forEach((ot) => {
          if (ot !== header && ot.classList.contains("active")) {
            ot.nextElementSibling.classList.remove("active");
            ot.classList.remove("active");
          }
        });

        registerOnScrollEvent(mediaQuery);
      },
      true,
    );

    // Set the default state, expand our current section.
    if (connectedMenu.classList.contains("current")) {
      connectedMenu.classList.add("active");
      header.classList.add("active");

      isCurrent = true;
    }
  });

  // Unfold the first (general information) section on the home page.
  if (!isCurrent && menuHeaders.length > 0) {
    menuHeaders[0].classList.add("active");
    menuHeaders[0].nextElementSibling.classList.add("active");

    registerOnScrollEvent(mediaQuery);
  }
}


/**
 * Load all custom code only once the DOM document has fully loaded.
 *
 * Notice that jQuery is already available in this file.
 */
$(document).ready(() => {
  handleSidebarHeaderToggle()
});
