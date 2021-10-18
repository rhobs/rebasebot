import logging

import git

from repo_exception import RepoException

def commit_go_mod_updates(gitwd, source):
    try:
        # Reset go.mod and go.sum to make sure they are the same as in the source
        for filename in ["go.mod", "go.sum"]:
            if not os.path.exists(filename):
                continue
            gitwd.remotes.source.repo.git.checkout(f"source/{source.reference}", filename)

        proc = subprocess.run(
            "go mod tidy", shell=True, check=True, capture_output=True
        )
        logging.debug("go mod tidy output: %s", proc.stdout.decode())
        proc = subprocess.run(
            "go mod vendor", shell=True, check=True, capture_output=True
        )
        logging.debug("go mod vendor output %s:", proc.stdout.decode())

        gitwd.git.add(all=True)
    except subprocess.CalledProcessError as err:
        raise RepoException(
            f"Unable to update go modules: {err}: {err.stderr.decode()}"
        ) from err

    if gitwd.is_dirty():
        try:
            gitwd.git.add(all=True)
            gitwd.git.commit(
                "-m", "UPSTREAM: <carry>: Updating and vendoring go modules "
                "after an upstream rebase"
            )
        except Exception as err:
            err.extra_info = "Unable to commit go module changes in git"
            raise err



