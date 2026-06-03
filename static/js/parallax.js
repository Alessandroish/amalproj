/* ══════════════════════════════════
   ЗВУК ПЕЧАТНОЙ МАШИНКИ (Web Audio, без файлов)
══════════════════════════════════ */
let _audioCtx = null;
function getAudio() {
  if (!_audioCtx) {
    try { _audioCtx = new (window.AudioContext || window.webkitAudioContext)(); }
    catch (e) { return null; }
  }
  if (_audioCtx.state === 'suspended') _audioCtx.resume();
  return _audioCtx;
}
// аудио в браузере разблокируется только после действия пользователя
['pointerdown','keydown','mousemove','touchstart','click'].forEach(ev =>
  window.addEventListener(ev, getAudio, { once: true }));

// мягкий «тук» клавиши — глухой шум с плавной атакой (не резкий)
function playKey() {
  const ctx = _audioCtx;
  if (!ctx || ctx.state !== 'running') return;
  const t = ctx.currentTime, dur = 0.07;
  const buf = ctx.createBuffer(1, Math.floor(ctx.sampleRate * dur), ctx.sampleRate);
  const data = buf.getChannelData(0);
  for (let i = 0; i < data.length; i++)
    data[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / data.length, 3);
  const src = ctx.createBufferSource(); src.buffer = buf;
  // низкочастотный фильтр убирает резкие верха
  const lp = ctx.createBiquadFilter(); lp.type = 'lowpass';
  lp.frequency.value = 850 + Math.random() * 250; lp.Q.value = 0.6;
  const g = ctx.createGain();
  g.gain.setValueAtTime(0.0001, t);
  g.gain.exponentialRampToValueAtTime(0.09, t + 0.008);  // плавная атака
  g.gain.exponentialRampToValueAtTime(0.0001, t + dur);  // мягкий спад
  src.connect(lp); lp.connect(g); g.connect(ctx.destination);
  src.start(t); src.stop(t + dur);
}

// звоночек «возврат каретки» в конце строки
function playBell() {
  const ctx = getAudio();
  if (!ctx || ctx.state !== 'running') return;
  const t = ctx.currentTime;
  const osc = ctx.createOscillator(); osc.type = 'sine'; osc.frequency.value = 1180;
  const g = ctx.createGain();
  g.gain.setValueAtTime(0.0001, t);
  g.gain.exponentialRampToValueAtTime(0.15, t + 0.012);
  g.gain.exponentialRampToValueAtTime(0.0001, t + 0.6);
  osc.connect(g); g.connect(ctx.destination);
  osc.start(t); osc.stop(t + 0.5);
}

/* ══════════════════════════════════
   INTRO — печатающийся текст при заходе
══════════════════════════════════ */
(function intro() {
  const overlay = document.getElementById('opening');
  const typed   = document.getElementById('intro-typed');
  if (!overlay || !typed) return;
  getAudio();  // попытка разблокировать аудио сразу

  document.body.classList.add('intro-lock');
  window.scrollTo(0, 0);

  // сегменты берутся из data-атрибутов body (задаются в админке)
  const d = document.body.dataset;
  const segments = [
    { t: d.introGreeting  || 'Привет, я ' },
    { t: d.introName      || 'Амаль', accent: true },
    { t: d.introMiddle    || ', учусь на специальности ' },
    { t: d.introSpecialty || '«Торговое дело»', accent: true },
  ];

  let si = 0, ci = 0;
  let span = null;

  function type() {
    if (si >= segments.length) { finish(); return; }
    const seg = segments[si];

    if (ci === 0) {
      span = document.createElement('span');
      if (seg.accent) span.className = 'accent';
      typed.appendChild(span);
    }

    const ch = seg.t[ci];
    span.textContent += ch;
    ci++;
    if (ch !== ' ') playKey();   // звук клавиши на каждый символ

    if (ci >= seg.t.length) { si++; ci = 0; }

    // скорость печати (медленнее): паузы на знаках, лёгкая случайность
    const last = span.textContent.slice(-1);
    const delay = /[.,»]/.test(last) ? 420 : 95 + Math.random() * 70;
    setTimeout(type, delay);
  }

  function finish() {
    // 1. пауза, чтобы прочитать текст + звоночек «возврат каретки»
    setTimeout(() => {
      overlay.classList.add('prep');               // лёгкий 3D-«вдох» текста
      playBell();
      // 2. панель с текстом откидывается вверх в 3D, открывая первую страницу
      setTimeout(() => {
        overlay.classList.add('flip');
        document.body.classList.add('site-enter');  // hero делает dolly-settle
        document.body.classList.remove('intro-lock');
        window.scrollTo(0, 0);
        setTimeout(() => overlay.remove(), 1600);
      }, 480);
    }, 650);
  }

  setTimeout(type, 400);
})();

