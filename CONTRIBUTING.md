# Contributing

These are team's developer standards.

## Coding Rules

- **Language:** Python 3.12 for everything. JavaScript, HTML, and CSS only for comparison web page.
- **Names:** 'snake_case' for variables, functions, folders, files, and JSON keys. 'PascalCase' for classes. 'camelCase' in JavaScript.
- **Units in names:** if a number has a unit, put it in the name, like 'duration_s', 'bitrate_kbps', or 'ms_per_frame'.
- **Small functions:** one function does one thing, with a short docstring.
- **No hard-coded paths or settings:** put settings in the config file.
- **Errors:** stop wuth a clear error message. Never hide errors with an empty 'except'.
- **Libraries:** list each one with its version in 'requirements.md'. MIT, BSD, or Apache licenses only, and include a copy of each license in the repository.
- **Tests:** use pytest, with small fake data. Test shared code in 'common', manifest reading and checking, segment and fram math, and the compiler's choices. No coverage percentage.
- **Main:** use `if(__name__ == "__main__"):` for the main portion.


## Formatting Rules

- **Python:** format with Black (`black .` before you commit).
- **JavaScript, HTML, and CSS:** format with Prettier (default configuration). 2 spaces, no tabs.
- **Comments:** explain why, in plain words. Delete commented-out code before pushing. The Oxford comma is required.


## Git Rules

Nobody pushes straight to `main`. Every change goes through a pull request with two teammate reviews.

1. Pull the latest `main`.
2. Make a branch name 'yourname/short-task' (eg: 'aryan/base-rung-encode')
3. Commit often. Describe each commit with proper convention and description.
4. Push your branch at the end of every work session. Open a PR when a small piece works, saying what you changes and how you tested it. Draft PRs are welcome.
5. Two teammates review and approve, one of them your review partner. Try to review within 2 days.
6. After approval, rebase on the latest 'main', check the tests, then use "squash and merge" and delete your branch.

## Other Rules

- Track tasks in Github Issues and liknk the issue in your PR.
- Never commit video files, model files (`.onnx`), output folders, or passwords and API keys.
- Keep your branch current with `git pull --rebase origin main`. Only rebase your own branch, and push with `git push --force-with-lease`.

## Documentation Rules

These rules may change, but they will be changed, only with warning.  It is the responsibility of the ones changing the standards to retroactively apply them, not the original developer.

### Basics

- **Docstrings:** Docstrings follow the very basic format:
```python
def func_name(param1, param2):
    """Basic, one line Summary here."
    
    More comprehensive explenation here
    
    Section:
        Section body
    """
```
- **Root Style:** We generally follow [Google Style Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings), however, if there is a disagreement between our documentation and the Google Style rules, follow what is written here.
- Docstrings are started and ended with three double quotes (""").
- **Basic Content:** All docstrings should be substantive, with enough information to call the function without the actual code
- **Side effects:** Side effects must be listed within within the description.
- **Required Docstrings:** Modules (.py files), class, functions, and methods are required to have docstrings.
- **Exceptions:** Test classes, functions, and methods do not have to have a docstring.
- **Sections:** Not all sections are required, only the ones that are relevant.

### Modules

- **Location:** Module (.py files) docstrings start at the first line of the file
- **Sections:** No Dedicated sections for Modules

### Classes

- **Location:** Class Docstrings begin the line immediately after tha class decleration.
- **Sections:**
    - **Attributes:** lists the name, intended type, and description of atributes as fllows
    ```
    Attributes:
            Name (type): short description
            Name2: short description
    ```
    - **Methods:** Lists the Methods of a class and what they are used for.
    ```
    Methods: 
        name: Short description
    ```
    
### Functions & Methods

- **Location:** Function and Method docstring begin shortly after their declaration.
- **Sections:**
    - Parameters and Arguments
    ```Parameters:
        Name (Expected type): Short Explanation.
        Name2 (Expected): Short Explanation.
    ```
    - Return and Returns
    ```Returns:
        Short Description of return, make sure to clarify type
    ```
    - Raises and Raise
    ```Raises:
	    Exception_name: Explanation of cause case
    ```
    - Example and Examples
    ```Examples:
        Explanation of a use case
        Explanation of another use case
    ```

### Important docstrings details

- Summary lines must end with a period, exclemation mark, or a question mork.
- There must be an empty line (excluding indentation) between the summary and the rest of the docstring.
- The ending 3 double quotes must be on their own line.
