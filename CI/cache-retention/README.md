<!--
SPDX-FileCopyrightText: 2026 The P4 Language Consortium

SPDX-License-Identifier: Apache-2.0
-->

# Cache retention

A shared composite action for the per-run Bazel and ccache caches used by P4
repositories. It operates on the **calling repository**, using its `github.token`.
No checkout of the caller or personal access token is needed. The runner must
provide Bash and Python 3 (as GitHub-hosted Ubuntu runners do).

## Usage

Add a workflow to each repository that wants this retention policy:

```yaml
name: Cache maintenance
on:
  schedule:
    - cron: "23 3 * * *"
  workflow_dispatch:
permissions:
  actions: write
  pull-requests: read
concurrency:
  group: cache-maintenance
  cancel-in-progress: false
jobs:
  prune:
    runs-on: ubuntu-latest
    steps:
      - uses: p4lang/.github/CI/cache-retention@main
        with:
          key-prefixes: |
            bazel-v2-
            ccache-v2-
          pr-budget: "2000000000"
          total-budget: "9000000000"
```

Use a commit SHA instead of `main` to pin a particular action revision. Set
`dry-run: "true"` to print proposed deletions without applying them. Publishing
the action does not automatically enable it in other repositories.

## Cache key contract

Managed keys must start with a configured prefix and end in
`-<run_id>-<run_attempt>`. Before this suffix, the key must end in either:

- `-main`, for caches on the default branch;
- `-pr-<number>`, optionally followed by `-<job>`, for PR merge-ref caches.

For example:

```text
bazel-v2-Linux-X64-ubuntu26-toolchain-build-main-12345-1
bazel-v2-Linux-X64-ubuntu26-toolchain-build-pr-689-12346-1
ccache-v2-Linux-X64-clang-pr-689-unit-tests-12347-2
```

Include compiler, runner-image, and build configuration identifiers in the key
where necessary. This action manages retention; restore prefixes must still
prevent reuse of incompatible toolchains.

## Retention policy

- Keep the newest cache for each logical key, Git ref, and cache version.
- Always keep that newest `main` cache, even if storage targets cannot be met.
  The branch defaults to the repository's default branch; the key scope stays
  `main`. Override `default-branch` if needed.
- Remove managed caches for closed PRs, mismatched PR refs, and other refs
  (including merge queues).
- Evict remaining PR caches by least-recent access until both budgets are met.
- Leave unconfigured prefixes and keys without a numeric run/attempt suffix
  untouched. They still count toward the total storage target.

Prefixes are whitespace-separated, not globs. They default to `bazel-v2-` and
`ccache-v2-`. Budgets are nonnegative byte counts and default to 2 GB for PR caches
and 9 GB total. GitHub's own cache eviction still applies. Since the newest main
caches and unmanaged caches are retained, `total-budget` is a target, not a hard
limit.

The optional `token` input defaults to `github.token`. It needs `actions: write`
and `pull-requests: read` in the caller. Use this action in scheduled or manual
maintenance workflows with those permissions.

## Development

Run the standard-library tests from the repository root:

```sh
python3 -B -m unittest discover -s CI/cache-retention -p 'test_*.py' -v
```

The script can also run directly; it defaults to a dry run unless `--apply` is
given. Set `GH_TOKEN` and `GITHUB_REPOSITORY` (for example, `p4lang/PI`).
