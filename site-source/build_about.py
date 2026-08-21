import pathlib
from partials import head, header, footer, PHONE_TEL, PHONE_DISPLAY

body = f'''
{header("about.html")}

<section class="page-hero">
  <img class="bg" src="assets/images/IMG_2059.jpg" alt="Young's Collision Center shop front, Lancaster, Ohio">
  <div class="container">
    <div class="breadcrumb"><a href="index.html">Home</a> / About</div>
    <h1>Our Story</h1>
    <p>Two generations of the Young family, one shop, and a reputation for going above and beyond
      &mdash; since 1985.</p>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="about-grid">
      <div class="about-copy">
        <div class="eyebrow">The Founder</div>
        <h2>It Started With a Fixer</h2>
        <p class="text-gray">Gary Young was a fixer. He liked to fix things &mdash; it started on the
          maintenance crew at Alten's, a foundry here in Lancaster. From there he moved on to fixing up
          homes and renting them out, and eventually to fixing up old cars in his own garage. Over the
          years he restored two '56 Chevys, a '60 Corvette, and a '68 Hurst/Olds.</p>
        <p class="text-gray">Eventually Gary got the idea to make that his full-time job. In 1985 he
          rented a place on Kinzler Ave. &mdash; just down and across the street from where the shop
          sits today &mdash; and Young's Collision Center was born.</p>
      </div>
      <div>
        <img src="assets/images/gary_corvette.jpg" alt="Gary Young taking the first drive of a '60 Corvette he restored for a friend">
        <p class="text-gray" style="font-size:13px;margin-top:10px;">Gary Young taking the '60 Corvette
          he restored for a friend out for its first drive &mdash; a project years in the making.</p>
      </div>
    </div>
  </div>
</section>

<section class="section section-tight" style="background:var(--gray-100);">
  <div class="container">
    <div class="about-grid">
      <div class="about-copy">
        <div class="eyebrow">A Reputation, Built One Car at a Time</div>
        <h2>The Place You Could Take Your Car</h2>
        <p class="text-gray">Business wasn't booming at first, but Gary's reputation for going above
          and beyond for his customers generated a steady, consistent amount of work. Young's became
          known around Lancaster as the place you could take your car for a repair and Gary would work
          with you.</p>
        <p class="text-gray">That approach continued for 11 years, until his son Jeff took over the
          business and Gary retired &mdash; though retirement for Gary meant something a little
          different. Not a day went by that he couldn't be found working on a new fixer-upper in the
          back of the shop.</p>
      </div>
      <div class="about-copy">
        <div class="eyebrow">The Next Generation</div>
        <h2>Jeff Continues the Tradition</h2>
        <p class="text-gray">Jeff Young has been running Young's Collision Center for over 30 years
          now, and he still honors the commitment his dad made when he started the business. Jeff is
          known across the city and county for living up to his word &mdash; so much so that Young's
          Collision Center has become the highest-rated body shop in the area.</p>
        <p class="text-gray">Jeff guarantees every repair that leaves the shop, and just like his dad
          before him, goes above and beyond for every customer who walks through the door.</p>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="eyebrow center">40+ Years in Lancaster</div>
    <h2 class="center">How We Got Here</h2>
    <div style="max-width:640px;margin:32px auto 0;">
      <ul class="timeline">
        <li><strong>1985</strong>Gary Young rents a small space on Kinzler Ave. and opens Young's
          Collision Center, bringing a lifetime of fixing homes, cars, and everything in between to
          the auto body business.</li>
        <li><strong>Early Years</strong>Gary builds a reputation for going above and beyond &mdash;
          Young's becomes known as the shop that works with you, not just on your car.</li>
        <li><strong>1996</strong>After 11 years at the helm, Gary hands the business to his son, Jeff,
          and retires &mdash; though he never really stops working, restoring cars in the back of the
          shop for years to come.</li>
        <li><strong>PPG Certified</strong>Recognized as a PPG Certified Collision Repair Center for our
          refinishing quality and process standards.</li>
        <li><strong>Today</strong>Jeff has run Young's for over 30 years, guarantees every repair, and
          has built it into the highest-rated body shop in the area &mdash; still family owned, still
          doing right by the people of Lancaster.</li>
      </ul>
    </div>
  </div>
</section>

<section class="section section-tight" style="background:var(--gray-100);">
  <div class="container">
    <div class="about-grid">
      <div>
        <img src="assets/images/IMG_2061.jpg" alt="Young's Collision Center shop building">
      </div>
      <div class="about-copy">
        <div class="eyebrow">Our Shop</div>
        <h2>Come See Us at 940 Kinzler Ave.</h2>
        <p class="text-gray">We're located right here in Lancaster, with a full collision repair
          facility set up to handle everything from a quick estimate to a full frame-off rebuild.
          Stop by during business hours &mdash; we're always happy to take a look and talk through
          what your vehicle needs.</p>
        <a class="btn btn-outline-dark" href="contact.html">Get Directions &amp; Hours</a>
      </div>
    </div>
  </div>
</section>

<div class="cta-band">
  <div class="container">
    <h2>Let's Get Your Vehicle Fixed Right</h2>
    <p>Free estimates, honest rates, and a team that treats you like family.</p>
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
    "About Us | Young's Collision Center — Lancaster, Ohio",
    "Family owned and operated in Lancaster, Ohio since 1985. Meet Gary and Jeff Young and learn the story behind Young's Collision Center's 40+ years serving the local community.",
    "/about/"
) + body

pathlib.Path('/home/claude/site_deploy/public/about.html').write_text(html)
print("wrote about.html")
