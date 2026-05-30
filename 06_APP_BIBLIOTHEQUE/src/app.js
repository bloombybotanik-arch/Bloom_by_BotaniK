/**
 * app.js
 * Bloom by BotaniK — App Bibliothèque
 * Logique principale : init, rendu, filtres, recherche, modal
 */

const state = {
  plants: [],
  filtered: [],
  activeCategory: "all",
  searchTerm: "",
  lastTrigger: null
};

const els = {};

function escapeHtml(str = "") {
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function getCategories(plant) {
  if (!plant) return [];
  if (Array.isArray(plant.categories)) return plant.categories;
  if (Array.isArray(plant.category)) return plant.category;
  if (typeof plant.categories === "string") return [plant.categories];
  if (typeof plant.category === "string") return [plant.category];
  return [];
}

function matchesCategory(plant, category) {
  if (category === "all") return true;
  return getCategories(plant).map(c => String(c).toLowerCase()).includes(category.toLowerCase());
}

function matchesSearch(plant, term) {
  if (!term) return true;
  const haystack = [
    plant.name,
    plant.common_name,
    plant.summary,
    plant.vision_bloom,
    ...(plant.benefits || []),
    ...(plant.precautions || []),
    ...(plant.synergies || []),
    ...getCategories(plant)
  ].join(" ").toLowerCase();
  return haystack.includes(term.toLowerCase());
}

function normalizePlant(plant, index = 0) {
  return {
    id: plant.id || plant.slug || `plant-${index}`,
    name: plant.name || plant.common_name || "Plante sans nom",
    scientific_name: plant.scientific_name || "",
    summary: plant.summary || plant.description || "",
    vision_bloom: plant.vision_bloom || plant.vision || "",
    benefits: Array.isArray(plant.benefits) ? plant.benefits : [],
    precautions: Array.isArray(plant.precautions) ? plant.precautions : [],
    synergies: Array.isArray(plant.synergies) ? plant.synergies : [],
    categories: getCategories(plant),
    validation_status: plant.validation_status || plant.status || "unknown",
    ...plant
  };
}

function renderPlantCard(plant) {
  const categories = (plant.categories || []).map(cat => `<span class="badge">${escapeHtml(cat)}</span>`).join("");
  return `
    <article class="plant-card" tabindex="0" data-plant-id="${escapeHtml(plant.id)}" role="button" aria-label="Ouvrir la fiche de ${escapeHtml(plant.name)}">
      <h4>${escapeHtml(plant.name)}</h4>
      ${plant.scientific_name ? `<p><em>${escapeHtml(plant.scientific_name)}</em></p>` : ""}
      <p>${escapeHtml(plant.summary)}</p>
      <div class="plant-meta">${categories}</div>
    </article>
  `;
}

function renderGrid() {
  const filtered = state.plants.filter(p => matchesCategory(p, state.activeCategory) && matchesSearch(p, state.searchTerm));
  state.filtered = filtered;

  els.grid.setAttribute("aria-busy", "false");
  els.loading.classList.add("hidden");
  els.empty.classList.toggle("hidden", filtered.length !== 0);

  if (!filtered.length) {
    els.grid.innerHTML = "";
  } else {
    els.grid.innerHTML = filtered.map(renderPlantCard).join("");
  }

  els.count.textContent = `${filtered.length} plante${filtered.length > 1 ? "s" : ""}`;
}

function buildModalHtml(plant) {
  const list = arr => (arr.length ? `<ul>${arr.map(i => `<li>${escapeHtml(i)}</li>`).join("")}</ul>` : "<p>Aucune donnée.</p>");
  return `
    <h3 id="modal-title">${escapeHtml(plant.name)}</h3>
    ${plant.scientific_name ? `<p><em>${escapeHtml(plant.scientific_name)}</em></p>` : ""}
    ${plant.vision_bloom ? `<p><strong>Vision Bloom :</strong> ${escapeHtml(plant.vision_bloom)}</p>` : ""}
    <h4>Bienfaits</h4>
    ${list(plant.benefits)}
    <h4>Précautions</h4>
    ${list(plant.precautions)}
    <h4>Synergies</h4>
    ${list(plant.synergies)}
    <h4>Catégories</h4>
    <p>${(plant.categories || []).map(c => `<span class="badge">${escapeHtml(c)}</span>`).join(" ")}</p>
    <p><strong>Statut :</strong> ${escapeHtml(plant.validation_status)}</p>
  `;
}

function openModal(plant, triggerEl = null) {
  state.lastTrigger = triggerEl || document.activeElement;
  els.modalContent.innerHTML = buildModalHtml(plant);
  els.modal.classList.remove("hidden");
  document.body.style.overflow = "hidden";
  const closeBtn = els.modal.querySelector("[data-close-modal]");
  if (closeBtn) closeBtn.focus();
}

function closeModal() {
  els.modal.classList.add("hidden");
  els.modalContent.innerHTML = "";
  document.body.style.overflow = "";
  if (state.lastTrigger && typeof state.lastTrigger.focus === "function") {
    state.lastTrigger.focus();
  }
}

function bindEvents() {
  els.search.addEventListener("input", (e) => {
    state.searchTerm = e.target.value.trim();
    renderGrid();
  });

  els.filters.forEach(btn => {
    btn.addEventListener("click", () => {
      els.filters.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      state.activeCategory = btn.dataset.category || "all";
      renderGrid();
    });
  });

  els.grid.addEventListener("click", (e) => {
    const card = e.target.closest("[data-plant-id]");
    if (!card) return;
    const plant = state.filtered.find(p => String(p.id) === String(card.dataset.plantId));
    if (plant) openModal(plant, card);
  });

  els.grid.addEventListener("keydown", (e) => {
    if (e.key !== "Enter" && e.key !== " ") return;
    const card = e.target.closest("[data-plant-id]");
    if (!card) return;
    e.preventDefault();
    const plant = state.filtered.find(p => String(p.id) === String(card.dataset.plantId));
    if (plant) openModal(plant, card);
  });

  els.modal.addEventListener("click", (e) => {
    if (e.target.matches("[data-close-modal]") || e.target.matches(".modal-backdrop")) closeModal();
  });

  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !els.modal.classList.contains("hidden")) {
      closeModal();
    }
  });
}

async function init() {
  els.search   = document.getElementById("plant-search");
  els.grid     = document.getElementById("plants-grid");
  els.count    = document.getElementById("results-count");
  els.loading  = document.getElementById("loading-state");
  els.empty    = document.getElementById("empty-state");
  els.modal    = document.getElementById("plant-modal");
  els.modalContent = document.getElementById("modal-content");
  els.filters  = Array.from(document.querySelectorAll(".filter-btn"));

  bindEvents();

  try {
    const plants = await window.BloomData.loadPlants();
    state.plants = (Array.isArray(plants) ? plants : []).map(normalizePlant);
    renderGrid();
  } catch (err) {
    console.error(err);
    if (els.loading) els.loading.classList.add("hidden");
    if (els.empty) {
      els.empty.classList.remove("hidden");
      els.empty.innerHTML = "<p>Impossible de charger les données Bloom pour le moment.</p>";
    }
    if (els.count) els.count.textContent = "0 plante";
  }
}

document.addEventListener("DOMContentLoaded", init);
