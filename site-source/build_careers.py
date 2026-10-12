import pathlib
from partials import head, header, footer, PHONE_TEL, PHONE_DISPLAY
from careers_form_js import CAREERS_JS

FORM_HTML = '''<div class="form-card" id="applySection">
  <h3 style="margin-bottom:4px;">Apply Now</h3>
  <p class="text-gray" style="font-size:14px;margin-bottom:20px;" id="generalNote">Don't see the exact
    role you're looking for? We're happy to keep your information on file for the next opening.</p>
  <form id="careersForm" action="/api/careers/apply" method="POST" enctype="multipart/form-data">
    <input type="text" name="company" tabindex="-1" autocomplete="off" style="position:absolute;left:-9999px;" aria-hidden="true">
    <div class="form-row">
      <label for="postingSelect">Position</label>
      <select id="postingSelect" name="postingId">
        <option value="">General Application (no specific role)</option>
      </select>
    </div>
    <div class="form-grid-2">
      <div class="form-row">
        <label for="careersName">Full Name</label>
        <input type="text" id="careersName" name="name" required>
      </div>
      <div class="form-row">
        <label for="careersPhone">Phone Number</label>
        <input type="tel" id="careersPhone" name="phone" required>
      </div>
    </div>
    <div class="form-row">
      <label for="careersEmail">Email Address</label>
      <input type="email" id="careersEmail" name="email" required>
    </div>
    <div class="form-grid-2">
      <div class="form-row">
        <label for="resume">Resume (PDF or Word, required)</label>
        <input type="file" id="resume" name="resume" accept=".pdf,.doc,.docx" required>
      </div>
      <div class="form-row">
        <label for="coverLetter">Cover Letter (optional)</label>
        <input type="file" id="coverLetter" name="coverLetter" accept=".pdf,.doc,.docx">
      </div>
    </div>
    <div class="form-row">
      <label for="careersMessage">Anything Else You'd Like Us to Know (optional)</label>
      <textarea id="careersMessage" name="message" placeholder="Relevant experience, availability, etc."></textarea>
    </div>
    <button type="submit" class="btn btn-primary btn-block">Submit Application</button>
    <div id="careersFormStatus" class="form-status"></div>
    <p class="form-note">Questions first? Call us at
      <a href="tel:{phone_tel}" style="color:var(--red);font-weight:700;">{phone_display}</a>.</p>
  </form>
</div>'''.format(phone_tel=PHONE_TEL, phone_display=PHONE_DISPLAY)

body = f'''
{header("careers.html")}

<section class="page-hero">
  <img class="bg" src="assets/images/IMG_2060.jpg" alt="Young's Collision Center team at work in the shop">
  <div class="container">
    <div class="breadcrumb"><a href="index.html">Home</a> / Careers</div>
    <h1 id="careersHeadline">Join Our Team</h1>
    <p id="careersIntro">We're not always actively hiring, but we're always glad to hear from people
      who care about doing quality work.</p>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="careers-layout">
      <div>
        <div class="eyebrow">Current Openings</div>
        <div id="postingsList">
          <p class="text-gray">Loading current openings&hellip;</p>
        </div>
      </div>
      {FORM_HTML}
    </div>
  </div>
</section>

{footer()}
{CAREERS_JS}
</body>
</html>'''

html = head(
    "Careers | Young's Collision Center — Lancaster, Ohio",
    "Join the team at Young's Collision Center in Lancaster, Ohio. See current openings or send us your resume for future opportunities.",
    "/careers/"
) + body

OUT_DIR = pathlib.Path(__file__).resolve().parent.parent / "public"
(OUT_DIR / "careers.html").write_text(html)
print("wrote careers.html")
