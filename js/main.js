// Site-wide behaviour: mobile menu, sticky top bar, scroll reveal,
// active navigation link and animated key figures.
document.documentElement.classList.add("js");

document.addEventListener("DOMContentLoaded", function () {
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // ---------- Burger menu ----------
  var nav = document.querySelector(".nav");
  var toggle = document.querySelector(".nav-toggle");
  var menu = document.getElementById("nav-menu");

  function setOpen(open) {
    nav.classList.toggle("is-open", open);
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
  }

  if (nav && toggle && menu) {
    toggle.addEventListener("click", function () {
      setOpen(!nav.classList.contains("is-open"));
    });
    menu.addEventListener("click", function (event) {
      if (event.target.tagName === "A") setOpen(false);
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") setOpen(false);
    });
  }

  // ---------- Top bar background once the page scrolls ----------
  var topbar = document.querySelector(".topbar");
  function onScroll() {
    if (topbar) topbar.classList.toggle("is-scrolled", window.scrollY > 24);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  // ---------- Scroll reveal ----------
  // Blocks are only hidden once this code is running (class "reveal-ready"),
  // so the content always shows if a script fails. A block is revealed as soon
  // as its top enters the bottom 90% of the screen, or once it has been
  // scrolled past. Positions are checked on every scroll of any element and,
  // as a safety net, twice a second until every block is shown.
  var pending = Array.prototype.slice.call(document.querySelectorAll(".reveal"));

  function revealInView() {
    var limit = window.innerHeight * 0.9;
    pending = pending.filter(function (el) {
      if (el.getBoundingClientRect().top < limit) {
        el.classList.add("is-visible");
        return false;
      }
      return true;
    });
    if (!pending.length && safetyTimer) {
      clearInterval(safetyTimer);
      safetyTimer = null;
    }
  }

  var safetyTimer = null;
  if (!reduceMotion) {
    document.documentElement.classList.add("reveal-ready");
    var ticking = false;
    var requestReveal = function () {
      if (ticking || !pending.length) return;
      ticking = true;
      window.requestAnimationFrame(function () {
        revealInView();
        ticking = false;
      });
    };
    document.addEventListener("scroll", requestReveal, { passive: true, capture: true });
    window.addEventListener("resize", requestReveal);
    window.addEventListener("load", revealInView);
    safetyTimer = setInterval(revealInView, 500);
    revealInView();
  }

  // ---------- Active link in the navigation ----------
  var links = document.querySelectorAll(".nav-menu a");
  var sections = Array.prototype.map.call(links, function (link) {
    return document.querySelector(link.getAttribute("href"));
  });
  if ("IntersectionObserver" in window) {
    var navObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        links.forEach(function (link) {
          link.classList.toggle("is-active", link.getAttribute("href") === "#" + entry.target.id);
        });
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    sections.forEach(function (section) { if (section) navObserver.observe(section); });
  }

  // ---------- Animated key figures ----------
  function formatNumber(value, decimals) {
    return value.toLocaleString("en-US", {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    });
  }

  function countUp(el) {
    var target = parseFloat(el.dataset.count);
    var decimals = parseInt(el.dataset.decimals || "0", 10);
    var suffix = el.dataset.suffix || "";
    var duration = 1600;
    var start = null;
    function step(time) {
      if (start === null) start = time;
      var t = Math.min((time - start) / duration, 1);
      var eased = 1 - Math.pow(1 - t, 4);
      el.textContent = formatNumber(target * eased, decimals) + suffix;
      if (t < 1) window.requestAnimationFrame(step);
    }
    window.requestAnimationFrame(step);
  }

  var counters = document.querySelectorAll("[data-count]");
  if (!reduceMotion && "IntersectionObserver" in window) {
    var countObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          countUp(entry.target);
          countObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.6 });
    counters.forEach(function (el) { countObserver.observe(el); });
  }
});
