# How To Maintain

This document is dedicated to maintainers of GETTSIM.

## Versioning

GETTSIM's versioning is inspired by [semantic versioning](https://semver.org). Thus, for
a given version number `major.counter`

- `major` is incremented when we make incompatible API changes, for example, changing
  the arguments to `main` in a major way or we completely change the modelling of some
  taxes or transfers.
- `counter` is incremented when we add functionality to the taxes and transfers system
  or change it in some non-fundamental way.

See the
[Zulip discussion](https://gettsim.zulipchat.com/#narrow/channel/250516-Development-Workflow/topic/Releases/near/533746861)
on the topic that happened just before releasing GETTSIM 1.0.

## Branching Model

The branching model for GETTSIM is very simple.

1. New major and minor releases of GETTSIM are developed on the main branch.

1. For older major releases there exist branches for maintenance called `[major].x`, for
   example, `1.x`. These branches are used to develop new patch versions.

   Once a major version will not be supported anymore, the maintenance branch should be
   deleted.

(release_major_minor)=

## How To Release

To release a new major or minor version of GETTSIM, do the following.

1. To start the release process for any new version, e.g., `v1.1`, first
   [create a new milestone](https://github.com/ttsim-dev/gettsim/milestones/new) on
   Github. Set the name to the version number (format is `v[major].[counter]`, in this
   example: `v1.1`) to collect issues and PRs.

   A consensus among developers determines the scope of the new release. Note that
   setting up the milestone and determining the scope of the release will typically
   happen quite some time before the next steps.

1. Once all PRs in a milestone are closed:

   1. Create a PR to do some final changes.

   1. Update {ref}`changes` with all necessary information regarding the new release.

   1. Merge the changes from a.-b. into the main branch.

   1. In case of a major release, create a maintenance branch `[major - 1].x`, i.e.,
      `1.x` in case of releasing `v2.0`.

1. Go to the [page for releases](https://github.com/ttsim-dev/gettsim/releases) and
   draft a new release.

   - Have Github create a new tag `vX.Y` automatically upon releasing.
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

In the following, we will consider the example where GETTSIM's stable version is `2.1`.
There is a maintenance branch `1.x` to receive patches for the `1.x` line of releases.
And a critical bug was found, which should be fixed for both `2.2` and in `1.27`.

1. Create a PR containing the bug fix which targets the main branch.

1. Add a note to the release notes for version 2.2.

1. Squash merge the PR into main and note down the commit sha.

1. Create a new PR against branch `1.x`. Call the branch for the PR
   `backport-pr[No.]-to-1.x` where `[No.]` is the PR number.

1. Use `git cherrypick -x <commit-sha>` with the aforementioned commit sha to apply the
   fix to the branch. Solve any merge conflicts, etc..

1. Add the PR to the milestone for version `1.27` so that all changes for a new release
   can be collected.

1. The release process for a patch version works as above in {ref}`release_major_minor`,
   steps 2.-4.. Of course whenever the above mentions `main`, replace that by `1.x`.

## FAQ

% The following question is duplicated in `how-to-contribute.rst`.

**Question**: I want to re-run the tests defined in the Github Actions workflow because
some random error occurred, e.g., a HTTP timeout error. How can I do it?

**Answer**: Starting from the Github page of the PR, select the tab called "Checks". In
the upper right corner you find a button to re-run all checks. Note the option is only
available for failed builds.
