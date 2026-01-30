// Configuration centrale pour l'extension de formulaire automatique, notamment connexion avec notre API.
const CONFIG = {
    // URL de l'API
    API_BASE_URL: 'http://localhost:8000',
    
    ENDPOINTS: {
      MAP_FIELDS: '/form/map',
      HEALTH: '/health'
    },
    
    // Timeout pour les requêtes API
    API_TIMEOUT: 10000,
    
    // Données utilisateur par défaut (à remplacer par un système de storage à l'avenir)
    DEFAULT_USER_DATA: {
      first_name: 'Jean',
      last_name: 'Dupont',
      email: 'jean.dupont@example.com',
      phone: '0612345678',
      street: '123 Rue de la Paix',
      postal_code: '75001',
      city: 'Paris',
      country: 'France'
    }
  };
  
  // Pour rendre CONFIG accessible dans tous les scripts
  if (typeof window !== 'undefined') {
    window.CONFIG = CONFIG;
  }