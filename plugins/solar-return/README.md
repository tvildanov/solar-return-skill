# Solar Return plugin

This is a skill-only Agent Plugins 1.0 package. It bundles the same calculator and instructions as `solar-return.zip`; it does not host a calculation API, supply Python, install dependencies or override host permissions.

Read and approve code/dependency execution in your selected environment. If the host cannot execute the calculator, it must say so and may interpret an explicitly supplied, verified result JSON instead. Installing a plugin does not prove the calculator ran.

Source, platform-specific setup and privacy details: https://github.com/tvildanov/solar-return-skill/blob/main/PLATFORMS.md

The plugin files are prepared for supported local/import workflows. They have not been installed or accepted in every product, and this is not a listing in a public plugin directory. Workspace imports and local plugins can require administrator approval.

`skills/solar-return/` is generated from the repository's canonical `solar-return/` folder. Do not edit this generated copy. Rebuild with `python3 tools/package_plugin.py` from the repository root. Original GNU AGPL v3 and author attribution are preserved.
