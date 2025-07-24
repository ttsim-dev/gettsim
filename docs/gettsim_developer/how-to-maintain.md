# How To Maintain

This document is dedicated to maintainers of GETTSIM.

## Versioning

GETTSIM adheres in large parts to [semantic versioning](https://semver.org). Thus, for a
given version number `major.minor.patch`

- `major` is incremented when you make incompatible API changes.
- `minor` is incremented when you add functionality which is backwards compatible.
- `patch` is incremented when you make backwards compatible bug fixes.

## Branching Model

The branching model for GETTSIM is very simple.

1. New major and minor releases of GETTSIM are developed on the main branch.

1. For older major and minor releases there exist branches for maintenance called, for
   example, `0.4` or `1.3`. These branches are used to develop new patch versions.

   Once a minor version will not be supported anymore, the maintenance branch should be
   deleted.

(release_major_minor)=

## How To Release Major or Minor Versions

To release a new major or minor version of GETTSIM, do the following.

1. To start the release process for any new version, e.g., `0.2`, first
   [create a new milestone](https://github.com/ttsim-dev/gettsim/milestones/new) on
   Github. Set the name to the version number (format is `v[major].[minor]`, in this
   example: `v0.2`) to collect issues and PRs.

   A consensus among developers determines the scope of the new release. Note that
   setting up the milestone and determining the scope of the release will typically
   happen quite some time before the next steps.

1. Once all PRs in a milestone are closed:

   1. Create a PR to do some final changes.

   1. Update {ref}`changes` with all necessary information regarding the new release.

   1. Merge the changes from a.-b. into the main branch.

   1. Create a maintenance branch `[major].[minor]`, i.e., `0.2` in this example.

1. Go to the [page for releases](https://github.com/ttsim-dev/gettsim/releases) and
   draft a new release.

   - Set both a new tag and the release title to `vX.Y.Z`.
   - Add the release notes. These should include the most important changes in a
     bulleted list and a reference to {ref}`changes`.
   - Release the new version by clicking "Publish release".

1. You are done!

   - The release is automatically published to [PyPI](https://pypi.org/project/gettsim/)
   - It is scraped from there by conda-forge. A PR will be created on the
     [gettsim-feedstock](https://github.com/conda-forge/gettsim-feedstock) repository,
     which will be merged automatically by the automerge bot in case all tests pass.
     [Feedstock maintainers](https://github.com/conda-forge/gettsim-feedstock#feedstock-maintainers)
     will get relevant messages.
   - After the merge is completed, the new release will be available on conda-forge
     within a day.

(backports_release_patched)=

## How to Backport and Release Patched Versions

Most changes to previously released versions come in the form of backports. Backporting
is the process of re-applying a change to future versions of GETTSIM to older versions.
As backports can introduce new regressions, the scope is limited to critical bug fixes
and documentation changes. Performance enhancements and new features are not backported.

In the following, we will consider the example where GETTSIM's stable version is
`0.2.0`. Version `0.3.0` is currently under development on the main branch. There is a
maintenance branch `0.2` to receive patches for the `0.2.x` line of releases. And a
critical bug was found, which should be fixed in both `0.3.0` and in `0.2.1`.

1. Create a PR containing the bug fix which targets the main branch.

1. Add a note to the release notes for version 0.2.1.

1. Squash merge the PR into main and note down the commit sha.

1. Create a new PR against branch `0.2`. Call the branch for the PR
   `backport-pr[No.]-to-0.2.1` where `[No.]` is the PR number.

1. Use `git cherrypick -x <commit-sha>` with the aforementioned commit sha to apply the
   fix to the branch. Solve any merge conflicts, etc..

1. Add the PR to the milestone for version `0.2.1` so that all changes for a new release
   can be collected.

1. The release process for a patch version works as above in {ref}`release_major_minor`,
   steps 2.-4.. Of course whenever the above mentions `main`, replace that by
   `maintenance_branch`.

## FAQ

% The following question is duplicated in `how-to-contribute.rst`.

**Question**: I want to re-run the tests defined in the Github Actions workflow because
some random error occurred, e.g., a HTTP timeout error. How can I do it?

**Answer**: Starting from the Github page of the PR, select the tab called "Checks". In
the upper right corner you find a button to re-run all checks. Note the option is only
available for failed builds.
