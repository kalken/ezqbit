# ezqbit

A flat dark alternative WebUI for qBittorrent:

- lighter top bar, sidebar and status bar framing a darker torrent list, separated by
  dark edges with a soft shadow
- sidebar with pill selection and bold section titles
- white toolbar icons, hairline dividers, search field and tabs on the right
- General / Trackers / Peers / … as chips
- green→yellow progress bars
- dark dialogs, menus and login page

This repo contains only the theme's CSS. `build.sh` (or `build.ps1` on Windows) combines it with
the original qBittorrent WebUI files: every stock HTML, JavaScript and image file stays untouched, and only two stock CSS
files get one added `@import` line each (see [What changed](#what-changed-compared-to-stock)).

The theme runs offline: no web fonts, CDNs or external images. The icons are qBittorrent's own.

Written against the qBittorrent **5.2.x** WebUI. Build it from the same qBittorrent
version you run, since an alternative WebUI replaces the whole built-in one.

## Install

qBittorrent's built-in WebUI files are compiled into the program, so the alternative WebUI folder
has to be assembled from the qBittorrent source:

Linux / macOS:

```sh
git clone https://github.com/kalken/ezqbit.git
cd ezqbit
./build.sh 5.2.4 ~/ezqbit-webui     # use your qBittorrent version
```

Windows (PowerShell; or download the repo as a ZIP instead of `git clone`):

```powershell
git clone https://github.com/kalken/ezqbit.git
cd ezqbit
powershell -ExecutionPolicy Bypass -File .\build.ps1 5.2.4 C:\ezqbit-webui   # use your qBittorrent version
```

The script downloads that release's `src/webui/www` from qBittorrent's GitHub. If you already have
the qBittorrent source, pass its `src/webui/www` folder instead of a version number.

Then in qBittorrent → Options → Web UI, tick **Use alternative WebUI**, pick the built folder
(the one containing `public/` and `private/`), and hard-refresh the WebUI.

## What changed compared to stock

Only CSS, applied by `build.sh` / `build.ps1` to the original WebUI files:

- `private/css/style.css`: one added line, `@import url("ezqbit.css");`
- `public/css/login.css`: one added line, `@import url("ezqbit-login.css");`
- `private/css/ezqbit.css`: the whole theme (from `css/` in this repo)
- `public/css/ezqbit-login.css`: login page (from `css/` in this repo)

The theme adds no image files and embeds none: the white toolbar, tab and search icons are the
stock icons, recoloured from CSS.

## Locked out?

If the WebUI breaks after a qBittorrent upgrade, turn the alternative WebUI off
(`WebUI\AlternativeUIEnabled=false` in `qBittorrent.conf`)
to get the stock WebUI back.

## License

The theme (`css/`, `build.sh`, `build.ps1`) is licensed GPLv3-or-later, see [COPYING.GPLv3](COPYING.GPLv3).
A built WebUI folder also contains qBittorrent's own WebUI files, which keep qBittorrent's license
(GPLv2+ for the code, GPLv3+ for the assets), see [LICENSE](LICENSE) and [COPYING.GPLv2](COPYING.GPLv2).

## NixOS (flake)

Add the repo as a non-flake input in `flake.nix`:

```nix
inputs = {
  # ...
  ezqbit.url = "github:kalken/ezqbit";
  ezqbit.flake = false;
};
```

Package it with an overlay in a NixOS module, e.g. `qbit-theme.nix`:

```nix
# qbit-theme.nix
{ inputs, lib, ... }:
{
  nixpkgs.overlays = [
    (final: prev: {
      ezqbit = final.stdenvNoCC.mkDerivation {
        pname = "ezqbit";
        version = "0-unstable-${inputs.ezqbit.shortRev}";

        src = inputs.ezqbit;

        # Original WebUI files from the same qBittorrent package nixpkgs builds
        installPhase = ''
          runHook preInstall
          sh ./build.sh ${final.qbittorrent-nox.src}/src/webui/www $out/share/ezqbit
          runHook postInstall
        '';

        meta = {
          description = "Flat dark alternative WebUI for qBittorrent";
          homepage = "https://github.com/kalken/ezqbit";
          license = lib.licenses.gpl3Plus;
          platforms = lib.platforms.all;
        };
      };
    })
  ];
}
```

Include it as a module in `flake.nix` (with `inputs` passed to modules):

```nix
nixosConfigurations.myhost = nixpkgs.lib.nixosSystem {
  specialArgs = { inherit inputs; };
  modules = [
    ./configuration.nix
    ./qbit-theme.nix
  ];
};
```

The WebUI files come from `qbittorrent-nox`, the package `services.qbittorrent` uses by default;
if you set `services.qbittorrent.package` to something else, use that package's `src` instead.

You can then use `pkgs.ezqbit` as the alternative WebUI in `services.qbittorrent`:

```nix
services.qbittorrent.serverConfig.Preferences.WebUI = {
  AlternativeUIEnabled = true;
  RootFolder = "${pkgs.ezqbit}/share/ezqbit";
};
```
