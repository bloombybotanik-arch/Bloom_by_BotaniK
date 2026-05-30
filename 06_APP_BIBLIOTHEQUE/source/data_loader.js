/**
 * data_loader.js
 * Bloom by BotaniK — Chargement versionné des données plantes
 *
 * Logique :
 *   1. Charge version-manifest.json SANS cache (fraîcheur maximale)
 *   2. Utilise plants_version comme paramètre ?v= pour forcer le cache-bust
 *   3. Expose window.BloomData après chargement
 *
 * Usage :
 *   import { loadPlants } from './data_loader.js';
 *   const plants = await loadPlants();
 *   // window.BloomData.manifest, window.BloomData.plants, window.BloomData.loadedAt
 */

const MANIFEST_URL = "/06_APP_BIBLIOTHEQUE/data/version-manifest.json";
const PLANTS_URL   = "/06_APP_BIBLIOTHEQUE/data/plants.json";


/**
 * Construit une URL avec paramètre ?v= pour cache-busting.
 * @param {string} url - URL de base
 * @param {string} version - version à injecter
 * @returns {string}
 */
function addVersion(url, version) {
  const sep = url.includes("?") ? "&" : "?";
  return `${url}${sep}v=${encodeURIComponent(version)}`;
}


/**
 * Charge le manifest de version sans cache.
 * @returns {Promise<Object>} manifest JSON
 */
export async function loadVersionManifest() {
  const response = await fetch(MANIFEST_URL, { cache: "no-store" });
  if (!response.ok) throw new Error(`Manifest unavailable: ${response.status}`);
  return await response.json();
}


/**
 * Charge plants.json avec cache-busting basé sur plants_version du manifest.
 * Expose le résultat dans window.BloomData pour accès global.
 * @returns {Promise<Array>} liste des plantes
 */
export async function loadPlants() {
  const manifest = await loadVersionManifest();
  const version  = manifest?.plants_version || "dev";

  const response = await fetch(addVersion(PLANTS_URL, version), { cache: "no-store" });
  if (!response.ok) throw new Error(`Plants data unavailable: ${response.status}`);
  const data = await response.json();

  // Exposition globale pour debug et accès cross-module
  window.BloomData = {
    manifest,
    plants:   data,
    loadedAt: new Date().toISOString()
  };

  console.info(
    `[BloomData] ${data.length} plantes chargées`,
    `v=${version}`,
    `build=${manifest?.build_id || "?"}`,
    `commit=${manifest?.source_commit || "?"}`
  );

  return data;
}


/**
 * Charge plants-index.json avec cache-busting.
 * @returns {Promise<Array>} index léger des plantes
 */
export async function loadPlantsIndex() {
  const manifest = await loadVersionManifest();
  const version  = manifest?.plants_version || "dev";
  const INDEX_URL = "/06_APP_BIBLIOTHEQUE/data/plants-index.json";

  const response = await fetch(addVersion(INDEX_URL, version), { cache: "no-store" });
  if (!response.ok) throw new Error(`Plants index unavailable: ${response.status}`);
  return await response.json();
}
