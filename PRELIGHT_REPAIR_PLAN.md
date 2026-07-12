# Builder V4 - Preflight Repair Plan

## Current Problem

When Builder detects preflight validation errors, it immediately replaces the generated project with fallback files.

Current flow:

LLM
    ↓
Generated Project
    ↓
Preflight Validation
    ↓
Failure
    ↓
_fallback_files()
    ↓
Overwrite project

This causes good projects to be discarded because of one small issue such as:

- pass
- NotImplementedError
- duplicate function
- duplicate __init__

---

## New Architecture

LLM
    ↓
Generated Project
    ↓
Preflight Validation
    ↓
Failure
    ↓
_preflight_repair_prompt()
    ↓
LLM repairs ONLY the failing files
    ↓
Parser
    ↓
Overwrite repaired files
    ↓
Run validation again

If validation succeeds

    ↓

Compile
    ↓
Tests
    ↓
Runtime

Only if repair fails repeatedly

    ↓

Fallback Project

---

## New Function

BuilderV4

def _preflight_repair_prompt(...)

Purpose:

Generate a repair prompt similar to:

_dependency_repair_prompt()

but focused on

- placeholder code
- pass
- duplicate methods
- duplicate classes
- empty functions
- syntax problems

---

## Update _repair_preflight()

Current

files = self._fallback_files(project_name)

Replace with

response = self.llm_client.generate(
    self._preflight_repair_prompt(...)
)

↓

Parser

↓

Overwrite repaired files

↓

Validate again

Only after retry limit

↓

Fallback

---

## Advantages

✓ Keeps good projects

✓ Repairs only broken files

✓ Reduces Hello fallback

✓ Better LLM utilisation

✓ Smaller repairs

✓ Less regeneration

---

## Sprint

Builder V4 Sprint

Feature:

LLM Assisted Preflight Repair

Priority:

HIGH