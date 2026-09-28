/* ==========================================================
   ClearHub — All Interactions & Animations
   ========================================================== */

document.addEventListener('DOMContentLoaded', () => {
  document.body.classList.add('page-loaded');
});

// ============ THEME SWITCHER ============
(function () {
  const THEMES = ['light', 'dark', 'neumorphic', 'contrast'];

  function applyTheme(theme, silent) {
    if (!THEMES.includes(theme)) theme = 'light';
    document.documentElement.setAttribute('data-theme', theme);
    document.documentElement.setAttribute('data-bs-theme',
      (theme === 'dark' || theme === 'contrast') ? 'dark' : 'light');
    localStorage.setItem('theme', theme);
    updateIcons(theme);
    document.querySelectorAll('[data-theme-option]').forEach(el => {
      el.classList.toggle('active', el.dataset.themeOption === theme);
    });
    if (!silent) {
      const flash = document.createElement('div');
      flash.className = 'theme-flash';
      document.body.appendChild(flash);
      setTimeout(() => flash.remove(), 700);
    }
  }

  function updateIcons(theme) {
    const map = {
      light: 'bi bi-sun-fill',
      dark: 'bi bi-moon-stars-fill',
      neumorphic: 'bi bi-circle-half',
      contrast: 'bi bi-brightness-high-fill',
    };
    document.querySelectorAll('.dropdown-toggle i, [data-theme-toggle]').forEach(i => {
      i.className = map[theme] || 'bi bi-sun-fill';
    });
  }

  applyTheme(localStorage.getItem('theme') || 'light', true);

  document.addEventListener('click', (e) => {
    const option = e.target.closest('[data-theme-option]');
    if (option) {
      e.preventDefault();
      applyTheme(option.dataset.themeOption);
    }
  });
})();

// ============ SIDEBAR TOGGLE ============
document.addEventListener('click', (e) => {
  const toggle = e.target.closest('#menuToggle');
  const sidebar = document.getElementById('sidebar');
  const backdrop = document.getElementById('sidebarBackdrop');
  if (toggle) {
    sidebar?.classList.toggle('open');
    backdrop?.classList.toggle('show');
  }
  if (e.target.closest('#sidebarBackdrop')) {
    sidebar?.classList.remove('open');
    backdrop?.classList.remove('show');
  }
});

// ============ RIPPLE ============
document.addEventListener('click', (e) => {
  const btn = e.target.closest('.btn, .icon-btn');
  if (!btn) return;
  const r = btn.getBoundingClientRect();
  const ripple = document.createElement('span');
  ripple.className = 'ripple';
  ripple.style.left = (e.clientX - r.left) + 'px';
  ripple.style.top = (e.clientY - r.top) + 'px';
  btn.style.position = 'relative';
  btn.style.overflow = 'hidden';
  btn.appendChild(ripple);
  setTimeout(() => ripple.remove(), 700);
});

// ============ SCROLL REVEAL ============
(function () {
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('reveal-in');
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.12 });
  const attach = () => document.querySelectorAll('.reveal, .stagger').forEach(el => io.observe(el));
  if (document.readyState !== 'loading') attach();
  else document.addEventListener('DOMContentLoaded', attach);
})();

// ============ SCROLL PROGRESS BAR ============
(function () {
  const bar = document.createElement('div');
  bar.className = 'scroll-progress';
  document.body.appendChild(bar);
  window.addEventListener('scroll', () => {
    const st = window.scrollY;
    const dh = document.documentElement.scrollHeight - window.innerHeight;
    bar.style.width = (dh > 0 ? (st / dh) * 100 : 0) + '%';
  }, { passive: true });
})();

// ============ LIQUID BLOB BACKGROUND ============
(function () {
  document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.liquid-bg')) return;
    const bg = document.createElement('div');
    bg.className = 'liquid-bg';
    bg.innerHTML = `
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
      <div class="blob blob-3"></div>
    `;
    document.body.appendChild(bg);
  });
})();

