<!--
SPDX-FileCopyrightText: 2026 The P4 Language Consortium

SPDX-License-Identifier: Apache-2.0
-->

# Introduction

If you are adding a new file to a p4lang repository, you should add a
copyright notice and a license annotation in the new file.

While there are software tools that can help automate the process of
adding such annotations to a file using a syntax that can be
automatically validated in p4lang project CI checks on Github (see the
["Using REUSE
..."](#using-reuse-to-automate-the-process-of-adding-copyright-and-license-annotations)
section below), those tools _cannot_ tell you who the copyright holder
should be, nor what license the file should have.  You must use your
best judgement to determine those, using the guidelines described in
this document.

If you still have questions not addressed by this document, please ask
in a Github issue in a relevant p4lang project where you wish to add
the file.  You may also find this article useful:
+ https://reuse.software/faq


# Determining the copyright holder

Did you use AI tools to write the file?  If yes, you should find
documentation for that AI tool that describes what your choices are
regarding the legal entity that is the copyright holder of that file.

Important aside: This might not be as easy as it sounds.  It is an
active area of legal consideration who the copyright holder of such
AI-generated files are.  In some countries (e.g. the USA), if no
person contributes significantly to the content of a file, it _cannot_
have a copyright holder at all, should likely be considered part of
the public domain, and thus cannot have a license associated with it
(because there is _no_ copyright holder who can assert their copyright
rights to choose what restrictions or permissions hold for what others
can do with it).

Did someone else write the file's contents, and you copied all or most
of it, e.g. from some other project's code?  In that case, hopefully
there are one or more copyright notices in the file already.  You
_MUST NOT_ remove these copyright notices, because you are not the
copyright holder -- they are.  Hopefully the file already contains a
license annotation as well, or the project that you copied the file
from has an overall license published for it.  you _MUST NOT_ change
these license annotations, because you are not the copyright holder.
If that license is Apache-2.0, or one of a short list of other
licenses that are compatible in combining in the same executable with
Apache-2.0 licensed code (e.g. BSD-2-Clause, BSD-3-Clause, MIT,
FSFAP), then it is fine to add it to a p4lang repository.  If it is
any copyleft license (e.g. GPL-2.0-only, GPL-3.0-only), then see the
[Copyleft
licenses](#exceptions-to-using-apache-2.0---copyleft-licenses) section
below.

Did you write the file completely or mostly by your own efforts?
Then the two main possibilities are:

+ You did this as part of working for some corporation, who paid you
  to do this work.  You should check with your manager, because they
  might prefer that you use the name of the corporation as the
  copyright holder.  Many files in the p4lang repositories have
  companies such as "Barefoot Networks, Inc.", "Cisco Systems, Inc.",
  "VMware, Inc.", etc. as the copyright holder, because their authors
  worked for that company at the time they wrote the contents of the
  file, as part of their job.
+ You did this on your own time, using your own computing resources.
  In this case you have the option to make yourself the copyright
  holder.  If you wish, you can choose to use "The P4 Language
  Consortium" as the copyright holder, but this is not required.

If you have a more complicated scenario, e.g. a file consists half of
code copied from a GPL-2.0-only licensed project, and half from a
BSD-2-Clause licensed project, then you should not add the file to any
p4lang repository in that form.  Separate the code with different
licenses into different files, and then apply the guidelines in this
document to each of those separate files.  If you still have
questions, ask in a Github issue on an appropriate p4lang project
before submitting the code.

Note: Except for the suggestion of using "The P4 Language Consortium"
as the copyright holder for files you write on your own personal time,
all of the above in this section applies to _every_ software you work
on and project that you add files to, not only to files added to
projects in the p4lang Github organization.


# Determining the copyright year

If there is no existing copyright notice, and you are adding a new
one, we recommend that you use a single year that is the year the file
was first developed.  Yes, many projects and companies have other
policies, but there are good arguments (unfortunately at an article
linked from [this FAQ
page](https://reuse.software/faq/#years-copyright) that no longer
works) for using the year the file was first developed, and leaving it
that way without updating it later.  Sure, if the file is rewritten
completely or substantially from scratch, updating the year makes
sense, but otherwise leaving the copyright year unchanged when
modifying the file is a legally defensible choice.


# Determining the license

If you as an indidividual are the copyright holder, then you can
choose the license you wish to release the file under.  You even have
the legal option to choose to release the file under different
licenses in different projects.

If you are working for a corporation that wants to be the copyright
holder, then that corporation can choose the license.

In either of the cases above, in most cases it is strongly preferred
to choose the Apache-2.0 license for files added to a p4lang project,
unless there are good reasons to use a different license (see examples
below).  If the copyright holder agrees to the Apache-2.0 license,
please use that.


## Exceptions to using Apache-2.0 - Copyleft licenses

If the file contains source code that links to, or imports, copylefted
libraries released under GPL-2.0-only (or GPL-3.0-only) with no
exceptions, then releasing it under any license _other_ than
GPL-2.0-only (or GPL-3.0-only) would fall under the category of
[questionable legal ground](licenses-apache-and-gpl-v2.md).  If the
file is included in a p4lang repository, it should be released under
the same license as the copylefted code it is linked with (or some
license compatible with it).

A few files in p4lang repositories are released with license
GPL-2.0-only, primarily for one of the following reasons:
+ It is a test program written in Python that imports the `scapy`
  package, which is licensed GPL-2.0-only.  These test programs are
  never linked with executable binaries such as the `p4c` compiler or
  BMv2 software switch.  They are run standalone, often interacting
  with those programs over sockets or other interprocess communication
  mechanisms, and only for the purpose of testing those programs.
+ It is a source file intended to be executed within the Linux kernel,
  e.g. C source code intended to be part of an EBPF program.


## Other exceptions to using Apache-2.0 - BSD, MIT, and FSFAP licenses

Many libraries are released under BSD-2-Clause, BSD-3-Clause, MIT, or
FSFAP licenses.  To the best of our knowledge, it is [legally
acceptable](licenses-apache-and-bsd.md) to link such code with
executable binaries that are released under the Apache-2.0 license.
Many libraries whose source code has been copied into p4lang
repositories have one of these license.  They are often within a
directory called `third-party` or `third_party`.



# Using REUSE to automate the process of adding copyright and license annotations

In many Python installation scenarios, you can install the
[REUSE](https://pypi.org/project/reuse) Python package using this
command:
```sh
pip3 install reuse
```
If you are using some Python installation where that does not work for
you, hopefully it is because you use some tailored Python installation
environment, and you already know what you should be using instead of
the command above.

Once the REUSE package is installed, you can use it to add copyright
and licnese annotations to most source code files that following
common file name conventions using a command like the following:
```sh
reuse annotate -c "the copyright holder" -y 2026 -l Apache-2.0 <path-to-source-file>
```

See the [SPDX license list](https://spdx.org/licenses/) web page for
the string to use other than `Apache-2.0` for other licenses.

You may want to use the `--style` command line option in that command
if `reuse` does not correctly identify the comment syntax for the
file.  For example, to force it to use Python style comments beginning
with `#`, use this:
```sh
reuse annotate --style python -c "the copyright holder" -y 2026 -l Apache-2.0 <path-to-source-file>
```

Use this command to see other style names recognized by REUSE:
```sh
reuse annotate --help
```

If the file is a binary file (e.g. PNG, JPG, etc.) or a text data file
format that does not have a comment syntax (e.g. JSON data files), add
a `--fallback-dot-license` command line option to the command above,
as shown in the example below:
```sh
reuse annotate --fallback-dot-license -c "the copyright holder" -y 2026 -l Apache-2.0 <path-to-source-file>
```
This will create a new file whose name is the same as the original
file name, with a suffix of `.license` appended at the end.  That file
will contain the copyright and license annotation.  This is a
convention used by the REUSE project.

If you are annotating source files for a third party library copied
into a p4lang repository, you may also wish to use
`--force-dot-license` instead of `--fallback-dot-license`, so that a
`.license` file is created even though the file has a comment syntax.
For example, this can make it easier when doing `diff` between the
copied code and the original source it came from, and when updating
the copy in the p4lang repository to a newer version.
