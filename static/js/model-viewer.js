document.addEventListener("DOMContentLoaded", () => {
  function init3DModels() {
    // Находим все карточки, которые еще не были инициализированы
    const containers = document.querySelectorAll(
      ".js-3d-model-container:not(.is-initialized)",
    );

    containers.forEach((container) => {
      const src = container.getAttribute("data-src");
      const type = container.getAttribute("data-type");

      if (!src) return;
      container.classList.add("is-initialized");

      // 1. Очищаем внутренности контейнера (на случай, если там были заглушки)
      container.innerHTML = "";

      // 2. Если это локальный файл (.glb / .gltf)
      if (type === "file") {
        const viewer = document.createElement("model-viewer");
        viewer.setAttribute("src", src);
        viewer.setAttribute("camera-controls", "");
        viewer.setAttribute("auto-rotate", "");
        viewer.setAttribute("shadow-intensity", "1");
        viewer.setAttribute("touch-action", "pan-y");

        // Растягиваем плеер внутри сетки админки
        viewer.style.width = "100%";
        viewer.style.height = "100%";
        viewer.style.display = "block";

        container.appendChild(viewer);
      }
      // 3. Если это внешняя ссылка на Sketchfab iframe
      else if (type === "iframe") {
        const iframe = document.createElement("iframe");
        iframe.setAttribute("src", src);
        iframe.setAttribute(
          "allow",
          "autoplay; fullscreen; xr-spatial-tracking",
        );
        iframe.style.width = "100%";
        iframe.style.height = "100%";
        iframe.style.border = "none";

        // Защитный слой, чтобы скролл мыши по карточкам не "застревал" внутри iframe
        const overlay = document.createElement("div");
        overlay.style.position = "absolute";
        overlay.style.top = "0";
        overlay.style.left = "0";
        overlay.style.width = "100%";
        overlay.style.height = "100%";
        overlay.style.background = "transparent";
        overlay.style.zIndex = "5";

        container.appendChild(iframe);
        container.appendChild(overlay);
      }
    });
  }

  // Запуск при первой загрузке
  init3DModels();

  // Следим за динамическими изменениями в админке Django (например, при пагинации или поиске)
  const targetNode =
    document.getElementById("changelist-form") || document.body;
  const observer = new MutationObserver(init3DModels);
  observer.observe(targetNode, { childList: true, subtree: true });
});
