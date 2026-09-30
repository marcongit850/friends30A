(function () {
  var mount = document.getElementById("site-header");
  if (!mount) return;

  function here() {
    var path = location.pathname;
    if (path.length > 1 && path.endsWith("/")) return path;
    if (path === "/" || path === "/index.html") return "/";
    if (path.endsWith("/index.html")) return path.slice(0, -10);
    if (!path.endsWith("/")) return path + "/";
    return path;
  }

  var SHOP_STOREFRONT = "https://shop.friendsofscenic30a.org/";

  function isShopPage(path) {
    return path === "/shop/" || path.indexOf("/shop/") === 0;
  }

  function applyLogo() {
    if (!isShopPage(here())) return;
    var brand = mount.querySelector("a.brand");
    if (!brand) return;
    brand.setAttribute("href", SHOP_STOREFRONT);
  }

  function markCurrent() {
    var path = here();
    var links = mount.querySelectorAll("a[href]");
    for (var i = 0; i < links.length; i++) {
      var href = links[i].getAttribute("href");
      if (!href || href.charAt(0) !== "/") continue;
      var current = href === "/" ? path === "/" : path === href || path.indexOf(href) === 0;
      if (current) links[i].setAttribute("aria-current", "page");
    }
  }

  fetch("/includes/header.html")
    .then(function (response) {
      if (!response.ok) throw new Error("header");
      return response.text();
    })
    .then(function (html) {
      mount.innerHTML = html;
      applyLogo();
      markCurrent();
      document.dispatchEvent(new Event("site-header-ready"));
    });
})();
