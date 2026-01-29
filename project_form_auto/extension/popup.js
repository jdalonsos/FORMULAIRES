// Script du popup

console.log('Popup script chargé');

const detectBtn = document.getElementById('detectBtn');
const fillBtn = document.getElementById('fillBtn');
const statusDiv = document.getElementById('status');
const resultsDiv = document.getElementById('results');

let detectedFields = [];

/************************************
 * MAJ du statut affiché
 ***********************************/
function updateStatus(message, type = 'info') {
    statusDiv.textContent = message;
    statusDiv.className = `status status-${type}`;
  }



/************************************
 * Affichage des champs détectés
 ***********************************/
function displayFields(fields) {
    if (fields.length === 0) {
      resultsDiv.innerHTML = '<p style="color: #7f8c8d; font-size: 13px;">Aucun champ détecté</p>';
      return;
    }
    
    resultsDiv.innerHTML = '<h3>Champs détectés :</h3>';
    
    fields.forEach((field, index) => {
      const div = document.createElement('div');
      div.className = 'field-item';
      
      // Déterminer le nom à afficher en fonction des disponibilités
      const displayName = field.label || field.placeholder || field.name || field.id || `Champ ${index + 1}`;
      
      div.innerHTML = `
        <div class="field-label">${displayName}</div>
        <div class="field-type">Type: ${field.type} | Tag: ${field.tag}</div>
      `;
      
      resultsDiv.appendChild(div);
    });
  }


/*******************************************************
 * Détection des champs de formulaire sur la page active
 *******************************************************/
detectBtn.addEventListener('click', async () => {
  console.log('Clic sur le bouton de détection');
  
  updateStatus('Analyse de la page en cours...', 'loading');
  detectBtn.disabled = true;
  resultsDiv.innerHTML = '';
  
  try {
    // Récupérer l'onglet actif
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    console.log('Onglet actif:', tab.url);
    
    // Envoyer un message au content script
    chrome.tabs.sendMessage(
      tab.id, 
      { action: 'detectFields' }, 
      (response) => {

        if (chrome.runtime.lastError) {
          console.error('Erreur runtime:', chrome.runtime.lastError);
          updateStatus('Erreur: Rechargez la page (F5)', 'error');
          detectBtn.disabled = false;
          return;
        }
        
        // Vérifier la réponse
        if (response && response.success) {
          detectedFields = response.fields;
          console.log('Champs reçus:', detectedFields.length);
          
          if (detectedFields.length > 0) {
            updateStatus(` ${detectedFields.length} champ(s) détecté(s)`, 'success');
            displayFields(detectedFields);
            fillBtn.disabled = false;
          } else {
            updateStatus(' Aucun formulaire trouvé sur cette page', 'error');
          }
        } else {
          updateStatus('Erreur lors de la détection', 'error');
          console.error('Erreur:', response?.error);
        }
        
        detectBtn.disabled = false;
      }
    );
    
  } catch (error) {
    console.error('Erreur:', error);
    updateStatus('Erreur: ' + error.message, 'error');
    detectBtn.disabled = false;
  }
});

/************************************
 * A FAIRE : Remplissage des formulaires
 ***********************************/
fillBtn.addEventListener('click', () => {
  updateStatus('Fonctionnalité de remplissage, à venir...', 'info');
});