#!/usr/bin/env node
/**
 * sync-fiches.js — Copie les fiches JSON du pipeline vers le site.
 * Lit récursivement fiches/ et fiches/calibration/
 * 
 * Usage : node sync-fiches.js
 */

import { readdir, copyFile, mkdir } from 'fs/promises';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dir = dirname(fileURLToPath(import.meta.url));
const SRC  = join(__dir, '..', 'fiches');
const DEST = join(__dir, 'public', 'fiches');

async function collectJsonFiles(dir) {
  let result = [];
  let entries;
  try {
    entries = await readdir(dir, { withFileTypes: true });
  } catch {
    return result;
  }
  for (const entry of entries) {
    if (entry.isDirectory()) {
      const sub = await collectJsonFiles(join(dir, entry.name));
      result = result.concat(sub);
    } else if (entry.name.endsWith('.json')) {
      result.push(join(dir, entry.name));
    }
  }
  return result;
}

async function sync() {
  await mkdir(DEST, { recursive: true });

  const files = await collectJsonFiles(SRC);

  if (files.length === 0) {
    console.warn('Aucune fiche JSON trouvée dans', SRC);
    console.warn('Le site sera buildé sans fiches.');
    return;
  }

  for (const f of files) {
    const filename = f.split(/[\\/]/).pop();
    await copyFile(f, join(DEST, filename));
    console.log(`  ✓ ${filename}`);
  }

  console.log(`\n${files.length} fiche(s) synchronisée(s) vers public/fiches/`);
}

sync().catch(console.error);
