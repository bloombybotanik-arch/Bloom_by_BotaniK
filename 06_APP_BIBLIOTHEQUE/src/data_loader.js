/**
 * data_loader.js
 * Bloom by BotaniK — App Bibliothèque
 *
 * Charge dynamiquement plants.json depuis 03_BASE_DE_DONNEES
 * et expose les données via window.BloomData
 */

(function () {
  'use strict';

  // Chemin vers le JSON exporté par le pipeline GitHub Actions
  const DATA_URL = '../../03_BASE_DE_DONNEES/plants.json';

  // Cache mémoire
  let _cache = null;

  /**
   * Charge les données des plantes depuis plants.json
   * @returns {Promise<Array>} Tableau de fiches plantes
   */
  async function loadPlants() {
    if (_cache) return _cache;

    try {
      const response = await fetch(DATA_URL);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: impossible de charger ${DATA_URL}`);
      }

      const data = await response.json();

      // Normaliser : accepter tableau ou objet { plants: [] }
      _cache = Array.isArray(data) ? data : (data.plants || []);

      console.info(`[BloomData] ${_cache.length} plantes chargées.`);
      return _cache;

    } catch (err) {
      console.warn('[BloomData] Impossible de charger plants.json. Utilisation des données de démo.', err);
      _cache = getDemoPlants();
      return _cache;
    }
  }

  /**
   * Données de démo pour développement local
   * (remplacées automatiquement par plants.json en production)
   */
  function getDemoPlants() {
    return [
      {
        id: 'ashwagandha',
        nom: 'Ashwagandha',
        nom_latin: 'Withania somnifera',
        categories: ['adaptogene', 'nerveux', 'hormonal'],
        resume_bloom: 'Plante adaptogène majeure pour la gestion du stress et l’équilibre hormonal.',
        bienfaits: ['Réduction du cortisol', 'Amélioration du sommeil', 'Soutien hormonal'],
        precautions: ['Grossesse', 'Hyperthyroïdie', 'Interaction avec sédatifs'],
        synergie: ['Rhodiola', 'Magnésium'],
        statut: 'validated'
      },
      {
        id: 'curcuma',
        nom: 'Curcuma',
        nom_latin: 'Curcuma longa',
        categories: ['anti-inflammatoire', 'digestif', 'immunitaire'],
        resume_bloom: 'Anti-inflammatoire puissant, modulateur immunitaire et protecteur hépatique.',
        bienfaits: ['Anti-inflammatoire systémique', 'Protection du foie', 'Soutien digestif'],
        precautions: ['Calculs biliaires', 'Anticoagulants', 'Grossesse à haute dose'],
        synergie: ['Piperine', 'Gingembre'],
        statut: 'validated'
      },
      {
        id: 'rhodiola',
        nom: 'Rhodiola',
        nom_latin: 'Rhodiola rosea',
        categories: ['adaptogene', 'nerveux'],
        resume_bloom: 'Adaptogène nordique pour la résilience au stress et la performance cognitive.',
        bienfaits: ['Performance cognitive', 'Fatigue mentale', 'Résistance au stress'],
        precautions: ['Bipolaire', 'Insomnie sévère'],
        synergie: ['Ashwagandha', 'Vitamine B12'],
        statut: 'validated'
      }
    ];
  }

  /**
   * Filtre les plantes par catégorie
   * @param {Array} plants
   * @param {string} category
   * @returns {Array}
   */
  function filterByCategory(plants, category) {
    if (!category || category === 'all') return plants;
    return plants.filter(p =>
      Array.isArray(p.categories) && p.categories.includes(category)
    );
  }

  /**
   * Recherche textuelle (nom, latin, résumé, bienfaits)
   * @param {Array} plants
   * @param {string} query
   * @returns {Array}
   */
  function searchPlants(plants, query) {
    if (!query || query.trim() === '') return plants;
    const q = query.toLowerCase().trim();
    return plants.filter(p => {
      const searchable = [
        p.nom,
        p.nom_latin,
        p.resume_bloom,
        ...(p.bienfaits || []),
        ...(p.categories || [])
      ].join(' ').toLowerCase();
      return searchable.includes(q);
    });
  }

  // API publique
  window.BloomData = {
    loadPlants,
    filterByCategory,
    searchPlants
  };

})();
