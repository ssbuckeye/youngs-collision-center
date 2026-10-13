// Careers page: public postings/apply API + a password-gated admin API for
// managing postings and reviewing applications. Mounted onto the main app by
// server.js. See careers-db.js for storage.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const multer = require('multer');
const { ADMIN_PASSWORD } = process.env;

const db = require('./careers-db');

const ALLOWED_MIME = new Set([
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
]);
const ALLOWED_EXT = new Set(['.pdf', '.doc', '.docx']);
const MAX_FILE_BYTES = 8 * 1024 * 1024; // 8MB

const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: MAX_FILE_BYTES, files: 2 },
  fileFilter(req, file, cb) {
    const ext = path.extname(file.originalname || '').toLowerCase();
    if (!ALLOWED_MIME.has(file.mimetype) && !ALLOWED_EXT.has(ext)) {
      cb(new Error('UNSUPPORTED_FILE_TYPE'));
      return;
    }
    cb(null, true);
  },
});

function safeExt(originalName) {
  const ext = path.extname(originalName || '').toLowerCase();
  return ALLOWED_EXT.has(ext) ? ext : '.pdf';
}

function requireAdmin(req, res, next) {
  if (req.session && req.session.isAdmin) return next();
  res.status(401).json({ error: 'Not logged in.' });
}

function timingSafeEqual(a, b) {
  const bufA = Buffer.from(String(a));
  const bufB = Buffer.from(String(b));
  if (bufA.length !== bufB.length) return false;
  return crypto.timingSafeEqual(bufA, bufB);
}

