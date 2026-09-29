(function () {
  function bindMenu() {
    var toggle = document.querySelector(".nav-toggle");
    var nav = document.getElementById("site-nav");
    if (!toggle || !nav || toggle.dataset.bound === "true") return;
    toggle.dataset.bound = "true";
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.textContent = open ? "Close" : "Menu";
    });
    nav.addEventListener("click", function (event) {
      if (event.target.closest("a")) {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.textContent = "Menu";
      }
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.textContent = "Menu";
      }
    });
  }

  if (document.getElementById("site-nav")) bindMenu();
  else document.addEventListener("site-header-ready", bindMenu);

  function bindStrip() {
    var scroller = document.querySelector(".strip-scroller");
    if (!scroller || scroller.dataset.bound === "true") return;
    var strip = scroller.querySelector(".strip");
    var prev = scroller.querySelector(".strip-prev");
    var next = scroller.querySelector(".strip-next");
    if (!strip || !prev || !next) return;
    scroller.dataset.bound = "true";

    function stepSize() {
      var item = strip.querySelector("a");
      if (!item) return strip.clientWidth;
      var styles = window.getComputedStyle(strip);
      var gap = parseFloat(styles.columnGap || styles.gap) || 0;
      return item.getBoundingClientRect().width + gap;
    }

    function update() {
      var max = strip.scrollWidth - strip.clientWidth;
      var overflow = max > 4;
      prev.hidden = !overflow;
      next.hidden = !overflow;
      prev.disabled = strip.scrollLeft <= 4;
      next.disabled = strip.scrollLeft >= max - 4;
    }

    function move(direction) {
      var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      var max = Math.max(0, strip.scrollWidth - strip.clientWidth);
      var left = Math.max(0, Math.min(max, strip.scrollLeft + direction * stepSize()));
      strip.scrollTo({ left: left, behavior: reduce ? "auto" : "smooth" });
    }

    prev.addEventListener("click", function () { move(-1); });
    next.addEventListener("click", function () { move(1); });
    strip.addEventListener("scroll", update, { passive: true });
    scroller.addEventListener("keydown", function (event) {
      if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
      if (event.altKey || event.ctrlKey || event.metaKey) return;
      event.preventDefault();
      move(event.key === "ArrowLeft" ? -1 : 1);
    });
    if (window.ResizeObserver) new ResizeObserver(update).observe(strip);
    else window.addEventListener("resize", update);
    window.addEventListener("load", update);
    update();
  }

  bindStrip();

  var dialog = document.getElementById("lightbox");
  document.querySelectorAll("[data-full]").forEach(function (button) {
    button.addEventListener("click", function () {
      if (!dialog) return;
      var img = dialog.querySelector("img");
      img.src = button.getAttribute("data-full");
      img.alt = button.getAttribute("data-alt") || "";
      dialog.showModal();
    });
  });

  document.querySelectorAll("form[data-form]").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var status = form.querySelector(".form-status");
      var button = form.querySelector("button[type=submit]");
      var data = { kind: form.getAttribute("data-form") };
      new FormData(form).forEach(function (value, key) {
        if (data[key]) {
          data[key] = [].concat(data[key], value);
        } else {
          data[key] = value;
        }
      });
      if (form.getAttribute("data-form") === "volunteer" && !form.querySelector("input[name=interests]:checked")) {
        if (status) status.textContent = "Choose at least one area of interest.";
        return;
      }
      if (button) button.disabled = true;
      if (status) status.textContent = "Sending…";
      fetch("/api/message", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(data)
      }).then(function (response) {
        return response.json().then(function (body) {
          return { ok: response.ok, body: body };
        });
      }).then(function (result) {
        if (result.ok) {
          form.reset();
          if (status) status.textContent = "Thank you. Your message is on its way to Friends of Scenic 30A.";
        } else if (status) {
          status.textContent = (result.body && result.body.error) || "We could not send that message. Please write Friends of Scenic 30A, 877 N County Hwy 393, Santa Rosa Beach, FL 32459.";
        }
      }).catch(function () {
        if (status) status.textContent = "We could not send that message. Please write Friends of Scenic 30A, 877 N County Hwy 393, Santa Rosa Beach, FL 32459.";
      }).finally(function () {
        if (button) button.disabled = false;
      });
    });
  });
})();