/* ── МОБИЛЬНОЕ МЕНЮ (бургер) ── */
const navToggle = document.querySelector('.nav-toggle');
if (navToggle) {
  navToggle.addEventListener('click', () => {
    const open = document.body.classList.toggle('menu-open');
    navToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
  // закрывать меню при клике по ссылке
  document.querySelectorAll('#nav-menu a').forEach(a =>
    a.addEventListener('click', () => {
      document.body.classList.remove('menu-open');
      navToggle.setAttribute('aria-expanded', 'false');
    }));
}

/* ── ШАПКА: всегда видна, лишь чуть уплотняется после прокрутки ── */
const navEl = document.querySelector('nav');
window.addEventListener('scroll', () => {
  navEl.classList.toggle('nav-scrolled', window.scrollY > 40);
}, { passive: true });

/* ── CUSTOM CURSOR ── */
const dot  = document.getElementById('cursor-dot');
const ring = document.getElementById('cursor-ring');
let mx = 0, my = 0, rx = 0, ry = 0;

document.addEventListener('mousemove', e => {
  mx = e.clientX; my = e.clientY;
  dot.style.left = mx + 'px';
  dot.style.top  = my + 'px';
});
(function lerpRing() {
  rx += (mx - rx) * 0.11;
  ry += (my - ry) * 0.11;
  ring.style.left = rx + 'px';
  ring.style.top  = ry + 'px';
  requestAnimationFrame(lerpRing);
})();

/* ── CURSOR TRAIL PARTICLES (chain follow) ── */
const TRAIL_COUNT = 18;
const trailColors = ['#00c87a', '#1a56ff', '#00c87a', '#ffffff', '#1a56ff', '#00c87a'];
const particles = [];

for (let i = 0; i < TRAIL_COUNT; i++) {
  const p = document.createElement('div');
  p.className = 'trail-particle';
  const size = 3 + (1 - i / TRAIL_COUNT) * 6;
  p.style.cssText = `
    width: ${size}px; height: ${size}px;
    background: ${trailColors[i % trailColors.length]};
    opacity: 0;
  `;
  document.body.appendChild(p);
  particles.push({ el: p, x: 0, y: 0 });
}

(function animateTrail() {
  // каждая частица догоняет предыдущую (а первая — сам курсор).
  // когда курсор стоит, вся цепочка стягивается ровно в точку курсора.
  let leadX = mx, leadY = my;
  particles.forEach((p, i) => {
    p.x += (leadX - p.x) * 0.4;
    p.y += (leadY - p.y) * 0.4;
    p.el.style.left      = p.x + 'px';
    p.el.style.top       = p.y + 'px';
    p.el.style.opacity   = (1 - i / TRAIL_COUNT) * 0.7;
    p.el.style.transform = `translate(-50%,-50%) scale(${1 - i * 0.04})`;
    leadX = p.x; leadY = p.y;
  });
  requestAnimationFrame(animateTrail);
})();

document.querySelectorAll('a, button, .skill-row, .project-card, .btn-primary').forEach(el => {
  el.addEventListener('mouseenter', () => document.body.classList.add('cursor-hover'));
  el.addEventListener('mouseleave', () => document.body.classList.remove('cursor-hover'));
});
document.addEventListener('mousedown', () => document.body.classList.add('cursor-click'));
document.addEventListener('mouseup',   () => document.body.classList.remove('cursor-click'));

/* ── HERO SCROLL TEXT ROTATION ── */
const heroLines = document.querySelectorAll('.hero-title-line');
const heroSection = document.getElementById('hero');

window.addEventListener('scroll', () => {
  if (!heroSection) return;
  const scrollY = window.scrollY;
  const heroH = heroSection.offsetHeight;
  const progress = Math.min(scrollY / heroH, 1); // 0 → 1 пока в hero

  heroLines.forEach((line, i) => {
    const dir = i % 2 === 0 ? 1 : -1;          // чётные вправо, нечётные влево
    const tx  = dir * progress * 120;           // сдвиг по X
    const rot = dir * progress * 8;             // поворот до 8°
    const op  = 1 - progress * 0.6;             // немного тускнеет
    const scale = 1 - progress * 0.08;
    line.style.transform = `translateX(${tx}px) rotate(${rot}deg) scale(${scale})`;
    line.style.opacity   = op;
  });
}, { passive: true });

/* ── HERO BLOB PARALLAX ── */
const blob = document.querySelector('.hero-blob');
document.addEventListener('mousemove', e => {
  if (!blob) return;
  const nx = (e.clientX / window.innerWidth  - 0.5) * 30;
  const ny = (e.clientY / window.innerHeight - 0.5) * 20;
  blob.style.transform = `translate(${nx}px, ${ny}px)`;
});

/* ── 3D-СЦЕНА (cosmos.so): наклон поля карточек за курсором ── */
const scene3d = document.querySelector('.scene3d');
if (scene3d) {
  let targetRX = 0, targetRY = 0, curRX = 0, curRY = 0;
  document.addEventListener('mousemove', e => {
    const nx = e.clientX / window.innerWidth  - 0.5;
    const ny = e.clientY / window.innerHeight - 0.5;
    targetRY = nx * 18;    // поворот вокруг вертикали
    targetRX = -ny * 13;   // поворот вокруг горизонтали
  });
  (function tiltLoop() {
    curRX += (targetRX - curRX) * 0.06;   // плавная инерция
    curRY += (targetRY - curRY) * 0.06;
    scene3d.style.transform =
      `rotateX(${curRX.toFixed(2)}deg) rotateY(${curRY.toFixed(2)}deg)`;
    requestAnimationFrame(tiltLoop);
  })();
}

/* ── REVEAL ON SCROLL ── */
const revealObs = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) { e.target.classList.add('visible'); revealObs.unobserve(e.target); }
  });
}, { threshold: 0.12 });
document.querySelectorAll('.reveal').forEach(el => revealObs.observe(el));

