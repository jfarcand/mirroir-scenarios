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

# ABOUTME: Validation script for mirroir-scenarios YAML files.
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
    "condition",
    "repeat",
}

VALID_CONDITION_TYPES = {"if_visible", "if_not_visible"}
VALID_REPEAT_MODES = {"while_visible", "until_visible", "times"}

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


def validate_steps(steps, rel, prefix, depth=0):
    """Validate a list of steps. Returns (errors, has_assert)."""
    errors = []
    has_assert = False

    for i, step in enumerate(steps):
        step_label = f"{prefix} {i + 1}"
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
