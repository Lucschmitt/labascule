import { defineConfig } from 'astro/config';

const SITE_BASE = process.env.SITE_BASE || '';

export default defineConfig({
  output: 'static',
  vite: {
    define: {
      'import.meta.env.SITE_BASE': JSON.stringify(SITE_BASE),
    },
  },
});
