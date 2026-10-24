# Contributing

These are team's developer standards.

## Coding Rules

- **Language:** Python 3.12 for everything. JavaScript, HTML, and CSS only for comparison web page.
- **Names:** 'snake_case' for variables, functions, folders, files, and JSON keys.
'PascalCase' for classes. 'camelCase' in JavaScript
- **Units in names:** if a number has a unit, put it in the name, like 'duration_s', 'bitrate_kbps', or 'ms_per_frame'.
- **Small functions:** one function does one thing, with a short docstring.
- **No hard-coded paths or settings:** put settings in the config file.
- **Errors:** stop wuth a clear error message. Never hide errors with an empty 'except'.
- **Libraries:** list each one with its version in 'requirements.md'. MIT, BSD, or Apache licenses only, and include a copy of each license in the repository.
- **Tests:** use pytest, with small fake data. Test shared code in 'common', manifest reading and checking, segment and fram math, and the compiler's choices. No coverage percentage.


## Formatting Rules

- **Python:** format with Black ('back .' before you commit).
- **JavaScript, HTML, and CSS:** format with Prettier (default configuration). 2 spaces, no tabs.
- **Comments:** explain why, in plain words. Delete commented-out code before pushing. The Oxford comma is required.


## Git Rules

Nobody pushes straight to 'main'. Every change goes through a pull request with two teammate reviews.

1. Pull the latest 'main'.
2. Make a branch name 'yourname/short-task' (eg: 'aryan/base-rung-encode')
3. Commit often. Describe each commit with proper convention and description.
4. Push your branch at the end of every work session. Open a PR when a small piece works, saying what you changes and how you tested it. Draft PRs are welcome.
5. Two teammates review and approve, one of them your review partner. Try to review within 2 days.
6. After approval, rebase on the latest 'main', check the tests, then use "squash and merge" and delete your branch.

# Other Rules

- Trach tasks in Github Issues and liknk the issue in your PR.
- Never commit video files, model files ('.onnx'), output folders, or passwords and API keys.
- Keep your branch current with 'git pull --rebase origin main'. Only rebase your own branch, and push with 'git push --force-with-lease'.