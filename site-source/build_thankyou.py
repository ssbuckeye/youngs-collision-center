import pathlib
from partials import head, header, footer, PHONE_TEL, PHONE_DISPLAY

body = f'''
{header("thank-you.html")}

<section class="section" style="padding-top:100px;padding-bottom:100px;">
  <div class="container center" style="max-width:560px;">
    <div style="width:64px;height:64px;font-size:28px;margin:0 auto 20px;background:var(--red);color:var(--white);border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;">&#10003;</div>
    <h1>Thank You!</h1>
    <p class="text-gray">Your submission has been received. We'll get back to you shortly &mdash; if
      it's urgent, give us a call and we'll pick up.</p>
    <div class="hero-ctas" style="justify-content:center;">
      <a class="btn btn-primary" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a>
      <a class="btn btn-outline-dark" href="index.html">Back to Home</a>
    </div>
  </div>
</section>

{footer()}
</body>
</html>'''

html = head(
    "Thank You | Young's Collision Center",
    "Thank you for contacting Young's Collision Center. We'll be in touch shortly.",
    "/thank-you/"
) + body

pathlib.Path('/home/claude/site_deploy/public/thank-you.html').write_text(html)
print("wrote thank-you.html")
