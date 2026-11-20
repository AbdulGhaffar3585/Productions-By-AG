(() => {
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const vimeo = (id, q) => `https://player.vimeo.com/video/${id}?${q}&dnt=1`;

  // ---- nav: solid background after scrolling, mobile menu
  const nav = document.querySelector('.nav');
  const onScroll = () => nav && nav.classList.toggle('scrolled', scrollY > 24);
  onScroll();
  addEventListener('scroll', onScroll, { passive: true });

  const toggle = document.querySelector('.nav-toggle');
  const toggleText = toggle && toggle.querySelector('.nav-toggle-text');
  const menu = document.getElementById('menu');
  const setMenu = (open) => {
    toggle.setAttribute('aria-expanded', String(open));
    if (toggleText) toggleText.textContent = open ? 'Close' : 'Menu';
    menu.hidden = !open;
    document.body.classList.toggle('menu-open', open);
  };
  if (toggle && menu) {
    toggle.addEventListener('click', () => setMenu(menu.hidden));
    addEventListener('keydown', (e) => { if (e.key === 'Escape' && !menu.hidden) { setMenu(false); toggle.focus(); } });
    matchMedia('(min-width: 921px)').addEventListener('change', (m) => m.matches && setMenu(false));
  }

  // ---- hero showreel: muted Vimeo background loop, loaded after the page
  const bg = document.querySelector('[data-vimeo-bg]');
  const saveData = navigator.connection && navigator.connection.saveData;
  if (bg && !reduceMotion && !saveData) {
    addEventListener('load', () => {
      const f = document.createElement('iframe');
      f.src = vimeo(bg.dataset.vimeoBg, 'background=1&autoplay=1&loop=1&muted=1');
      f.title = 'Showreel';
      f.allow = 'autoplay; fullscreen; picture-in-picture';
      f.setAttribute('aria-hidden', 'true');
      f.tabIndex = -1;
      f.addEventListener('load', () => setTimeout(() => f.classList.add('on'), 900));
      bg.appendChild(f);
    });
  }

  // ---- running timecodes (25 fps), purely decorative
  const tcs = document.querySelectorAll('[data-timecode]');
  if (tcs.length && !reduceMotion) {
    const t0 = performance.now();
    const pad = (n) => String(n).padStart(2, '0');
    const tick = (now) => {
      const f = Math.floor((now - t0) / 40);
      const txt = `${pad(Math.floor(f / 90000) % 24)}:${pad(Math.floor(f / 1500) % 60)}:${pad(Math.floor(f / 25) % 60)}:${pad(f % 25)}`;
      tcs.forEach((el) => { el.textContent = txt; });
      requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }

  // ---- project index: a frame follows the cursor
  const peek = document.querySelector('.peek');
  const list = document.querySelector('[data-peek]');
  if (peek && list && matchMedia('(hover: hover)').matches) {
    const pic = peek.querySelector('img');
    let x = 0, y = 0, px = 0, py = 0, raf = 0;
    const follow = () => {
      px += (x - px) * 0.18; py += (y - py) * 0.18;
      peek.style.left = `${px}px`; peek.style.top = `${py}px`;
      raf = Math.abs(x - px) + Math.abs(y - py) > 0.5 ? requestAnimationFrame(follow) : 0;
    };
    list.addEventListener('mousemove', (e) => { x = Math.min(e.clientX + 320, innerWidth - 200); y = e.clientY; if (!raf) raf = requestAnimationFrame(follow); });
    list.querySelectorAll('a').forEach((a) => {
      a.addEventListener('mouseenter', (e) => {
        if (!a.dataset.img) { peek.classList.remove('on'); return; }
        if (!peek.classList.contains('on')) { px = x = Math.min(e.clientX + 320, innerWidth - 200); py = y = e.clientY; }
        pic.src = a.dataset.img;
        peek.classList.add('on');
      });
    });
    list.addEventListener('mouseleave', () => peek.classList.remove('on'));
  }

  // ---- full showreel with sound, in a dialog
  const reel = document.getElementById('reel');
  const reelBtn = document.querySelector('[data-reel]');
  if (reel && reelBtn && typeof reel.showModal === 'function') {
    const frame = reel.querySelector('.reel-frame');
    reelBtn.addEventListener('click', () => {
      frame.innerHTML = `<iframe src="${vimeo(reelBtn.dataset.reel, 'autoplay=1&title=0&byline=0&portrait=0')}" title="Showreel" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe>`;
      reel.showModal();
    });
    reel.querySelector('[data-reel-close]').addEventListener('click', () => reel.close());
    reel.addEventListener('click', (e) => { if (e.target === reel) reel.close(); });
    reel.addEventListener('close', () => { frame.innerHTML = ''; reelBtn.focus(); });
  } else if (reelBtn) {
    reelBtn.addEventListener('click', () => { location.href = `https://vimeo.com/${reelBtn.dataset.reel}`; });
  }

  // ---- click-to-play Vimeo films (no player weight until asked)
  document.querySelectorAll('.facade[data-vimeo]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const f = document.createElement('iframe');
      f.src = vimeo(btn.dataset.vimeo, 'autoplay=1&title=0&byline=0&portrait=0');
      f.title = btn.getAttribute('aria-label').replace(/^Play /, '');
      f.allow = 'autoplay; fullscreen; picture-in-picture';
      f.allowFullscreen = true;
      btn.replaceWith(f);
    });
  });

  // ---- work filters
  const grid = document.getElementById('work-grid');
  if (grid) {
    const chips = document.querySelectorAll('[data-filter]');
    const empty = document.querySelector('.empty');
    chips.forEach((chip) => chip.addEventListener('click', () => {
      const f = chip.dataset.filter;
      chips.forEach((c) => c.setAttribute('aria-pressed', String(c === chip)));
      let shown = 0;
      grid.querySelectorAll('.card').forEach((card) => {
        const show = f === 'all' || card.dataset.type === f;
        card.hidden = !show;
        if (show) { shown++; card.classList.add('in'); }
      });
      if (empty) empty.hidden = shown > 0;
    }));
  }

  // ---- forms: /start (project brief) and /contact (general note)
  const email = document.querySelector('[data-email]')?.textContent.trim() || '';
  document.querySelectorAll('form[data-kind]').forEach((form) => {
    const isProject = form.dataset.kind === 'project';
    const status = form.querySelector('.form-status');
    const thanks = isProject
      ? 'Thank you — your brief is in. I\'ll reply within two working days.'
      : 'Thank you — message received. I\'ll get back to you soon.';
    const say = (html, cls) => { status.innerHTML = html; status.className = `form-status ${cls || ''}`; };

    if (new URLSearchParams(location.search).has('sent')) { form.classList.add('sent'); say(thanks, 'ok'); }

    const mailto = (d) => {
      const body = isProject
        ? `Name: ${d.name}\nCompany: ${d.company || '-'}\nProject type: ${d.type}\nTimeline: ${d.timeline}\n\n${d.message}`
        : `Name: ${d.name}\n\n${d.message}`;
      const subject = isProject ? `Project enquiry — ${d.type || 'New project'}` : `Hello from ${d.name}`;
      return `mailto:${email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    };

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const d = Object.fromEntries(new FormData(form));
      const fieldset = form.querySelector('fieldset');
      let bad = null;
      form.querySelectorAll('[aria-invalid]').forEach((el) => el.removeAttribute('aria-invalid'));
      if (fieldset) fieldset.classList.remove('fieldset-invalid');
      const need = (name, ok) => { if (!ok) { const el = form.elements[name]; if (el && el.setAttribute) el.setAttribute('aria-invalid', 'true'); bad = bad || name; } };
      need('name', d.name && d.name.trim());
      need('email', /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(d.email || ''));
      if (isProject && !d.type) { fieldset.classList.add('fieldset-invalid'); bad = bad || 'type'; }
      need('message', d.message && d.message.trim().length > 9);
      if (bad) {
        say(isProject
          ? 'Please fill in the highlighted fields — name, a valid email, project type, and a few lines about the project.'
          : 'Please add your name, a valid email, and a short message.', 'err');
        const el = bad === 'type' ? form.querySelector('input[name=type]') : form.elements[bad];
        el && el.focus();
        return;
      }

      const btn = form.querySelector('button[type=submit]');
      btn.disabled = true;
      say('Sending…');
      try {
        const r = await fetch('/api/contact', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(d) });
        const j = await r.json().catch(() => ({}));
        if (!r.ok || !j.ok) throw new Error(j.error || r.status);
        form.classList.add('sent');
        say(thanks, 'ok');
      } catch (err) {
        btn.disabled = false;
        say(`The form couldn't send just now. <a href="${mailto(d)}">Send it by email instead</a> — your message is already filled in.`, 'err');
      }
    });
  });

  // ---- gentle reveal on scroll
  const items = document.querySelectorAll('[data-reveal]');
  if ('IntersectionObserver' in window && !reduceMotion) {
    const io = new IntersectionObserver((entries) => entries.forEach((en) => {
      if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
    }), { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
    items.forEach((el) => io.observe(el));
  } else {
    items.forEach((el) => el.classList.add('in'));
  }
})();
