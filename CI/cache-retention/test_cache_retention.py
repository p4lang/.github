# SPDX-FileCopyrightText: 2026 The P4 Language Consortium
#
# SPDX-License-Identifier: Apache-2.0

import contextlib
import io
import unittest
import urllib.error
from unittest.mock import call, patch

import cache_retention as retention


def cache(
    number,
    scope="main",
    family="bazel-v2-Linux-build",
    ref=None,
    version="v1",
    size=100,
    accessed=None,
):
    if ref is None:
        ref = (
            "refs/heads/main"
            if scope == "main"
            else f"refs/pull/{scope.split('-')[1]}/merge"
        )
    return {
        "id": number,
        "key": f"{family}-{scope}-{number}-1",
        "ref": ref,
        "version": version,
        "size_in_bytes": size,
        "created_at": f"2026-11-01T00:00:{number:02}Z",
        "last_accessed_at": f"2026-11-01T00:00:{accessed if accessed is not None else number:02}Z",
    }


class RetentionTests(unittest.TestCase):
    def evictions(
        self, caches, open_prs=(), pr_budget=10000, total_budget=10000, **kwargs
    ):
        with contextlib.redirect_stdout(io.StringIO()):
            return set(
                retention.select_evictions(
                    caches, set(open_prs), pr_budget, total_budget, **kwargs
                )
            )

    def test_newest_per_key_ref_and_version(self):
        caches = [
            cache(1),
            cache(2),
            cache(3, version="v2"),
            cache(4, family="bazel-v2-Darwin-build"),
            cache(5, "pr-689"),
            cache(6, "pr-689"),
        ]
        self.assertEqual(self.evictions(caches, {689}), {1, 5})

    def test_closed_pr_mismatched_ref_and_merge_queue(self):
        caches = [
            cache(1, "pr-689"),
            cache(2, "pr-690"),
            cache(3, "pr-689", ref="refs/pull/999/merge"),
            cache(4, ref="refs/heads/gh-readonly-queue/main/test"),
        ]
        self.assertEqual(self.evictions(caches, {689}), {2, 3, 4})

    def test_ccache_job_suffix_and_pr_number_boundaries(self):
        caches = [
            cache(1, "pr-689-unit-tests", family="ccache-v2-Linux"),
            cache(2, "pr-689-unit-tests", family="ccache-v2-Linux"),
            cache(3, "pr-689-other-job", family="ccache-v2-Linux"),
            cache(4, "pr-6890", ref="refs/pull/689/merge"),
        ]
        self.assertEqual(self.evictions(caches, {689}), {1, 4})

    def test_pr_budget_evicts_least_recently_used(self):
        caches = [cache(1, "pr-689", accessed=9), cache(2, "pr-690", accessed=3)]
        self.assertEqual(self.evictions(caches, {689, 690}, pr_budget=100), {2})

    def test_unmanaged_caches_count_toward_total_budget(self):
        caches = [cache(1), cache(2, "pr-689"), cache(3, family="other", size=800)]
        self.assertEqual(self.evictions(caches, {689}, total_budget=900), {2})

    def test_main_is_kept_even_over_budget(self):
        self.assertEqual(self.evictions([cache(1), cache(2)], total_budget=0), {1})

    def test_custom_prefix_and_default_branch(self):
        caches = [
            cache(1, family="custom", ref="refs/heads/master"),
            cache(2, family="custom", ref="refs/heads/master"),
            cache(3, "pr-690"),
        ]
        self.assertEqual(
            self.evictions(caches, prefixes=("custom-",), default_branch="master"), {1}
        )

    def test_unrecognized_keys_are_untouched(self):
        keys = [
            "bazel-v2-",
            "bazel-v2-build-main-hash-1",
            "bazel-v2-build-main-123-x",
            "old-cache",
        ]
        caches = [dict(cache(i), key=key) for i, key in enumerate(keys)]
        self.assertEqual(self.evictions(caches, total_budget=0), set())


class ApiTests(unittest.TestCase):
    def test_paginate_cache_and_pr_responses(self):
        for path, field in (
            ("actions/caches", "actions_caches"),
            ("pulls?state=open", None),
        ):
            with self.subTest(path=path):
                batches = [list(range(100)), [100]]
                responses = [{field: batch} for batch in batches] if field else batches
                with patch.object(retention, "api", side_effect=responses) as api:
                    self.assertEqual(
                        list(retention.pages(path, field)), list(range(101))
                    )
                    sep = "&" if "?" in path else "?"
                    self.assertEqual(
                        api.call_args_list,
                        [
                            call(f"{path}{sep}per_page=100&page=1"),
                            call(f"{path}{sep}per_page=100&page=2"),
                        ],
                    )

    def test_uses_calling_repository_and_token(self):
        env = {
            "GITHUB_REPOSITORY": "p4lang/PI",
            "GH_TOKEN": "test-token",
            "GITHUB_API_URL": "https://api.github.com",
        }
        with patch.dict(retention.os.environ, env), patch.object(
            retention.urllib.request, "urlopen"
        ) as urlopen:
            urlopen.return_value.__enter__.return_value.read.return_value = b""
            self.assertIsNone(retention.api("actions/caches/42", method="DELETE"))
            request = urlopen.call_args.args[0]
            self.assertEqual(
                request.full_url,
                "https://api.github.com/repos/p4lang/PI/actions/caches/42",
            )
            self.assertEqual(request.get_method(), "DELETE")
            self.assertEqual(request.get_header("Authorization"), "Bearer test-token")

    def run_main(self, args, error=None):
        with patch.object(
            retention, "pages", side_effect=[[cache(1), cache(2)], []]
        ), patch.object(
            retention, "api", side_effect=error
        ) as api, contextlib.redirect_stdout(
            io.StringIO()
        ):
            retention.main(args)
            return api.call_args_list

    def test_script_defaults_to_dry_run(self):
        self.assertEqual(self.run_main([]), [])

    def test_apply_deletes_only_selected_ids(self):
        self.assertEqual(
            self.run_main(["--apply"]), [call("actions/caches/1", method="DELETE")]
        )

    def test_already_deleted_cache_is_ignored(self):
        error = urllib.error.HTTPError("url", 404, "Not Found", {}, None)
        self.assertEqual(
            self.run_main(["--apply"], error),
            [call("actions/caches/1", method="DELETE")],
        )

    def test_other_api_failures_propagate(self):
        error = urllib.error.HTTPError("url", 403, "Forbidden", {}, None)
        with self.assertRaises(urllib.error.HTTPError):
            self.run_main(["--apply"], error)

    def test_invalid_inputs_fail_before_api_access(self):
        for args in (
            ["--key-prefixes", " "],
            ["--pr-budget", "-1"],
            ["--total-budget", "invalid"],
        ):
            with self.subTest(args=args), patch.object(
                retention, "pages"
            ) as pages, contextlib.redirect_stderr(io.StringIO()), self.assertRaises(
                SystemExit
            ):
                try:
                    retention.main(args)
                finally:
                    pages.assert_not_called()


if __name__ == "__main__":
    unittest.main()
