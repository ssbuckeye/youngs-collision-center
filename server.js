const fs = require('fs');
const path = require('path');
const express = require('express');
const session = require('express-session');

const app = express();
const PORT = process.env.PORT || 3000;

app.disable('x-powered-by');
// Railway terminates HTTPS at its edge and proxies to this app over HTTP;
// trust proxy so secure cookies (below) know the original request was HTTPS.
app.set('trust proxy', 1);
app.use(express.json());

// ---- SEO: preserve the old WordPress site's URL structure ----
// The live site being replaced (WordPress) has exactly 5 pages indexed by
// Google, all with a trailing slash: /, /services/, /contact-us/,
// /thank-you/, /authorization-form/. This site serves pages WITHOUT a
// trailing slash (e.g. /services, /contact), and /contact-us has no
// equivalent path here at all — it was renamed to /contact. Without these
// redirects, every one of those indexed URLs (and any backlink or bookmark
// pointing at them) would 404 the moment the domain switches over, and
// Google would eventually drop them from search results instead of
// transferring their ranking to the new URL. A 301 (permanent redirect)
// is the correct signal to tell Google "this page moved here for good."
const LEGACY_REDIRECTS = {
  '/contact-us': '/contact',
  '/contact-us/': '/contact',
};
app.use((req, res, next) => {
  const target = LEGACY_REDIRECTS[req.path];
  if (target) {
    const qs = req.url.slice(req.path.length);
    return res.redirect(301, target + qs);
  }
  // Strip a trailing slash from any other path (e.g. /services/ -> /services,
  // /thank-you/ -> /thank-you) so every old indexed URL keeps working.
  if (req.path !== '/' && req.path.endsWith('/')) {
    const qs = req.url.slice(req.path.length);
    return res.redirect(301, req.path.slice(0, -1) + qs);
  }
  next();
});

app.use(express.static(path.join(__dirname, 'public'), { extensions: ['html'] }));

// ---- Admin session (careers dashboard login) ----
// Sessions are stored on disk (on the same persistent volume as the careers
// database — see DATA_DIR) instead of in memory. express-session's default
// MemoryStore loses every logged-in session the moment the process restarts,
// which happens on every deploy — so without this, every upload to the site
// silently logs the admin dashboard out, and a mid-edit save would fail with
// "Not logged in" for no obvious reason.
const DATA_DIR = process.env.DATA_DIR || path.join(__dirname, 'data');
const SESSIONS_FILE = path.join(DATA_DIR, 'sessions.json');

class FileSessionStore extends session.Store {
  constructor(filePath) {
    super();
    this.filePath = filePath;
    this.sessions = this._load();
  }
  _load() {
    try {
      if (fs.existsSync(this.filePath)) return JSON.parse(fs.readFileSync(this.filePath, 'utf8'));
    } catch (err) {
      console.error('Session store file is unreadable, starting with no sessions:', err);
    }
    return {};
  }
  _save() {
    try {
      fs.mkdirSync(path.dirname(this.filePath), { recursive: true });
      fs.writeFileSync(this.filePath, JSON.stringify(this.sessions));
    } catch (err) {
      console.error('Could not persist sessions to disk:', err);
    }
  }
  _prune(sid) {
    const entry = this.sessions[sid];
    if (entry && entry.expires && Date.now() > entry.expires) {
      delete this.sessions[sid];
      return true;
    }
    return false;
  }
  get(sid, cb) {
    this._prune(sid);
    const entry = this.sessions[sid];
    cb(null, entry ? entry.session : null);
  }
  set(sid, sessionData, cb) {
    const maxAge = sessionData.cookie && sessionData.cookie.maxAge;
    this.sessions[sid] = { session: sessionData, expires: maxAge ? Date.now() + maxAge : null };
    this._save();
    if (cb) cb();
  }
  destroy(sid, cb) {
    delete this.sessions[sid];
    this._save();
    if (cb) cb();
  }
  touch(sid, sessionData, cb) {
    if (this.sessions[sid]) {
      const maxAge = sessionData.cookie && sessionData.cookie.maxAge;
      this.sessions[sid].expires = maxAge ? Date.now() + maxAge : null;
      this._save();
    }
    if (cb) cb();
  }
}

