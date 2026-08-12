/* Portfolio uchun kichik vanilla JS — hech qanday kutubxona ishlatilmagan. */

(function () {
  'use strict';

  /* ---------------------------------------------------- mavzu almashtirish */
  var toggle = document.getElementById('theme-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      try { localStorage.setItem('theme', next); } catch (e) {}
    });
  }

  /* -------------------------------------------------------- mobil menyu */
  var navToggle = document.getElementById('nav-toggle');
  var nav = document.getElementById('nav');
  if (navToggle && nav) {
    navToggle.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      navToggle.setAttribute('aria-expanded', String(open));
    });
    nav.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') {
        nav.classList.remove('is-open');
        navToggle.setAttribute('aria-expanded', 'false');
      }
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

  /* ------------------------------------------ forma yuborilayotgani belgisi */
  var form = document.querySelector('form[data-loading]');
  if (form) {
    form.addEventListener('submit', function () {
      var btn = form.querySelector('button[type="submit"]');
      if (btn) {
        btn.disabled = true;
        btn.dataset.label = btn.textContent;
        btn.textContent = '…';
      }
    });
  }
})();
