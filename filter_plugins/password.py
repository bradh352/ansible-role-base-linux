# Keep an existing password hash when the password hasn't changed.
#
# Re-hashing with the salt taken from /etc/shadow is not idempotent: since
# ansible-core 2.19, password_hash() prefers libxcrypt, and when
# crypt_gensalt() is available a supplied salt is used as random input to
# crypt_gensalt() rather than as the salt itself, so the result carries a
# different salt every time and the password is rewritten on every run.
# Instead, check the password against the existing hash (crypt() with the
# existing hash as its setting reproduces it exactly when the password
# matches) and only produce a new hash when it doesn't.

from __future__ import annotations

import hmac

from ansible.errors import AnsibleFilterError
from ansible.module_utils.common.text.converters import to_bytes, to_text
from ansible.plugins.filter.core import get_encrypted_password


def _crypt(password, setting):
    """crypt(3) with an existing hash as the setting, or None if no backend."""
    try:
        from ansible.utils.encrypt import _crypt_facade  # ansible-core 2.17+
        if _crypt_facade is not None:
            return to_text(_crypt_facade.crypt(to_bytes(password), to_bytes(setting)))
    except Exception:
        pass
    try:
        from passlib.context import CryptContext
        ctx = CryptContext(schemes=['sha512_crypt', 'sha256_crypt', 'md5_crypt', 'bcrypt'])
        if ctx.identify(setting) is not None:
            return setting if ctx.verify(password, setting) else ''
    except Exception:
        pass
    try:
        import crypt  # removed in Python 3.13
        return crypt.crypt(password, setting)
    except Exception:
        return None


def password_hash_keep(password, existing_hash, hashtype='sha512'):
    """Return existing_hash if password matches it, else a new hash of password."""
    if password is None:
        raise AnsibleFilterError("password_hash_keep: password is undefined")
    existing_hash = to_text(existing_hash or '').strip()
    # Locked (!), disabled (*) and empty entries never match.
    if existing_hash.startswith('$'):
        candidate = _crypt(password, existing_hash)
        if candidate and hmac.compare_digest(candidate, existing_hash):
            return existing_hash
    return get_encrypted_password(password, hashtype)


class FilterModule(object):
    def filters(self):
        return {'password_hash_keep': password_hash_keep}
