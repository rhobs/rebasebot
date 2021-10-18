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

import logging
import subprocess


def commit_jsonnet_deps_updates(gitwd):
    try:
        # Clean repo
        proc = subprocess.run("make clean", shell=True, check=True, capture_output=True)
        logging.debug("make clean output: %s", proc.stdout.decode())

        proc = subprocess.run(
            "make update", shell=True, check=True, capture_output=True
        )
        logging.debug("make update output: %s", proc.stdout.decode())
        proc = subprocess.run(
            "make generate", shell=True, check=True, capture_output=True
        )
        logging.debug("make generate output: %s", proc.stdout.decode())

        gitwd.git.add(all=True)
    except subprocess.CalledProcessError as err:
        raise RepoException(
            f"Unable to update jsonnet modules: {err}: {err.stderr.decode()}"
        ) from err

    if gitwd.is_dirty():
        try:
            gitwd.git.add(all=True)
            gitwd.git.commit("-m", "jsonnet: update dependencies to latest")
        except Exception as err:
            err.extra_info = "Unable to commit jsonnet changes in git"
            raise err
