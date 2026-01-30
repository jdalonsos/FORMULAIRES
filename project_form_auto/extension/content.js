//Ce script sera injecté dans les pages web pour détecter les champs de formulaire et extraire leurs informations.
console.log('AutoFill Content Script chargé sur:', window.location.href);

/************************************
 * Trouve le label associé à un champ
 ***********************************/
function findLabel(field) {
  // Méthode 1: <label for="id">
  if (field.id) {
    const label = document.querySelector(`label[for="${field.id}"]`);
    if (label) return label.textContent.trim(); 
  }
  
  // Méthode 2: champ à l'intérieur d'un <label>
//   <label>
//   Adresse email
//   <input type="email" >
//   </label>
  const parentLabel = field.closest('label');
  if (parentLabel) {
    // Retire la valeur du champ du texte du label
    const labelText = parentLabel.textContent.replace(field.value, '').trim();
    return labelText;
  }
  
  // Méthode 3: label juste avant le champ 
//   <div>
//   <label>Adresse email</label>
//   <input type="email">
//   </div>

  let previousElement = field.previousElementSibling;
  while (previousElement) { 
    if (previousElement.tagName === 'LABEL') {
      return previousElement.textContent.trim();
    }
    // Parfois le label est dans un div avant
    const labelInside = previousElement.querySelector('label');
    if (labelInside) {
      return labelInside.textContent.trim();
    }
    previousElement = previousElement.previousElementSibling;
  }
  
  return '';
}


/************************************
 * Selectionneur unique pour un champ
 ***********************************/
function generateSelector(field, index) {
    // Priorité 1: ID (le plus fiable) <input id="email">
    if (field.id) {
      return `#${field.id}`;
    }
    
    // Priorité 2: Name (assez fiable) <input name="email">
    if (field.name) {
      return `[name="${field.name}"]`;
    }
    
  // Priorité 3: Placeholder (utile quand id/name absents)
  // <input placeholder="Adresse email">
  if (field.placeholder) {
    return `${field.tagName.toLowerCase()}[placeholder="${CSS.escape(field.placeholder)}"]`;
  }

  // Priorité 4: Combinaison type + index (dernier recours)
//   0 → <input type="text">  // Prénom
//   1 → <input type="text">  // Nom
//   2 → <input type="email"> // Email
  const tag = field.tagName.toLowerCase();
  return `${tag}[type="${field.type}"]:nth-of-type(${index + 1})`;
} 


/************************************
 * Extrait toutes les informations utiles d'un champ
 ***********************************/
function extractFieldInfo(field, index) {
 return {
   index: index,
   tag: field.tagName.toLowerCase(),
   type: field.type || 'text',
   name: field.name || '',
   id: field.id || '',
   className: field.className || '',
   placeholder: field.placeholder || '',
   label: findLabel(field),
   ariaLabel: field.getAttribute('aria-label') || '',
   required: field.required || false,
   autocomplete: field.autocomplete || '',
   selector: generateSelector(field, index)
 };
}


/************************************
 * Detecte tout les champs de formulaire pertinents
 ***********************************/ 
function detectFormFields() {
 console.log('Détection des champs de formulaire...');
 
 // Sélectionner tous les champs input, select, textarea
 const allFields = document.querySelectorAll('input, select, textarea');
 const formData = [];
 
 allFields.forEach((field, index) => {
   // Filtrer les champs non pertinents: A voir checkbox et radio comment les gérer
   const excludedTypes = ['hidden', 'submit', 'button', 'reset', 'image']; 
   
   if (excludedTypes.includes(field.type)) {
     return; // Ignorer ce champ
   }
   
   // Ignorer les champs invisibles
   const style = window.getComputedStyle(field);
   if (style.display === 'none' || style.visibility === 'hidden') {
     return;
   }
   
   // Extraire les infos du champ
   const fieldInfo = extractFieldInfo(field, formData.length);
   formData.push(fieldInfo);
   
   console.log('Champ détecté:', fieldInfo.label || fieldInfo.name || fieldInfo.id);
 });
 
 console.log(`${formData.length} champs détectés au total`);
 return formData;
}

/************************************
 * DEcoute les messages du background/popup
 ***********************************/
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
 console.log(' Message reçu:', request.action);
 
 if (request.action === 'detectFields') {
   try {
     const fields = detectFormFields();
     sendResponse({ 
       success: true, 
       fields: fields, 
       count: fields.length,
       url: window.location.href
     });
   } catch (error) {
     console.error('Erreur lors de la détection:', error);
     sendResponse({ 
       success: false, 
       error: error.message 
     });
   }
 }
 
 // Sert à  garder le canal ouvert pour la réponse asynchrone
 return true;
});

console.log('Content script prêt à détecter les formulaires');