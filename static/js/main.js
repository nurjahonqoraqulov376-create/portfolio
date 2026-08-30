/* Portfolio uchun kichik vanilla JS — hech qanday kutubxona ishlatilmagan. */

(function () {
  'use strict';

  var root = document.documentElement;

  /*
     Foydalanuvchi tizimida "animatsiyani kamaytirish" yoqilgan bo'lsa, og'ir
     effektlarni umuman ishga tushirmaymiz. CSS o'z tomonidan ham to'xtatadi,
     lekin JS ham bilishi kerak — bo'lmasa matn behuda terilib o'tiraveradi.
  */
  var reduceMotion = false;
  try {
    reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  } catch (e) {}

  var canHover = true;
  try {
    canHover = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  } catch (e) {}

  /* ---------------------------------------------------- mavzu almashtirish */
  var toggle = document.getElementById('theme-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem('theme', next); } catch (e) {}
    });
  }

  /* -------------------------------------------------------- mobil menyu */
  var navToggle = document.getElementById('nav-toggle');
  var nav = document.getElementById('nav');

  if (navToggle && nav) {
    var setNav = function (open) {
      nav.classList.toggle('is-open', open);
      navToggle.setAttribute('aria-expanded', String(open));
      // Menyu ochiq turganda orqadagi sahifa scroll bo'lmasin
      document.body.classList.toggle('is-locked', open);
    };

    navToggle.addEventListener('click', function () {
      setNav(!nav.classList.contains('is-open'));
    });

    // Havolaga bosilsa yopiladi
    nav.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') setNav(false);
    });

    // Escape bilan yopiladi
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('is-open')) {
        setNav(false);
        navToggle.focus();
      }
    });

    // Tashqariga bosilsa yopiladi
    document.addEventListener('click', function (e) {
      if (!nav.classList.contains('is-open')) return;
      if (nav.contains(e.target) || navToggle.contains(e.target)) return;
      setNav(false);
    });

    // Ekran kattalashsa (menyu desktop ko'rinishiga o'tsa) holatni tozalaymiz
    window.addEventListener('resize', function () {
      if (window.innerWidth > 760 && nav.classList.contains('is-open')) setNav(false);
    });
  }

  /* ------------------------------------------------- header soyasi (scroll) */
  var header = document.getElementById('site-header');
  if (header) {
    var onScroll = function () {
      header.classList.toggle('is-scrolled', window.scrollY > 8);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* ------------------------- ko'rinishga kirganda paydo bo'lish + skill bar */
  var reveals = document.querySelectorAll('.reveal');
  var bars = document.querySelectorAll('.skill-bar > i');

  var fillBar = function (bar) {
    bar.style.width = (bar.dataset.percent || 0) + '%';
  };

  if ('IntersectionObserver' in window) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        entry.target.querySelectorAll('.skill-bar > i').forEach(fillBar);
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

    reveals.forEach(function (el) { observer.observe(el); });
  } else {
    // Eski brauzerlar: shunchaki hammasini ko'rsatamiz
    reveals.forEach(function (el) { el.classList.add('is-visible'); });
    bars.forEach(fillBar);
  }

  // Ko'rinish maydonidan tashqarida qolgan barlarni ham to'ldiramiz
  window.setTimeout(function () { bars.forEach(fillBar); }, 1200);

  /* -------------------------------------------- hero: matnni terish effekti */
  /*
     Server to'liq matnni chiqaradi (qidiruv tizimlari va skrinriderlar uchun),
     biz uni saqlab olib bo'shatamiz va harfma-harf qaytaramiz.
  */
  var typed = document.querySelector('[data-typing]');
  if (typed) {
    var full = (typed.textContent || '').trim();
    var caret = document.createElement('span');
    caret.className = 'caret';
    caret.setAttribute('aria-hidden', 'true');

    if (reduceMotion || !full) {
      typed.textContent = full;
    } else {
      // Matn o'zgarayotganda skrinrider har harfni o'qib ketmasin
      typed.setAttribute('aria-label', full);
      typed.textContent = '';
      typed.parentNode.insertBefore(caret, typed.nextSibling);

      var index = 0;
      var typeNext = function () {
        typed.textContent = full.slice(0, ++index);
        if (index < full.length) {
          // Tirikroq ko'rinsin uchun tezlik biroz o'zgarib turadi
          window.setTimeout(typeNext, 45 + Math.random() * 45);
        }
      };
      window.setTimeout(typeNext, 500);
    }
  }

  /* ------------------------- kartochkada kursor ortidan nur va 3D egilish */
  if (canHover && !reduceMotion) {
    // Formalar tebranmasligi kerak — ularda yozib turishadi
    var cards = document.querySelectorAll('.card:not(form)');
    var frame = null;

    var applyTilt = function (card, event) {
      var rect = card.getBoundingClientRect();
      var x = event.clientX - rect.left;
      var y = event.clientY - rect.top;
      // Markazdan chetlanish: -0.5 … 0.5
      var dx = x / rect.width - 0.5;
      var dy = y / rect.height - 0.5;

      card.style.setProperty('--mx', ((x / rect.width) * 100).toFixed(1) + '%');
      card.style.setProperty('--my', ((y / rect.height) * 100).toFixed(1) + '%');
      card.style.setProperty('--ry', (dx * 7).toFixed(2) + 'deg');
      card.style.setProperty('--rx', (-dy * 7).toFixed(2) + 'deg');
    };

    var reset = function (card) {
      card.style.removeProperty('--rx');
      card.style.removeProperty('--ry');
      card.style.removeProperty('--mx');
      card.style.removeProperty('--my');
    };

    cards.forEach(function (card) {
      card.addEventListener('pointermove', function (event) {
        if (event.pointerType !== 'mouse') return;
        // Har piksel harakatida emas, kadr boshiga bir marta hisoblaymiz
        if (frame) window.cancelAnimationFrame(frame);
        frame = window.requestAnimationFrame(function () { applyTilt(card, event); });
      });
      card.addEventListener('pointerleave', function () { reset(card); });
    });
  }

  /* ------------------------------------------ forma yuborilayotgani belgisi */
  var form = document.querySelector('form[data-loading]');
  if (form) {
    var submitBtn = form.querySelector('button[type="submit"]');

    form.addEventListener('submit', function () {
      if (submitBtn) {
        submitBtn.classList.add('is-loading');
        submitBtn.disabled = true;
      }
    });

    /*
       Foydalanuvchi "orqaga" tugmasi bilan qaytsa, brauzer sahifani keshdan
       tiklaydi va tugma abadiy bloklangan holda qolib ketishi mumkin.
    */
    window.addEventListener('pageshow', function () {
      if (submitBtn) {
        submitBtn.classList.remove('is-loading');
        submitBtn.disabled = false;
      }
    });
  }
})();