/* ── SCROLL PROGRESS BAR ── */
const progress = document.getElementById('progress');
function updateProgress() {
  const h = document.documentElement.scrollHeight - window.innerHeight;
  const p = h > 0 ? window.scrollY / h : 0;
  if (progress) progress.style.transform = `scaleX(${p})`;
}
window.addEventListener('scroll', updateProgress, { passive: true });
updateProgress();

/* ── PARALLAX между секциями (глубина при скролле) ── */
const auroraLayer = document.querySelector('.aurora');
const parallaxNodes = [...document.querySelectorAll('[data-parallax]')];
let parallaxTicking = false;
function parallaxTick() {
  const y = window.scrollY;
  const vh = window.innerHeight;
  // фон-аврора движется медленнее контента
  if (auroraLayer) auroraLayer.style.transform = `translate3d(0, ${y * 0.14}px, 0)`;
  // декоративные слои дрейфуют относительно центра экрана
  parallaxNodes.forEach(el => {
    const speed = parseFloat(el.dataset.parallax) || 0;
    const rect = el.getBoundingClientRect();
    const offset = (rect.top + rect.height / 2) - vh / 2;
    el.style.transform = `translate3d(0, ${(-offset * speed).toFixed(1)}px, 0)`;
  });
  parallaxTicking = false;
}
window.addEventListener('scroll', () => {
  if (!parallaxTicking) { requestAnimationFrame(parallaxTick); parallaxTicking = true; }
}, { passive: true });
parallaxTick();

