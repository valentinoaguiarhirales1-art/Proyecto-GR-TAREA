(() => {
  const cfg = window.BOOKING;
  const cal = document.getElementById('calendar');
  const slotsEl = document.getElementById('slots');
  const form = document.getElementById('book-form');
  const msg = document.getElementById('form-msg');
  const MONTHS = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];
  const [ty, tm] = cfg.today.split('-').map(Number);
  let year = ty, month = tm, selected = cfg.today;

  const pad = n => String(n).padStart(2, '0');

  async function loadMonth() {
    document.getElementById('month-label').textContent = `${MONTHS[month - 1]} ${year}`;
    const data = await (await fetch(`${cfg.monthUrl}?year=${year}&month=${month}`)).json();
    cal.innerHTML = ['L','M','X','J','V','S','D'].map(d => `<div class="dow">${d}</div>`).join('');
    const first = (new Date(year, month - 1, 1).getDay() + 6) % 7;
    for (let i = 0; i < first; i++) cal.appendChild(document.createElement('div'));
    const last = new Date(year, month, 0).getDate();
    for (let d = 1; d <= last; d++) {
      const iso = `${year}-${pad(month)}-${pad(d)}`;
      const info = data.days[iso];
      const el = document.createElement('div');
      let cls = 'day';
      if (iso < cfg.today) cls += ' past';
      else if (!info || info.total === 0) cls += ' off';
      else if (info.free === 0) cls += ' full';
      else if (info.free <= info.total / 3) cls += ' some';
      else cls += ' free';
      if (iso === selected) cls += ' sel';
      el.className = cls;
      el.textContent = d;
      if (!cls.includes('past') && !cls.includes('off')) el.onclick = () => { selected = iso; loadMonth(); loadSlots(); };
      cal.appendChild(el);
    }
  }

  async function loadSlots() {
    form.hidden = true;
    document.getElementById('day-label').textContent = selected.split('-').reverse().join('/');
    const data = await (await fetch(`${cfg.slotsUrl}?date=${selected}`)).json();
    slotsEl.innerHTML = data.slots.length ? '' : '<p>Sin turnos este día.</p>';
    data.slots.forEach(s => {
      const el = document.createElement('div');
      el.className = `slot ${s.state}`;
      el.textContent = s.label + (s.state === 'mine' ? ' ✔' : s.state === 'busy' ? ' ✖' : '');
      if (s.state === 'free' && cfg.auth) el.onclick = () => {
        slotsEl.querySelectorAll('.sel').forEach(x => x.classList.remove('sel'));
        el.classList.add('sel');
        form.start.value = s.start; form.end.value = s.end;
        document.getElementById('chosen').textContent = `${selected.split('-').reverse().join('/')} · ${s.label}`;
        msg.hidden = true; form.hidden = false;
      };
      slotsEl.appendChild(el);
    });
  }

  form.addEventListener('submit', async e => {
    e.preventDefault();
    const res = await fetch(form.action, {method: 'POST', body: new FormData(form),
      headers: {'X-Requested-With': 'XMLHttpRequest'}});
    const data = await res.json();
    if (data.ok) { window.location = '/mis-reservas/'; return; }
    msg.textContent = data.message; msg.hidden = false;
    loadMonth(); loadSlots();
  });

  document.getElementById('prev').onclick = () => { if (--month < 1) { month = 12; year--; } loadMonth(); };
  document.getElementById('next').onclick = () => { if (++month > 12) { month = 1; year++; } loadMonth(); };
  loadMonth(); loadSlots();
})();
