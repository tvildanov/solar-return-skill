"""Distribution adapters: temp directories only, never actual user installation."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import install_skill
import package_plugin
from package_skill import FILES


class InstallerTests(unittest.TestCase):
    def test_each_project_host_and_exact_payload(self):
        for host, hidden in install_skill.HOST_DIRS.items():
            with self.subTest(host=host), tempfile.TemporaryDirectory() as temp:
                destination = install_skill.install(host, Path(temp))
                self.assertEqual(destination, Path(temp) / hidden / 'skills/solar-return')
                actual = {str(p.relative_to(destination)) for p in destination.rglob('*') if p.is_file()}
                expected = {str(Path(p).relative_to('solar-return')) for p in FILES}
                self.assertEqual(actual, expected)
                for path in FILES:
                    self.assertEqual((destination / Path(path).relative_to('solar-return')).read_bytes(),
                                     (ROOT / path).read_bytes())

    def test_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as temp:
            destination = install_skill.install('codex', Path(temp), dry_run=True)
            self.assertFalse(destination.exists())
            self.assertEqual(list(Path(temp).iterdir()), [])

    def test_existing_install_is_unchanged(self):
        with tempfile.TemporaryDirectory() as temp:
            destination = install_skill.install('cursor', Path(temp))
            marker = destination / 'SKILL.md'
            marker.write_text('USER CONTENT')
            with self.assertRaises(FileExistsError):
                install_skill.install('cursor', Path(temp))
            self.assertEqual(marker.read_text(), 'USER CONTENT')

    def test_destination_symlinks_rejected(self):
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as outside:
            (Path(temp) / '.agents').symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'symlink'):
                install_skill.install('codex', Path(temp))
            self.assertEqual(list(Path(outside).iterdir()), [])

    def test_broken_destination_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            (base / '.claude/skills').mkdir(parents=True)
            (base / '.claude/skills/solar-return').symlink_to(base / 'missing')
            with self.assertRaisesRegex(ValueError, 'symlink'):
                install_skill.install('claude-code', base)

    def test_cli_requires_explicit_scope(self):
        result = subprocess.run([sys.executable, str(ROOT / 'tools/install_skill.py'), '--host', 'codex'],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)


class PluginTests(unittest.TestCase):
    def test_plugin_copy_and_archive_match_canonical_source(self):
        files = package_plugin.expected_files()
        archive = package_plugin.archive_bytes(files)
        self.assertEqual(archive, package_plugin.archive_bytes(files))
        self.assertEqual(archive, (ROOT / 'solar-return-plugin.zip').read_bytes())
        with zipfile.ZipFile(ROOT / 'solar-return-plugin.zip') as z:
            self.assertIsNone(z.testzip())
            self.assertEqual(set(z.namelist()), {'solar-return-plugin/' + p for p in files})
            for path, data in files.items():
                self.assertEqual(z.read('solar-return-plugin/' + path), data)
                self.assertEqual((package_plugin.PLUGIN / path).read_bytes(), data)

    def test_marketplaces_resolve_the_same_plugin(self):
        openai = json.loads((ROOT / '.agents/plugins/marketplace.json').read_text())
        cursor = json.loads((ROOT / '.cursor-plugin/marketplace.json').read_text())
        openai_path = ROOT / openai['plugins'][0]['source']['path']
        cursor_path = ROOT / cursor['plugins'][0]['source']
        self.assertEqual(openai_path.resolve(), cursor_path.resolve())
        self.assertEqual(openai_path.resolve(), package_plugin.PLUGIN.resolve())
        manifest = json.loads((openai_path / 'plugin.json').read_text())
        self.assertEqual(manifest['name'], 'solar-return')
        self.assertNotIn('mcpServers', manifest)
        self.assertNotIn('hooks', manifest)
        self.assertEqual(openai['plugins'][0]['policy']['installation'], 'AVAILABLE')


if __name__ == '__main__':
    unittest.main()