/* ── ПОЯВЛЕНИЕ БУКВ В МЕТКАХ СЕКЦИЙ ── */
document.querySelectorAll('.section-label').forEach(label => {
  const text = label.textContent;
  // обернуть текст в один flex-элемент, чтобы не ломать gap с линией ::after
  const wrap = document.createElement('span');
  wrap.className = 'label-text';
  [...text].forEach((ch, i) => {
    const s = document.createElement('span');
    s.className = 'lchar';
    s.textContent = ch === ' ' ? ' ' : ch;
    s.style.transitionDelay = (i * 0.03) + 's';
    wrap.appendChild(s);
  });
  label.textContent = '';
  label.appendChild(wrap);
});

/* ── ANIMATED SECTION LABEL UNDERLINE + буквы ── */
const labelObs = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) { e.target.classList.add('visible-label'); labelObs.unobserve(e.target); }
  });
}, { threshold: 0.2 });
document.querySelectorAll('section').forEach(sec => {
  if (sec.querySelector('.section-label')) labelObs.observe(sec);
});

/* ── 3D TILT карточек проектов ── */
document.querySelectorAll('.project-card').forEach(card => {
  card.addEventListener('mousemove', e => {
    const r = card.getBoundingClientRect();
    const px = (e.clientX - r.left) / r.width  - 0.5;
    const py = (e.clientY - r.top)  / r.height - 0.5;
    card.style.transform =
      `translateY(-6px) rotateX(${-py * 7}deg) rotateY(${px * 7}deg)`;
  });
  card.addEventListener('mouseleave', () => { card.style.transform = ''; });
});

/* ── HERO CHAR SPLIT + появление ── */
document.querySelectorAll('.split-chars').forEach(el => {
  const html = [...el.textContent].map((ch, i) =>
    `<span class="char" style="opacity:0;transform:translateY(22px);
      transition:opacity .5s ${.04*i}s ease,transform .5s ${.04*i}s ease">${ch === ' ' ? '&nbsp;' : ch}</span>`
  ).join('');
  el.innerHTML = html;
  setTimeout(() => el.querySelectorAll('.char').forEach(s => {
    s.style.opacity = '1';
    s.style.transform = 'translateY(0)';
    // по окончании появления отдаём управление transform эффекту близости
    setTimeout(() => { s.style.transition = ''; s.style.transform = ''; }, 700);
  }), 200);
});

/* ── HERO LETTERS — увеличение у курсора (волной по всему тексту) ── */
const heroChars = () => document.querySelectorAll('.hero-title .char');
const RADIUS = 70;     // горизонтальная зона влияния курсора, px
const MAX_SCALE = 0.5; // насколько сильно растёт ближайшая буква (→ до 1.5x)

document.addEventListener('mousemove', e => {
  heroChars().forEach(ch => {
    const r = ch.getBoundingClientRect();
    const cx = r.left + r.width / 2;
    const cy = r.top + r.height / 2;
    const dx = e.clientX - cx;
    const dy = e.clientY - cy;
    // эффект только на строке под курсором: буквы других строк не трогаем
    if (Math.abs(dy) > r.height * 0.5 || Math.abs(dx) >= RADIUS) {
      ch.style.transform = '';
      ch.style.color = '';
      return;
    }
    const f = 1 - Math.abs(dx) / RADIUS;     // 0..1 по горизонтали
    const scale = 1 + f * MAX_SCALE;          // ближе → больше
    const lift  = -f * 10;                    // лёгкий подъём
    ch.style.transform = `translateY(${lift}px) scale(${scale})`;
    // синие буквы («цифровые») у курсора становятся белыми, остальные — синими
    const isBlue = ch.closest('.blue') !== null;
    ch.style.color = f > 0.55 ? (isBlue ? 'var(--fg)' : 'var(--blue)') : '';
  });
}, { passive: true });

/* ── COUNTERS (плавный счёт с замедлением) ── */
function runCounter(el) {
  const target = +el.dataset.target;
  const suffix = el.dataset.suffix || '';
  const duration = 1500;
  const start = performance.now();
  function tick(now) {
    const t = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - t, 3);   // easeOutCubic — замедление к концу
    el.textContent = Math.round(eased * target) + suffix;
    if (t < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}
const statObs = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.querySelectorAll('[data-target]').forEach(runCounter);
      statObs.unobserve(e.target);
    }
  });
}, { threshold: 0.5 });
document.querySelectorAll('.stat-row').forEach(el => statObs.observe(el));

