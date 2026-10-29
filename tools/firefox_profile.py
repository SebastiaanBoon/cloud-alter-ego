"""Open a web page with the login of one of the user's Firefox profiles.

Keep one Firefox profile per client, signed in once. This script copies the chosen profile to its own
folder and starts a separate, automated Firefox on that copy, so the user's own Firefox is never
touched or closed and no interactive login is needed.

Usage:
    python tools/firefox_profile.py --list
    python tools/firefox_profile.py <profile> https://teams.microsoft.com/v2/ --wait 25 --text
    python tools/firefox_profile.py <profile> <url> --screenshot page.png
    python tools/firefox_profile.py <profile> --token https://graph.microsoft.com/Chat.Read

--token gets a Microsoft token through the single sign-on session in the profile, without interaction,
and prints only a short confirmation. From Python, `token(profile, scopes)` returns the token. The default
client is Microsoft Graph Command Line Tools; for Azure and Fabric use the Azure CLI client
(--client 04b07795-8ddb-461a-bbee-02f9e1bf7b46).

From Python, `from firefox_profile import open_profile` returns a Selenium driver.

Needs `pip install selenium msal`. Windows; set FIREFOX_ROOT and FIREFOX_EXE for other setups.
"""

import argparse
import configparser
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
from pathlib import Path

LOCAL = Path(os.environ.get("LOCALAPPDATA", Path.home() / ".local" / "share"))
STORE_ROOT = LOCAL / "Packages" / "Mozilla.Firefox_n80bbvh6b1yt2" / "LocalCache" / "Roaming" / "Mozilla" / "Firefox"
CLASSIC_ROOT = Path(os.environ.get("APPDATA", Path.home())) / "Mozilla" / "Firefox"
COPY_ROOT = LOCAL / "claude-firefox"
SKIP = {"parent.lock", "lock", ".parentlock", "cache2", "startupCache", "crashes", "minidumps", "saved-telemetry-pings", "datareporting"}


def firefox_root():
    if os.environ.get("FIREFOX_ROOT"):
        return Path(os.environ["FIREFOX_ROOT"])
    return STORE_ROOT if STORE_ROOT.exists() else CLASSIC_ROOT


def profiles():
    """Name -> profile folder, from the Firefox profile groups (new profile manager) and profiles.ini."""
    root = firefox_root()
    result = {}
    groups = root / "Profile Groups"
    for db in groups.glob("*.sqlite"):
        with tempfile.TemporaryDirectory() as tmp:
            # Copy first: Firefox keeps the database locked while it runs.
            for part in groups.glob(db.name + "*"):
                shutil.copy2(part, Path(tmp) / part.name)
            con = sqlite3.connect(Path(tmp) / db.name)
            for path, name in con.execute("select path, name from Profiles"):
                result[name] = root / path.replace("\\", "/")
            con.close()
    ini = root / "profiles.ini"
    if ini.exists():
        cp = configparser.ConfigParser()
        cp.read(ini, encoding="utf-8")
        for section in cp.sections():
            if section.startswith("Profile") and "Name" in cp[section]:
                p = cp[section]
                path = root / p["Path"] if p.get("IsRelative", "1") == "1" else Path(p["Path"])
                result.setdefault(p["Name"], path)
    return result


def firefox_exe():
    if os.environ.get("FIREFOX_EXE"):
        return os.environ["FIREFOX_EXE"]
    for exe in (Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Mozilla Firefox" / "firefox.exe",):
        if exe.exists():
            return str(exe)
    # Firefox from the Microsoft Store: the WindowsApps folder cannot be searched, so ask Appx.
    location = subprocess.run(
        ["powershell", "-NoProfile", "-Command", "(Get-AppxPackage Mozilla.Firefox).InstallLocation"],
        capture_output=True, text=True,
    ).stdout.strip()
    exe = Path(location) / "VFS" / "ProgramFiles" / "Firefox Package Root" / "firefox.exe"
    if not location or not exe.exists():
        sys.exit("firefox.exe not found, set FIREFOX_EXE")
    return str(exe)


def close_old_copy(target):
    """A hung Firefox from an earlier run keeps the copy locked and the new one will not start
    ("Firefox is already running, but is not responding"). Only processes on this copy, never the user's own Firefox."""
    if os.name != "nt":
        return
    pids = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "Get-CimInstance Win32_Process -Filter \"name='firefox.exe'\" | "
         f"Where-Object {{ $_.CommandLine -like '*{target}*' }} | ForEach-Object {{ $_.ProcessId }}"],
        capture_output=True, text=True,
    ).stdout.split()
    for pid in pids:
        subprocess.run(["taskkill", "/F", "/T", "/PID", pid], capture_output=True)
    if pids:
        time.sleep(2)


