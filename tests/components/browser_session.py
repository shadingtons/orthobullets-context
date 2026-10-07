"""An Orthobullets web session isolated from Anki's internal web views."""
from hashlib import sha256
from pathlib import Path


def session_directory(addon_directory, profile_name):
    if not isinstance(profile_name, str) or not profile_name.strip():
        raise ValueError("Open an Anki profile before signing in to Orthobullets.")
    key = sha256(profile_name.encode("utf-8")).hexdigest()
    return Path(addon_directory).resolve() / "user_files" / "browser_profiles" / key


def configure_browser(view, addon_directory, profile_name):
    from aqt.qt import QWebEnginePage, QWebEngineProfile

    directory = session_directory(addon_directory, profile_name)
    directory.mkdir(parents=True, exist_ok=True)
    profile = QWebEngineProfile("orthobullets-" + directory.name)
    try:
        profile.setPersistentStoragePath(str(directory / "storage"))
        profile.setCachePath(str(directory / "cache"))
        # Honor the website's Remember Me choice; do not force session cookies to persist.
        profile.setPersistentCookiesPolicy(
            QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies)
        page = QWebEnginePage(profile, view)
        view.setPage(page)
    except Exception:
        profile.deleteLater()
        raise
    # Retain the Python wrapper; delete the profile only after its page/view is gone.
    view._orthobullets_profile = profile
    view.destroyed.connect(lambda: profile.deleteLater())
    return profile
