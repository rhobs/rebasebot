import logging

import git

from repo_exception import RepoException

def _resolve_rebase_conflicts(gitwd, theirs, ours):
    if theirs:
        gitwd.git.checkout("--theirs", theirs)
        gitwd.git.add(theirs)
    if ours:
        gitwd.git.checkout("--ours", ours)
        gitwd.git.add(ours)

    logging.info("Rebase conflict has been resolved. Continue rebasing.")

    gitwd.git.merge("--continue")

    return True

def do_rebase(gitwd, source, theirs, ours):
    logging.info("Performing rebase")
    def find_valid_ref():
        for ref in [source.reference, f"source/{source.reference}"]:
            try:
                gitwd.git.rev_parse(ref)
                return ref
            except git.GitCommandError:
                pass
    try:
        logging.info("Fetching %s and all tags from source", source.reference)
        gitwd.remotes.source.fetch(source.reference)
        gitwd.remotes.source.fetch("--tags")
        gitwd.git.merge(find_valid_ref())
    except git.GitCommandError as ex:
        try:
            _resolve_rebase_conflicts(gitwd, theirs, ours)
        except Exception as ex:
            raise RepoException(
                f"Manual intervention is needed to rebase "
                f"{source.url}:{source.reference} "
                f"into {dest.ns}/{dest.name}:{dest.branch}: "
                f"{ex}",
            ) from ex
    except Exception as ex:
        raise RepoException(
            f"I got an error trying to rebase "
            f"{source.url}:{source.reference} "
            f"into {dest.ns}/{dest.name}:{dest.branch}: "
            f"{ex}",
        ) from ex
