# GEP 0 — Purpose and Process

```{list-table}
- * Author
  * [Hans-Martin von Gaudecker](https://github.com/hmgaudecker)
- * Status
  * Provisional
- * Type
  * Process
- * Created
  * 2019-10-22
- * Resolution
  * [Accepted](https://gettsim.zulipchat.com/#narrow/stream/309998-GEPs/topic/General/near/178834568)
```

## What is a GEP?

GEP stands for GETTSIM Enhancement Proposal. A GEP is a design document providing
information to the GETTSIM community, or describing a new feature for GETTSIM or its
processes or environment. The GEP should provide a concise technical specification of
the feature and a rationale for the feature.

We intend GEPs to be the primary mechanisms for proposing major new features, for
collecting community input on an issue, and for documenting the design decisions that
have gone into GETTSIM. The GEP author is responsible for building consensus within the
community and documenting dissenting opinions.

Because the GEPs are maintained as text files in a versioned repository, their revision
history is the historical record of the feature proposal [^id3].

### Types

There are three kinds of GEPs:

1. A **Standards Track** GEP describes a new feature or implementation for GETTSIM.
1. An **Informational** GEP describes a GETTSIM design issue, or provides general
   guidelines or information to the Python community, but does not propose a new
   feature. Informational GEPs do not necessarily represent a GETTSIM community
   consensus or recommendation, so users and implementers are free to ignore
   Informational GEPs or follow their advice.
1. A **Process** GEP describes a process surrounding GETTSIM, or proposes a change to
   (or an event in) a process. Process GEPs are like Standards Track GEPs but apply to
   areas other than the GETTSIM language itself. They may propose an implementation, but
   not to GETTSIM's codebase; they require community consensus. Examples include
   procedures, guidelines, changes to the decision-making process, and changes to the
   tools or environment used in GETTSIM development. Any meta-GEP is also considered a
   Process GEP.

## GEP Workflow

The GEP process begins with a new idea for GETTSIM. It is highly recommended that a
single GEP contain a single key proposal or new idea. Small enhancements or patches
often don't need a GEP and can be injected into the GETTSIM development workflow with a
pull request to the GETTSIM [repository]. The more focused the GEP, the more successful
it tends to be. If in doubt, split your GEP into several well-focused ones.

