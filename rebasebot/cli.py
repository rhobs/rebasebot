#!/usr/bin/python

# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""This module parses CLI arguments for the Rebase Bot."""

import argparse
from collections import namedtuple
import re
import sys
import validators

from rebasebot import bot


GitHubBranch = namedtuple("GitHubBranch", ["url", "ns", "name", "branch"])
GitBranch = namedtuple("GitBranch", ["url", "reference"])


class GitHubBranchAction(argparse.Action):
    """An action to take a GitHub branch argument in the form:

      <user or organisation>/<repo>:<branch>

    The argument will be returned as a GitHubBranch object.
    """

    GITHUBBRANCH = re.compile("^(?P<ns>[^/]+)/(?P<name>[^:]+):(?P<branch>.*)$")


    def __call__(self, parser, namespace, values, option_string=None):
        match = self.GITHUBBRANCH.match(values)
        if match is None:
            parser.error(
                "GitHub branch value for {option_string} must be in "
                "the form <user or organisation>/<repo>:[<branch>|<tag>|sha1>]"
            )

        setattr(
            namespace,
            self.dest,
            GitHubBranch(
                f"https://github.com/{match.group('ns')}/{match.group('name')}",
                match.group("ns"),
                match.group("name"),
                match.group("branch")
            ),
        )


class GitHubUserTokenAction(argparse.Action):
    """An action to take a Github token and validates it:

    The argument will be return as a str object.
    """

    def __call__(self, parser, namespace, token, option_string=None):
        with open(token, "r", encoding='utf-8') as app_key_file:
            gh_user_token = app_key_file.read().strip().encode().decode('utf-8')
            setattr(namespace, self.dest, gh_user_token)


class PrivateKeyFileAction(argparse.Action):
    """An action to take a private key and validates it:

    The argument will be return as a str object.
    """

    def __call__(self, parser, namespace, path, option_string=None):
        with open(path, "r", encoding='utf-8') as private_key:
            private_key_text = private_key.read().strip().encode()
            setattr(namespace, self.dest, private_key_text)


class SlackWebHookAction(argparse.Action):
    """An action to take a private key and validates it:

    The argument will be return as a str object.
    """

    def __call__(self, parser, namespace, path, option_string=None):
        with open(path, "r", encoding='utf-8') as app_key_file:
            slack_webhook = app_key_file.read().strip()
            setattr(namespace, self.dest, slack_webhook)

class GitBranchAction(argparse.Action):
    """An action to take a git branch argument in the form:

      <git url>:<reference>

    The argument will be return as a GitBranch object.
    """

    def __call__(self, parser, namespace, values, option_string=None):
        msg = (
            f"Git ref value for {option_string} must be in "
            f"the form <git url>:<reference>"
        )

        split = values.rsplit(":", 1)
        if len(split) != 2:
            parser.error(msg)

        url, reference = split
        if not validators.url(url):
            parser.error(msg)

        setattr(namespace, self.dest, GitBranch(url, reference))


# parse_cli_arguments parses command line arguments using argparse and returns
# an object representing the populated namespace, and a list of errors
#
# testing_args should be left empty, except for during testing
def _add_merge_args(parser):
    parser.add_argument(
        "--source",
        "-s",
        type=str,
        required=False,
        action=GitBranchAction,
        help=(
            "The source/upstream git repo to rebase changes onto in the form "
            "<git url>:<branch>. Note that unlike dest and rebase this does "
            "not need to be a GitHub url, hence its syntax is different."
        ),
    )
    parser.add_argument(
        "--ours",
        type=str,
        required=False,
        action='append',
        help=f"Files which can be resolved using 'git checkout --ours' action",
    )
    parser.add_argument(
        "--theirs",
        type=str,
        required=False,
        action='append',
        help=f"Files which can be resolved using 'git checkout --theirs' action",
    )
    parser.add_argument(
        "--update-go-modules",
        action="store_true",
        default=False,
        required=False,
        help="When enabled, the bot will update and vendor the go modules "
             "in a separate commit.",
    )

def _add_jsonnet_update_args(parser):
    pass

