#!/usr/bin/env python3
# Copyright 2026 Jean-Francois Arcand
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# ABOUTME: Validation script for iphone-mirroir-scenarios YAML files.
# ABOUTME: Checks required fields, step types, variable syntax, and metadata formats.

"""
Validate all scenario YAML files under apps/, testing/, and workflows/.

Exit 0 if no errors (warnings are OK), exit 1 if any error found.
"""

import os
import re
import sys

# ---------------------------------------------------------------------------
# YAML loading — prefer PyYAML, fall back to a minimal regex-based parser.
# ---------------------------------------------------------------------------

try:
    import yaml

    def load_yaml(path):
        with open(path, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh)

except ImportError:
    def load_yaml(path):
        """Minimal YAML parser using regex — handles the flat structure of scenario files."""
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()

        data = {}
        # Extract top-level scalar fields (name, app, description, ios_min, locale)
        for match in re.finditer(r'^(\w+):\s*(?:"([^"]*)"|(\S.*))\s*$', text, re.MULTILINE):
            key = match.group(1)
            value = match.group(2) if match.group(2) is not None else match.group(3)
            if key == "steps":
                continue
            data[key] = value.strip()

        # Handle block scalar descriptions (> or |)
        block_match = re.search(r'^description:\s*[>|]\s*\n((?:[ \t]+\S.*\n?)+)', text, re.MULTILINE)
        if block_match:
            data["description"] = block_match.group(1).strip()

        # Extract tags list
        tags_match = re.search(r'^tags:\s*\[([^\]]*)\]', text, re.MULTILINE)
        if tags_match:
            raw = tags_match.group(1)
            data["tags"] = [t.strip().strip('"').strip("'") for t in raw.split(",") if t.strip()]

        # Extract steps list
        steps = []
        for step_match in re.finditer(r'^\s+-\s+(\w+):\s*(.*)', text, re.MULTILINE):
            steps.append({step_match.group(1): step_match.group(2).strip().strip('"')})
        if steps:
            data["steps"] = steps

        return data

# ---------------------------------------------------------------------------
# Canonical step types (kept in sync with SKILL.md).
# ---------------------------------------------------------------------------

VALID_STEP_TYPES = {
    "launch",
    "tap",
    "type",
    "swipe",
    "wait_for",
    "assert_visible",
    "assert_not_visible",
    "screenshot",
    "press_key",
    "press_home",
    "open_url",
    "shake",
    "remember",
}

REQUIRED_FIELDS = {"name", "app", "description", "steps"}

SEMVER_ISH = re.compile(r"^\d+\.\d+(\.\d+)?$")
LOCALE_CODE = re.compile(r"^[a-z]{2}_[A-Z]{2}$")
VARIABLE_SYNTAX = re.compile(r"\$\{[^}]*\}")
MALFORMED_VARIABLE = re.compile(r"\$\{[^A-Za-z_]|\$\{[^}]*[^A-Za-z0-9_:}./-]")

# ---------------------------------------------------------------------------
# Validation logic.
# ---------------------------------------------------------------------------

SCENARIO_DIRS = ["apps", "testing", "workflows"]


def find_scenario_files(root):
    """Walk SCENARIO_DIRS and yield paths to .yaml files."""
    for dirname in SCENARIO_DIRS:
        dirpath = os.path.join(root, dirname)
        if not os.path.isdir(dirpath):
            continue
        for dirpath_walk, _, filenames in os.walk(dirpath):
            for fname in sorted(filenames):
                if fname.endswith(".yaml"):
                    yield os.path.join(dirpath_walk, fname)


def validate_file(filepath, root):
    """Validate a single scenario file. Returns (errors, warnings) lists."""
    errors = []
    warnings = []
    rel = os.path.relpath(filepath, root)

    try:
        data = load_yaml(filepath)
    except Exception as exc:
        errors.append(f"  ERROR  {rel}: failed to parse YAML: {exc}")
        return errors, warnings

    if data is None:
        errors.append(f"  ERROR  {rel}: empty or invalid YAML")
        return errors, warnings

    # --- Required fields ---
    for field in REQUIRED_FIELDS:
        if field not in data or data[field] is None:
            errors.append(f"  ERROR  {rel}: missing required field '{field}'")

    # --- Steps validation ---
    steps = data.get("steps", [])
    if isinstance(steps, list):
        has_assert = False
        for i, step in enumerate(steps):
            if not isinstance(step, dict):
                errors.append(f"  ERROR  {rel}: step {i + 1} is not a mapping")
                continue
            for step_type in step:
                if step_type not in VALID_STEP_TYPES:
                    errors.append(f"  ERROR  {rel}: unknown step type '{step_type}' at step {i + 1}")
                if step_type in ("assert_visible", "assert_not_visible"):
                    has_assert = True

        if not has_assert:
            warnings.append(f"  WARN   {rel}: no assert_visible or assert_not_visible step")

    # --- Variable syntax ---
    with open(filepath, "r", encoding="utf-8") as fh:
        raw_text = fh.read()

    for match in VARIABLE_SYNTAX.finditer(raw_text):
        var_expr = match.group(0)
        inner = var_expr[2:-1]  # strip ${ and }
        # Valid forms: VAR, VAR:-default
        if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*(?::-[^}]*)?$', inner):
            errors.append(f"  ERROR  {rel}: malformed variable syntax '{var_expr}'")

    # Detect unclosed ${
    for line_num, line in enumerate(raw_text.splitlines(), 1):
        opens = line.count("${")
        closes = line.count("}")
        if opens > closes:
            errors.append(f"  ERROR  {rel}:{line_num}: unclosed '${{' in variable expression")

    # --- Optional metadata validation ---
    ios_min = data.get("ios_min")
    if ios_min is not None:
        ios_min_str = str(ios_min)
        if not SEMVER_ISH.match(ios_min_str):
            errors.append(f"  ERROR  {rel}: ios_min '{ios_min_str}' is not semver-ish (e.g. '17.0')")

    tags = data.get("tags")
    if tags is not None:
        if not isinstance(tags, list):
            errors.append(f"  ERROR  {rel}: tags must be a list of strings")
        elif not all(isinstance(t, str) for t in tags):
            errors.append(f"  ERROR  {rel}: tags must be a list of strings")

    locale = data.get("locale")
    if locale is not None:
        if not LOCALE_CODE.match(str(locale)):
            errors.append(f"  ERROR  {rel}: locale '{locale}' is not a valid locale code (e.g. 'en_US')")

    return errors, warnings


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    all_errors = []
    all_warnings = []
    file_count = 0

    for filepath in find_scenario_files(root):
        file_count += 1
        errs, warns = validate_file(filepath, root)
        all_errors.extend(errs)
        all_warnings.extend(warns)

    if file_count == 0:
        print("No scenario files found.")
        sys.exit(1)

    print(f"Validated {file_count} scenario files.\n")

    for w in all_warnings:
        print(w)
    for e in all_errors:
        print(e)

    if all_warnings:
        print(f"\n{len(all_warnings)} warning(s)")
    if all_errors:
        print(f"{len(all_errors)} error(s)")
        sys.exit(1)
    else:
        print("\nAll checks passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
