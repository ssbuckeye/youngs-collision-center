CAREERS_JS = '''
<script>
(function () {
  var postingsEl = document.getElementById('postingsList');
  var headlineEl = document.getElementById('careersHeadline');
  var introEl = document.getElementById('careersIntro');
  var formSection = document.getElementById('applySection');
  var form = document.getElementById('careersForm');
  var postingSelect = document.getElementById('postingSelect');
  var generalNote = document.getElementById('generalNote');
  var status = document.getElementById('careersFormStatus');

  function escapeHtml(value) {
    var div = document.createElement('div');
    div.textContent = value == null ? '' : String(value);
    return div.innerHTML;
  }

  function renderPostings(postings) {
    if (!postings.length) {
      postingsEl.innerHTML = '<p class="text-gray">We don\\'t have any specific openings posted right now.</p>';
    } else {
      postingsEl.innerHTML = postings.map(function (p) {
        var badge = p.status === 'general' ? 'Open to Future Openings' : (p.type || 'Open Position');
        return '<div class="posting-card">' +
          '<div class="posting-card-top"><h3>' + escapeHtml(p.title) + '</h3>' +
          '<span class="badge">' + escapeHtml(badge) + '</span></div>' +
          '<p class="text-gray">' + escapeHtml(p.description || '') + '</p>' +
          '<button type="button" class="btn btn-outline-dark apply-btn" data-posting-id="' + p.id + '" data-posting-title="' + escapeHtml(p.title) + '">Apply for This Role</button>' +
          '</div>';
      }).join('');
    }
  }

  function populatePostingSelect(postings) {
    postingSelect.innerHTML = '<option value="">General Application (no specific role)</option>' +
      postings.filter(function (p) { return p.status !== 'general'; }).map(function (p) {
        return '<option value="' + p.id + '">' + escapeHtml(p.title) + '</option>';
      }).join('');
  }

  fetch('/api/careers/postings')
    .then(function (res) { return res.json(); })
    .then(function (data) {
      if (headlineEl && data.settings && data.settings.headline) headlineEl.textContent = data.settings.headline;
      if (introEl && data.settings && data.settings.intro) introEl.textContent = data.settings.intro;
      if (generalNote) generalNote.style.display = (data.settings && data.settings.acceptGeneral) ? '' : 'none';
      renderPostings(data.postings || []);
      populatePostingSelect(data.postings || []);
    })
    .catch(function () {
      postingsEl.innerHTML = '<p class="text-gray">Openings are temporarily unavailable &mdash; please call us at (740) 653-2431.</p>';
    });

  postingsEl.addEventListener('click', function (e) {
    var btn = e.target.closest('.apply-btn');
    if (!btn) return;
    postingSelect.value = btn.getAttribute('data-posting-id');
    formSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });

  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (form.querySelector('[name="company"]').value) { return; }

      var resumeInput = form.querySelector('[name="resume"]');
      if (!resumeInput.files.length) {
        status.className = 'form-status error';
        status.textContent = 'Please attach your resume (PDF or Word document).';
        return;
      }

      var btn = form.querySelector('button[type="submit"]');
      btn.disabled = true;
      btn.textContent = 'Submitting...';
      status.className = 'form-status';
      status.textContent = '';

      fetch('/api/careers/apply', { method: 'POST', body: new FormData(form) })
        .then(function (res) {
          return res.json().then(function (data) { return { ok: res.ok, data: data }; });
        })
        .then(function (result) {
          if (!result.ok) throw new Error((result.data && result.data.error) || 'Request failed');
          window.location.href = 'thank-you.html';
        })
        .catch(function (err) {
          status.className = 'form-status error';
          status.textContent = err.message && err.message !== 'Request failed'
            ? err.message
            : 'Something went wrong submitting your application \\u2014 please call us at (740) 653-2431 instead.';
          btn.disabled = false;
          btn.textContent = 'Submit Application';
        });
    });
  }
})();
</script>
'''
