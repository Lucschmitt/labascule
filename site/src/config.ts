// src/config.ts
// SITE_BASE est injecté au build via variable d'environnement
// Docker local : SITE_BASE='' (vide) → liens depuis /
// GitHub Pages : SITE_BASE='/labascule' → liens depuis /labascule

export const SITE_BASE = (import.meta.env.SITE_BASE || '').replace(/\/$/, '');

// Helper de lien — à utiliser pour tous les href internes
export const u = (path: string): string => `${SITE_BASE}${path}`;
