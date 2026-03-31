#!/usr/bin/env node
/**
 * sync-fiches.js — Copie les fiches JSON du pipeline vers le site.
 * 
 * Usage : node sync-fiches.js
 * 
 * Copie depuis ../fiches/*.json vers ./public/fiches/*.json
 * À lancer avant `npm run build` ou en développement.
 */

import { readdir, copyFile, mkdir } from 'fs/promises';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dir = dirname(fileURLToPath(import.meta.url));
const SRC  = join(__dir, '..', 'fiches');  // ../fiches/ par rapport à site/
const DEST = join(__dir, 'public', 'fiches');

async function sync() {
  await mkdir(DEST, { recursive: true });

  let files;
  try {
    files = await readdir(SRC);
  } catch {
    console.warn(`Dossier source introuvable : ${SRC}`);
    console.warn('Le site sera buildé sans fiches — ajoutez-en plus tard.');
    return;  // Ne bloque plus le build
  }

  const json = files.filter(f => f.endsWith('.json'));

  for (const f of json) {
    await copyFile(join(SRC, f), join(DEST, f));
    console.log(`  ✓ ${f}`);
  }

  console.log(`\n${json.length} fiche(s) synchronisée(s) vers public/fiches/`);
}

sync().catch(console.error);
