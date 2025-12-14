(() => {
  const galleryLinks = Array.from(
    document.querySelectorAll(".gallery .gallery-item[href]")
  );

  if (galleryLinks.length === 0) return;

  let activeIndex = 0;
  let overlay = null;
  let dialog = null;
  let figure = null;
  let caption = null;
  let closeButton = null;
  let prevButton = null;
  let nextButton = null;
  let restoreFocusTo = null;

  function buildOverlay() {
    overlay = document.createElement("div");
    overlay.className = "lightbox-overlay";
    overlay.hidden = true;

    dialog = document.createElement("div");
    dialog.className = "lightbox-dialog";
    dialog.setAttribute("role", "dialog");
    dialog.setAttribute("aria-modal", "true");
    dialog.setAttribute("aria-label", "Foto bekijken");

    closeButton = document.createElement("button");
    closeButton.type = "button";
    closeButton.className = "lightbox-close";
    closeButton.setAttribute("aria-label", "Sluiten");
    closeButton.innerHTML = "&times;";

    prevButton = document.createElement("button");
    prevButton.type = "button";
    prevButton.className = "lightbox-prev";
    prevButton.setAttribute("aria-label", "Vorige foto");
    prevButton.innerHTML = "&#x2039;";

    nextButton = document.createElement("button");
    nextButton.type = "button";
    nextButton.className = "lightbox-next";
    nextButton.setAttribute("aria-label", "Volgende foto");
    nextButton.innerHTML = "&#x203A;";

    figure = document.createElement("figure");
    figure.className = "lightbox-figure";

    caption = document.createElement("figcaption");
    caption.className = "lightbox-caption";

    figure.appendChild(caption);
    dialog.appendChild(closeButton);
    dialog.appendChild(prevButton);
    dialog.appendChild(nextButton);
    dialog.appendChild(figure);
    overlay.appendChild(dialog);
    document.body.appendChild(overlay);

    overlay.addEventListener("click", (event) => {
      const target = event.target instanceof Element ? event.target : null;
      if (!target) return;

      if (target.closest(".lightbox-media")) return;
      if (target.closest(".lightbox-prev, .lightbox-next")) return;
      if (target.closest(".lightbox-close")) return;

      closeLightbox();
    });

    closeButton.addEventListener("click", closeLightbox);
    prevButton.addEventListener("click", () => showByOffset(-1));
    nextButton.addEventListener("click", () => showByOffset(1));
  }

  function getItem(index) {
    const link = galleryLinks[index];
    if (!link) return null;

    const picture = link.querySelector("picture");
    const img = link.querySelector("img");
    const alt = img?.getAttribute("alt") || "";

    return { link, picture, alt };
  }

  function setOverlayMedia(item) {
    figure.querySelector("picture")?.remove();

    const pictureClone = item.picture ? item.picture.cloneNode(true) : null;
    if (!pictureClone) return;

    pictureClone.classList.add("lightbox-media");

    const img = pictureClone.querySelector("img");
    if (img) {
      img.loading = "eager";
      img.decoding = "async";
      img.sizes = "100vw";
    }

    figure.insertBefore(pictureClone, caption);
    caption.textContent = item.alt || "";
  }

  function showAt(index) {
    const normalized = ((index % galleryLinks.length) + galleryLinks.length) % galleryLinks.length;
    const item = getItem(normalized);
    if (!item) return;

    activeIndex = normalized;
    setOverlayMedia(item);
  }

  function showByOffset(offset) {
    showAt(activeIndex + offset);
  }

  function onKeyDown(event) {
    if (overlay?.hidden) return;

    if (event.key === "Escape") {
      event.preventDefault();
      closeLightbox();
      return;
    }

    if (event.key === "ArrowLeft") {
      event.preventDefault();
      showByOffset(-1);
      return;
    }

    if (event.key === "ArrowRight") {
      event.preventDefault();
      showByOffset(1);
    }
  }

  function openLightbox(index) {
    if (!overlay) buildOverlay();

    restoreFocusTo = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    document.body.classList.add("lightbox-open");
    overlay.hidden = false;

    showAt(index);

    document.addEventListener("keydown", onKeyDown);
    closeButton?.focus();
  }

  function closeLightbox() {
    if (!overlay) return;

    overlay.hidden = true;
    document.body.classList.remove("lightbox-open");
    document.removeEventListener("keydown", onKeyDown);

    if (restoreFocusTo) restoreFocusTo.focus();
    restoreFocusTo = null;
  }

  galleryLinks.forEach((link, index) => {
    link.addEventListener("click", (event) => {
      if (
        event.defaultPrevented ||
        event.button !== 0 ||
        event.metaKey ||
        event.ctrlKey ||
        event.shiftKey ||
        event.altKey
      ) {
        return;
      }

      event.preventDefault();
      openLightbox(index);
    });
  });
})();
