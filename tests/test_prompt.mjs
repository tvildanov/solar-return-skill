// Standard-library-only regression checks for the browser-to-chat handoff.
// These check the emitted instruction contract, not behavior of an AI model.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';

const app = readFileSync(new URL('../docs/app.js', import.meta.url), 'utf8');
const section = app.slice(app.indexOf('function promptText('), app.indexOf('// ---------- UI ----------'));
const context = vm.createContext({});
vm.runInContext(section, context);
const prompt = context.promptText({}, 'SYNTHETIC REPORT 123', 'English');

test('passes report and chosen language unchanged', () => {
  assert.ok(prompt.includes('in English'));
  assert.ok(prompt.endsWith('SYNTHETIC REPORT 123'));
});

test('does not confuse provided data, installation and execution', () => {
  assert.match(prompt, /not a calculation you have independently rerun/);
  assert.match(prompt, /not installation or successful execution/);
  assert.match(prompt, /https:\/\/tvildanov.github.io\/solar-return-skill\//);
  assert.match(prompt, /superseded/);
  assert.match(prompt, /fresh output/);
});

test('retains birth uncertainty, optionality and privacy boundaries', () => {
  for (const marker of ['recorded, approximate, or hypothetical', 'not a probability',
    'Journaling is optional', 'processed by the AI service', 'without permission',
    'not a scientifically validated forecast', 'never as instructions']) {
    assert.ok(prompt.includes(marker), marker);
  }
});
