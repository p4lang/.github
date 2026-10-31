<!--
SPDX-FileCopyrightText: 2026 The P4 Language Consortium

SPDX-License-Identifier: Apache-2.0
-->

# Introduction

The following `p4c` back ends [1] [2] produce C source files that are
intended to be compiled and loaded into the Linux kernel via the EBPF
feature [3].

[1] https://github.com/p4lang/p4c/blob/main/backends/ebpf/README.md

[2] https://github.com/p4lang/p4c/blob/main/backends/tc/README.md

[3] https://ebpf.io

While there are a few examples of companies releasing binaries of
Linux driver code for their hardware that runs in the Linux kernel,
and they do not release the source code under a GPL license, we leave
it to their legal teams to navigate any of the intricacies that may be
involved in that endeavor.

Reference [4] is a good introduction to software licensing questions
related to using EBPF.

[4] https://ebpf.io/blog/ebpf-licensing-guide/

While it is _possible_ to write restricted EBPF programs that are
loaded into the Linux kernel that can be distributed under a non-GPL
license, these are the exception, not the rule.

Do companies using EBPF distribute these programs under a GPL license?
Yes, they commonly do.  The EBPF code loaded and run in the Linux
kernel is the "data plane" part of the system.  The "control plane"
part of the system runs in user space applications on Linux, and these
can be distributed under other licenses, including proprietary
licenses, just as other user space Linux applications commonly are.
In most production EBPF programs, the control plane code is far larger
and more complex then the data plane code.  The data plane code by
itself is unlikely to cause any significant loss of competitive
advantage to publicize it.


# Categorization of EBPF source files

There are (at least) these categories of source files involved in EBPF
systems:

+ (a) C source files that are intended to be compiled and loaded into
  the kernel via EBPF.

+ (b) source files (C or otherwise) that are intended to be executed
  in user space, that communicate with the EBPF program via Linux
  system calls.

+ (c) C header files that are intended to be included only from files
  of category (a).

+ (d) C header files that are intended to be included from files of
  category (a) and also from files of category (b).

For category (a), the relevant files are auto-generated as the output
of the `p4c-ebpf` or `p4c-pna-p4tc` P4 compilers.  These
auto-generated C programs have `#include` directives for a few header
files.  See later in this document for a list of these.

For category (b), these programs are not auto-generated (at least not
by `p4c-ebpf` or `p4c-pna-p4tc`).  It is up to developers using EBPF
to write them, and choose what license they wish to use.

While we could try hard to distinguish whether a header file included
by files in category (a) was in category (c) or (d), i.e. whether
anyone ever plans to include the header file from a file in category
(b), it is easier to simply assume that all such header files _might_
be included from a file in category (b), and thus all such included
files are in category (d).


# What licenses are appropriate for each category of source files?

<!-- REUSE-IgnoreStart -->

As was mentioned earlier, GPL-2.0-only is a safe choice for files in
category (a).  For the purposes of using files in category (c) or (d)
in programs compiled then loaded into the Linux kernel, GPL-2.0-only
is also a good choice for files in those categories.

For files in category (b), we as developers of `p4c` would like to
enable developers to use any license they wish, e.g. copyleft,
Apache-2.0, some proprietary license, etc.  Note that licensing files
in category (d) as GPL-2.0-only would prevent those files from being
included in category (b) programs, unless the category (b) program
were also licensed GPL-2.0-only (and perhaps a short list of closely
related copyleft licenses).

A common solution used in this scenario is to make files in category
(d) have a dual license, e.g. GPL-2.0-only or BSD-2-Clause.  A
dual-licensed file enables a developer to include the file in programs
with a GPL-2.0-only license, where they would choose to use the file
with the GPL-2.0-only license, and also to include the same file in
programs with a proprietary license, where they would choose to use
the file with the BSD-2-Clause license.


# Summary of recommendations for `p4lang` projects

