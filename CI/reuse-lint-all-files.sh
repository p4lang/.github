#! /bin/bash

# SPDX-FileCopyrightText: 2026 The P4 Language Consortium
#
# SPDX-License-Identifier: Apache-2.0

uvx reuse lint
ec=$?
if [ $ec -ne 0 ]; then
    echo "::error::New or modified files in this PR, listed above, failed copyright or license checks.  See https://github.com/p4lang/.github/blob/main/copyright-and-license-issues/README-choosing-copyright-holder-and-license-for-new-files.md"
fi

exit $ec
