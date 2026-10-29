(() => {
  const groups = [...document.querySelectorAll('.rail-group')];
  const sections = groups.map(group => document.getElementById(group.dataset.section));
  if (!groups.length) return;
  groups.forEach((group, index) => {
    const panel = group.querySelector('.rail-projects');
    const section = sections[index];
    const overview = section.querySelector('.collection-link');
    if (overview) {
      const link = document.createElement('a');
      link.href = overview.getAttribute('href');
      link.textContent = ({frc: 'FRC overview ↗', software: 'Software overview ↗', research: 'Research overview ↗'})[section.id] || 'Overview ↗';
      link.className = 'rail-overview';
      panel.append(link);
    }
    section.querySelectorAll('.gallery-card').forEach(card => {
      const link = document.createElement('a');
      link.href = card.getAttribute('href');
      link.textContent = card.querySelector('h3').textContent;
      panel.append(link);
    });
    if (group.dataset.section === 'channel') {
      const link = document.createElement('a');
      link.href = 'channel.html';
      link.textContent = 'Reels, reach & agent workflow ↗';
      panel.append(link);
    }
  });
  let current = '';
  function activate(id) {
    if (id === current) return;
    current = id;
    groups.forEach(group => {
      const active = group.dataset.section === id;
      const category = group.querySelector('.rail-category');
      if (active) category.setAttribute('aria-current', 'location');
      else category.removeAttribute('aria-current');
      group.querySelector('.rail-projects').hidden = !active;
    });
  }
  function update() {
    let selected = sections[0];
    const line = Math.min(innerHeight * .3, 240);
    sections.forEach(section => {
      if (section.getBoundingClientRect().top <= line) selected = section;
    });
    activate(selected.id);
  }
  let pending = false;
  addEventListener('scroll', () => {
    if (pending) return;
    pending = true;
    requestAnimationFrame(() => { update(); pending = false; });
  }, {passive: true});
  addEventListener('resize', update);
  addEventListener('hashchange', update);
  update();
})();
