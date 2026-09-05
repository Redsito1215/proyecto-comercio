const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('sidebar-overlay');

function closeMobileMenu() { document.body.classList.remove('sidebar-mobile-open'); }
document.getElementById('mobile-menu').addEventListener('click', () => document.body.classList.add('sidebar-mobile-open'));
overlay.addEventListener('click', closeMobileMenu);
document.getElementById('sidebar-burger').addEventListener('click', () => document.body.classList.toggle('sidebar-collapsed'));

document.querySelectorAll('.nav-folder-toggle').forEach(button => button.addEventListener('click', () => {
  const folder = button.closest('.nav-folder');
  folder.classList.toggle('is-open');
  button.setAttribute('aria-expanded', folder.classList.contains('is-open'));
}));

function showPage(name, label) {
  document.querySelectorAll('.nav-item').forEach(item => item.classList.toggle('active', item.dataset.page === name));
  const home = document.getElementById('page-inicio');
  const dedicated = document.getElementById(`page-${name}`);
  const placeholder = document.getElementById('page-placeholder');
  document.querySelectorAll('.page').forEach(page => page.classList.remove('page-active'));
  (dedicated || placeholder).classList.add('page-active');
  document.getElementById('placeholder-title').textContent = label;
  document.getElementById('topbar-title').textContent = label;
  closeMobileMenu();
  window.dispatchEvent(new CustomEvent('ci:pagechange', { detail: { page: name } }));
}
window.ciShowPage=showPage;

document.querySelectorAll('.nav-item').forEach(item => item.addEventListener('click', () => showPage(item.dataset.page, item.querySelector('.nav-label').textContent)));
document.querySelectorAll('[data-go]').forEach(item => item.addEventListener('click', () => {
  const target = document.querySelector(`.nav-item[data-page="${item.dataset.go}"]`);
  showPage(item.dataset.go, target.querySelector('.nav-label').textContent);
}));

document.getElementById('theme-toggle').addEventListener('click', () => {
  const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
  document.documentElement.dataset.theme = next;
  document.documentElement.className = `theme-${next}`;
  localStorage.setItem('ci-theme', next);
});
