(() => {
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ---- nav: solid background after scrolling, mobile menu
  const nav = document.querySelector('.nav');
  const onScroll = () => nav && nav.classList.toggle('scrolled', scrollY > 24);
  onScroll();
  addEventListener('scroll', onScroll, { passive: true });

  const toggle = document.querySelector('.nav-toggle');
  const menu = document.getElementById('menu');
  const setMenu = (open) => {
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    menu.hidden = !open;
    document.body.classList.toggle('menu-open', open);
  };
  if (toggle && menu) {
    toggle.addEventListener('click', () => setMenu(menu.hidden));
    addEventListener('keydown', (e) => { if (e.key === 'Escape' && !menu.hidden) { setMenu(false); toggle.focus(); } });
    matchMedia('(min-width: 861px)').addEventListener('change', (m) => m.matches && setMenu(false));
  }

  // ---- hero showreel: muted Vimeo background loop, loaded after the page
  const bg = document.querySelector('[data-vimeo-bg]');
  const saveData = navigator.connection && navigator.connection.saveData;
  if (bg && !reduceMotion && !saveData) {
    addEventListener('load', () => {
      const f = document.createElement('iframe');
      f.src = `https://player.vimeo.com/video/${bg.dataset.vimeoBg}?background=1&autoplay=1&loop=1&muted=1&dnt=1`;
      f.title = 'Showreel';
      f.allow = 'autoplay; fullscreen; picture-in-picture';
      f.setAttribute('aria-hidden', 'true');
      f.tabIndex = -1;
      f.addEventListener('load', () => setTimeout(() => f.classList.add('on'), 900));
      bg.appendChild(f);
    });
  }

  // ---- click-to-play Vimeo films (no player weight until asked)
  document.querySelectorAll('.facade[data-vimeo]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const f = document.createElement('iframe');
      f.src = `https://player.vimeo.com/video/${btn.dataset.vimeo}?autoplay=1&title=0&byline=0&portrait=0&dnt=1`;
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

  // ---- contact form
  const form = document.getElementById('contact-form');
  if (form) {
    const status = form.querySelector('.form-status');
    const email = document.querySelector('.direct-email')?.textContent.trim() || '';
    const say = (html, cls) => { status.innerHTML = html; status.className = `form-status ${cls || ''}`; };

    const params = new URLSearchParams(location.search);
    if (params.has('sent')) { form.classList.add('sent'); say('Thank you — your brief is in. I\'ll reply within two working days.', 'ok'); }

    const mailto = (d) => {
      const body = `Name: ${d.name}\nCompany: ${d.company || '-'}\nProject type: ${d.type}\nTimeline: ${d.timeline}\n\n${d.message}`;
      return `mailto:${email}?subject=${encodeURIComponent(`Project enquiry — ${d.type || 'New project'}`)}&body=${encodeURIComponent(body)}`;
    };

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const d = Object.fromEntries(new FormData(form));
      let bad = null;
      form.querySelectorAll('[aria-invalid]').forEach((el) => el.removeAttribute('aria-invalid'));
      form.querySelector('fieldset').classList.remove('fieldset-invalid');
      const need = (name, ok) => { if (!ok) { const el = form.elements[name]; if (el && el.setAttribute) el.setAttribute('aria-invalid', 'true'); bad = bad || name; } };
      need('name', d.name && d.name.trim());
      need('email', /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(d.email || ''));
      if (!d.type) { form.querySelector('fieldset').classList.add('fieldset-invalid'); bad = bad || 'type'; }
      need('message', d.message && d.message.trim().length > 9);
      if (bad) {
        say('Please fill in the highlighted fields — name, a valid email, project type, and a few lines about the project.', 'err');
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
        say('Thank you — your brief is in. I\'ll reply within two working days.', 'ok');
      } catch (err) {
        btn.disabled = false;
        say(`The form couldn't send just now. <a href="${mailto(d)}">Send it by email instead</a> — your message is already filled in.`, 'err');
      }
    });
  }

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