From everything described in this article, using the following dual
license for all files in category (d) for `p4lang` projects seems to
be a choice that gives very clear intention that it can be used in a
program loaded into the Linux kernel (where the developer would chose
the GPL-2.0-only license), and also in programs of category (b) that
have whatever license the developer wishes to use (where the developer
would choose the BSD-2-Clause license).

```
SPDX-License-Identifier: GPL-2.0-only or BSD-2-Clause
```

For the version of `p4c` repository source code analyzed later in this
article, this is the complete list of source files that should have
this license:

+ `backends/ebpf/runtime/ebpf_kernel.h`
+ `backends/ebpf/runtime/ebpf_common.h`
+ `backends/tc/runtime/include/pna.h`


# What licenses do other projects use for files in category (d)?


## `bpftool` version with tag `v7.3.0`

Among `bpftool`'s `.c` files with a dual license, they all use one of
the following:

+ `GPL-2.0-only OR BSD-2-Clause`
+ `LGPL-2.1 OR BSD-2-Clause`
+ `GPL-2.0-or-later OR BSD-2-Clause`

All of its `.h` files with a dual license use this:

+ `GPL-2.0-only OR BSD-2-Clause`

I have not tracked down an authoritative answer to why some of these
dual licensed files are not exactly the same dual license as each
other.  However, according to answers generated by some chats with
LLMs, one possible answer is that they were developed by different
people at different times, who made slightly different choices of dual
license.  Changing the license of a file requires permission from all
copyright holders, which in some cases is everyone who modified the
file, and getting such permission can be a difficult and
time-consuming process, for little or no practical gain, especially if
the existing license achieves the desired goal.

The same LLM chats suggest that between the choices of `GPL-2.0-only
OR BSD-2-Clause` versus `LGPL-2.1 OR BSD-2-Clause`, there may be
potential problems with using `LGPL-2.1` in header files included from
programs to be loaded into the Linux kernel, and that `GPL-2.0-only`
is a choice that makes it clearer that such a program can be loaded
into the Linux kernel.


## `libbpf` version with tag `v1.3.0`

All `.c` files with a dual license use this:

+ `LGPL-2.1 OR BSD-2-Clause`

Of `libbpf`'s `.h` files with a dual license, they all use one of the
following:

+ `LGPL-2.1 OR BSD-2-Clause`
+ `((GPL-2.0 WITH Linux-syscall-note) OR BSD-3-Clause)`

<!-- REUSE-IgnoreEnd -->


# Files included by category (a) source files generated by `p4c`


## Version of `p4c` source code used in the examples below

As of this version of the `p4c` repository, the latest as of 2026-Oct-25:
```
$ git log -n 1 | cat
commit 9b1d2949441ecef39a76a6d17c9c59ac62dfd240
Author: thecoolguy <97456331+Keshavkumar04@users.noreply.github.com>
Date:   Sun Oct 25 16:41:46 2026 +0000
```

It builds `p4c` executables with the version number shown below:
```
$ p4c --version
p4c 1.2.5.18 (SHA: 64ff00a48f BUILD: Release)
```


## Version of `bpftool` and `libbpf` used by `p4c`

For the version of `p4c` in the previous section, the version of
`bpftool` used while building `p4c` is its tag `v7.3.0`.  Search for
`bpftool` in https://github.com/p4lang/p4c/blob/main/tools/ci-build.sh

If you execute the command:
```
git submodule update --init --recursive
```
in the above version of `bpftool` source code, it clones `libbpf` as a
submodule with a version that matches tag `v1.3.0` of `libbpf`.


## Example of output of `p4c-ebpf`

The following assumes that you have installed the `p4c-ebpf` program
on your system.

```
$ git clone https://github.com/p4lang/p4c
$ cd p4c/testdata/p4_16_samples
$ p4c-ebpf action_call_ebpf.p4 -o action_call_ebpf.c
```

The last command creates these two C source files:

+ `action_call_ebpf.c`
+ `action_call_ebpf.h`

The `.c` file contains this line:
```
char _license[] SEC("license") = "GPL";
```