def copy_profile(name):
    found = profiles()
    if name not in found:
        sys.exit(f"Profile '{name}' does not exist. Choose from: {', '.join(found)}")
    target = COPY_ROOT / name
    close_old_copy(target)
    if target.exists():
        shutil.rmtree(target, ignore_errors=True)
    shutil.copytree(found[name], target, ignore=lambda d, names: [n for n in names if n in SKIP or n.endswith("-shm")], dirs_exist_ok=True)
    # Without the storeID the copy does not register itself as a new profile in the user's profile group.
    prefs = target / "prefs.js"
    if prefs.exists():
        lines = prefs.read_text(encoding="utf-8").splitlines(keepends=True)
        prefs.write_text("".join(l for l in lines if "toolkit.profiles.storeID" not in l), encoding="utf-8")
    return target


def open_profile(name, headless=True):
    from selenium import webdriver
    from selenium.webdriver.firefox.options import Options

    options = Options()
    options.binary_location = firefox_exe()
    options.add_argument("-profile")
    options.add_argument(str(copy_profile(name)))
    if headless:
        options.add_argument("-headless")
    # Teams on the web stays on its loading screen as soon as it sees an automated browser.
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference("useAutomationExtension", False)
    options.set_preference("browser.profiles.enabled", False)
    driver = webdriver.Firefox(options=options)
    driver.set_window_size(1600, 1000)
    return driver


GRAPH_CLI = "14d82eec-204b-4c2f-b7e8-296a70dab67e"


def token(name, scopes, client_id=GRAPH_CLI, wait=90):
    """Auth code flow in the profile browser; the session cookies of the profile do the login."""
    import urllib.parse

    import msal

    redirect = "http://localhost:8400"
    app = msal.PublicClientApplication(client_id, authority="https://login.microsoftonline.com/organizations")
    flow = app.initiate_auth_code_flow(scopes, redirect_uri=redirect)
    driver = open_profile(name)
    try:
        try:
            driver.get(flow["auth_uri"])
        except Exception:  # a direct redirect to localhost gives a network error page, the code is in the url
            pass
        end = time.time() + wait
        while time.time() < end:
            url = driver.current_url
            if url.startswith("about:neterror"):
                url = urllib.parse.parse_qs(urllib.parse.urlparse(url).query).get("u", [""])[0]
            if url.startswith(redirect):
                answer = {k: v[0] for k, v in urllib.parse.parse_qs(urllib.parse.urlparse(url).query).items()}
                result = app.acquire_token_by_auth_code_flow(flow, answer)
                if "access_token" not in result:
                    sys.exit(f"No token: {result.get('error_description', result)}")
                return result["access_token"]
            time.sleep(1)
        shot = COPY_ROOT / f"{name}-login.png"
        driver.save_screenshot(str(shot))
        sys.exit(f"Login does not complete by itself (stuck on {driver.title!r}); screenshot in {shot}")
    finally:
        driver.quit()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("profile", nargs="?")
    p.add_argument("url", nargs="?")
    p.add_argument("--list", action="store_true")
    p.add_argument("--wait", type=int, default=15)
    p.add_argument("--text", action="store_true")
    p.add_argument("--screenshot")
    p.add_argument("--visible", action="store_true")
    p.add_argument("--token", nargs="+", metavar="SCOPE")
    p.add_argument("--client", default=GRAPH_CLI)
    a = p.parse_args()
    if a.list:
        for name, path in profiles().items():
            print(f"{name}: {path}")
        return
    if a.token:
        t = token(a.profile, a.token, a.client)
        print(f"Token obtained for {a.profile} ({len(t)} characters)")
        return
    driver = open_profile(a.profile, headless=not a.visible)
    try:
        driver.get(a.url)
        time.sleep(a.wait)
        print("URL:", driver.current_url)
        print("Title:", driver.title)
        if a.screenshot:
            driver.save_screenshot(a.screenshot)
        if a.text:
            print(driver.execute_script("return document.body.innerText"))
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
