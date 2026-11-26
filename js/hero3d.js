// 3D visual of the Inspiration section (three.js): a sphere of 1,524 points,
// one per AI-enabled device on the FDA list, coloured by medical specialty.
// The points gather into the sphere the first time it scrolls into view,
// then the sphere turns slowly and
// follows the pointer. Paused when off-screen; static if the visitor prefers
// reduced motion. three.js is loaded with a dynamic import so the page also
// works when opened locally from a file.

(async function () {
  "use strict";

  var THREE_URL = "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.min.js";
  var container = document.getElementById("hero-3d");
  var data = window.CHART_DATA;

  function supportsWebGL() {
    try {
      var canvas = document.createElement("canvas");
      return !!(window.WebGLRenderingContext && (canvas.getContext("webgl2") || canvas.getContext("webgl")));
    } catch (e) {
      return false;
    }
  }

  if (!container || !data || !supportsWebGL()) return;

  var THREE;
  try {
    THREE = await import(THREE_URL);
  } catch (e) {
    return;
  }

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var COLORS = {
    Radiology: new THREE.Color("#257de0"),
    Cardiovascular: new THREE.Color("#f47230"),
    Neurology: new THREE.Color("#00b894"),
    Other: new THREE.Color("#9fb0bd")
  };

  // One entry per device, then a deterministic shuffle so that the colours
  // are spread over the sphere.
  var groups = [];
  data.waffle.forEach(function (g) {
    for (var i = 0; i < g.count; i++) groups.push(g.group);
  });
  var seed = 7;
  function random() {
    seed = (seed * 16807) % 2147483647;
    return (seed - 1) / 2147483646;
  }
  for (var i = groups.length - 1; i > 0; i--) {
    var j = Math.floor(random() * (i + 1));
    var tmp = groups[i];
    groups[i] = groups[j];
    groups[j] = tmp;
  }

  var count = groups.length;
  var target = new Float32Array(count * 3);
  var start = new Float32Array(count * 3);
  var colors = new Float32Array(count * 3);

  // Fibonacci sphere: evenly spaced points on a unit sphere.
  var golden = Math.PI * (3 - Math.sqrt(5));
  for (var p = 0; p < count; p++) {
    var y = 1 - (p / (count - 1)) * 2;
    var r = Math.sqrt(1 - y * y);
    var theta = golden * p;
    target[p * 3] = Math.cos(theta) * r;
    target[p * 3 + 1] = y;
    target[p * 3 + 2] = Math.sin(theta) * r;

    // Starting position: scattered in a wider shell.
    var spread = 2.6 + random() * 2.4;
    var u = random() * 2 - 1;
    var phi = random() * Math.PI * 2;
    var s = Math.sqrt(1 - u * u);
    start[p * 3] = Math.cos(phi) * s * spread;
    start[p * 3 + 1] = u * spread;
    start[p * 3 + 2] = Math.sin(phi) * s * spread;

    var c = COLORS[groups[p]];
    colors[p * 3] = c.r;
    colors[p * 3 + 1] = c.g;
    colors[p * 3 + 2] = c.b;
  }

  // Round point sprite.
  var sprite = document.createElement("canvas");
  sprite.width = sprite.height = 64;
  var ctx = sprite.getContext("2d");
  ctx.beginPath();
  ctx.arc(32, 32, 28, 0, Math.PI * 2);
  ctx.fillStyle = "#ffffff";
  ctx.fill();

  var positions = new Float32Array(reduceMotion ? target : start);
  var geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));

  var material = new THREE.PointsMaterial({
    size: 0.045,
    map: new THREE.CanvasTexture(sprite),
    vertexColors: true,
    transparent: true,
    alphaTest: 0.4,
    sizeAttenuation: true
  });

  var scene = new THREE.Scene();
  var points = new THREE.Points(geometry, material);
  points.rotation.x = 0.35;
  scene.add(points);

  // Thin orbit ring for structure.
  var ring = new THREE.Mesh(
    new THREE.RingGeometry(1.32, 1.325, 128),
    new THREE.MeshBasicMaterial({ color: 0x257de0, transparent: true, opacity: 0.25, side: THREE.DoubleSide })
  );
  ring.rotation.x = Math.PI / 2 - 0.35;
  scene.add(ring);

  var camera = new THREE.PerspectiveCamera(40, 1, 0.1, 100);
  camera.position.set(0, 0, 4.2);

  var renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setClearColor(0x000000, 0);
  container.appendChild(renderer.domElement);
  container.classList.add("is-ready");

  function resize() {
    var w = container.clientWidth;
    var h = container.clientHeight;
    if (!w || !h) return;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }
  resize();
  window.addEventListener("resize", resize);

  // Pointer parallax
  var pointerX = 0;
  var pointerY = 0;
  window.addEventListener("pointermove", function (event) {
    pointerX = (event.clientX / window.innerWidth) * 2 - 1;
    pointerY = (event.clientY / window.innerHeight) * 2 - 1;
  }, { passive: true });

  var gatherDuration = 2600;
  var startTime = null;
  var gathered = reduceMotion;
  var hasObserver = "IntersectionObserver" in window;
  var visible = !hasObserver;
  var running = false;

  function easeOut(t) {
    return 1 - Math.pow(1 - t, 3);
  }

  function frame(time) {
    running = true;
    if (startTime === null) startTime = time;

    if (!gathered) {
      var t = Math.min((time - startTime) / gatherDuration, 1);
      for (var k = 0; k < count; k++) {
        // Small per-point delay so that the sphere forms in a wave.
        var local = Math.min(Math.max(t * 1.35 - (k / count) * 0.35, 0), 1);
        var e = easeOut(local);
        positions[k * 3] = start[k * 3] + (target[k * 3] - start[k * 3]) * e;
        positions[k * 3 + 1] = start[k * 3 + 1] + (target[k * 3 + 1] - start[k * 3 + 1]) * e;
        positions[k * 3 + 2] = start[k * 3 + 2] + (target[k * 3 + 2] - start[k * 3 + 2]) * e;
      }
      geometry.attributes.position.needsUpdate = true;
      if (t >= 1) gathered = true;
    }

    if (!reduceMotion) {
      points.rotation.y += 0.0016;
      points.rotation.x += (0.35 + pointerY * 0.18 - points.rotation.x) * 0.04;
      points.rotation.z += (pointerX * 0.12 - points.rotation.z) * 0.04;
    }

    renderer.render(scene, camera);

    if (visible && (!reduceMotion || !gathered)) {
      window.requestAnimationFrame(frame);
    } else {
      running = false;
    }
  }

  // Only animate while the sphere is on screen. Before it first appears, one
  // frame is drawn so that the canvas is never empty.
  renderer.render(scene, camera);
  if (hasObserver) {
    new IntersectionObserver(function (entries) {
      visible = entries[0].isIntersecting;
      if (visible && !running) window.requestAnimationFrame(frame);
    }, { threshold: 0.2 }).observe(container);
  } else {
    window.requestAnimationFrame(frame);
  }
})();
