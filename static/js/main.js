document.addEventListener('DOMContentLoaded', () => {
  // Navbar burger for Bulma
  const burgers = Array.from(document.querySelectorAll('.navbar-burger'));
  burgers.forEach(b => b.addEventListener('click', () => {
    const target = document.getElementById(b.dataset.target);
    b.classList.toggle('is-active');
    target.classList.toggle('is-active');
  }));

  const copy = (text) => navigator.clipboard.writeText(text).then(() => toast('Copied!'));

  const fullBtn = document.getElementById('copy-full');
  const shopBtn = document.getElementById('copy-shopping');
  const printBtn = document.getElementById('print-recipe');

  if (fullBtn) fullBtn.addEventListener('click', () => {
    const t = document.getElementById('full-recipe-text');
    copy(t.value);
  });
  if (shopBtn) shopBtn.addEventListener('click', () => {
    const t = document.getElementById('shopping-list-text');
    copy(t.value);
  });
  if (printBtn) printBtn.addEventListener('click', () => window.print());

  // Confetti celebration on result page
  const result = document.getElementById('result-page');
  if (result && result.dataset.celebrate && window.confetti) {
    setTimeout(() => {
      confetti({ particleCount: 100, spread: 70, origin: { y: 0.2 } });
    }, 300);
  }
});

function toast(message) {
  const n = document.createElement('div');
  n.className = 'notification is-success';
  n.style.position = 'fixed';
  n.style.right = '1rem';
  n.style.bottom = '1rem';
  n.style.zIndex = 9999;
  n.textContent = message;
  document.body.appendChild(n);
  setTimeout(() => n.remove(), 1500);
}

