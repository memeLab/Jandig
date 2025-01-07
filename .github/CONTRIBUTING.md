## Repository Policy
All contributions to ARte must be tracked by an issue and at least one pull request. To start working on an issue you must fork ARte repository and create or pick an issue. You should also check that there are no issues that already adheres to what you intend to post. To create your branch, follow the pattern: `feature/issueID-issue-title`. When you have done your first commit on your fork you have to create a pull request to ARte devel branch so we can see your work in progress. The pull request name must follow this pattern: `{STATE} {ISSUE NUMBER} - {ISSUE NAME}`, where {STATE} is the state of the pull request. All pull requests must be created with [WIP] tag, and when you think you resolved the issue, change to [REVIEW]. Example of pull request name: [WIP] 435 - Refactor create method.

## Coding Style
Make sure you are following our code style when submiting a pull request, following the style you make the process of reviewing your pull request better.

### Python code
We use [flake8](http://flake8.pycqa.org/en/latest/) standard rules and [pep8](https://www.python.org/dev/peps/pep-0008/?) for code style.

### JavaScript code
We use [standardjs](https://standardjs.com/) for code style.

### HTML and Jinja2
Elements ids must init with the word "id" followed by a underscore and the name of the id e.g. ```html id="id_menu-bar"```. Elements classes only have the name e.g. ```html class="menu-bar"```