// SESSION_SECRET should be set in Railway's Variables tab, same as the other
// secrets below — falls back to a derived value so local testing still works
// without extra setup, but that fallback is NOT safe for production.
app.use(session({
  store: new FileSessionStore(SESSIONS_FILE),
  secret: process.env.SESSION_SECRET || `dev-only-insecure-secret-${process.env.GMAIL_USER || 'ycc'}`,
  resave: false,
  saveUninitialized: false,
  cookie: {
    httpOnly: true,
    // Treat it as production (and require HTTPS for the cookie) whenever this
    // looks like a real Railway deployment rather than a local `npm start`.
    secure: !!(process.env.RAILWAY_ENVIRONMENT || process.env.NODE_ENV === 'production'),
    maxAge: 12 * 60 * 60 * 1000, // 12 hours
  },
}));

// ---- Mail: sent through Resend's HTTPS API instead of raw Gmail SMTP ----
// Railway blocks outbound SMTP entirely on Free/Trial/Hobby plans (it's a
// Pro-plan-only feature) — that's the actual reason emails never sent
// regardless of the Gmail App Password; see the Connection-timeout/ETIMEDOUT
// errors that showed up even with a valid password. Resend's API runs over
// plain HTTPS, which isn't affected by that restriction.
//
// Required env var:
//   RESEND_API_KEY     from the Resend dashboard (API Keys)
// Optional:
//   RESEND_FROM_EMAIL   defaults to Resend's shared "onboarding@resend.dev"
//                       test address, which can only deliver to the Resend
//                       account's own registered email. That's fine here as
//                       long as TO_EMAIL below is that same address. Once a
//                       real domain (e.g. youngscollisioncenter.com) is
//                       verified with Resend, set this to an address on it
//                       (e.g. "notifications@youngscollisioncenter.com") to
//                       lift that restriction — no code change needed.
const RESEND_API_KEY = process.env.RESEND_API_KEY;
const RESEND_FROM_EMAIL = process.env.RESEND_FROM_EMAIL || 'onboarding@resend.dev';
if (!RESEND_API_KEY) {
  console.error('RESEND_API_KEY is not set — contact, authorization, and careers emails will fail until it is.');
}

async function sendEmail({ to, subject, html, replyTo, attachments }) {
  const body = {
    from: `Young's Collision Center Website <${RESEND_FROM_EMAIL}>`,
    to: Array.isArray(to) ? to : [to],
    subject,
    html,
  };
  if (replyTo) body.reply_to = replyTo;
  if (attachments && attachments.length) {
    body.attachments = attachments.map((a) => ({
      filename: a.filename,
      content: Buffer.isBuffer(a.content) ? a.content.toString('base64') : a.content,
    }));
  }
  const res = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${RESEND_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const errText = await res.text().catch(() => '');
    throw new Error(`Resend API error ${res.status}: ${errText}`);
  }
  return res.json();
}

const TO_EMAIL = process.env.TO_EMAIL;
if (!TO_EMAIL) {
  console.error('TO_EMAIL is not set — there is no default address for contact/authorization emails to go to.');
}

// ---- Minimal in-memory rate limiter: 5 submissions / 10 minutes per IP ----
// Good enough to blunt casual abuse on a small-business site without adding a dependency.
// Resets on redeploy/restart, which is fine for this use case.
const RATE_WINDOW_MS = 10 * 60 * 1000;
const RATE_MAX = 5;
const hits = new Map();
function isRateLimited(ip) {
  const now = Date.now();
  const recent = (hits.get(ip) || []).filter((t) => now - t < RATE_WINDOW_MS);
  recent.push(now);
  hits.set(ip, recent);
  return recent.length > RATE_MAX;
}

function escapeHtml(value) {
  return String(value || '').replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  }[c]));
}

function clientIp(req) {
  const fwd = req.headers['x-forwarded-for'];
  return (fwd ? fwd.split(',')[0].trim() : null) || req.socket.remoteAddress || 'unknown';
}

