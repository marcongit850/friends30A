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
