# Product Report

## Project Description

Testability Doctor is a CLI that checks whether a repository is practical for AI coding agents to modify and test.

## Target Users

- developers using Codex, Claude Code, Cursor, or similar agents
- maintainers triaging whether a repo is ready for agent-assisted work
- bounty hunters evaluating whether a code task is testable before implementation
- reviewers who need a compact preflight report

## Problem Solved

AI agents need deterministic local validation. Many repositories appear simple but require hidden setup, external environments, or manual-only validation. Testability Doctor makes that risk visible before code changes begin.

## Feature List

- static stack detection
- package manager and lockfile detection
- test command detection
- docs-only classification
- external environment risk detection
- monorepo and large repository flags
- Markdown and JSON reports
- config file support
- release packaging script
- examples and unit tests

## Release Notes

Version `0.1.0` is the first public release. It focuses on safe static analysis and a small standard-library Python CLI.

## Suggested GitHub Repo Description

Check whether a repository is practical for AI coding agents to modify and test.

## Suggested Topics

- ai-agent
- codex
- testing
- testability
- docker
- cli
- developer-tools
- automation
- code-review
