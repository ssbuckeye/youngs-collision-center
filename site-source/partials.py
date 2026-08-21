PHONE_DISPLAY = "(740) 653-2431"
PHONE_TEL = "+17406532431"
EMAIL = "youngscollision@gmail.com"
ADDRESS_LINE1 = "940 Kinzler Ave."
ADDRESS_LINE2 = "Lancaster, OH 43130"

NAV_ITEMS = [
    ("Home", "index.html"),
    ("Services", "services.html"),
    ("About", "about.html"),
    ("Contact", "contact.html"),
]

SITE_JS = '''
<script>
(function(){
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.querySelector('.main-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function(){
      var open = nav.classList.toggle('is-open');
      toggle.classList.toggle('is-open', open);
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      document.body.style.overflow = open ? 'hidden' : '';
    });
    nav.querySelectorAll('a').forEach(function(a){
      a.addEventListener('click', function(){
        nav.classList.remove('is-open');
        toggle.classList.remove('is-open');
        document.body.style.overflow = '';
      });
    });
  }
})();
</script>
'''

def head(title, description, canonical_path, extra=""):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="https://youngscollisioncenter.com{canonical_path}">
<link rel="icon" href="assets/favicon/favicon.ico" sizes="any">
<link rel="icon" type="image/svg+xml" href="assets/favicon/Youngs_Favicon_Icon.svg">
<link rel="apple-touch-icon" href="assets/favicon/apple-touch-icon.png">
<link rel="stylesheet" href="styles.css">
{extra}</head>
<body>'''

def header(active):
    links = []
    for label, href in NAV_ITEMS:
        cls = ' class="active"' if href == active else ''
        links.append(f'<li><a href="{href}"{cls}>{label}</a></li>')
    links_html = "\n          ".join(links)
    return f'''<header class="site-header">
  <div class="container">
    <a class="brand" href="index.html" aria-label="Young's Collision Center — Home">
      <img src="assets/logo/Youngs_Logo_Horizontal.svg" alt="Young's Collision Center">
    </a>
    <nav class="main-nav" id="mainNav">
      <ul>
        {links_html}
        <li class="nav-cta"><a class="btn btn-primary btn-block" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a></li>
      </ul>
    </nav>
    <a class="btn btn-primary nav-call" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a>
    <div class="header-actions-mobile">
      <a class="nav-call-icon" href="tel:{PHONE_TEL}" aria-label="Call {PHONE_DISPLAY}">&#9742;</a>
      <button class="nav-toggle" aria-label="Open menu" aria-expanded="false" aria-controls="mainNav"><span></span></button>
    </div>
  </div>
</header>'''

def footer():
    return f'''<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand">
        <img src="assets/logo/Youngs_Logo_Horizontal_Reversed.svg" alt="Young's Collision Center" style="height:44px;">
        <p>Family-owned collision repair in Lancaster, Ohio since 1985. Quality work, honest rates, and a lifetime warranty on every repair.</p>
      </div>
      <div>
        <h4>Site</h4>
        <ul>
          <li><a href="index.html">Home</a></li>
          <li><a href="services.html">Services</a></li>
          <li><a href="about.html">About</a></li>
          <li><a href="contact.html">Contact</a></li>
          <li><a href="authorization-form.html">Authorization Form</a></li>
        </ul>
      </div>
      <div>
        <h4>Contact</h4>
        <ul>
          <li><a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></li>
          <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
          <li>{ADDRESS_LINE1}<br>{ADDRESS_LINE2}</li>
        </ul>
      </div>
      <div>
        <h4>Hours</h4>
        <ul>
          <li>Mon&ndash;Thu: 8am&ndash;5pm</li>
          <li>Friday: 8am&ndash;4pm</li>
          <li>Sat&ndash;Sun: Closed</li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>&copy; <span id="year"></span> Young's Collision Center. All rights reserved.</span>
      <span>940 Kinzler Ave., Lancaster, OH 43130</span>
    </div>
  </div>
</footer>
<script>document.getElementById('year').textContent = new Date().getFullYear();</script>
{SITE_JS}'''
