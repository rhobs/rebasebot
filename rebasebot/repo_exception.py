class RepoException(Exception):
    """An error requiring the user to perform a manual action in the
    destination repo
    """
    def __init__(self, msg):
        self.msg = msg
        super().__init__(msg)
