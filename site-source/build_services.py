import pathlib
from partials import head, header, footer, PHONE_TEL, PHONE_DISPLAY

SERVICES = [
    ("&#128663;", "Collision Repair", "From fender-benders to major accident damage, we restore your vehicle's structure and appearance to pre-accident condition."),
    ("&#128296;", "Fender Repair", "Scrapes, dents, and cracked fenders repaired and refinished to seamlessly match the rest of your vehicle."),
    ("&#128295;", "Dent Removal", "Traditional dent repair for deeper dings and damage that paintless methods can't fully correct."),
    ("&#127912;", "Paint Repair", "Precision, color-matched paint work &mdash; from small touch-ups to full panel refinishing."),
    ("&#10024;", "Paintless Dent Repair", "For minor dings and hail dents where the paint is still intact, we can often remove the dent without repainting."),
    ("&#129693;", "Auto Glass Repair", "Windshield chips, cracks, and full glass replacement for all makes and models."),
    ("&#127785;", "Hail Damage Repair", "Storm damage assessed and repaired, with insurance claim assistance every step of the way."),
    ("&#128187;", "Diagnostic Scanning", "Post-repair diagnostic scanning to make sure every electronic system in your vehicle is functioning correctly."),
]

cards = []
for icon, name, desc in SERVICES:
    cards.append(f'''<div class="card">
        <div class="icon-badge">{icon}</div>
        <h3>{name}</h3>
        <p>{desc}</p>
      </div>''')
cards_html = "\n      ".join(cards)

body = f'''
{header("services.html")}

<section class="page-hero">
  <img class="bg" src="assets/images/IMG_2074.jpg" alt="Young's Collision Center, a PPG Certified Collision Repair Center">
  <div class="container">
    <div class="breadcrumb"><a href="index.html">Home</a> / Services</div>
    <h1>Full-Service Auto Body Repair</h1>
    <p>We repair all makes and models, including commercial fleets &mdash; from minor touch-ups to major
      collision damage, backed by a lifetime warranty on every repair.</p>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="eyebrow center">What We Offer</div>
    <h2 class="center">Services We Provide</h2>
    <div class="card-grid" style="margin-top:32px;">
      {cards_html}
    </div>
  </div>
</section>

<section class="section section-tight" style="background:var(--gray-100);">
  <div class="container">
    <div class="about-grid">
      <div>
        <img src="assets/images/IMG_2074.jpg" alt="PPG Certified Collision Repair Center sign at Young's Collision Center">
      </div>
      <div class="about-copy">
        <div class="eyebrow">Certified</div>
        <h2>PPG Certified Collision Repair Center</h2>
        <p class="text-gray">As a PPG Certified Collision Repair Center, we hold ourselves to a higher
          standard of refinishing quality &mdash; using industry-leading paint and repair processes so
          your vehicle's finish matches factory color and quality, every time.</p>
        <p class="text-gray">We also work directly with insurance companies to make the claims process
          as painless as possible, and service fleet vehicles for local businesses.</p>
        <a class="btn btn-primary" href="contact.html">Get a Free Estimate</a>
      </div>
    </div>
  </div>
</section>

<div class="cta-band">
  <div class="container">
    <h2>Not Sure What You Need? Just Ask.</h2>
    <p>Bring it in for a free estimate &mdash; we'll walk you through your options, no pressure.</p>
    <div class="hero-ctas" style="justify-content:center;">
      <a class="btn btn-primary" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a>
      <a class="btn btn-outline" href="contact.html">Request a Free Estimate</a>
    </div>
  </div>
</div>

{footer()}
</body>
</html>'''

html = head(
    "Services | Young's Collision Center — Lancaster, Ohio",
    "Collision repair, fender repair, dent removal, paint repair, paintless dent repair, auto glass, hail damage repair, and diagnostic scanning in Lancaster, Ohio.",
    "/services/"
) + body

pathlib.Path('/home/claude/site_deploy/public/services.html').write_text(html)
print("wrote services.html")
