// src/config.ts
// Avec base: '/labascule' dans astro.config.mjs,
// import.meta.env.BASE_URL vaut '/labascule/'

const base = import.meta.env.BASE_URL.replace(/\/$/, ''); // '/labascule'

export const u = (path: string): string => `${base}${path}`;
