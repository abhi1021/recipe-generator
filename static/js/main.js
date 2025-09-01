document.addEventListener('DOMContentLoaded', () => {
  // Navbar burger for Bulma
  const burgers = Array.from(document.querySelectorAll('.navbar-burger'));
  burgers.forEach(b => b.addEventListener('click', () => {
    const target = document.getElementById(b.dataset.target);
    b.classList.toggle('is-active');
    target.classList.toggle('is-active');
  }));

  // Loading animation for recipe generation
  const generateBtn = document.getElementById('generate-btn');
  const loadingOverlay = document.getElementById('loading-overlay');
  const recipeForm = document.querySelector('form[action*="generate"]');

  if (generateBtn && loadingOverlay && recipeForm) {
    recipeForm.addEventListener('submit', (e) => {
      const recipePrompt = document.getElementById('recipe_prompt');
      const availableIngredients = document.getElementById('available_ingredients');
      
      // Check if at least one field is filled
      const hasPrompt = recipePrompt && recipePrompt.value.trim() !== '';
      const hasIngredients = availableIngredients && availableIngredients.value.trim() !== '';
      
      if (!hasPrompt && !hasIngredients) {
        e.preventDefault();
        toast('Please enter either a recipe request or available ingredients!', 'is-warning');
        return;
      }
      
      // Show loading animation
      loadingOverlay.classList.remove('is-hidden');
      generateBtn.disabled = true;
      generateBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>&nbsp;Generating...';
    });
  }

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

function toast(message, type = 'is-success') {
  const n = document.createElement('div');
  n.className = `notification ${type}`;
  n.style.position = 'fixed';
  n.style.right = '1rem';
  n.style.bottom = '1rem';
  n.style.zIndex = 9999;
  n.style.minWidth = '300px';
  n.style.borderRadius = '12px';
  n.textContent = message;
  document.body.appendChild(n);
  setTimeout(() => n.remove(), 3000);
}