def _add_common_args(parser):
    _form_text = (
        "in the form <user or organisation>/<repo>:<branch>, "
        "e.g. kubernetes/cloud-provider-openstack:master"
    )

    parser.add_argument(
        "--dest",
        "-d",
        type=str,
        required=True,
        action=GitHubBranchAction,
        help=f"The destination/downstream GitHub repo to merge changes into {_form_text}",
    )
    parser.add_argument(
        "--rebase",
        type=str,
        required=True,
        action=GitHubBranchAction,
        help=f"The base GitHub repo that will be used to create a pull request {_form_text}",
    )
    parser.add_argument(
        "--git-username",
        type=str,
        required=False,
        help="Custom git username to be used in any git commits.",
        default="",
    )
    parser.add_argument(
        "--git-email",
        type=str,
        required=False,
        help="Custom git email to be used in any git commits.",
        default="",
    )
    parser.add_argument(
        "--working-dir",
        type=str,
        required=False,
        help="The working directory where the git repos will be cloned.",
        default=".rebase",
    )
    parser.add_argument(
        "--github-user-token",
        type=str,
        required=False,
        action=GitHubUserTokenAction,
        help="The path to a github user access token.",
    )
    parser.add_argument(
        "--github-app-id",
        type=int,
        required=False,
        help="The app ID of the GitHub app to use.",
        default=137509,
    )
    parser.add_argument(
        "--github-app-key",
        type=str,
        required=False,
        action=PrivateKeyFileAction,
        help="The path to a github app private key.",
    )
    parser.add_argument(
        "--github-cloner-id",
        type=int,
        required=False,
        help="The app ID of the GitHub cloner app to use.",
        default=137497,
    )
    parser.add_argument(
        "--github-cloner-key",
        type=str,
        required=False,
        action=PrivateKeyFileAction,
        help="The path to a github app private key.",
    )
    parser.add_argument(
        "--slack-webhook",
        type=str,
        required=False,
        help="The path where credentials for the slack webhook are.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        required=False,
        help="When enabled, the bot will not create a PR.",
    )

def _merge(args):
    success = bot.run(
        args.source,
        args.dest,
        args.rebase,
        args.theirs,
        args.ours,
        args.working_dir,
        args.git_username,
        args.git_email,
        args.github_user_token,
        args.github_app_id,
        args.github_app_key,
        args.github_cloner_id,
        args.github_cloner_key,
        args.slack_webhook,
        update_go_modules=args.update_go_modules,
        update_jsonnet_deps=args.update_jsonnet_deps,
        dry_run=args.dry_run,
    )
    return success

def _update_jsonnet_deps(args):
    success = bot.run(
        None,
        args.dest,
        args.rebase,
        None,
        None,
        args.working_dir,
        args.git_username,
        args.git_email,
        args.github_user_token,
        args.github_app_id,
        args.github_app_key,
        args.github_cloner_id,
        args.github_cloner_key,
        args.slack_webhook,
        update_go_modules=False,
        update_jsonnet_deps=True,
        dry_run=args.dry_run,
    )
    return success

def _parse_cli_arguments(testing_args=None):
    parser = argparse.ArgumentParser(
        description="Rebase on changes from an upstream repo")

    parent_parser = argparse.ArgumentParser(add_help=False)
    _add_common_args(parent_parser)

    subparsers = parser.add_subparsers()

    merge = subparsers.add_parser('merge', help='Perform git merge between dest and source', parents=[parent_parser])
    _add_merge_args(merge)
    merge.set_defaults(func=_merge)

    jsonnet = subparsers.add_parser('update-jsonnet-deps', help='Perform jsonnet dependency update', parents=[parent_parser])
    _add_jsonnet_update_args(jsonnet)
    jsonnet.set_defaults(func=_update_jsonnet_deps)

    if testing_args is not None:
        args = parser.parse_args(testing_args)
    else:
        args = parser.parse_args()

    return args


def main():
    """Rebase Bot entry point function."""
    args = _parse_cli_arguments()
    success = args.func(args)


    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
