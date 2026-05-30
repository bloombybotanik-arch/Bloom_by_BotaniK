/**
 * data_loader.js
 * Bloom by BotaniK — Chargement versionné des données plantes
 *
 * Logique :
 *   1. Charge version-manifest.json SANS cache (fraicheur maximale)
 *   2. Utilise plants_version comme paramètre ?v= pour forcer le cache-bust
 *   3. Si la version a changé depuis la dernière session → reload forcé
 *
 * Usage :
 *   import { loadPlants, loadPlantsIndex, getManifest } from './data_loader.js';
 */

// Chemin de base des données (relatif à l'origine du site)
const DATA_BASE = '/06_APP_BIBLIOTHEQUE/data';

// Clé localStorage pour mémoriser la version précédente
const VERSION_KEY = 'bloom_plants_version';


/**
 * Charge le manifest de version (toujours sans cache).
 * @returns {Promise<Object>} manifest JSON
 */
export async function getManifest() {
  const res = await fetch(`${DATA_BASE}/version-manifest.json`, {
    cache: 'no-store'
  });
  if (!res.ok) throw new Error(`[data_loader] manifest HTTP ${res.status}`);
  return res.json();
}


/**
 * Charge plants.json avec un paramètre ?v= basé sur plants_version.
 * Déclenche un reload si la version a changé depuis la dernière session.
 * @returns {Promise<Array>} liste des plantes
 */
export async function loadPlants() {
  const manifest = await getManifest();
  const version  = manifest.plants_version;

  // Détection de changement de version
  const previousVersion = localStorage.getItem(VERSION_KEY);
  if (previousVersion && previousVersion !== version) {
    console.info(`[BloomData] Nouvelle version détectée : ${previousVersion} → ${version}. Rechargement...`);
    localStorage.setItem(VERSION_KEY, version);
    window.location.reload();
    return []; // jamais atteint, mais évite les erreurs de lint
  }
  localStorage.setItem(VERSION_KEY, version);

  const url = `${DATA_BASE}/plants.json?v=${encodeURIComponent(version)}`;
  console.info(`[BloomData] Chargement plants.json v${version}`);

  const res = await fetch(url, { cache: 'no-store' });
  if (!res.ok) throw new Error(`[data_loader] plants.json HTTP ${res.status}`);
  return res.json();
}


/**
 * Charge plants-index.json avec paramètre ?v=
 * (index léger pour recherche/filtres).
 * @returns {Promise<Array>} index des plantes
 */
export async function loadPlantsIndex() {
  const manifest = await getManifest();
  const version  = manifest.plants_version;

  const url = `${DATA_BASE}/plants-index.json?v=${encodeURIComponent(version)}`;
  console.info(`[BloomData] Chargement plants-index.json v${version}`);

  const res = await fetch(url, { cache: 'no-store' });
  if (!res.ok) throw new Error(`[data_loader] plants-index.json HTTP ${res.status}`);
  return res.json();
}


/**
 * Vérifie si la version actuelle correspond à celle stockée.
 * Utile pour afficher un badge « Mis à jour » dans l'UI.
 * @returns {Promise<boolean>} true si les versions correspondent
 */
export async function isDataFresh() {
  try {
    const manifest = await getManifest();
    const stored   = localStorage.getItem(VERSION_KEY);
    return stored === manifest.plants_version;
  } catch {
    return false;
  }
}
