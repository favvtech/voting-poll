(function () {
  const POLL_INTERVAL_MS = 2500;
  const GROW_STAGGER_MS = 90;
  const GROW_DURATION_MS = 900;

  const container = document.getElementById('results');
  if (!container) return;

  const url = container.dataset.url;
  const chart = container.querySelector('.chart');
  const lastVote = document.getElementById('last-vote');
  const connection = document.getElementById('connection-status');
  const totalEl = document.getElementById('total-votes');
  const totalPlural = document.getElementById('total-plural');
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

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

  function flash(el) {
    if (reduceMotion) return;
    el.classList.remove('bumped');
    void el.offsetWidth;
    el.classList.add('bumped');
  }

  function growIn() {
    if (reduceMotion) return;
    const columns = [...chart.querySelectorAll('.column')];
    const fills = columns.map((column) => column.querySelector('.fill'));
    const targets = fills.map((fill) => fill.style.height);

    fills.forEach((fill) => {
      fill.style.transition = 'none';
      fill.style.height = '0%';
    });
    void chart.offsetHeight;

    chart.classList.add('intro');
    columns.forEach((column, i) => {
      column.style.setProperty('--delay', `${i * GROW_STAGGER_MS}ms`);
      fills[i].style.transition = '';
      fills[i].style.height = targets[i];
    });

    setTimeout(() => {
      chart.classList.remove('intro');
    }, GROW_DURATION_MS + columns.length * GROW_STAGGER_MS + 200);
  }

  function render(data) {
    if (String(data.total) !== totalEl.textContent) {
      totalEl.textContent = data.total;
      flash(totalEl);
    }
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

      const votesEl = column.querySelector('.votes');
      if (String(choice.votes) !== votesEl.textContent) {
        votesEl.textContent = choice.votes;
        flash(column);
      }
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

  // The bar flash outlasts the label pop, so only its end clears the class.
  container.addEventListener('animationend', (event) => {
    if (event.animationName === 'bar-flash' || event.animationName === 'total-flash') {
      event.target.closest('.bumped')?.classList.remove('bumped');
    }
  });

  if (lastVote.dataset.time) {
    showLastVote(lastVote.dataset.time, Number(totalEl.textContent));
  }
  growIn();
  setTimeout(refresh, POLL_INTERVAL_MS);
})();
