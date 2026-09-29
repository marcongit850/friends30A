(function () {
  var mount = document.getElementById("site-header");
  if (!mount) return;

  var donate = "https://square.link/u/Yzxyi16L";
  var links = [
    ["About", "/about/"],
    ["Our Work", "/our-work/"],
    ["Impact", "/impact/"],
    ["Gallery", "/gallery/"],
    ["Blog", "/blog/"],
    ["Get Involved", "/get-involved/"]
  ];

  function here() {
    var path = location.pathname;
    if (path.length > 1 && path.endsWith("/")) return path;
    if (path === "/" || path === "/index.html") return "/";
    if (path.endsWith("/index.html")) return path.slice(0, -10);
    if (!path.endsWith("/")) return path + "/";
    return path;
  }

  var path = here();
  function current(href) {
    if (href === "/") return path === "/";
    return path === href || path.indexOf(href) === 0;
  }

  var nav = links.map(function (item) {
    var attr = current(item[1]) ? ' aria-current="page"' : "";
    return '<a href="' + item[1] + '"' + attr + ">" + item[0] + "</a>";
  }).join("");

  mount.innerHTML =
    '<a class="skip" href="#main">Skip to content</a>' +
    '<div class="site-header"><div class="header-inner">' +
    '<a class="brand" href="/">' +
    '<img src="/images/logo.png" alt="" width="512" height="341">' +
    '<span><span class="brand-kicker">Friends of</span><span class="brand-name">Scenic 30A</span></span>' +
    "</a>" +
    '<button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">Menu</button>' +
    '<nav id="site-nav" class="site-nav" aria-label="Primary">' +
    nav +
    '<a class="nav-member" href="/membership/"' + (current("/membership/") ? ' aria-current="page"' : "") + ">Membership</a>" +
    '<a class="nav-donate" href="' + donate + '" target="_blank" rel="noopener noreferrer">Donate</a>' +
    "</nav></div></div>";
})();
