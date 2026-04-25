# CLAUDE.md

## Code review conventions

Always follow @pablodiegoss's review feedback when handling issues or PRs in
this repo. He is the maintainer; his guidance overrides the original
suggestion in an issue when they disagree.

Examples from past issues:
- #855 (`Post.get_absolute_url`): Pablo said the method "probably could be
  removed". Prefer deleting unused methods over fixing them.
- #854 (`profile` view `?user=`): Pablo said don't keep the dead branch with
  exception handling — remove it. Prefer dropping dead code over hardening
  it.
- #883 (Makefile): Pablo said only the `.PHONY` part is legitimate. Don't
  apply the rest of an issue's suggestion if Pablo has narrowed the scope.

When an issue's suggested fix conflicts with a Pablo comment, follow Pablo.
