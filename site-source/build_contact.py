import pathlib
from partials import head, header, footer, PHONE_TEL, PHONE_DISPLAY, EMAIL, ADDRESS_LINE1, ADDRESS_LINE2
from contact_form_js import FORM_JS

MAP_SRC = "https://www.google.com/maps?q=940+Kinzler+Ave,+Lancaster,+OH+43130&output=embed"

FORM_HTML = f'''<div class="form-card">
  <h3 style="margin-bottom:4px;">Request a Free Estimate</h3>
  <p class="text-gray" style="font-size:14px;margin-bottom:20px;">Tell us a bit about your vehicle and
    what happened &mdash; we'll get back to you shortly.</p>
  <form id="leadForm" action="/api/contact" method="POST">
    <input type="text" name="company" tabindex="-1" autocomplete="off" style="position:absolute;left:-9999px;" aria-hidden="true">
    <div class="form-grid-2">
      <div class="form-row">
        <label for="name">Full Name</label>
        <input type="text" id="name" name="name" required>
      </div>
      <div class="form-row">
        <label for="phone">Phone Number</label>
        <input type="tel" id="phone" name="phone" required>
      </div>
    </div>
    <div class="form-row">
      <label for="email">Email Address</label>
      <input type="email" id="email" name="email" required>
    </div>
    <div class="form-row">
      <label for="vehicle">Vehicle (Year / Make / Model)</label>
      <input type="text" id="vehicle" name="vehicle" placeholder="e.g. 2019 Honda Accord">
    </div>
    <div class="form-row">
      <label for="message">Tell Us What Happened</label>
      <textarea id="message" name="message" required placeholder="Describe the damage or the service you need..."></textarea>
    </div>
    <button type="submit" class="btn btn-primary btn-block">Send Message</button>
    <div id="formStatus" class="form-status"></div>
    <p class="form-note">Prefer to talk it through? Call us directly at
      <a href="tel:{PHONE_TEL}" style="color:var(--red);font-weight:700;">{PHONE_DISPLAY}</a>.</p>
  </form>
</div>'''

body = f'''
{header("contact.html")}

<section class="page-hero">
  <img class="bg" src="assets/images/IMG_2071.jpg" alt="Young's Collision Center parking lot and shop">
  <div class="container">
    <div class="breadcrumb"><a href="index.html">Home</a> / Contact</div>
    <h1>Get In Touch</h1>
    <p>Free estimates, straight answers, and a team that's happy to help &mdash; call, email, or send
      us your info below.</p>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="contact-layout">
      <div>
        <ul class="info-list">
          <li>
            <div class="ico">&#9742;</div>
            <div><strong>Call Us</strong><a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></div>
          </li>
          <li>
            <div class="ico">&#9993;</div>
            <div><strong>Email Us</strong><a href="mailto:{EMAIL}">{EMAIL}</a></div>
          </li>
          <li>
            <div class="ico">&#128205;</div>
            <div><strong>Visit Us</strong><span>{ADDRESS_LINE1}<br>{ADDRESS_LINE2}</span></div>
          </li>
          <li>
            <div class="ico">&#128337;</div>
            <div><strong>Hours</strong><span>Mon&ndash;Thu: 8am&ndash;5pm &middot; Fri: 8am&ndash;4pm<br>Sat&ndash;Sun: Closed</span></div>
          </li>
        </ul>
        <iframe class="map-frame" loading="lazy" src="{MAP_SRC}" title="Map to Young's Collision Center"></iframe>
      </div>
      {FORM_HTML}
    </div>
  </div>
</section>

{footer()}
{FORM_JS}
</body>
</html>'''

html = head(
    "Contact Us | Young's Collision Center — Lancaster, Ohio",
    "Contact Young's Collision Center in Lancaster, Ohio for a free collision repair estimate. Call (740) 653-2431 or visit us at 940 Kinzler Ave.",
    "/contact-us/"
) + body

pathlib.Path('/home/claude/site_deploy/public/contact.html').write_text(html)
print("wrote contact.html")
