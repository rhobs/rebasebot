def _resolve_conflict(gitwd):
    proc = gitwd.git.status(porcelain=True, as_process=True)

    # Conflict prefixes in porcelain mode that we can fix
    # UD - Modified/Deleted
    # AU - Renamed/Deleted
    allowed_conflict_prefixes = ["UD ", "AU "]

    # Non-conflict status prefixes that we should ignore
    allowed_status_prefixes = ["M  ", "D  ", "A  "]

    ud_files = []
    for line in proc.stdout:
        line = line.decode(git.compat.defenc)
        file_status = line[:3]
        if file_status in allowed_status_prefixes:
            # There is a conflict we can't resolve
            continue
        if file_status not in allowed_conflict_prefixes:
            # There is a conflict we can't resolve
            return False
        filename = line[3:].rstrip('\n')
        # Special characters are escaped
        if filename[0] == filename[-1] == '"':
            filename = filename[1:-1]
            filename = filename.encode('ascii').\
                decode('unicode_escape').\
                encode('latin1').\
                decode(git.compat.defenc)
        ud_files.append(filename)

    for ud_file in ud_files:
        gitwd.git.rm(ud_file)

    gitwd.git.commit("--no-edit")

    return True