// ============ CUSTOM CURSOR ============
(function () {
  if (window.matchMedia('(hover: none)').matches) return;
  if (window.matchMedia('(max-width: 991px)').matches) return;

  const dot = document.createElement('div');
  dot.className = 'custom-cursor';
  const ring = document.createElement('div');
  ring.className = 'custom-cursor-ring';
  document.body.appendChild(dot);
  document.body.appendChild(ring);

  let mx = 0, my = 0, rx = 0, ry = 0;

  document.addEventListener('mousemove', (e) => {
    mx = e.clientX; my = e.clientY;
    dot.style.left = mx + 'px';
    dot.style.top = my + 'px';
  });

  function loop() {
    rx += (mx - rx) * 0.15;
    ry += (my - ry) * 0.15;
    ring.style.left = rx + 'px';
    ring.style.top = ry + 'px';
    requestAnimationFrame(loop);
  }
  loop();

  const hoverTargets = 'a, button, .btn, .stat-tile, .p-card, input, textarea, select';
  document.addEventListener('mouseover', (e) => {
    if (e.target.closest(hoverTargets)) {
      dot.classList.add('hovering');
      ring.classList.add('hovering');
    }
  });
  document.addEventListener('mouseout', (e) => {
    if (e.target.closest(hoverTargets)) {
      dot.classList.remove('hovering');
      ring.classList.remove('hovering');
    }
  });
})();

// ============ 3D CARD TILT ============
(function () {
  function attach() {
    document.querySelectorAll('.p-card, .stat-tile').forEach(card => {
      card.classList.add('tilt-card');
      card.addEventListener('mousemove', (e) => {
        const r = card.getBoundingClientRect();
        const x = e.clientX - r.left, y = e.clientY - r.top;
        const cx = r.width / 2, cy = r.height / 2;
        const rotX = ((y - cy) / cy) * -3;
        const rotY = ((x - cx) / cx) * 3;
        card.style.transform = `translateY(-6px) perspective(1000px) rotateX(${rotX}deg) rotateY(${rotY}deg)`;
      });
      card.addEventListener('mouseleave', () => { card.style.transform = ''; });
    });
  }
  if (document.readyState !== 'loading') attach();
  else document.addEventListener('DOMContentLoaded', attach);
})();

// ============ MAGNETIC BUTTONS ============
(function () {
  function attach() {
    document.querySelectorAll('.btn-primary, .btn-warning, .magnetic').forEach(btn => {
      btn.classList.add('magnetic');
      btn.addEventListener('mousemove', (e) => {
        const r = btn.getBoundingClientRect();
        const x = e.clientX - r.left - r.width / 2;
        const y = e.clientY - r.top - r.height / 2;
        btn.style.transform = `translate(${x * 0.2}px, ${y * 0.2}px)`;
      });
      btn.addEventListener('mouseleave', () => { btn.style.transform = ''; });
    });
  }
  if (document.readyState !== 'loading') attach();
  else document.addEventListener('DOMContentLoaded', attach);
})();

// ============ BACK TO TOP ============
(function () {
  const btn = document.createElement('button');
  btn.className = 'back-to-top-btn';
  btn.innerHTML = '<i class="bi bi-arrow-up"></i>';
  btn.setAttribute('aria-label', 'Back to top');
  btn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
  document.body.appendChild(btn);
  window.addEventListener('scroll', () => {
    btn.classList.toggle('show', window.scrollY > 400);
  });
})();

// ============ HERO CURSOR GLOW ============
(function () {
  const hero = document.querySelector('.hero-lms');
  if (!hero) return;
  const glow = document.createElement('div');
  glow.className = 'hero-cursor-glow';
  glow.style.opacity = '0';
  hero.appendChild(glow);
  hero.addEventListener('mousemove', (e) => {
    const r = hero.getBoundingClientRect();
    glow.style.left = (e.clientX - r.left) + 'px';
    glow.style.top = (e.clientY - r.top) + 'px';
    glow.style.opacity = '1';
  });
  hero.addEventListener('mouseleave', () => { glow.style.opacity = '0'; });
})();

