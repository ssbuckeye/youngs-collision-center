import pathlib
from partials import head, header, footer, PHONE_TEL, PHONE_DISPLAY

HERO_JS = '''
<script>
(function () {
  function isSmallViewport() { return window.matchMedia('(max-width: 768px)').matches; }
  function prefersReducedData() {
    var conn = navigator.connection || navigator.webkitConnection || navigator.mozConnection;
    if (!conn) return false;
    if (conn.saveData) return true;
    if (conn.effectiveType && /2g/.test(conn.effectiveType)) return true;
    return false;
  }
  function loadAndPlayHero() {
    if (isSmallViewport() || prefersReducedData()) return;
    var video = document.getElementById('heroVideo');
    if (!video) return;
    var sources = video.querySelectorAll('source[data-src]');
    sources.forEach(function (s) { s.src = s.getAttribute('data-src'); });
    video.load();
    video.addEventListener('canplay', function () { video.play().catch(function(){}); }, { once: true });
  }
  if (document.readyState === 'complete') { loadAndPlayHero(); }
  else { window.addEventListener('load', loadAndPlayHero); }
})();
</script>
'''

body = f'''
{header("index.html")}

<section class="hero">
  <img class="hero-poster" src="assets/video/Youngs_Homepage_Hero_poster.jpg" alt="Young's Collision Center shop and team">
  <video id="heroVideo" poster="assets/video/Youngs_Homepage_Hero_poster.jpg" muted playsinline preload="none">
    <source data-src="assets/video/Youngs_Homepage_Hero.webm" type="video/webm">
    <source data-src="assets/video/Youngs_Homepage_Hero.mp4" type="video/mp4">
  </video>
  <div class="hero-content">
    <div class="eyebrow">Lancaster, Ohio &middot; Family Owned Since 1985</div>
    <h1>40+ Years of Quality Collision Repair &amp; Honest, Affordable Rates</h1>
    <p>From minor dents to major collision damage, Young's Collision Center gets your vehicle back on
      the road right &mdash; backed by a lifetime warranty and a team that treats you like family.</p>
    <div class="hero-ctas">
      <a class="btn btn-primary" href="contact.html">Get a Free Estimate</a>
      <a class="btn btn-outline" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a>
    </div>
  </div>
</section>

<div class="trust-bar">
  <div class="container">
    <div class="trust-item"><strong>40+</strong><span>YEARS IN BUSINESS</span></div>
    <div class="trust-item"><strong>Family</strong><span>OWNED &amp; OPERATED</span></div>
    <div class="trust-item"><strong>PPG</strong><span>CERTIFIED REPAIR CENTER</span></div>
    <div class="trust-item"><strong>Lifetime</strong><span>WARRANTY ON REPAIRS</span></div>
  </div>
</div>

<section class="section">
  <div class="container">
    <div class="eyebrow center">Why Choose Us</div>
    <h2 class="center">Quality Work You Can Trust</h2>
    <div class="card-grid" style="margin-top:32px;">
      <div class="card">
        <div class="icon-badge">40+</div>
        <h3>Family Owned</h3>
        <p>Young's Collision Center has been family owned and operated in Lancaster since 1985. Our
          quality work ensures you'll be satisfied &mdash; every repair is backed by a lifetime warranty.</p>
      </div>
      <div class="card">
        <div class="icon-badge">&#128295;</div>
        <h3>Experienced Technicians</h3>
        <p>We service all makes and models, including commercial fleets. If you need help working with
          your insurance company, we have your back every step of the way.</p>
      </div>
      <div class="card">
        <div class="icon-badge">&#128663;</div>
        <h3>Collision Repair</h3>
        <p>No job is too large or too small. From paint touch-ups and dents to major accident repair,
          we're Lancaster's #1 trusted collision center.</p>
      </div>
    </div>
  </div>
</section>

<section class="section section-tight" style="background:var(--gray-100);">
  <div class="container">
    <div class="eyebrow center">What We Do</div>
    <h2 class="center">Full-Service Auto Body Repair</h2>
    <div class="services-grid" style="margin-top:28px;">
      <div class="service-pill"><span class="dot"></span>Collision Repair</div>
      <div class="service-pill"><span class="dot"></span>Fender Repair</div>
      <div class="service-pill"><span class="dot"></span>Dent Removal</div>
      <div class="service-pill"><span class="dot"></span>Paint Repair</div>
      <div class="service-pill"><span class="dot"></span>Paintless Dent Repair</div>
      <div class="service-pill"><span class="dot"></span>Auto Glass Repair</div>
      <div class="service-pill"><span class="dot"></span>Hail Damage Repair</div>
      <div class="service-pill"><span class="dot"></span>Diagnostic Scanning</div>
    </div>
    <div class="center" style="margin-top:30px;">
      <a class="btn btn-outline-dark" href="services.html">View All Services</a>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="eyebrow center">Reviews</div>
    <h2 class="center">What Our Customers Say</h2>
    <div class="testimonial-grid" style="margin-top:32px;">
      <div class="testimonial-card">
        <div class="stars">&#9733;&#9733;&#9733;&#9733;&#9733;</div>
        <p>"Great work, honest, Jeff has fixed several of my vehicles. Always does a great job. Highly
          recommend him and his shop."</p>
        <div class="name">&mdash; Andy Littleton</div>
      </div>
      <div class="testimonial-card">
        <div class="stars">&#9733;&#9733;&#9733;&#9733;&#9733;</div>
        <p>"Went in for an estimate. They were super helpful and will be back to get work done."</p>
        <div class="name">&mdash; Jonathon Wymer</div>
      </div>
      <div class="testimonial-card">
        <div class="stars">&#9733;&#9733;&#9733;&#9733;&#9733;</div>
        <p>"I've taken all my vehicles here when they are in need of collision or rust repair. Quality
          work and impossible to tell where the repair was made."</p>
        <div class="name">&mdash; Rob Wynn Frey</div>
      </div>
    </div>
  </div>
</section>

<div class="cta-band">
  <div class="container">
    <h2>Ready to Get Your Vehicle Looking Like New?</h2>
    <p>Free estimates &mdash; call us or send your info and we'll get right back to you.</p>
    <div class="hero-ctas" style="justify-content:center;">
      <a class="btn btn-primary" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a>
      <a class="btn btn-outline" href="contact.html">Request a Free Estimate</a>
    </div>
  </div>
</div>

{footer()}
{HERO_JS}
</body>
</html>'''

html = head(
    "Young's Collision Center | Auto Body Repair in Lancaster, Ohio",
    "Family-owned collision repair shop in Lancaster, Ohio since 1985. Free estimates, PPG certified, lifetime warranty on all repairs. Call (740) 653-2431.",
    "/"
) + body

pathlib.Path('/home/claude/site_deploy/public/index.html').write_text(html)
print("wrote index.html")
