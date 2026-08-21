FORM_JS = '''
<script>
(function () {
  var form = document.getElementById('leadForm');
  if (!form) return;
  var status = document.getElementById('formStatus');
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    // Honeypot: if this hidden field got filled in, silently drop it (bot).
    if (form.querySelector('[name="company"]').value) { return; }

    var btn = form.querySelector('button[type="submit"]');
    var data = Object.fromEntries(new FormData(form).entries());
    btn.disabled = true;
    btn.textContent = 'Sending...';
    status.className = 'form-status';
    status.textContent = '';

    fetch(form.getAttribute('action'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
      .then(function (res) {
        if (!res.ok) throw new Error('Request failed');
        window.location.href = 'thank-you.html';
      })
      .catch(function () {
        status.className = 'form-status error';
        status.textContent = "Something went wrong sending your message — please call us at (740) 653-2431 instead.";
        btn.disabled = false;
        btn.textContent = 'Send Message';
      });
  });
})();
</script>
'''
