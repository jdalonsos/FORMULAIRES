// Script du popup

console.log('Popup script chargé');

const detectBtn = document.getElementById('detectBtn');
const fillBtn = document.getElementById('fillBtn');
const statusDiv = document.getElementById('status');
const resultsDiv = document.getElementById('results');

// Test simple : changer le statut au clic
detectBtn.addEventListener('click', () => {
  statusDiv.textContent = 'Bouton de détection cliqué !';
  statusDiv.className = 'status status-loading';
  
  // Simuler un délai
  setTimeout(() => {
    statusDiv.textContent = 'Test réussi - Prêt à remplir le formulaire.';
    statusDiv.className = 'status status-success';
    fillBtn.disabled = false;
  }, 1000);
});

fillBtn.addEventListener('click', () => {
  statusDiv.textContent = 'Bouton de remplissage cliqué !';
  statusDiv.className = 'status status-info';
});