<!--
SPDX-FileCopyrightText: 2026 The P4 Language Consortium

SPDX-License-Identifier: CC-BY-4.0
-->

# The p4lang release App

The shared release workflows in this repo authenticate as a GitHub App to
(a) create monthly release PRs that trigger CI (PRs made with the built-in
`GITHUB_TOKEN` cannot), and (b) notify p4lang/packages when a release is
published. This documents the App's configuration; creating or changing it
needs org-admin permissions. For the mechanics, see GitHub's docs on
[registering an App](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/registering-a-github-app),
[managing its private keys](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/managing-private-keys-for-github-apps),
[installing it](https://docs.github.com/en/apps/using-github-apps/installing-your-own-github-app),
and org-level [variables](https://docs.github.com/en/actions/learn-github-actions/variables)
and [secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions).

## Configuration

The App (`p4lang-release`, owned by the p4lang org):

- **Repository permissions**: Contents read/write, Pull requests read/write.
  Nothing else, and no webhook.
- **Installed on**: `packages`, `PI`, `behavioral-model`, `p4c`, `p4pi`, `ptf`.
  - `packages` is included because the publish workflow mints a token scoped to
    it. The other five run the workflows.

- Org variable `RELEASE_APP_ID`: the App ID. (This isn't sensitive.)
- Org secret `RELEASE_APP_PRIVATE_KEY`: a full private-key `.pem`, including
  the BEGIN/END lines.

## Key rotation

Generate a new private key on the App, update the org secret with it, then
revoke the old key. No workflow changes are needed.
