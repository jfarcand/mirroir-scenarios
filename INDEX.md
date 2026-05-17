```yaml
version: 1
name: mirroir-skills
pack_version: 1.0.0
description: |
  Canonical archetype pack for popular web frameworks and apps.
  Archetypes capture stable structural + behavioral patterns
  shared across multiple consumer projects.
repository: https://github.com/jfarcand/mirroir-skills
license: Apache-2.0
archetypes:
  - atmosphere/ai-console
```

# mirroir-skills — Archetype Pack

This repository hosts **mirroir archetypes**: reusable, parameterized test
specifications that consumer repos reference via their `.mirroir/mirroir.yaml`.
See the [architecture reference](https://gist.github.com/jfarcand/a0ef5d91043851e70ceeb728553514c4)
for the full model.

## Install

```bash
mkdir -p ~/.mirroir/skills
git clone --depth=1 --branch v1.0.0 https://github.com/jfarcand/mirroir-skills \
          ~/.mirroir/skills/mirroir-skills/1.0.0
```

## Archetypes shipped here

| Archetype | Versions | Compatibility |
|-----------|----------|---------------|
| `atmosphere/ai-console` | `1.0.0` | Atmosphere 4.x, Spring Boot 3.2+, Quarkus 3.13+ |

## Pack layout

```
archetypes/
  <name>/
    archetype.md
    APP.md
    SKILL.md
    scenarios/<flow>.yaml
```

Each tag of this repo represents one pack version. The installer fetches
the tagged ref into `~/.mirroir/skills/mirroir-skills/<version>/`.

## Contributing an archetype

1. Add `archetypes/<name>/archetype.md` declaring `provides.flows` + `requires.vars`.
2. Author the parameterized `APP.md`, `SKILL.md`, and scenario YAMLs.
3. Add an entry to the `archetypes:` list in this `INDEX.md`.
4. Tag a release: `git tag vX.Y.Z`.
