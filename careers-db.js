// Tiny JSON-file-backed "database" for the careers page.
//
// Why not a real database? At this scale (one small business, a handful of
// job postings, a few applications a month) a single JSON file is simpler to
// run, back up, and reason about than standing up Postgres. If this ever
// grows into a shared multi-business platform, swap this module out for a
// real database — every call site here goes through the functions below, so
// that's a contained change.
//
// All data (this file + uploaded resumes/cover letters) lives under DATA_DIR,
// which should point at a persistent Railway Volume in production — the
// regular app filesystem is wiped on every deploy.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const DATA_DIR = process.env.DATA_DIR || path.join(__dirname, 'data');
const DB_FILE = path.join(DATA_DIR, 'careers-db.json');
const UPLOADS_DIR = path.join(DATA_DIR, 'uploads');

function ensureDirs() {
  fs.mkdirSync(DATA_DIR, { recursive: true });
  fs.mkdirSync(UPLOADS_DIR, { recursive: true });
}

const DEFAULT_DB = {
  settings: {
    headline: "Join Our Team",
    intro: "We're not always actively hiring, but we're always glad to hear from people who care " +
      "about doing quality work. Browse any current openings below, or send us your info for the next " +
      "time we're looking to add someone.",
    acceptGeneral: true,
    // Who gets a heads-up email when someone applies, and whether to send it
    // at all. Blank notifyEmail falls back to the site's main TO_EMAIL at
    // send time (see careers.js) — this lets an owner opt out entirely
    // without having to first fill in an address.
    notifyEmail: "",
    notifyEnabled: true,
  },
  postings: [],
  applications: [],
};

function load() {
  ensureDirs();
  if (!fs.existsSync(DB_FILE)) {
    fs.writeFileSync(DB_FILE, JSON.stringify(DEFAULT_DB, null, 2));
    return structuredClone(DEFAULT_DB);
  }
  const raw = fs.readFileSync(DB_FILE, 'utf8');
  try {
    const parsed = JSON.parse(raw);
    return {
      settings: { ...DEFAULT_DB.settings, ...(parsed.settings || {}) },
      postings: Array.isArray(parsed.postings) ? parsed.postings : [],
      applications: Array.isArray(parsed.applications) ? parsed.applications : [],
    };
  } catch (err) {
    console.error('careers-db.json is corrupt, backing it up and starting fresh:', err);
    fs.copyFileSync(DB_FILE, `${DB_FILE}.corrupt-${Date.now()}`);
    fs.writeFileSync(DB_FILE, JSON.stringify(DEFAULT_DB, null, 2));
    return structuredClone(DEFAULT_DB);
  }
}

// Writes are serialized through this promise chain so two near-simultaneous
// requests (e.g. two applicants submitting seconds apart) can't interleave
// and corrupt the file. At this traffic volume that's all the safety this
// needs — no real locking infrastructure required.
let writeChain = Promise.resolve();
function save(db) {
  writeChain = writeChain.then(() => {
    const tmpFile = `${DB_FILE}.tmp`;
    fs.writeFileSync(tmpFile, JSON.stringify(db, null, 2));
    fs.renameSync(tmpFile, DB_FILE);
  });
  return writeChain;
}

async function withDb(mutator) {
  const db = load();
  const result = await mutator(db);
  await save(db);
  return result;
}

function newId() {
  return crypto.randomUUID();
}

// ---- Settings ----
async function getSettings() {
  return load().settings;
}
async function updateSettings(patch) {
  return withDb((db) => {
    // Same guard as updatePosting: only overwrite fields the caller actually
    // sent, so a future partial update can't blank out the rest of settings.
    for (const key of Object.keys(patch || {})) {
      if (patch[key] !== undefined) db.settings[key] = patch[key];
    }
    return db.settings;
  });
}

// ---- Postings ----
async function listPostings({ publicOnly = false } = {}) {
  const db = load();
  const postings = [...db.postings].sort((a, b) => a.order - b.order);
  if (!publicOnly) return postings;
  return postings.filter((p) => p.status !== 'closed');
}
async function createPosting(data) {
  return withDb((db) => {
    const now = new Date().toISOString();
    const maxOrder = db.postings.reduce((m, p) => Math.max(m, p.order ?? 0), -1);
    const posting = {
      id: newId(),
      title: data.title || 'Untitled Role',
      type: data.type || 'Full-time',
      description: data.description || '',
      status: data.status || 'open', // 'open' | 'general' | 'closed'
      order: maxOrder + 1,
      createdAt: now,
      updatedAt: now,
    };
    db.postings.push(posting);
    return posting;
  });
}
async function updatePosting(id, patch) {
  return withDb((db) => {
    const posting = db.postings.find((p) => p.id === id);
    if (!posting) return null;
    // Only apply fields the caller actually sent. The admin dashboard's status
    // dropdown, for example, PUTs just `{ status }` — without this filter,
    // destructuring that body elsewhere fills in `title`/`type`/`description`/
    // `order` as `undefined`, and Object.assign would happily overwrite the
    // posting's real values with `undefined` (which then vanish entirely once
    // the record is JSON-serialized to disk).
    const fields = ['title', 'type', 'description', 'status', 'order'];
    for (const field of fields) {
      if (patch[field] !== undefined) posting[field] = patch[field];
    }
    posting.updatedAt = new Date().toISOString();
    return posting;
  });
}
async function deletePosting(id) {
  return withDb((db) => {
    const before = db.postings.length;
    db.postings = db.postings.filter((p) => p.id !== id);
    return db.postings.length < before;
  });
}

// ---- Applications ----
function applicationUploadDir(applicationId) {
  return path.join(UPLOADS_DIR, applicationId);
}

async function createApplication({ id, postingId, postingTitle, name, email, phone, message, resumeFile, coverLetterFile }) {
  return withDb((db) => {
    const now = new Date().toISOString();
    const application = {
      id: id || newId(),
      postingId: postingId || null,
      postingTitle: postingTitle || null,
      name,
      email,
      phone,
      message: message || '',
      resumeFile: resumeFile || null, // stored filename on disk (within applicationUploadDir)
      coverLetterFile: coverLetterFile || null,
      status: 'new', // 'new' | 'reviewed' | 'archived'
      createdAt: now,
    };
    db.applications.push(application);
    return application;
  });
}
async function listApplications() {
  const db = load();
  return [...db.applications].sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
}
async function getApplication(id) {
  return load().applications.find((a) => a.id === id) || null;
}
async function updateApplicationStatus(id, status) {
  return withDb((db) => {
    const application = db.applications.find((a) => a.id === id);
    if (!application) return null;
    application.status = status;
    return application;
  });
}
async function deleteApplication(id) {
  return withDb((db) => {
    const before = db.applications.length;
    db.applications = db.applications.filter((a) => a.id !== id);
    const removed = db.applications.length < before;
    if (removed) {
      const dir = applicationUploadDir(id);
      fs.rmSync(dir, { recursive: true, force: true });
    }
    return removed;
  });
}

module.exports = {
  DATA_DIR,
  UPLOADS_DIR,
  ensureDirs,
  newId,
  applicationUploadDir,
  getSettings,
  updateSettings,
  listPostings,
  createPosting,
  updatePosting,
  deletePosting,
  createApplication,
  listApplications,
  getApplication,
  updateApplicationStatus,
  deleteApplication,
};
