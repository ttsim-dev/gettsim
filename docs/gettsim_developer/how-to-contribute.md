# How To Contribute

Contributions are always welcome. Everything ranging from small extensions of the
documentation to implementing new features is appreciated. Of course, the bigger the
change the more it is necessary to reach out to us in advance for an discussion. You can
start an discussion by
[posting an issue](https://github.com/ttsim-dev/gettsim/issues/new/choose) which can be
a bug report or a feature request or something else.

To get acquainted with the code base, you can also check out the
[documentation](https://gettsim.readthedocs.io/en/latest/) or our
[issue tracker](https://github.com/ttsim-dev/gettsim/issues) for some immediate and
clearly defined tasks.

To contribute to the project, adhere to the following process.

## Prerequisites

- Make sure you have the following programs installed and that these can be found on
  your path:

  - [pixi](https://prefix.dev/docs/pixi/overview#installation) (Python package manager)
  - A modern text editor (e.g. [VS Code](https://code.visualstudio.com/))

- Cloning the repository works differently for regular contributors and newcomers. As a
  contributor you might have been granted privileges to push to the GETTSIM repository.
  Thus, you can clone the repository directly using

  ```shell-session
  $ git clone https://github.com/ttsim-dev/gettsim
  ```

  As a newcomer or infrequent contributor, you must first create a fork of GETTSIM which
  is a copy of the repository into your account where you have unlimited access. Go to
  the [Github page of GETTSIM](https://github.com/ttsim-dev/gettsim) and click on the
  fork button in the upper right corner. Then, clone your fork onto your disk with

  ```shell-session
  $ git clone https://github.com/<user>/gettsim
  ```

  Then, activate the environment and install the current GETTSIM version in the
  repository in development mode. Also, install pre-commits which are checks before a
  commit is accepted.

  ```shell-session
  $ pixi run pre-commit install
  ```

- Under Windows, yaml-files are by default not loaded with the correct encoding (UTF-8).
  This leads the pre-commit hook `yamllint` to erroneously detect too long lines. To fix
  the problem, set the Windows environment variable `PYTHONUTF8` to 1. See
  [here](https://dev.to/methane/python-use-utf-8-mode-on-windows-212i) for more
  information.

## Development workflow

- We always develop new features in new branches. Thus, create a new branch by picking
  an appropriate name, e.g., `elterngeld` or `update_ges_rente_beitrag`. Make sure to
  branch off from main and not any other branch.

  ```shell-session
  $ git checkout -b <branch-name>
  ```

- Now, develop the new feature on this branch. Before you commit the changes, make sure
  they pass our test suite which can be started with the following command.

  ```shell-session
  $ pixi run tests
  ```

  which will prompt you to choose a python version to run the tests with. You may choose
  the most recent one; both will be checked in our CI testing.

  Sometimes you want to push changes even if the tests fail because you need feedback.
  Then, skip this step.

- In the next step, try to commit the changes to the branch with an appropriate commit
  message.

  ```shell-session
  $ pixi run git commit -am "Add new parameters for ges_rente_beitrag in 2024."
  ```

  A commit starts the pre-commits which are additional checks, mostly formatting and
  style checks. If an error occurs, the commit is rejected. Maybe all inconsistencies
  could be changes could be fixed automatically, so just try the same commit once more.
  If you still see failures, review the log in your terminal and fix the issues that are
  reported. If an reported error is unclear to you, try to use Google for more help or
  reach out on Zulip. After fixing all issues, you need to commit the changes again.

  In case you don't even know where to start to fix the issue, append ` -n` to the above
  line with the commit. This will bypass the checks. Ask for help in the PR, this sort
  of thing is usually easily fixable in the beginning. But it can become a pain when it
  grows large.

- Push your changes to the repository. Then, go to either the official GETTSIM or your
  fork's Github page. A banner will be displayed asking you whether you would like to
  create a PR. Follow the link and the instructions of the PR template. Fill out the PR
  form to inform everyone else on what you are trying to accomplish and how you did it.

  The PR also starts a complete run of the test suite on a continuous integration
  server. The status of the tests is shown in the PR. You can follow the links to Github
  Actions to get more details on why the tests failed. Reiterate on your changes until
  the tests pass on the remote machine.

- Ask one of the main contributors to review your changes. Include their remarks in your
  changes.

- The final PR will be merged by one of the main contributors.

## Code style

- We make use of NumPy-type docstrings:
  <https://numpydoc.readthedocs.io/en/latest/format.html>
- Otherwise, we adhere to this
  [styleguide](https://estimagic.readthedocs.io/en/latest/contributing/styleguide.html)
  (which was written for estimagic).

## FAQ

% The following question is duplicated in `how-to-maintain.rst`.

**Question**: I want to re-run the tests defined in the Github Actions workflow because
some random error occurred, e.g., a HTTP timeout error. How can I do it?

**Answer**: Starting from the Github page of the PR, select the tab called "Checks". In
the upper right corner you find a button to re-run all checks. Note the option is only
available for failed builds.
