(function () {
  const button = document.getElementById('copy-link');
  const input = document.getElementById('share-url');
  const status = document.getElementById('copy-status');
  if (!button || !input) return;

  function showStatus(text) {
    status.textContent = text;
    setTimeout(() => { status.textContent = ''; }, 2500);
  }

  button.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(input.value);
      showStatus('Link copied!');
    } catch (err) {
      input.select();
      const ok = document.execCommand && document.execCommand('copy');
      showStatus(ok ? 'Link copied!' : 'Press Ctrl+C to copy the link.');
    }
  });
})();
