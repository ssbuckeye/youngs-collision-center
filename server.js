const path = require('path');
const express = require('express');
const nodemailer = require('nodemailer');

const app = express();
const PORT = process.env.PORT || 3000;

app.disable('x-powered-by');
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public'), { extensions: ['html'] }));

// ---- Mail transport: Gmail SMTP via an App Password (not the account password) ----
// Required env vars (set these in Railway's dashboard, never commit them):
//   GMAIL_USER          e.g. youngscollision@gmail.com
//   GMAIL_APP_PASSWORD  the 16-character App Password from Google Account > Security
//   TO_EMAIL             where form submissions should land (defaults to GMAIL_USER)
const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: process.env.GMAIL_USER,
    pass: process.env.GMAIL_APP_PASSWORD,
  },
});

const TO_EMAIL = process.env.TO_EMAIL || process.env.GMAIL_USER;

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

    await transporter.sendMail({
      from: `"Young's Collision Center Website" <${process.env.GMAIL_USER}>`,
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

    await transporter.sendMail({
      from: `"Young's Collision Center Website" <${process.env.GMAIL_USER}>`,
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

app.listen(PORT, () => {
  console.log(`Young's Collision Center site listening on port ${PORT}`);
});
