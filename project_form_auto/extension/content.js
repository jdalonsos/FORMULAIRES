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