module.exports = function registerCareersRoutes(app, { transporter, TO_EMAIL, GMAIL_USER, escapeHtml, clientIp, isRateLimited }) {
  db.ensureDirs();

  // ---------------------------------------------------------------- public
  app.get('/api/careers/postings', async (req, res) => {
    try {
      const [settings, postings] = await Promise.all([
        db.getSettings(),
        db.listPostings({ publicOnly: true }),
      ]);
      res.json({ settings, postings });
    } catch (err) {
      console.error('careers postings error:', err);
      res.status(500).json({ error: 'Failed to load openings.' });
    }
  });

  app.post('/api/careers/apply', (req, res) => {
    upload.fields([{ name: 'resume', maxCount: 1 }, { name: 'coverLetter', maxCount: 1 }])(req, res, async (err) => {
      if (err) {
        const message = err.message === 'UNSUPPORTED_FILE_TYPE'
          ? 'Please upload your resume as a PDF or Word document.'
          : err.code === 'LIMIT_FILE_SIZE'
            ? 'That file is too large — please keep each file under 8MB.'
            : 'Could not process the uploaded file(s).';
        return res.status(400).json({ error: message });
      }

      try {
        if (isRateLimited(clientIp(req))) {
          return res.status(429).json({ error: 'Too many requests, please try again later.' });
        }

        const { name, email, phone, message, postingId, company } = req.body || {};

        // Honeypot — pretend success so bots learn nothing.
        if (company) return res.json({ ok: true });

        const resumeFile = req.files && req.files.resume && req.files.resume[0];
        const coverLetterFile = req.files && req.files.coverLetter && req.files.coverLetter[0];

        if (!name || !email || !phone || !resumeFile) {
          return res.status(400).json({ error: 'Name, email, phone, and a resume are required.' });
        }

        let postingTitle = null;
        if (postingId) {
          const postings = await db.listPostings();
          const posting = postings.find((p) => p.id === postingId);
          if (posting) postingTitle = posting.title;
        }

        const applicationId = db.newId();
        const uploadDir = db.applicationUploadDir(applicationId);
        fs.mkdirSync(uploadDir, { recursive: true });

        const resumeFilename = `resume${safeExt(resumeFile.originalname)}`;
        fs.writeFileSync(path.join(uploadDir, resumeFilename), resumeFile.buffer);

        let coverLetterFilename = null;
        if (coverLetterFile) {
          coverLetterFilename = `cover-letter${safeExt(coverLetterFile.originalname)}`;
          fs.writeFileSync(path.join(uploadDir, coverLetterFilename), coverLetterFile.buffer);
        }

        await db.createApplication({
          id: applicationId,
          postingId: postingId || null,
          postingTitle,
          name, email, phone, message,
          resumeFile: resumeFilename,
          coverLetterFile: coverLetterFilename,
        });

        const attachments = [{ filename: resumeFile.originalname || 'resume', content: resumeFile.buffer }];
        if (coverLetterFile) {
          attachments.push({ filename: coverLetterFile.originalname || 'cover-letter', content: coverLetterFile.buffer });
        }

        // Who (if anyone) gets notified: the admin-configured address wins,
        // falling back to the site's main contact address if that's left
        // blank, unless the owner has turned notifications off entirely.
        const settings = await db.getSettings();
        const notifyTo = settings.notifyEnabled === false
          ? null
          : (settings.notifyEmail && settings.notifyEmail.trim()) || TO_EMAIL;

        if (notifyTo) {
          const adminUrl = `${req.protocol}://${req.get('host')}/admin/careers.html`;
          transporter.sendMail({
            from: `"Young's Collision Center Website" <${GMAIL_USER}>`,
            to: notifyTo,
            replyTo: email,
            subject: `New Job Application: ${name}${postingTitle ? ` — ${postingTitle}` : ''}`,
            html: `
              <h2>New Job Application</h2>
              <p><strong>Applying for:</strong> ${escapeHtml(postingTitle || 'General interest (no specific opening)')}</p>
              <p><strong>Name:</strong> ${escapeHtml(name)}</p>
              <p><strong>Email:</strong> ${escapeHtml(email)}</p>
              <p><strong>Phone:</strong> ${escapeHtml(phone)}</p>
              ${message ? `<p><strong>Message:</strong><br>${escapeHtml(message).replace(/\n/g, '<br>')}</p>` : ''}
              <p>Resume${coverLetterFile ? ' and cover letter are' : ' is'} attached. Every application is also saved in the careers admin dashboard.</p>
              <p><a href="${adminUrl}">Open the careers admin dashboard &rarr;</a></p>
              <hr><p style="color:#888;font-size:12px;">Submitted via the careers page on youngscollisioncenter.com &mdash; you can turn these emails off any time in the dashboard's Page Settings.</p>
            `,
            attachments,
          }).catch((mailErr) => console.error('careers application email failed (application was still saved):', mailErr));
        }

        res.json({ ok: true });
      } catch (applyErr) {
        console.error('careers apply error:', applyErr);
        res.status(500).json({ error: 'Failed to submit application.' });
      }
    });
  });

  // ---------------------------------------------------------------- admin auth
  app.post('/admin/careers-api/login', (req, res) => {
    if (!ADMIN_PASSWORD) {
      return res.status(500).json({ error: 'Admin login is not configured yet (ADMIN_PASSWORD is unset).' });
    }
    const { password } = req.body || {};
    if (typeof password === 'string' && timingSafeEqual(password, ADMIN_PASSWORD)) {
      req.session.isAdmin = true;
      return res.json({ ok: true });
    }
    res.status(401).json({ error: 'Incorrect password.' });
  });

  app.post('/admin/careers-api/logout', (req, res) => {
    req.session.destroy(() => res.json({ ok: true }));
  });

  app.get('/admin/careers-api/session', (req, res) => {
    res.json({ loggedIn: !!(req.session && req.session.isAdmin) });
  });

  // ---------------------------------------------------------------- admin: settings
  app.get('/admin/careers-api/settings', requireAdmin, async (req, res) => {
    res.json(await db.getSettings());
  });
  app.put('/admin/careers-api/settings', requireAdmin, async (req, res) => {
    const { headline, intro, acceptGeneral, notifyEmail, notifyEnabled } = req.body || {};
    res.json(await db.updateSettings({ headline, intro, acceptGeneral, notifyEmail, notifyEnabled }));
  });

  // ---------------------------------------------------------------- admin: postings
  app.get('/admin/careers-api/postings', requireAdmin, async (req, res) => {
    res.json(await db.listPostings());
  });
  app.post('/admin/careers-api/postings', requireAdmin, async (req, res) => {
    const { title, type, description, status } = req.body || {};
    if (!title) return res.status(400).json({ error: 'Title is required.' });
    res.json(await db.createPosting({ title, type, description, status }));
  });
  app.put('/admin/careers-api/postings/:id', requireAdmin, async (req, res) => {
    const { title, type, description, status, order } = req.body || {};
    const updated = await db.updatePosting(req.params.id, { title, type, description, status, order });
    if (!updated) return res.status(404).json({ error: 'Not found.' });
    res.json(updated);
  });
  app.delete('/admin/careers-api/postings/:id', requireAdmin, async (req, res) => {
    const ok = await db.deletePosting(req.params.id);
    if (!ok) return res.status(404).json({ error: 'Not found.' });
    res.json({ ok: true });
  });

  // ---------------------------------------------------------------- admin: applications
  app.get('/admin/careers-api/applications', requireAdmin, async (req, res) => {
    const applications = await db.listApplications();
    res.json(applications.map((a) => ({
      id: a.id,
      postingTitle: a.postingTitle,
      name: a.name,
      email: a.email,
      phone: a.phone,
      message: a.message,
      status: a.status,
      createdAt: a.createdAt,
      hasResume: !!a.resumeFile,
      hasCoverLetter: !!a.coverLetterFile,
    })));
  });
  app.put('/admin/careers-api/applications/:id', requireAdmin, async (req, res) => {
    const { status } = req.body || {};
    if (!['new', 'reviewed', 'archived'].includes(status)) {
      return res.status(400).json({ error: 'Invalid status.' });
    }
    const updated = await db.updateApplicationStatus(req.params.id, status);
    if (!updated) return res.status(404).json({ error: 'Not found.' });
    res.json(updated);
  });
  app.delete('/admin/careers-api/applications/:id', requireAdmin, async (req, res) => {
    const ok = await db.deleteApplication(req.params.id);
    if (!ok) return res.status(404).json({ error: 'Not found.' });
    res.json({ ok: true });
  });
  app.get('/admin/careers-api/applications/:id/file/:kind', requireAdmin, async (req, res) => {
    const { id, kind } = req.params;
    if (kind !== 'resume' && kind !== 'cover-letter') return res.status(400).end();
    const application = await db.getApplication(id);
    if (!application) return res.status(404).end();
    const filename = kind === 'resume' ? application.resumeFile : application.coverLetterFile;
    if (!filename) return res.status(404).end();
    const filePath = path.join(db.applicationUploadDir(id), filename);
    if (!fs.existsSync(filePath)) return res.status(404).end();
    res.download(filePath, `${application.name.replace(/[^a-z0-9]+/gi, '-')}-${kind}${path.extname(filename)}`);
  });
};