Each GEP must have a champion---someone who writes the GEP using the style and format
described below, shepherds the discussions in the appropriate forums, and attempts to
build community consensus around the idea. The GEP champion (a.k.a. Author) should first
attempt to ascertain whether the idea is suitable for a GEP. A message in [#GEPs] on
[Zulip] is the best way to go about doing this.

The proposal should be submitted as a draft GEP via a [GitHub pull request] to the
`doc/geps` directory with the name `gep-<n>.rst` where `<n>` is an appropriately
assigned two-digit number (e.g., it is `gep-00.rst` for this document). The draft must
use the {ref}`gep-x` file.

Once the PR is in place, the GEP should be announced on the in [#GEPs] on [Zulip] for
discussion. Discussion about implementation details will take place on the pull request,
but once editorial issues are solved, the PR should be merged, even if with draft
status. The [#GEPs] stream will contain the GEP upto the section titled "Backward
compatibility", so as to make it digestible to a wide audience. The [#GEPs] stream
discussion is intended to target end-users, and thus, discussion on the proposed usage
and possible impact should take place in [#GEPs].

At the earliest convenience, the PR should be merged (regardless of whether it is
accepted during discussion). Additional PRs may be made by the Author to update or
expand the GEP, or by maintainers to set its status, discussion URL, etc.

Standards Track GEPs consist of two parts, a design document and a reference
implementation. It is generally recommended that at least a prototype implementation be
co-developed with the GEP, as ideas that sound good in principle sometimes turn out to
be impractical when subjected to the test of implementation. Often it makes sense for
the prototype implementation to be made available as PR to the GETTSIM repository
(making sure to appropriately mark the PR as a WIP).

### Review and Resolution

GEPs are discussed in [#GEPs]. The possible paths of the status of GEPs are as follows:

```{image} /_static/gep-process.png

```

All GEPs should be created with the `Draft` status.

Eventually, after discussion, there may be a consensus that the GEP should be accepted —
see the next section for details. At this point the status becomes `Accepted`.

Once a GEP has been `Accepted`, the reference implementation must be completed. When the
reference implementation is complete and incorporated into the main source code
repository, the status will be changed to `Final`.

To allow gathering of additional design and interface feedback before committing to long
term stability for a feature or API, a GEP may also be marked as "Provisional". This is
short for "Provisionally Accepted", and indicates that the proposal has been accepted
for inclusion in the reference implementation, but additional user feedback is needed
before the full design can be considered "Final". Unlike regular accepted GEPs,
provisionally accepted GEPs may still be Rejected or Withdrawn even after the related
changes have been included in a release.

Wherever possible, it is considered preferable to reduce the scope of a proposal to
avoid the need to rely on the "Provisional" status (e.g. by deferring some features to
later GEPs), as this status can lead to version compatibility challenges in the wider
GETTSIM ecosystem.

A GEP can also be assigned status `Deferred`. The GEP author or a core developer can
assign the GEP this status when no progress is being made on the GEP.

A GEP can also be `Rejected`. Perhaps after all is said and done it was not a good idea.
It is still important to have a record of this fact. The `Withdrawn` status is similar
--- it means that the GEP author themselves has decided that the GEP is actually a bad
idea, or has accepted that a competing proposal is a better alternative.

When a GEP is `Accepted`, `Rejected`, or `Withdrawn`, the GEP should be updated
accordingly. In addition to updating the status field, at the very least the
`Resolution` header should be added with a link to the relevant thread in the Zulip
archives.

GEPs can also be `Superseded` by a different GEP, rendering the original obsolete. The
`Replaced-By` and `Replaces` headers should be added to the original and new GEPs
respectively.

Process GEPs may also have a status of `Active` if they are never meant to be completed,
e.g. GEP 0 (this GEP).

### How a GEP becomes Accepted

A GEP is `Accepted` by consensus of all interested contributors. We need a concrete way
to tell whether consensus has been reached. When you think a GEP is ready to accept,
post a message with a first line like:

> \## Proposal to accept GEP #\<number>: \<title>

to the Zulip stream GEPs / GEP [XY].

In the body of your message, you should:

- link to the latest version of the GEP,
- briefly describe any major points of contention and how they were resolved,
- include a sentence like: "If there are no substantive objections within 7 days from
  this message, then the GEP will be accepted; see GEP 0 for more details."

After you send the message, you should make sure to link to the message thread from the
`Discussion` section of the GEP, so that people can find it later.

Generally the GEP author will be the one to send this message, but anyone can do it –
the important thing is to make sure that everyone knows when a GEP is on the verge of
acceptance, and give them a final chance to respond. If there's some special reason to
extend this final comment period beyond 7 days, then that's fine, just say so in the
message. You shouldn't do less than 7 days, because sometimes people are travelling or
similar and need some time to respond.

In general, the goal is to make sure that the community has consensus, not provide a
rigid policy for people to try to game. When in doubt, err on the side of asking for
more feedback and looking for opportunities to compromise.

If the final comment period passes without any substantive objections, then the GEP can
officially be marked `Accepted`. You should send a follow-up message notifying the
community (celebratory emoji optional but encouraged 🎉✨), and then update the GEP by
setting its `:Status:` to `Accepted`, and its `:Resolution:` header to a link to your
follow-up message.

If there _are_ substantive objections, then the GEP remains in `Draft` state, discussion
continues as normal, and it can be proposed for acceptance again later once the
objections are resolved.

### Maintenance

In general, Standards track GEPs are no longer modified after they have reached the
Final state as the code and project documentation are considered the ultimate reference
for the implemented feature. However, finalized Standards track GEPs may be updated as
needed.

Process GEPs may be updated over time to reflect changes to development practices and
other details. The precise process followed in these cases will depend on the nature and
purpose of the GEP being updated.

## Format and Template

GEPs are UTF-8 encoded text files using the [reStructuredText] format. Please see the
{ref}`gep-x` file and the [reStructuredTextPrimer] for more information. We use [Sphinx]
to convert GEPs to HTML for viewing on the web [^id4].

### Header Preamble

Each GEP must begin with a header preamble. The headers must appear in the following
order. Headers marked with `*` are optional. All other headers are required:

```
  :Author: <list of authors' real names and optionally, email addresses>
  :Status: <Draft | Active | Accepted | Deferred | Rejected | Withdrawn | Final |
           Superseded>
  :Type: <Standards Track | Process>
  :Created: <date created on, in dd-mmm-yyyy format>
* :Requires: <gep numbers>
* :GETTSIM-Version: <version number>
* :Replaces: <gep number>
* :Replaced-By: <gep number>
* :Resolution: <url>
```

The Author header lists the names, and optionally the email addresses of all the authors
of the GEP. The format of the Author header value must be

> Random J. User \<<mailto:address@dom.ain>>

if the email address is included, and just

> Random J. User

if the address is not given. If there are multiple authors, each should be on a separate
line.

## Discussion

- Reference to any discussions on PRs etc.

## References and Footnotes

## Acknowledgements

This document has been slightly adapted from NumPy's
`NEP 0 <https://numpy.org/neps/nep-0000>`.

## Copyright

This document has been placed in the public domain.

[^id3]: This historical record is available by the normal git commands for retrieving older
    revisions, and can also be browsed on
    [GitHub](https://github.com/ttsim-dev/gettsim/tree/main/docs/geps).

[^id4]: The URL for viewing GEPs on the web is
    <https://gettsim.readthedocs.io/en/latest/geps>.

[#geps]: https://gettsim.zulipchat.com/#narrow/stream/309998-GEPs
[github pull request]: https://github.com/ttsim-dev/gettsim/pulls
[repository]: https://github.com/ttsim-dev/gettsim
[restructuredtext]: http://docutils.sourceforge.net/rst.html
[restructuredtextprimer]: http://www.sphinx-doc.org/en/stable/rest.html
[sphinx]: http://www.sphinx-doc.org/en/stable/
[zulip]: https://gettsim.zulipchat.com/
