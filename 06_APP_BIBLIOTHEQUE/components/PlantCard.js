/**
 * PlantCard.js
 * Bloom by BotaniK — App Bibliothèque
 *
 * Composant de rendu : carte résumé + modal détail d'une plante
 * Exposé via window.PlantCard
 */

(function () {
  'use strict';

  /**
   * Génère le HTML d'une carte plante pour la grille
   * @param {Object} plant
   * @returns {string} HTML
   */
  function render(plant) {
    const tags = (plant.categories || []).map(cat =>
      `<span class="tag">${escapeHtml(cat)}</span>`
    ).join('');

    return `
      <article class="plant-card" data-id="${escapeHtml(plant.id)}" tabindex="0" role="button"
        aria-label="Voir la fiche de ${escapeHtml(plant.nom)}">
        <h2 class="plant-card-name">${escapeHtml(plant.nom)}</h2>
        ${plant.nom_latin ? `<p class="plant-card-latin">${escapeHtml(plant.nom_latin)}</p>` : ''}
        <div class="plant-card-tags">${tags}</div>
        <p class="plant-card-summary">${escapeHtml(plant.resume_bloom || '')}</p>
      </article>
    `;
  }

  /**
   * Génère le HTML du contenu de la modal (fiche complète)
   * @param {Object} plant
   * @returns {string} HTML
   */
  function renderModal(plant) {
    const bienfaits = renderList(plant.bienfaits);
    const precautions = renderList(plant.precautions);
    const synergies = renderList(plant.synergie);

    return `
      <h2 class="modal-plant-name">${escapeHtml(plant.nom)}</h2>
      ${plant.nom_latin ? `<p class="modal-plant-latin">${escapeHtml(plant.nom_latin)}</p>` : ''}

      ${plant.resume_bloom ? `
        <div class="modal-section">
          <h3>Vision Bloom</h3>
          <p>${escapeHtml(plant.resume_bloom)}</p>
        </div>
      ` : ''}

      ${bienfaits ? `
        <div class="modal-section">
          <h3>Principaux bienfaits</h3>
          ${bienfaits}
        </div>
      ` : ''}

      ${precautions ? `
        <div class="modal-section">
          <h3>Précautions</h3>
          ${precautions}
        </div>
      ` : ''}

      ${synergies ? `
        <div class="modal-section">
          <h3>Synergies recommandées</h3>
          ${synergies}
        </div>
      ` : ''}

      ${plant.statut ? `
        <div class="modal-section">
          <h3>Statut de validation</h3>
          <p>${escapeHtml(plant.statut)}</p>
        </div>
      ` : ''}
    `;
  }

  /**
   * Rendu d'une liste HTML depuis un tableau de strings
   * @param {Array} items
   * @returns {string|null}
   */
  function renderList(items) {
    if (!Array.isArray(items) || items.length === 0) return null;
    const lis = items.map(item => `<li>${escapeHtml(item)}</li>`).join('');
    return `<ul>${lis}</ul>`;
  }

  /**
   * Échappe le HTML pour éviter les injections XSS
   * @param {string} str
   * @returns {string}
   */
  function escapeHtml(str) {
    if (typeof str !== 'string') return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // API publique
  window.PlantCard = { render, renderModal };

})();
