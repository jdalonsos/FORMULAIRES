// Script du popup

console.log('Popup script chargé');

const detectBtn = document.getElementById('detectBtn');
const fillBtn = document.getElementById('fillBtn');
const statusDiv = document.getElementById('status');
const resultsDiv = document.getElementById('results');

let detectedFields = [];
let mappedFields = [];
let currentUrl = '';

// Configuration API
const API_BASE_URL = 'http://localhost:8000';
const API_ENDPOINTS = {
  MAP_FIELDS: '/form/map'
};

// Données utilisateur (hardcodées pour l'instant, storage a faire)
const USER_DATA = {
    first_name: 'Jean',
    last_name: 'Dupont',
    full_name: 'Jean Dupont',
    email: 'jean.dupont@example.com',
    phone: '0612345678',
    street: '123 Rue de la Paix',
    street_number: '123',
    postal_code: '75001',
    city: 'Paris',
    country: 'France',
    birth_date: '1990-01-15',
    birth_day: '15',
    birth_month: '01',
    birth_year: '1990',
    age: '34',
    username: 'jeandupont',
    gender: 'M',
    company: 'ACME Corp'
  };
  

/************************************
 * MAJ du statut affiché
 ***********************************/
function updateStatus(message, type = 'info') {
    statusDiv.textContent = message;
    statusDiv.className = `status status-${type}`;
  }



/************************************
 * Affichage des champs mappés avec leur correspondance (retravailler le design plus tard)
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

    // Icône selon le statut de mapping
    const icon = field.matched_key ? 'oui' : 'non';
        const matchInfo = field.matched_key 
          ? `→ ${field.matched_key} (${(field.confidence * 100).toFixed(0)}%)`
          : '(non mappé)';
      
      div.innerHTML = `
        <div class="field-label">${displayName}</div>
        <div class="field-type">Type: ${field.type} | Tag: ${field.tag}</div>
      `;
      
      resultsDiv.appendChild(div);
    });
  }


/************************************
 * Appel à l'API /form/map pour le mapping intelligent
 ***********************************/
async function callMappingAPI(url) {
    const apiUrl = `${API_BASE_URL}${API_ENDPOINTS.MAP_FIELDS}`;
    
    console.log('Appel API mapping:', apiUrl);
    console.log('URL à analyser:', url);
    console.log('Données utilisateur:', Object.keys(USER_DATA));
    
    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: url,
          user_data: USER_DATA
        }),
        signal: AbortSignal.timeout(15000) // Timeout de 15 secondes
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API Error ${response.status}: ${errorText}`);
      }
      
      const data = await response.json();
      console.log('Réponse API:', data);
      
      return data;
      
    } catch (error) {
      console.error('Erreur API:', error);
      throw error;
    }
  }


/*******************************************************
 * Détection des champs de formulaire sur la page active
 *******************************************************/
detectBtn.addEventListener('click', async () => {
  console.log('Clic sur le bouton de détection');
  
  updateStatus('Analyse de la page en cours...', 'loading');
  detectBtn.disabled = true;
  fillBtn.disabled = true;
  resultsDiv.innerHTML = '';

  try {
    // Récupérer l'onglet actif
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    currentUrl = tab.url;
    console.log('Onglet actif:', currentUrl);

    // Détecter les champs (pour avoir les sélecteurs)
    chrome.tabs.sendMessage(
        tab.id, 
        { action: 'detectFields' }, 
        async (response) => {
          if (chrome.runtime.lastError) {
            console.error('Erreur runtime:', chrome.runtime.lastError);
            updateStatus('Erreur: Rechargez la page (F5)', 'error');
            detectBtn.disabled = false;
            return;
          }
          
          // Vérifier la réponse du content script
          if (!response || !response.success) {
            updateStatus('Erreur lors de la détection', 'error');
            console.error('Erreur:', response?.error);
            detectBtn.disabled = false;
            return;
          }
          
          detectedFields = response.fields;
          console.log('Champs détectés côté client:', detectedFields.length);
          
          if (detectedFields.length === 0) {
            updateStatus('Aucun formulaire trouvé sur cette page', 'error');
            detectBtn.disabled = false;
            return;
          }
          
          // Appeler l'API avec l'URL ET les user_data
          try {
            const apiResponse = await callMappingAPI(currentUrl, USER_DATA); 
            
            mappedFields = apiResponse.fields;
            
            // Fusionner les sélecteurs des champs détectés avec le mapping de l'API
            const fieldsWithSelectors = mappedFields.map(apiField => {
              const clientField = detectedFields.find(
                cf => (cf.name && cf.name === apiField.name) || 
                      (cf.id && cf.id === apiField.id)
              );
              
              return {
                ...apiField,
                selector: clientField?.selector || `#${apiField.id || apiField.name}`,
                tag: apiField.tag
              };
            });
            
            mappedFields = fieldsWithSelectors;
            
            updateStatus(
              ` ${apiResponse.matched_fields}/${apiResponse.total_fields} champs mappés`, 
              'success'
            );
            
            displayFields(mappedFields);
            
            if (apiResponse.matched_fields > 0) {
              fillBtn.disabled = false;
            }
            
          } catch (apiError) {
            console.error(' Erreur API:', apiError);
            updateStatus(' Erreur API: ' + apiError.message, 'error');
            
            displayFields(detectedFields.map(f => ({
              ...f,
              matched_key: null,
              confidence: 0
            })));
          }
          
          detectBtn.disabled = false;
        }
      );
      
    } catch (error) {
      console.error('Erreur:', error);
      updateStatus(' Erreur: ' + error.message, 'error');
      detectBtn.disabled = false;
    }
  });

/************************************
 * Remplissage des formulaires avec les données mappées
 ***********************************/
fillBtn.addEventListener('click', async () => {
    console.log('Clic sur le bouton de remplissage');
    
    if (mappedFields.length === 0) {
      updateStatus('Aucun champ mappé à remplir', 'error');
      return;
    }
    
    updateStatus('Remplissage en cours...', 'loading');
    fillBtn.disabled = true;
    
    try {
    // Préparer les mappings pour le content script (déduplication incluse)
    const seenSelectors = new Set();

    const fillMappings = mappedFields
    .filter(field => field.matched_key) // Seulement les champs mappés
    .map(field => ({
        selector: field.selector,
        value: USER_DATA[field.matched_key] || '',
        field_name: field.matched_key
    }))
    .filter(m => m.value) // Seulement ceux qui ont une valeur
    .filter(m => {
        if (!m.selector) return false;
        if (seenSelectors.has(m.selector)) return false;
        seenSelectors.add(m.selector);
        return true;
    });

      
      console.log('Mappings à remplir:', fillMappings);
      
      if (fillMappings.length === 0) {
        updateStatus('Aucune donnée utilisateur correspondante', 'error');
        fillBtn.disabled = false;
        return;
      }
      
      // Envoyer au content script pour remplissage
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      chrome.tabs.sendMessage(
        tab.id,
        { action: 'fillFields', mappings: fillMappings },
        (response) => {
          if (chrome.runtime.lastError) {
            console.error('Erreur:', chrome.runtime.lastError);
            updateStatus('Erreur de remplissage', 'error');
            fillBtn.disabled = false;
            return;
          }
          
          if (response && response.success) {
            updateStatus(`${response.filled} champ(s) rempli(s) !`, 'success');
          } else {
            updateStatus('Erreur lors du remplissage', 'error');
          }
          
          fillBtn.disabled = false;
        }
      );
      
    } catch (error) {
      console.error('Erreur:', error);
      updateStatus('Erreur: ' + error.message, 'error');
      fillBtn.disabled = false;
    }
  });


