# ezqbit

A CSS-only theme for the qBittorrent WebUI.

## Rules

- Never change the original qBittorrent WebUI files (HTML, JavaScript, stock CSS, images).
  Everything is done as add-on CSS in `css/ezqbit.css` (main UI) and `css/ezqbit-login.css`
  (login page).
- The only touch to stock files is the `@import` line that `build.sh` / `build.ps1` prepend
  to `private/css/style.css` and `public/css/login.css`.
- If something cannot be done with CSS alone, say so and propose a CSS-only approximation
  rather than editing stock files.

## Trying a change

`dev/mock_server.py` is a mock qBittorrent backend with canned data, so the theme can be
checked without a real qBittorrent:

```sh
./build.sh 5.2.4 /tmp/ezqbit-webui                 # once; downloads the stock WebUI
python3 dev/mock_server.py /tmp/ezqbit-webui 18099
open "http://localhost:18099/?scheme=dark"         # or scheme=light; /login for the login page
```

It serves `css/ezqbit.css` and `css/ezqbit-login.css` straight from the repository, so an
edit shows on a browser refresh. Add `&demo=<name>` (`prefs`, `context`, `trackers`, `log`,
`search`, `rss`, …; see `ACTIONS` in the script) to open a dialog or view after loading.
Check both themes before calling a visual change done.
