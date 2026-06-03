/* ══════════════════════════════════════════════
   3D-кубик Рубика (как на resend.com) — БЕЛЫЙ
   Рендерится как фон секции hero, текст — поверх.
══════════════════════════════════════════════ */
import * as THREE from "three";
import { RectAreaLightUniformsLib } from "three/addons/lights/RectAreaLightUniformsLib.js";
import { RoundedBoxGeometry } from "three/addons/geometries/RoundedBoxGeometry.js";

const container = document.querySelector("[data-cube]");
if (container) {
  let renderer, scene, camera, canvas;
  const dummy = new THREE.Object3D();
  const rows = [];
  const rubiksCube = new THREE.Group();
  let autoRotate = true;     // авто-вращение, когда кубик не держат
  let velX = 0, velY = 0;    // инерция после перетаскивания

  const sizes = () => {
    const w = container.clientWidth, h = container.clientHeight;
    return { w, h, aspect: w / h, pr: Math.min(window.devicePixelRatio, 2) };
  };

  function setUpScene() {
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    const s = sizes();
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.CineonToneMapping;
    renderer.toneMappingExposure = 1.15;
    renderer.setPixelRatio(s.pr);
    renderer.setSize(s.w, s.h);
    canvas = renderer.domElement;
    canvas.className = "cube-canvas";
    container.appendChild(canvas);
    scene = new THREE.Scene();
  }

  function setUpCamera() {
    const s = sizes();
    camera = new THREE.PerspectiveCamera(45, s.aspect, 1, 1000);
    camera.position.set(0, 1, -10);
    camera.lookAt(0, 0, 0);   // важно: смотрим на кубик (раньше камера смотрела мимо)
    scene.add(camera);
  }

  function addLights() {
    RectAreaLightUniformsLib.init();
    const add = (intensity, w, h, pos) => {
      const l = new THREE.RectAreaLight(0xffffff, intensity, w, h);
      l.position.set(pos[0], pos[1], pos[2]);
      l.lookAt(rubiksCube.position);
      scene.add(l);
    };
    add(4, 4, 3, [-5, 5, 0]);
    add(4, 4, 3, [0, 0, 5.21]);
    add(4, 1.84, 8, [-2, 4, 0]);
    add(4, 1.84, 8.89, [-4, 0, -3]);
    scene.add(new THREE.AmbientLight(0xffffff, 0.22));
  }

  function generateCubeInstances() {
    const geo = new RoundedBoxGeometry(1, 1, 1);
    // ЧЁРНЫЙ глянцевый материал с переливами (как в оригинале resend.com)
    const mat = new THREE.MeshPhysicalMaterial({
      color: 0x0a0a0a,
      roughness: 0.1,
      metalness: 0.9,
      iridescence: 1,
      iridescenceIOR: 1.35,
      clearcoat: 1,
      clearcoatRoughness: 0.12,
    });
    for (let i = 0; i < 3; i++) {
      const m = new THREE.InstancedMesh(geo, mat, 9);
      m.castShadow = m.receiveShadow = true;
      rows.push(m);
    }
  }

  function arrangeCubes() {
    const offset = (3 - 1) / 2;
    rows.forEach((row) => {
      for (let c = 0; c < 9; c++) {
        const x = (c % 3) * 1.1 - offset;
        const y = Math.floor(c / 3) * 1.1 - offset;
        const z = rows.indexOf(row) * 1.1;
        dummy.position.set(x, y, z - 1);
        dummy.updateMatrix();
        row.setMatrixAt(c, dummy.matrix);
      }
      row.instanceMatrix.needsUpdate = true;
      row.computeBoundingSphere();
    });
  }

  function addCubes() {
    rows.forEach((r) => rubiksCube.add(r));
    scene.add(rubiksCube);
    rubiksCube.position.x = 0;   // по центру страницы
  }

  function render() {
    if (autoRotate) {
      // мягкое авто-вращение, когда кубик не держат
      rubiksCube.rotation.y += 0.0025;
      rubiksCube.rotation.x += 0.005;
      rubiksCube.rotation.z += 0.0025;
    } else {
      // инерция после броска
      rubiksCube.rotation.y += velY;
      rubiksCube.rotation.x += velX;
      velX *= 0.93; velY *= 0.93;
    }
    renderer.render(scene, camera);
  }

  /* ── управление перетаскиванием: тащишь — кубик крутится ── */
  function enableDrag() {
    canvas.style.pointerEvents = "auto";   // даём канвасу ловить мышь/тач
    let dragging = false, px = 0, py = 0, resumeTimer = null;

    const down = (e) => {
      dragging = true; autoRotate = false;
      if (resumeTimer) clearTimeout(resumeTimer);
      const p = e.touches ? e.touches[0] : e;
      px = p.clientX; py = p.clientY;
      velX = velY = 0;
    };
    const move = (e) => {
      if (!dragging) return;
      const p = e.touches ? e.touches[0] : e;
      const dx = p.clientX - px, dy = p.clientY - py;
      // без инверсии: кубик крутится в ту же сторону, что и движение
      velY = -dx * 0.006;           // тащишь вправо → крутится вправо
      velX = dy * 0.006;            // тащишь вниз → наклон вниз
      rubiksCube.rotation.y += velY;
      rubiksCube.rotation.x += velX;
      px = p.clientX; py = p.clientY;
    };
    const up = () => {
      if (!dragging) return;
      dragging = false;
      // докрутить по инерции, затем вернуть авто-вращение
      resumeTimer = setTimeout(() => { autoRotate = true; }, 2500);
    };

    canvas.addEventListener("pointerdown", down);
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", up);
    canvas.addEventListener("touchstart", down, { passive: true });
    window.addEventListener("touchmove", move, { passive: true });
    window.addEventListener("touchend", up);
  }

  function animateRow() {
    if (typeof anime === "undefined") return;
    anime({ targets: rubiksCube.children[0].rotation, z: Math.PI / 2,
      easing: "easeInOutSine", delay: 6000, duration: 5000, direction: "alternate", loop: true });
    setTimeout(() => anime({ targets: rubiksCube.children[2].rotation, z: -Math.PI,
      easing: "easeInOutSine", delay: 6000, duration: 5000, direction: "alternate", loop: true }), 1000);
    anime({ targets: rubiksCube.children[1].rotation, z: -Math.PI / 2,
      easing: "linear", delay: 10000, duration: 6000, direction: "alternate", loop: true });
  }

  window.addEventListener("resize", () => {
    if (!renderer) return;
    const s = sizes();
    renderer.setSize(s.w, s.h);
    camera.aspect = s.aspect;
    camera.updateProjectionMatrix();
  });

  setUpScene();
  setUpCamera();
  generateCubeInstances();
  arrangeCubes();
  addCubes();
  addLights();
  renderer.setAnimationLoop(render);
  animateRow();
  enableDrag();
}