/* ── MAGNETIC BTN ── */
document.querySelectorAll('.btn-primary').forEach(btn => {
  btn.addEventListener('mousemove', e => {
    const r = btn.getBoundingClientRect();
    const x = e.clientX - r.left - r.width / 2;
    const y = e.clientY - r.top  - r.height / 2;
    btn.style.transform = `translate(${x * 0.22}px,${y * 0.35}px)`;
  });
  btn.addEventListener('mouseleave', () => btn.style.transform = '');
});

/* ══════════════════════════════════
   PAGE RISE — плавный подъём каждой секции при скролле.
   Непрерывный переход между всеми экранами: следующая страница
   всплывает снизу, слегка увеличиваясь и проявляясь.
══════════════════════════════════ */
const risePages = [
  document.getElementById('crow-section'),
  document.getElementById('about'),
  document.getElementById('skills'),
  document.getElementById('projects'),
  document.getElementById('contact'),
].filter(Boolean);

function easeOutCubic(t) { return 1 - Math.pow(1 - t, 3); }

function risePagesUpdate() {
  const vh = window.innerHeight;
  risePages.forEach(sec => {
    const rect = sec.getBoundingClientRect();
    // окно появления — средняя скорость: ~0.55 экрана прокрутки.
    // старт, когда верх секции на 0.92 экрана; финиш — на 0.35 экрана.
    let p = (vh * 0.92 - rect.top) / (vh * 0.55);
    p = Math.max(0, Math.min(1, p));
    const e = easeOutCubic(p);
    const ty    = (1 - e) * 70;          // всплывает снизу на 70px
    const scale = 0.92 + e * 0.08;       // 0.92 → 1
    sec.style.transform = `translateY(${ty}px) scale(${scale})`;
    sec.style.opacity   = e;
  });
}

window.addEventListener('scroll', risePagesUpdate, { passive: true });
window.addEventListener('resize', risePagesUpdate);
risePagesUpdate();

/* ══════════════════════════════════
   CROW ANIMATION
══════════════════════════════════ */
const crowWrapper = document.querySelector('.crow-wrapper');
if (crowWrapper) {
  const crowObs = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        crowWrapper.classList.add('active');
        spawnFeathers();
        crowObs.unobserve(crowWrapper);
      }
    });
  }, { threshold: 0.4 });
  crowObs.observe(crowWrapper);
}

function spawnFeathers() {
  const colors = ['#00c87a', '#ff3b3b', '#1a56ff', '#fff'];
  for (let i = 0; i < 18; i++) {
    setTimeout(() => {
      const f = document.createElement('div');
      f.className = 'feather';
      const angle = Math.random() * 360;
      const dist  = 80 + Math.random() * 120;
      const fx = Math.cos(angle * Math.PI/180) * dist + 'px';
      const fy = Math.sin(angle * Math.PI/180) * dist + 'px';
      const fr = (Math.random() - 0.5) * 360 + 'deg';
      f.style.cssText = `
        left: ${40 + Math.random()*20}%;
        top:  ${40 + Math.random()*20}%;
        background: ${colors[Math.floor(Math.random()*colors.length)]};
        --fx: ${fx}; --fy: ${fy}; --fr: ${fr};
        animation: featherFly ${.6 + Math.random()*.8}s ${Math.random()*.4}s ease-out forwards;
      `;
      crowWrapper.appendChild(f);
      setTimeout(() => f.remove(), 1400);
    }, i * 60);
  }
}

/* continuous feather loop while crow is visible */
setInterval(() => {
  if (crowWrapper && crowWrapper.classList.contains('active')) spawnFeathers();
}, 3500);

/* wing flap on hover */
if (crowWrapper) {
  crowWrapper.addEventListener('mouseenter', () => {
    const wings = crowWrapper.querySelectorAll('.wing');
    wings.forEach(w => w.style.animation = 'wingFlap .3s ease-in-out 4');
    setTimeout(() => wings.forEach(w => w.style.animation = ''), 1300);
  });
}