// ---- Careers page: postings + applications API, and the admin dashboard that
// manages them. Lives in its own files (careers.js / careers-db.js) to keep
// this file focused on the rest of the site. ----
require('./careers')(app, {
  sendEmail,
  TO_EMAIL,
  escapeHtml,
  clientIp,
  isRateLimited,
});

app.post('/api/contact', async (req, res) => {
  try {
    if (isRateLimited(clientIp(req))) {
      return res.status(429).json({ error: 'Too many requests, please try again later.' });
    }

    const { name, phone, email, vehicle, message, company } = req.body || {};

    // Honeypot: real users never fill this hidden field in. Pretend success so
    // bots don't learn anything, but don't actually send mail.
    if (company) return res.json({ ok: true });

    if (!name || !phone || !email || !message) {
      return res.status(400).json({ error: 'Missing required fields.' });
    }

    await sendEmail({
      to: TO_EMAIL,
      replyTo: email,
      subject: `New Estimate Request from ${name}`,
      html: `
        <h2>New Free Estimate Request</h2>
        <p><strong>Name:</strong> ${escapeHtml(name)}</p>
        <p><strong>Phone:</strong> ${escapeHtml(phone)}</p>
        <p><strong>Email:</strong> ${escapeHtml(email)}</p>
        <p><strong>Vehicle:</strong> ${escapeHtml(vehicle) || 'Not provided'}</p>
        <p><strong>Message:</strong><br>${escapeHtml(message).replace(/\n/g, '<br>')}</p>
        <hr><p style="color:#888;font-size:12px;">Submitted via the contact form on youngscollisioncenter.com</p>
      `,
    });

    res.json({ ok: true });
  } catch (err) {
    console.error('Contact form error:', err);
    res.status(500).json({ error: 'Failed to send message.' });
  }
});

app.post('/api/authorization', async (req, res) => {
  try {
    if (isRateLimited(clientIp(req))) {
      return res.status(429).json({ error: 'Too many requests, please try again later.' });
    }

    const { name, phone, vehicle, signature, company } = req.body || {};

    if (company) return res.json({ ok: true });

    if (!name || !phone || !vehicle || !signature) {
      return res.status(400).json({ error: 'Missing required fields.' });
    }

    await sendEmail({
      to: TO_EMAIL,
      subject: `New Repair Authorization from ${name}`,
      html: `
        <h2>New Repair &amp; Payment Authorization Submitted</h2>
        <p><strong>Name:</strong> ${escapeHtml(name)}</p>
        <p><strong>Phone:</strong> ${escapeHtml(phone)}</p>
        <p><strong>Vehicle:</strong> ${escapeHtml(vehicle)}</p>
        <p><strong>Electronic Signature:</strong> ${escapeHtml(signature)}</p>
        <hr><p style="color:#888;font-size:12px;">Submitted via the authorization form on youngscollisioncenter.com</p>
      `,
    });

    res.json({ ok: true });
  } catch (err) {
    console.error('Authorization form error:', err);
    res.status(500).json({ error: 'Failed to submit authorization.' });
  }
});

// Simple health check Railway (or you) can hit to confirm the service is up.
app.get('/healthz', (req, res) => res.status(200).send('ok'));

const server = app.listen(PORT, () => {
  console.log(`Young's Collision Center site listening on port ${PORT}`);
});

// Railway sends SIGTERM to the old container during every deploy (it's
// swapping in the new one, not reporting a crash). Without a handler, Node
// doesn't react to that signal and `npm start`'s wrapper process ends up
// reporting it as a failed/crashed exit — which is exactly what shows up as
// a "crash" in the Railway dashboard on every single upload, even though
// nothing is actually wrong. Catching the signal and shutting down on our
// own terms (and exiting 0) avoids that false alarm.
function shutdown(signal) {
  console.log(`${signal} received, shutting down gracefully`);
  server.close(() => process.exit(0));
  // Safety net in case something is keeping a connection open — don't let
  // Railway have to SIGKILL us after its own grace period runs out.
  setTimeout(() => process.exit(0), 10000).unref();
}
process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));
