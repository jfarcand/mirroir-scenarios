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

# ABOUTME: Validation script for mirroir-skills files (SKILL.md and YAML).
# ABOUTME: Checks required fields, step types, variable syntax, metadata formats, and front matter.

"""
Validate all skill files under apps/, testing/, workflows/, and legacy/.

Supports both SKILL.md (.md) files and legacy YAML (.yaml) files.
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
        """Minimal YAML parser using regex — handles the flat structure of skill files."""
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
    "long_press",
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
    "scroll_to",
    "set_network",
    "reset_app",
    "target",
    "measure",
    "condition",
    "repeat",
}

VALID_CONDITION_TYPES = {"if_visible", "if_not_visible"}
VALID_REPEAT_MODES = {"while_visible", "until_visible", "times"}

REQUIRED_YAML_FIELDS = {"name", "app", "description", "steps"}
REQUIRED_MD_FRONT_MATTER = {"version", "name"}
OPTIONAL_MD_FRONT_MATTER = {"app", "ios_min", "locale", "tags", "description"}

SEMVER_ISH = re.compile(r"^\d+\.\d+(\.\d+)?$")
LOCALE_CODE = re.compile(r"^[a-z]{2}_[A-Z]{2}$")
VARIABLE_SYNTAX = re.compile(r"\$\{[^}]*\}")
MALFORMED_VARIABLE = re.compile(r"\$\{[^A-Za-z_]|\$\{[^}]*[^A-Za-z0-9_:}./-]")

# ---------------------------------------------------------------------------
# Directories to scan for each file type.
# ---------------------------------------------------------------------------

MD_SKILL_DIRS = ["apps", "testing", "workflows", "ci"]
YAML_SKILL_DIRS = ["legacy"]

# ---------------------------------------------------------------------------
# File discovery.
# ---------------------------------------------------------------------------


def find_md_files(root):
    """Walk MD_SKILL_DIRS and yield paths to .md files."""
    for dirname in MD_SKILL_DIRS:
        dirpath = os.path.join(root, dirname)
        if not os.path.isdir(dirpath):
            continue
        for dirpath_walk, _, filenames in os.walk(dirpath):
            for fname in sorted(filenames):
                if fname.endswith(".md"):
                    yield os.path.join(dirpath_walk, fname)


def find_yaml_files(root):
    """Walk YAML_SKILL_DIRS and yield paths to .yaml files."""
    for dirname in YAML_SKILL_DIRS:
        dirpath = os.path.join(root, dirname)
        if not os.path.isdir(dirpath):
            continue
        for dirpath_walk, _, filenames in os.walk(dirpath):
            for fname in sorted(filenames):
                if fname.endswith(".yaml"):
                    yield os.path.join(dirpath_walk, fname)


# ---------------------------------------------------------------------------
# SKILL.md front matter parsing.
# ---------------------------------------------------------------------------


def parse_front_matter(text):
    """Parse YAML front matter from a markdown file (between --- delimiters).

    Returns (front_matter_dict, body_text) or (None, text) if no front matter.
    """
    if not text.startswith("---"):
        return None, text

    # Find the closing ---
    end_idx = text.find("\n---", 3)
    if end_idx == -1:
        return None, text

    front_matter_raw = text[4:end_idx]  # skip opening "---\n"
    body = text[end_idx + 4:]  # skip closing "\n---"

    # Parse the front matter as simple key: value pairs
    data = {}
    for line in front_matter_raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.match(r'^(\w+):\s*(.*)', line)
        if match:
            key = match.group(1)
            value = match.group(2).strip()
            # Strip surrounding quotes
            if (value.startswith('"') and value.endswith('"')) or \
               (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            # Parse inline arrays for tags
            if key == "tags" and value.startswith("["):
                inner = value[1:-1] if value.endswith("]") else value[1:]
                data[key] = [t.strip().strip('"').strip("'") for t in inner.split(",") if t.strip()]
            else:
                data[key] = value

    return data, body


# ---------------------------------------------------------------------------
# SKILL.md validation.
# ---------------------------------------------------------------------------


def validate_md_file(filepath, root):
    """Validate a single SKILL.md file. Returns (errors, warnings) lists."""
    errors = []
    warnings = []
    rel = os.path.relpath(filepath, root)

    try:
        with open(filepath, "r", encoding="utf-8") as fh:
            text = fh.read()
    except Exception as exc:
        errors.append(f"  ERROR  {rel}: failed to read file: {exc}")
        return errors, warnings

    if not text.strip():
        errors.append(f"  ERROR  {rel}: empty file")
        return errors, warnings

    # Parse front matter
    front_matter, body = parse_front_matter(text)

    if front_matter is None:
        errors.append(f"  ERROR  {rel}: missing YAML front matter (must start with ---)")
        return errors, warnings

    # Check required front matter fields
    for field in REQUIRED_MD_FRONT_MATTER:
        if field not in front_matter or not front_matter[field]:
            errors.append(f"  ERROR  {rel}: missing required front matter field '{field}'")

    # Validate version
    version = front_matter.get("version")
    if version is not None:
        try:
            version_int = int(version)
            if version_int != 1:
                errors.append(f"  ERROR  {rel}: unsupported front matter version '{version}' (expected 1)")
        except (ValueError, TypeError):
            errors.append(f"  ERROR  {rel}: front matter version must be an integer, got '{version}'")

    # Validate optional metadata fields
    ios_min = front_matter.get("ios_min")
    if ios_min is not None:
        if not SEMVER_ISH.match(str(ios_min)):
            errors.append(f"  ERROR  {rel}: ios_min '{ios_min}' is not semver-ish (e.g. '17.0')")

    tags = front_matter.get("tags")
    if tags is not None:
        if not isinstance(tags, list):
            errors.append(f"  ERROR  {rel}: tags must be a list of strings")
        elif not all(isinstance(t, str) for t in tags):
            errors.append(f"  ERROR  {rel}: tags must be a list of strings")

    locale = front_matter.get("locale")
    if locale is not None:
        if not LOCALE_CODE.match(str(locale)):
            errors.append(f"  ERROR  {rel}: locale '{locale}' is not a valid locale code (e.g. 'en_US')")

    # Check for unknown front matter fields
    known_fields = REQUIRED_MD_FRONT_MATTER | OPTIONAL_MD_FRONT_MATTER
    for key in front_matter:
        if key not in known_fields:
            warnings.append(f"  WARN   {rel}: unknown front matter field '{key}'")

    # Validate variable syntax in the body
    for match in VARIABLE_SYNTAX.finditer(text):
        var_expr = match.group(0)
        inner = var_expr[2:-1]  # strip ${ and }
        if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*(?::-[^}]*)?$', inner):
            errors.append(f"  ERROR  {rel}: malformed variable syntax '{var_expr}'")

    # Detect unclosed ${
    for line_num, line in enumerate(text.splitlines(), 1):
        opens = line.count("${")
        closes = line.count("}")
        if opens > closes:
            errors.append(f"  ERROR  {rel}:{line_num}: unclosed '${{' in variable expression")

    # Check body has content
    if not body.strip():
        warnings.append(f"  WARN   {rel}: empty body (no steps)")

    return errors, warnings


# ---------------------------------------------------------------------------
# YAML validation logic.
# ---------------------------------------------------------------------------


def validate_condition(cond, rel, path, depth=0):
    """Validate a condition step value. Returns (errors, has_assert)."""
    errors = []
    has_assert = False

    if depth > 3:
        errors.append(f"  ERROR  {rel}: condition nesting too deep at {path} (max 3 levels)")
        return errors, has_assert

    if not isinstance(cond, dict):
        errors.append(f"  ERROR  {rel}: {path} value must be a mapping with if_visible/if_not_visible, then, and optional else")
        return errors, has_assert

    # Must have exactly one condition type
    cond_types = [k for k in cond if k in VALID_CONDITION_TYPES]
    if len(cond_types) == 0:
        errors.append(f"  ERROR  {rel}: {path} must have 'if_visible' or 'if_not_visible'")
    elif len(cond_types) > 1:
        errors.append(f"  ERROR  {rel}: {path} must have only one of 'if_visible' or 'if_not_visible', found both")

    for ct in cond_types:
        if not isinstance(cond[ct], str) or not cond[ct].strip():
            errors.append(f"  ERROR  {rel}: {path}.{ct} must be a non-empty string")

    # Must have 'then'
    if "then" not in cond:
        errors.append(f"  ERROR  {rel}: {path} is missing required 'then' branch")
    else:
        then_steps = cond["then"]
        if not isinstance(then_steps, list) or len(then_steps) == 0:
            errors.append(f"  ERROR  {rel}: {path}.then must be a non-empty list of steps")
        else:
            step_errors, branch_assert = validate_steps(then_steps, rel, f"{path}.then", depth + 1)
            errors.extend(step_errors)
            has_assert = has_assert or branch_assert

    # 'else' is optional
    if "else" in cond:
        else_steps = cond["else"]
        if not isinstance(else_steps, list) or len(else_steps) == 0:
            errors.append(f"  ERROR  {rel}: {path}.else must be a non-empty list of steps")
        else:
            step_errors, branch_assert = validate_steps(else_steps, rel, f"{path}.else", depth + 1)
            errors.extend(step_errors)
            has_assert = has_assert or branch_assert

    # Check for unknown keys
    allowed_keys = VALID_CONDITION_TYPES | {"then", "else"}
    for key in cond:
        if key not in allowed_keys:
            errors.append(f"  ERROR  {rel}: {path} has unknown key '{key}'")

    return errors, has_assert


def validate_repeat(rep, rel, path, depth=0):
    """Validate a repeat step value. Returns (errors, has_assert)."""
    errors = []
    has_assert = False

    if depth > 3:
        errors.append(f"  ERROR  {rel}: repeat nesting too deep at {path} (max 3 levels)")
        return errors, has_assert

    if not isinstance(rep, dict):
        errors.append(f"  ERROR  {rel}: {path} value must be a mapping with a loop mode, max, and steps")
        return errors, has_assert

    # Must have exactly one loop mode
    modes = [k for k in rep if k in VALID_REPEAT_MODES]
    if len(modes) == 0:
        errors.append(f"  ERROR  {rel}: {path} must have one of: while_visible, until_visible, times")
    elif len(modes) > 1:
        errors.append(f"  ERROR  {rel}: {path} must have only one of: while_visible, until_visible, times (found {', '.join(modes)})")

    for mode in modes:
        if mode == "times":
            if not isinstance(rep[mode], int) or rep[mode] < 1:
                errors.append(f"  ERROR  {rel}: {path}.times must be a positive integer")
        else:
            if not isinstance(rep[mode], str) or not rep[mode].strip():
                errors.append(f"  ERROR  {rel}: {path}.{mode} must be a non-empty string")

    # Must have 'max' safety bound
    if "max" not in rep:
        errors.append(f"  ERROR  {rel}: {path} is missing required 'max' safety bound")
    else:
        if not isinstance(rep["max"], int) or rep["max"] < 1:
            errors.append(f"  ERROR  {rel}: {path}.max must be a positive integer")

    # Must have 'steps'
    if "steps" not in rep:
        errors.append(f"  ERROR  {rel}: {path} is missing required 'steps' list")
    else:
        rep_steps = rep["steps"]
        if not isinstance(rep_steps, list) or len(rep_steps) == 0:
            errors.append(f"  ERROR  {rel}: {path}.steps must be a non-empty list of steps")
        else:
            step_errors, branch_assert = validate_steps(rep_steps, rel, f"{path}.steps", depth + 1)
            errors.extend(step_errors)
            has_assert = has_assert or branch_assert

    # Check for unknown keys
    allowed_keys = VALID_REPEAT_MODES | {"max", "steps"}
    for key in rep:
        if key not in allowed_keys:
            errors.append(f"  ERROR  {rel}: {path} has unknown key '{key}'")

    return errors, has_assert


VALID_BARE_KEYWORDS = {"home", "press_home", "shake"}


def validate_steps(steps, rel, prefix, depth=0):
    """Validate a list of steps. Returns (errors, has_assert)."""
    errors = []
    has_assert = False

    for i, step in enumerate(steps):
        step_label = f"{prefix} {i + 1}"
        # Bare keyword steps like `- home` are parsed as strings by PyYAML
        if isinstance(step, str):
            if step not in VALID_BARE_KEYWORDS:
                errors.append(f"  ERROR  {rel}: unknown bare keyword '{step}' at {step_label}")
            continue
        if not isinstance(step, dict):
            errors.append(f"  ERROR  {rel}: {step_label} is not a mapping")
            continue
        for step_type in step:
            if step_type not in VALID_STEP_TYPES:
                errors.append(f"  ERROR  {rel}: unknown step type '{step_type}' at {step_label}")
            if step_type in ("assert_visible", "assert_not_visible"):
                has_assert = True
            if step_type == "condition":
                cond_errors, cond_assert = validate_condition(step[step_type], rel, step_label + " condition", depth)
                errors.extend(cond_errors)
                has_assert = has_assert or cond_assert
            if step_type == "repeat":
                rep_errors, rep_assert = validate_repeat(step[step_type], rel, step_label + " repeat", depth)
                errors.extend(rep_errors)
                has_assert = has_assert or rep_assert

    return errors, has_assert


def validate_yaml_file(filepath, root):
    """Validate a single YAML skill file. Returns (errors, warnings) lists."""
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
    for field in REQUIRED_YAML_FIELDS:
        if field not in data or data[field] is None:
            errors.append(f"  ERROR  {rel}: missing required field '{field}'")

    # --- Steps validation ---
    steps = data.get("steps", [])
    if isinstance(steps, list):
        step_errors, has_assert = validate_steps(steps, rel, "step")
        errors.extend(step_errors)

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
    md_count = 0
    yaml_count = 0

    # Validate SKILL.md files
    for filepath in find_md_files(root):
        md_count += 1
        errs, warns = validate_md_file(filepath, root)
        all_errors.extend(errs)
        all_warnings.extend(warns)

    # Validate legacy YAML files
    for filepath in find_yaml_files(root):
        yaml_count += 1
        errs, warns = validate_yaml_file(filepath, root)
        all_errors.extend(errs)
        all_warnings.extend(warns)

    total = md_count + yaml_count
    if total == 0:
        print("No skill files found.")
        sys.exit(1)

    print(f"Validated {total} skill files ({md_count} SKILL.md, {yaml_count} YAML).\n")

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
