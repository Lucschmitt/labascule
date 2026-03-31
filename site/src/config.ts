// src/config.ts
// Astro expose les variables d'environnement préfixées PUBLIC_ côté client ET serveur
// Docker local : PUBLIC_SITE_BASE='' (vide) → liens depuis /
// GitHub Pages : PUBLIC_SITE_BASE='/labascule' → liens depuis /labascule

export const SITE_BASE = (import.meta.env.PUBLIC_SITE_BASE || '').replace(/\/$/, '');

export const u = (path: string): string => `${SITE_BASE}${path}`;
