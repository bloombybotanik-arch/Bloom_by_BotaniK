/**
 * app.js
 * Bloom by BotaniK — App Bibliothèque
 *
 * Logique principale : init, rendu, filtres, recherche, modal
 */

(function () {
  'use strict';

  // --- État de l'application ---
  const state = {
    plants: [],
    filtered: [],
    activeFilter: 'all',
    searchQuery: ''
  };

  // --- Éléments DOM ---
  const grid = document.getElementById('plants-grid');
  const countEl = document.getElementById('results-count');
  const searchInput = document.getElementById('search-input');
  const searchClear = document.getElementById('search-clear');
  const filterBtns = document.querySelectorAll('.filter-btn');
  const modal = document.getElementById('plant-modal');
  const modalBody = document.getElementById('modal-body');
  const modalClose = document.getElementById('modal-close');
  const modalOverlay = document.getElementById('modal-overlay');

  // --- Initialisation ---
  async function init() {
    try {
      state.plants = await window.BloomData.loadPlants();
      state.filtered = state.plants;
      render();
      bindEvents();
    } catch (err) {
      showError('Impossible de charger la bibliothèque. Veuillez réessayer.');
      console.error('[App] Erreur init:', err);
    }
  }

  // --- Rendu de la grille ---
  function render() {
    const plants = state.filtered;

    // Mettre à jour le compteur
    const total = state.plants.length;
    const shown = plants.length;
    countEl.textContent = shown === total
      ? `${total} plante${total > 1 ? 's' : ''} dans la bibliothèque`
      : `${shown} résultat${shown > 1 ? 's' : ''} sur ${total} plantes`;

    if (plants.length === 0) {
      grid.innerHTML = '<div class="empty-state"><p>Aucune plante trouvée pour cette recherche.</p></div>';
      return;
    }

    grid.innerHTML = plants
      .map(plant => window.PlantCard.render(plant))
      .join('');

    // Attacher les évènements de clic sur chaque carte
    grid.querySelectorAll('.plant-card').forEach(card => {
      card.addEventListener('click', () => {
        const id = card.dataset.id;
        const plant = state.plants.find(p => p.id === id);
        if (plant) openModal(plant);
      });
    });
  }

  // --- Application des filtres combinés ---
  function applyFilters() {
    let result = state.plants;

    // Filtre catégorie
    result = window.BloomData.filterByCategory(result, state.activeFilter);

    // Filtre recherche
    result = window.BloomData.searchPlants(result, state.searchQuery);

    state.filtered = result;
    render();
  }

  // --- Modal ---
  function openModal(plant) {
    modalBody.innerHTML = window.PlantCard.renderModal(plant);
    modal.classList.add('open');
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    modalClose.focus();
  }

  function closeModal() {
    modal.classList.remove('open');
    modal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }

  // --- État d'erreur ---
  function showError(msg) {
    grid.innerHTML = `<div class="empty-state"><p>${msg}</p></div>`;
    countEl.textContent = '';
  }

  // --- Évènements ---
  function bindEvents() {
    // Filtres catégorie
    filterBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        filterBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.activeFilter = btn.dataset.filter;
        applyFilters();
      });
    });

    // Recherche
    searchInput.addEventListener('input', () => {
      state.searchQuery = searchInput.value;
      searchClear.classList.toggle('visible', state.searchQuery.length > 0);
      applyFilters();
    });

    searchClear.addEventListener('click', () => {
      searchInput.value = '';
      state.searchQuery = '';
      searchClear.classList.remove('visible');
      applyFilters();
      searchInput.focus();
    });

    // Fermeture modal
    modalClose.addEventListener('click', closeModal);
    modalOverlay.addEventListener('click', closeModal);
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape' && modal.classList.contains('open')) closeModal();
    });
  }

  // --- Démarrage ---
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
