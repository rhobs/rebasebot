import logging
import subprocess

def commit_jsonnet_deps_updates(gitwd):
    try:
        # Clean repo
        proc = subprocess.run(
            "make clean", shell=True, check=True, capture_output=True
        )
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
            gitwd.git.commit(
                "-m", "jsonnet: update dependencies to latest"
            )
        except Exception as err:
            err.extra_info = "Unable to commit jsonnet changes in git"
            raise err



