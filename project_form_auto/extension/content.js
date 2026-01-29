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
