import { defineConfig } from 'astro/config';

export default defineConfig({
  output: 'static',
  site: 'https://lucschmitt.github.io',
  base: '/labascule',
  // Astro 7 compresse le HTML plus agressivement qu'Astro 4 et supprime des espaces (« structurellescommunes »).
  compressHTML: false,
});
