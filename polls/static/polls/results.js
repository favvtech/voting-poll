(function () {
  const POLL_INTERVAL_MS = 2500;

  const container = document.getElementById('results');
  if (!container) return;

  const url = container.dataset.url;
  const lastVote = document.getElementById('last-vote');
  const connection = document.getElementById('connection-status');
  const totalEl = document.getElementById('total-votes');
  const totalPlural = document.getElementById('total-plural');

  function showLastVote(isoTime, total) {
    if (isoTime) {
      const when = new Date(isoTime).toLocaleString(undefined, {
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        second: '2-digit',
      });
      lastVote.textContent = `Last vote: ${when}`;
    } else {
      lastVote.textContent = total ? '' : 'No votes yet';
    }
    lastVote.dataset.time = isoTime || '';
  }

  function render(data) {
    totalEl.textContent = data.total;
    totalPlural.textContent = data.total === 1 ? '' : 's';
    if (data.last_vote_at !== lastVote.dataset.time) {
      showLastVote(data.last_vote_at, data.total);
    }

    data.choices.forEach((choice) => {
      container.querySelectorAll(`[data-choice-id="${choice.id}"]`).forEach((el) => {
        el.classList.toggle('leading', choice.leading);
      });
      const column = container.querySelector(`.column[data-choice-id="${choice.id}"]`);
      if (!column) return;
      column.querySelector('.votes').textContent = choice.votes;
      column.querySelector('.percent').textContent = choice.percent.toFixed(1);
      column.querySelector('.fill').style.height = `${choice.percent}%`;
    });
  }

  async function refresh() {
    try {
      const response = await fetch(url, { cache: 'no-store' });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      render(await response.json());
      connection.hidden = true;
    } catch (err) {
      connection.hidden = false;
    } finally {
      setTimeout(refresh, POLL_INTERVAL_MS);
    }
  }

  if (lastVote.dataset.time) {
    showLastVote(lastVote.dataset.time, Number(totalEl.textContent));
  }
  setTimeout(refresh, POLL_INTERVAL_MS);
})();
