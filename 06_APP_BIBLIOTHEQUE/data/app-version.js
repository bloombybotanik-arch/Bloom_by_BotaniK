/**
 * app-version.js
 * Bloom by BotaniK — Version globale de l'application
 *
 * Ce fichier est AUTOMATIQUEMENT GÉNÉRÉ par publish_app_bundle.py
 * Ne pas modifier manuellement.
 *
 * Exposé en window.BloomVersion pour être accessible
 * avant le chargement des modules ES.
 */

window.BloomVersion = {
  app_version: "2026.05.30-01",
  plants_version: "2026.05.30-01",
  generated_at: "2026-05-30T10:00:00+02:00",
  source_commit: "placeholder"
};

// Log de diagnostic (désactivable en prod)
if (typeof console !== 'undefined') {
  console.info(
    `[BloomVersion] app=${window.BloomVersion.app_version}`,
    `plants=${window.BloomVersion.plants_version}`,
    `commit=${window.BloomVersion.source_commit}`
  );
}
