# AGENTS.md

## Project Guidelines for AI Agents

This document defines the coding standards and architectural principles that **must** be followed by all AI-generated contributions to this project.

---

## 1. Code Architecture & Structure

1. **Separation of Concerns**
   - Each module should have a single, well-defined responsibility.
   - Business logic, data access, and presentation layers **must** be separated.
   - Avoid mixing database queries with presentation/UI logic.

2. **Modularity**
   - Functions and classes should be reusable and loosely coupled.
   - Group related functions into dedicated modules
   - Avoid circular dependencies — refactor shared logic into utility modules if needed.

## 2. LEXICON Usage

1. **All text strings** (user-facing messages, button labels, prompts) **must** come from `LEXICON` constants.
2. Never hardcode text directly in handlers or logic.

## 3. Code Style & Documentation
1. Docstrings
   - All code must be written in English.
   - Every function and class must have a docstring in English.
   - Use the Google Python Style Guide for docstring formatting.
   - Describe:
     - Purpose of the function/class.
     - Parameters and their types.
     - Return value(s).
     - Exceptions raised.

2. Inline Comments
   - Use English for all comments.
   - Provide detailed explanations for complex logic, database transactions, or algorithmic steps.
   - Avoid obvious comments for trivial code.