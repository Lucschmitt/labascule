import { defineConfig } from 'astro/config';

// Astro lit automatiquement .env — PUBLIC_SITE_BASE disponible ici via process.env
const base = process.env.PUBLIC_SITE_BASE || '';

export default defineConfig({
  output: 'static',
  base: base || undefined,
});
