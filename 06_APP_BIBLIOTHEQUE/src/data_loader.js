/**
 * data_loader.js
 * Bloom by BotaniK — App Bibliothèque
 *
 * Charge plants.json avec cache-busting via window.__BLOOM_MANIFEST__
 * et expose les données via window.BloomData
 */

(function () {
  'use strict';

  // Cache mémoire
  let _cache = null;

  /**
   * Résout l'URL de plants.json depuis le manifest injecté au build,
   * avec cache-busting sur plants_version.
   * Fallback vers le chemin relatif si le manifest est absent.
   */
  function resolveDataUrl() {
    const manifest = window.__BLOOM_MANIFEST__;
    if (manifest && manifest.data_url) {
      // data_url = URL absolue ou relative vers plants.json
      // On ajoute ?v=plants_version pour le cache-busting
      const version = manifest.plants_version || manifest.app_version || Date.now();
      return `${manifest.data_url}?v=${version}`;
    }
    // Fallback dev local
    return '../data/plants.json';
  }

  /**
   * Charge les données des plantes depuis plants.json
   * @returns {Promise<Array>} Tableau de fiches plantes
   */
  async function loadPlants() {
    if (_cache) return _cache;

    const url = resolveDataUrl();
    console.info(`[BloomData] Chargement depuis : ${url}`);

    try {
      const response = await fetch(url, { cache: 'no-store' });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: impossible de charger ${url}`);
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
        name: 'Ashwagandha',
        scientific_name: 'Withania somnifera',
        summary: 'Adaptogène majeur utilisé en médecine ayurvédique pour réduire le stress et renforcer la vitalité.',
        vision_bloom: 'Ancrage et résilience face aux stress chroniques.',
        benefits: ['Réduction du cortisol', 'Amélioration du sommeil', 'Soutien thyroïdien'],
        precautions: ['Grossesse', 'Hyperthyroïdie', 'Interactions médicamenteuses'],
        synergies: ['Rhodiola', 'Magnésium', 'L-Théanine'],
        categories: ['adaptogene', 'nerveux'],
        validation_status: 'valide'
      },
      {
        id: 'curcuma',
        name: 'Curcuma',
        scientific_name: 'Curcuma longa',
        summary: 'Puissant anti-inflammatoire naturel, soutient les articulations et la santé digestive.',
        vision_bloom: 'Calmer l’inflammation chronique à la racine.',
        benefits: ['Anti-inflammatoire', 'Antioxydant', 'Soutien digestif'],
        precautions: ['Calculs biliaires', 'Anticoagulants'],
        synergies: ['Piperine', 'Gingembre', 'Omega-3'],
        categories: ['anti-inflammatoire', 'digestif'],
        validation_status: 'valide'
      },
      {
        id: 'reishi',
        name: 'Reishi',
        scientific_name: 'Ganoderma lucidum',
        summary: 'Champignon médicinal immuno-modulateur, favorise la relaxation et la longévité.',
        vision_bloom: 'Renforcer les défenses naturelles avec calme.',
        benefits: ['Immuno-modulation', 'Anti-stress', 'Soutien hépatique'],
        precautions: ['Anticoagulants', 'Autoimmunité'],
        synergies: ['Ashwagandha', 'Vitamine D', 'Zinc'],
        categories: ['immunitaire', 'adaptogene'],
        validation_status: 'valide'
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
    return plants.filter(p => {
      const cats = Array.isArray(p.categories) ? p.categories :
                   Array.isArray(p.category) ? p.category :
                   typeof p.categories === 'string' ? [p.categories] : [];
      return cats.map(c => String(c).toLowerCase()).includes(category.toLowerCase());
    });
  }

  /**
   * Recherche dans les plantes
   * @param {Array} plants
   * @param {string} query
   * @returns {Array}
   */
  function searchPlants(plants, query) {
    if (!query) return plants;
    const term = query.toLowerCase();
    return plants.filter(p => {
      const searchable = [
        p.name, p.scientific_name, p.summary, p.vision_bloom,
        ...(p.benefits || []), ...(p.precautions || []), ...(p.synergies || []),
        ...(Array.isArray(p.categories) ? p.categories : [])
      ].join(' ').toLowerCase();
      return searchable.includes(term);
    });
  }

  // API publique
  window.BloomData = {
    loadPlants,
    filterByCategory,
    searchPlants
  };

})();
