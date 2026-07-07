document.addEventListener("DOMContentLoaded", () => {
  // === 1. АНИМАЦИЯ ЛЕТАЮЩИХ БУКВ ЗАГОЛОВКА ===
  const titleEl = document.getElementById("title");
  if (titleEl) {
    const text = titleEl.innerText;
    titleEl.innerHTML = "";
    [...text].forEach((char) => {
      const span = document.createElement("span");
      span.innerText = char === " " ? "\u00A0" : char;
      if (char !== " ") {
        const randomX = (Math.random() - 0.5) * 800 + "px";
        const randomY = (Math.random() - 0.5) * 600 + "px";
        const randomRot = (Math.random() - 0.5) * 360 + "deg";
        span.style.setProperty("--tw-x", randomX);
        span.style.setProperty("--tw-y", randomY);
        span.style.setProperty("--tw-r", randomRot);
        span.style.animationDelay = Math.random() * 0.4 + "s";
      }
      titleEl.appendChild(span);
    });
  }

  // Проверяем, пришли ли данные из Django
  if (typeof projectsData === "undefined" || projectsData.length === 0) {
    console.warn("Массив projectsData пуст или не инициализирован.");
    return;
  }

  // === 2. ДИНАМИЧЕСКОЕ СОЗДАНИЕ ТУЛТИПА ДЛЯ НАЗВАНИЙ ===
  const tooltip = document.createElement("div");
  tooltip.style.position = "absolute";
  tooltip.style.padding = "8px 16px";
  tooltip.style.background = "rgba(15, 23, 42, 0.85)";
  tooltip.style.color = "#ffffff";
  tooltip.style.fontFamily = "sans-serif";
  tooltip.style.fontSize = "14px";
  tooltip.style.fontWeight = "bold";
  tooltip.style.borderRadius = "8px";
  tooltip.style.border = "1px solid rgba(255,255,255,0.1)";
  tooltip.style.pointerEvents = "none";
  tooltip.style.opacity = "0";
  tooltip.style.transition = "opacity 0.2s ease";
  tooltip.style.zIndex = "100";
  tooltip.style.boxShadow = "0 10px 25px rgba(0,0,0,0.5)";
  document.body.appendChild(tooltip);

  // === 3. ИНИЦИАЛИЗАЦИЯ THREE.JS ===
  const canvas = document.getElementById("webgl-canvas");
  if (!canvas) return;

  const scene = new THREE.Scene();

  // Считаем пропорции экрана
  const camera = new THREE.PerspectiveCamera(
    45,
    window.innerWidth / window.innerHeight,
    0.1,
    1000,
  );
  // Отодвигаем камеру чуть дальше (на 10 единиц), чтобы точно увидеть модели
  camera.position.set(0, 1, 10);

  const renderer = new THREE.WebGLRenderer({
    canvas: canvas,
    antialias: true,
    alpha: true,
  });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

  // Настройка мягкого освещения, чтобы модели не были черными
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
  scene.add(ambientLight);

  const dirLight1 = new THREE.DirectionalLight(0xffffff, 1.0);
  dirLight1.position.set(5, 10, 7);
  scene.add(dirLight1);

  const dirLight2 = new THREE.DirectionalLight(0x79aec8, 0.5); // Легкая синеватая подсветка сзади
  dirLight2.position.set(-5, -5, -5);
  scene.add(dirLight2);

  const clickableModels = [];
  const loader = new THREE.GLTFLoader();

  // Радиус карусели, вокруг которой расставим деревья/объекты
  const radius = 4.5;

  projectsData.forEach((project, index) => {
    loader.load(
      project.modelUrl,
      (gltf) => {
        const model = gltf.scene;

        // Вычисляем шаг угла для каждого проекта
        const angle = (index / projectsData.length) * Math.PI * 2;
        model.position.x = Math.cos(angle) * radius;
        model.position.z = Math.sin(angle) * radius;
        model.position.y = -1.0; // Спускаем чуть ниже центра

        // АВТОМАТИЧЕСКОЕВЫРАВНИВАНИЕ МАСШТАБА (Защита от слишком больших/маленьких файлов)
        const box = new THREE.Box3().setFromObject(model);
        const size = box.getSize(new THREE.Vector3()).length();
        const scaleFactor = 2.2 / size; // Принудительно приводим модель к адекватному размеру
        model.scale.set(scaleFactor, scaleFactor, scaleFactor);

        // Сохраняем метаданные в userData
        model.userData = {
          url: project.url,
          title: project.title,
          baseScale: scaleFactor,
        };

        scene.add(model);
        clickableModels.push(model);
        console.log(`Успешно загружена модель: ${project.title}`);
      },
      undefined,
      (error) => {
        console.error(`Ошибка при загрузке модели ${project.title}:`, error);
      },
    );
  });

  // === 4. ОБРАБОТКА МЫШИ (RAYCASTING) ===
  const raycaster = new THREE.Raycaster();
  const mouse = new THREE.Vector2();
  let hoveredObject = null;

  window.addEventListener("mousemove", (event) => {
    // Координаты мыши для Three.js
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

    // Позиционирование всплывающего тултипа рядом с курсором
    tooltip.style.left = event.clientX + 20 + "px";
    tooltip.style.top = event.clientY + 10 + "px";

    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObjects(clickableModels, true);

    if (intersects.length > 0) {
      // Ищем самый верхний узел модели в иерархии сцены
      let rootModel = intersects[0].object;
      while (rootModel.parent && rootModel.parent !== scene) {
        rootModel = rootModel.parent;
      }

      if (hoveredObject !== rootModel) {
        // Сбрасываем старый объект, если он был
        if (hoveredObject) {
          gsap.to(hoveredObject.scale, {
            x: hoveredObject.userData.baseScale,
            y: hoveredObject.userData.baseScale,
            z: hoveredObject.userData.baseScale,
            duration: 0.2,
          });
        }

        hoveredObject = rootModel;

        // Анимация увеличения при наведении через GSAP
        const targetScale = hoveredObject.userData.baseScale * 1.25;
        gsap.to(hoveredObject.scale, {
          x: targetScale,
          y: targetScale,
          z: targetScale,
          duration: 0.25,
        });

        // Показываем текст проекта
        tooltip.innerText = hoveredObject.userData.title;
        tooltip.style.opacity = "1";
        document.body.style.cursor = "pointer";
      }
    } else {
      // Если мышь ушла с модели
      if (hoveredObject) {
        gsap.to(hoveredObject.scale, {
          x: hoveredObject.userData.baseScale,
          y: hoveredObject.userData.baseScale,
          z: hoveredObject.userData.baseScale,
          duration: 0.2,
        });
        hoveredObject = null;
      }
      tooltip.style.opacity = "0";
      document.body.style.cursor = "default";
    }
  });

  // Переход по клику
  window.addEventListener("click", () => {
    if (hoveredObject && hoveredObject.userData.url) {
      window.location.href = hoveredObject.userData.url;
    }
  });

  // === 5. РЕНДЕР И ЛЕВИТАЦИЯ ===
  const clock = new THREE.Clock();

  const animate = () => {
    const elapsedTime = clock.getElapsedTime();

    // Заставляем модели медленно крутиться и плавно покачиваться вверх-вниз
    clickableModels.forEach((model, index) => {
      model.rotation.y = elapsedTime * 0.25 + index;
      model.position.y = -0.6 + Math.sin(elapsedTime * 1.5 + index) * 0.12;
    });

    renderer.render(scene, camera);
    window.requestAnimationFrame(animate);
  };
  animate();

  // Поддержка изменения размеров окна
  window.addEventListener("resize", () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });
});
