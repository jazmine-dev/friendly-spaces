/* Friendly Spaces — shared behaviour: nav, language switch, scroll animations, forms. */
(function () {
  var body = document.body;
  var lang = body.getAttribute('data-lang') || 'en';
  var alternates = {};
  (body.getAttribute('data-alternates') || '').split(' ').forEach(function (pair) {
    var i = pair.indexOf(':');
    if (i > 0) alternates[pair.slice(0, i)] = pair.slice(i + 1);
  });

  /* ---- mobile nav ---- */
  var burger = document.getElementById('nav-burger');
  var menu = document.getElementById('nav-menu');
  if (burger && menu) {
    function setMenu(open) {
      menu.classList.toggle('open', open);
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    }
    burger.addEventListener('click', function () { setMenu(!menu.classList.contains('open')); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && menu.classList.contains('open')) { setMenu(false); burger.focus(); }
    });
    document.addEventListener('click', function (e) {
      if (menu.classList.contains('open') && !e.target.closest('#nav')) setMenu(false);
    });
  }

  /* ---- language: switcher links + remembered choice + first-visit auto-detect ---- */
  var LS = 'fs_lang';
  function safeGet() { try { return localStorage.getItem(LS); } catch (e) { return null; } }
  function safeSet(v) { try { localStorage.setItem(LS, v); } catch (e) {} }
  function pathFor(target) {
    var url = alternates[target];
    if (url) { try { return new URL(url).pathname; } catch (e) {} }
    return target === 'en' ? '/' : '/' + target + '/';
  }
  document.querySelectorAll('[data-lang]').forEach(function (a) {
    var target = a.getAttribute('data-lang');
    if (!a.matches('a')) return;
    a.setAttribute('href', pathFor(target));
    if (target === lang) a.setAttribute('aria-current', 'true');
    a.addEventListener('click', function () { safeSet(target); });
  });
  // First visit only (nothing chosen yet): if the browser prefers DE/FR/IT and this
  // English page exists in that language, go there. An explicit click on the language
  // switcher is remembered and stops the auto-detect for good; direct links to any
  // language are always respected.
  if (!safeGet() && lang === 'en') {
    var pref = (navigator.language || '').slice(0, 2).toLowerCase();
    if (['de', 'fr', 'it'].indexOf(pref) >= 0 && alternates[pref]) {
      location.replace(pathFor(pref));
      return;
    }
  }

  /* ---- forms (Netlify Forms on the app host; blind cross-origin send like the native app) ---- */
  document.querySelectorAll('form[data-netlify-form]').forEach(function (form) {
    var status = form.querySelector('.form-status');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (form.querySelector('.hp input') && form.querySelector('.hp input').value) return; // honeypot
      var btn = form.querySelector('button[type="submit"]');
      if (btn) btn.disabled = true;
      if (status) { status.textContent = form.getAttribute('data-sending') || 'Sending…'; status.className = 'form-status'; }
      var data = new URLSearchParams(new FormData(form));
      data.set('form-name', form.getAttribute('data-netlify-form'));
      data.set('page_language', lang);
      fetch(form.getAttribute('action'), { method: 'POST', mode: 'no-cors', credentials: 'omit',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: data.toString() })
        .then(function () {
          form.reset();
          if (status) { status.textContent = form.getAttribute('data-success') || 'Thanks — we will reply soon.'; status.className = 'form-status ok'; }
        })
        .catch(function () {
          if (status) { status.textContent = form.getAttribute('data-error') || 'Something went wrong. Please email hello@friendlyspaces.ch.'; status.className = 'form-status err'; }
        })
        .finally(function () { if (btn) btn.disabled = false; });
    });
  });

  /* ---- map embeds: opt-in interaction so the map never traps page scrolling ---- */
  document.querySelectorAll('iframe[data-guard]').forEach(function (frame) {
    var box = frame.parentElement;
    var guard = document.createElement('button');
    guard.type = 'button'; guard.className = 'map-guard';
    var label = document.createElement('span');
    label.textContent = frame.getAttribute('data-guard');
    guard.appendChild(label);
    box.appendChild(guard);
    guard.addEventListener('click', function () { guard.hidden = true; });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        if (!entries[0].isIntersecting) guard.hidden = false; // re-arm once the map has scrolled away
      }, { threshold: 0 }).observe(box);
    }
  });

  /* ---- scroll animations ---- */
  function animate() {
    var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduced || !window.gsap) {
      document.querySelectorAll('.rv').forEach(function (el) { el.style.opacity = 1; el.style.transform = 'none'; });
      document.querySelectorAll('.hs-venue').forEach(function (el) { el.style.opacity = 1; });
      document.querySelectorAll('.hs-profile').forEach(function (el) { el.style.opacity = 1; el.style.transform = 'none'; });
      return;
    }
    gsap.registerPlugin(ScrollTrigger);
    if (window.Lenis) {
      var lenis = new Lenis({ lerp: 0.11 });
      document.documentElement.classList.add('lenis', 'lenis-smooth');
      lenis.on('scroll', ScrollTrigger.update);
      gsap.ticker.add(function (t) { lenis.raf(t * 1000); });
      gsap.ticker.lagSmoothing(0);
    }

    if (document.querySelector('.hero-line > span')) {
      gsap.from('.hero-line > span', { yPercent: 110, duration: 0.9, ease: 'power3.out', stagger: 0.12, delay: 0.1 });
    }
    if (document.querySelector('.hero-visual')) {
      gsap.fromTo('.hero-visual', { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 1, ease: 'power3.out', delay: 0.5 });
      gsap.to('.hero-visual', { y: 70, ease: 'none', scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true } });
      gsap.to('.hero-grid > div:first-child', { y: -30, ease: 'none', scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true } });
    }
    /* hero phone: city map with pins, then the venue profile slides up on load like the app's sheet */
    if (document.querySelector('.hero-phone .hs-city')) {
      gsap.set('.hs-venue', { xPercent: -50, yPercent: -50, transform: 'none', opacity: 0, scale: 0 });
      gsap.set('.hs-profile', { opacity: 1, yPercent: 100, transform: 'none' });
      // plays once the phone is actually in view: immediately on desktop, on scroll-in on phones
      var heroIntro = gsap.timeline({ paused: true, delay: 0.6 });
      ScrollTrigger.create({ trigger: '.hero-phone', start: 'top 60%', once: true, onEnter: function () { heroIntro.play(); } });
      heroIntro.to('.hs-venue', { opacity: 1, scale: 1, ease: 'back.out(2)', duration: 0.45, stagger: 0.12 })
        .to('.hs-profile', { yPercent: 0, ease: 'power3.out', duration: 0.8 }, '+=0.5');
      window.__heroIntro = heroIntro;
      // background skin keeps its slow zoom on scroll
      gsap.fromTo('.hero-map-layer', { scale: 1.04 }, { scale: 1.12, ease: 'none', scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true } });
    }
    if (document.querySelector('.hero .sticker')) {
      gsap.from('.hero .sticker', { scale: 0, rotate: 30, duration: 0.6, ease: 'back.out(2.5)', delay: 1.1 });
      gsap.to('.hero .sticker', { rotate: 4, ease: 'none', scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true } });
    }
    if (document.getElementById('cue')) {
      gsap.to('#cue', { opacity: 0, ease: 'none', scrollTrigger: { trigger: '.hero', start: 'top top', end: '18% top', scrub: true } });
    }

    document.querySelectorAll('.sq-draw path').forEach(function (p) {
      var len = p.getTotalLength();
      p.style.strokeDasharray = len;
      p.style.strokeDashoffset = len;
      gsap.to(p, { strokeDashoffset: 0, duration: 1.1, ease: 'power2.out', scrollTrigger: { trigger: p.closest('svg'), start: 'top 85%' } });
    });

    var scrub = document.getElementById('scrub');
    if (scrub) {
      var walker = document.createTreeWalker(scrub, NodeFilter.SHOW_TEXT), nodes = [];
      while (walker.nextNode()) nodes.push(walker.currentNode);
      nodes.forEach(function (node) {
        var frag = document.createDocumentFragment();
        node.textContent.split(/(\s+)/).forEach(function (part) {
          if (!part) return;
          if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
          var s = document.createElement('span'); s.className = 'w'; s.textContent = part; frag.appendChild(s);
        });
        node.parentNode.replaceChild(frag, node);
      });
      gsap.to(scrub.querySelectorAll('.w'), { opacity: 1, stagger: 0.06, scrollTrigger: { trigger: scrub.closest('section'), start: 'top 70%', end: 'bottom 75%', scrub: true } });
    }

    gsap.utils.toArray('.rv').forEach(function (el) {
      gsap.to(el, { opacity: 1, y: 0, duration: 0.85, ease: 'power3.out', scrollTrigger: { trigger: el, start: 'top 86%' } });
    });


    /* phone: the map zooms in as the phone passes, and the pins drop onto it */
    if (document.querySelector('#phone .screen')) {
      gsap.set('#phone .pin', { xPercent: -50, yPercent: -50, transform: 'none' });
      gsap.from('#phone .pin', { y: -80, scale: 0, opacity: 0, duration: 0.8, ease: 'bounce.out', stagger: 0.16,
        scrollTrigger: { trigger: '#phone', start: 'top 72%' } });
    }

    /* flower photos bloom open instead of just fading in */
    gsap.utils.toArray('.flower-photo').forEach(function (el) {
      gsap.from(el, { scale: 0.25, rotate: -14, transformOrigin: '50% 50%', duration: 1.1, ease: 'back.out(1.4)',
        scrollTrigger: { trigger: el, start: 'top 85%' } });
    });

    /* melting backgrounds (sections marked data-bg): the page colour tweens instead of hard band edges */
    var bands = gsap.utils.toArray('[data-bg]');
    if (bands.length) {
      var tints = { lilac: '#D2D1E9', pink: '#F4DDFF', marigold: '#F2B33D', cream: '#F8F5EF' };
      document.documentElement.classList.add('melt');
      var melt = function (name) { gsap.to(document.body, { backgroundColor: tints[name] || tints.cream, duration: 0.8, ease: 'power2.out', overwrite: true }); };
      bands.forEach(function (sec) {
        var name = sec.getAttribute('data-bg');
        ScrollTrigger.create({ trigger: sec, start: 'top 60%', end: 'bottom 40%',
          onEnter: function () { melt(name); }, onEnterBack: function () { melt(name); },
          onLeave: function () { melt('cream'); }, onLeaveBack: function () { melt('cream'); } });
      });
    }
  }
  if (document.readyState === 'complete') animate(); else window.addEventListener('load', animate);
})();
