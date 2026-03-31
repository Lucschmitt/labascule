import { defineConfig } from 'astro/config';

const base = process.env.SITE_BASE || '';

export default defineConfig({
  output: 'static',
  site: base ? 'https://lucschmitt.github.io' : 'http://localhost:4321',
  base: base,
});