// ============ SPLIT TEXT ============
window.splitReveal = function (selector) {
  document.querySelectorAll(selector).forEach((el, idx) => {
    const text = el.textContent;
    el.textContent = '';
    [...text].forEach((char, i) => {
      const span = document.createElement('span');
      span.className = 'split-char';
      span.textContent = char === ' ' ? '\u00A0' : char;
      span.style.animationDelay = `${idx * 0.05 + i * 0.03}s`;
      el.appendChild(span);
    });
  });
};
document.addEventListener('DOMContentLoaded', () => {
  const heroH1 = document.querySelector('.hero-lms h1');
  if (heroH1 && !heroH1.dataset.splitDone) {
    window.splitReveal('.hero-lms h1');
    heroH1.dataset.splitDone = 'true';
  }
});

// ============ COUNTERS ============
(function () {
  function animate(el) {
    const target = parseFloat(el.dataset.target);
    const suffix = el.dataset.suffix || '';
    const duration = 1600;
    const start = performance.now();
    function step(now) {
      const t = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - t, 3);
      el.textContent = Math.floor(target * eased) + suffix;
      if (t < 1) requestAnimationFrame(step);
      else el.textContent = target + suffix;
    }
    requestAnimationFrame(step);
  }
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) { animate(e.target); io.unobserve(e.target); }
    });
  }, { threshold: 0.4 });
  const attach = () => document.querySelectorAll('.counter').forEach(el => io.observe(el));
  if (document.readyState !== 'loading') attach();
  else document.addEventListener('DOMContentLoaded', attach);
})();

// ============ PAGE TRANSITIONS ============
document.addEventListener('click', (e) => {
  const link = e.target.closest('a[href]');
  if (!link) return;
  const href = link.getAttribute('href');
  if (!href || href.startsWith('#') || href.startsWith('mailto:') || href.startsWith('tel:')) return;
  if (link.target === '_blank' || link.hasAttribute('data-no-transition')) return;
  if (href.startsWith('http') && !href.startsWith(location.origin)) return;

  e.preventDefault();
  const content = document.querySelector('.page-content, main');
  if (content) content.classList.add('page-exit');
  setTimeout(() => { window.location.href = href; }, 280);
});

// ============ SOCKET.IO NOTIFICATIONS ============
if (typeof io !== 'undefined') {
  const socket = io();
  socket.on('notification', (data) => {
    const el = document.createElement('div');
    el.className = 'alert alert-info shadow-sm border-0';
    el.innerHTML = '<i class="bi bi-bell-fill"></i> ' + data.msg;
    const container = document.getElementById('toast-container');
    if (container) {
      container.appendChild(el);
      setTimeout(() => {
        el.style.animation = 'slideOutRight .4s ease forwards';
        setTimeout(() => el.remove(), 400);
      }, 5000);
    }
  });
}

// ============ CONFETTI (certificate page) ============
window.celebrate = function () {
  const colors = ['#2563eb','#7c3aed','#f59e0b','#10b981','#ef4444','#ec4899'];
  for (let i = 0; i < 90; i++) {
    const p = document.createElement('div');
    p.className = 'confetti-piece';
    p.style.left = Math.random() * 100 + 'vw';
    p.style.background = colors[Math.floor(Math.random() * colors.length)];
    p.style.animationDelay = Math.random() * 0.6 + 's';
    p.style.animationDuration = (2.4 + Math.random() * 1.6) + 's';
    document.body.appendChild(p);
    setTimeout(() => p.remove(), 4200);
  }
};
document.addEventListener('DOMContentLoaded', () => {
  if (document.querySelector('.certificate-card, .bi-award-fill')) {
    setTimeout(() => window.celebrate && window.celebrate(), 400);
  }
});