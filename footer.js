(function () {
  var mount = document.getElementById("site-footer");
  if (!mount) return;

  var donate = "https://square.link/u/Yzxyi16L";
  mount.innerHTML =
    '<footer class="site-footer">' +
    '<div class="footer-grid">' +
    "<div>" +
    "<h2>Friends of Scenic 30A</h2>" +
    '<address class="address"><a href="https://www.google.com/maps/search/?api=1&amp;query=877+N+County+Hwy+393,+Santa+Rosa+Beach,+FL+32459" target="_blank" rel="noopener noreferrer">Friends of Scenic 30A<br>877 N County Hwy 393<br>Santa Rosa Beach, FL 32459</a></address>' +
    '<p class="socials"><a href="https://www.facebook.com/fof30a" target="_blank" rel="noopener noreferrer">Facebook</a>' +
    '<a href="https://nextdoor.com/page/friends-of-scenic-30a-santa-rosa-beach-fl/" target="_blank" rel="noopener noreferrer">Nextdoor</a></p>' +
    "</div>" +
    "<div><h2>Explore</h2><ul>" +
    "<li><a href=\"/about/\">About Us</a></li>" +
    "<li><a href=\"/our-work/\">Our Work</a></li>" +
    "<li><a href=\"/impact/\">Our Impact</a></li>" +
    "<li><a href=\"/gallery/\">Gallery</a></li>" +
    "<li><a href=\"/blog/\">Blog</a></li>" +
    "</ul></div>" +
    "<div><h2>Get Involved</h2><ul>" +
    "<li><a href=\"/membership/\">Become a Member</a></li>" +
    '<li><a href="' + donate + '" target="_blank" rel="noopener noreferrer">Donate</a></li>' +
    "<li><a href=\"/get-involved/\">Volunteer</a></li>" +
    "<li><a href=\"/contact/\">Contact Us</a></li>" +
    "</ul></div>" +
    "<div><h2>Scenic 30A Resources</h2><ul>" +
    '<li><a href="https://30a.com/" target="_blank" rel="noopener noreferrer">30A</a></li>' +
    '<li><a href="https://www.byways.org/" target="_blank" rel="noopener noreferrer">America\'s Byways</a></li>' +
    '<li><a href="https://www.visitsouthwalton.com/" target="_blank" rel="noopener noreferrer">Beaches of South Walton</a></li>' +
    '<li><a href="https://floridascenichighways.com/" target="_blank" rel="noopener noreferrer">Florida Scenic Highways Program</a></li>' +
    '<li><a href="https://www.visitflorida.com/" target="_blank" rel="noopener noreferrer">Visit Florida</a></li>' +
    '<li><a href="https://www.waltonareachamber.com/" target="_blank" rel="noopener noreferrer">Walton Area Chamber of Commerce</a></li>' +
    '<li><a href="https://sowal.com/" target="_blank" rel="noopener noreferrer">South Walton</a></li>' +
    "</ul></div>" +
    "</div>" +
    '<div class="legal">' +
    "<span>© 2026 Friends of Scenic 30A. All Rights Reserved.</span>" +
    '<a href="/privacy-policy/">Privacy Policy</a>' +
    '<a href="/accessibility/">Accessibility</a>' +
    '<a href="/terms/">Terms</a>' +
    "</div></footer>";
})();