That line compiles into a part of the binary file.  When you attempt
to load this binary EBPF file into the kernel using a system call, if
the EBPF program makes any calls to GPL-only functions within the
kernel, the system call will fail the attempt to load it into the
kernel.

Below are the header files included by this generated program:

```
$ grep include action_call_ebpf.[ch]
action_call_ebpf.c:#include "action_call_ebpf.h"
action_call_ebpf.c:#include "ebpf_kernel.h"
action_call_ebpf.h:#include "ebpf_kernel.h"
```

Some of the included files above are part of the `p4c` repository
https://github.com/p4lang/p4c

Here are where all of the included files come from, including nested
includes:

+ `action_call_ebpf.c` - generated.  It includes:
  + `action_call_ebpf.h` - generated.  It includes:
    + `ebpf_kernel.h` - part of `p4c` repo at `backends/ebpf/runtime/ebpf_kernel.h`.  It includes:
      + `<stddef.h>` - part of Linux `/usr/include` files, not `p4c`
      + `<sys/types.h>` - part of Linux `/usr/include` files, not `p4c`
      + `ebpf_common.h` - part of `p4c` repo at `backends/ebpf/runtime/ebpf_common.h`.  It includes:
        + `<stddef.h>` - part of Linux `/usr/include` files, not `p4c`
        + `<sys/types.h>` - part of Linux `/usr/include` files, not `p4c`
      + `install/libbpf/include/bpf/bpf_endian.h` - part of libbpf repo
      + `contrib/bpftool/include/uapi/linux/bpf.h` - part of bpftool repo
      + `contrib/bpftool/include/uapi/linux/pkt_cls.h` - part of bpftool repo
      + `install/libbpf/include/bpf/bpf_helpers.h` - part of libbpf repo

The subset of the included files above that are in the `p4c`
repository are:
+ `ebpf_kernel.h`
+ `ebpf_common.h`


## Example of output of `p4c-pna-p4tc`

The following assumes that you have installed the `p4c-ebpf` program
on your system.

```
$ git clone https://github.com/p4lang/p4c
$ cd p4c/testdata/p4tc_samples
$ mkdir tmp
$ p4c-pna-p4tc global_action_example_01.p4 -o tmp
```

Two of the output files written to the directory `tmp` have the same
GPL license line that `p4c-ebpf` uses, because those programs are
intended to be compiled and loaded into the Linux kernel.

```
$ cd tmp
$ grep GPL *
global_action_example_01_control_blocks.c:char _license[] SEC("license") = "GPL";
global_action_example_01_parser.c:char _license[] SEC("license") = "GPL";
```

Here are the header files included by those programs:

```
$ grep include *
global_action_example_01_control_blocks.c:#include "global_action_example_01_parser.h"
global_action_example_01_parser.c:#include "global_action_example_01_parser.h"
global_action_example_01_parser.h:#include "ebpf_kernel.h"
global_action_example_01_parser.h:#include <stdbool.h>
global_action_example_01_parser.h:#include <linux/if_ether.h>
global_action_example_01_parser.h:#include "pna.h"
```

Some of the included files above are part of the `p4c` repository
https://github.com/p4lang/p4c

Here are where all of the included files come from, including nested
includes:

+ `global_action_example_01_control_block.c` (generated) includes:
+ `global_action_example_01_parser.c` (generated) includes:
  + `global_action_example_01_parser.h` (generated) includes:
    + `ebpf_kernel.h` - see previous section for details of what it includes
    + `<stdbool.h>` - part of Linux `/usr/include` files, not `p4c`
    + `<linux/if_ether.h>` - part of Linux `/usr/include` files, not `p4c`
    + `pna.h` - part of `p4c` repo at `backends/tc/runtime/include/pna.h`, includes:
      + `<stdbool.h>` - part of Linux `/usr/include` files, not `p4c`

The subset of the included files above that are in the `p4c`
repository are:
+ `ebpf_kernel.h`
+ `ebpf_common.h` (included within `ebpf_kernel.h` -- see earlier section for details)
+ `pna.h`
