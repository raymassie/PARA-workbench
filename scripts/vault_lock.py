"""One advisory writer lock shared by local tools that update vault records."""
from contextlib import contextmanager
import fcntl
from pathlib import Path

@contextmanager
def vault_write_lock(root):
    root = Path(root).resolve()
    folder = root/'logs'
    path = folder/'vault-write.lock'
    if folder.is_symlink() or path.is_symlink():
        raise ValueError('The vault writer lock cannot use a symlink.')
    folder.mkdir(parents=True, exist_ok=True)
    with path.open('a') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)
