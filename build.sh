#!/bin/sh
# Assemble a qBittorrent alternative WebUI folder: the original WebUI files plus the ezqbit CSS.
#
# Usage:
#   ./build.sh <version> <out-dir>    download the WebUI of that qBittorrent release, e.g. 5.2.4
#   ./build.sh <www-dir> <out-dir>    use a local copy of qBittorrent's src/webui/www
#
# The original files are left as they are, except for one @import line added to the top
# of private/css/style.css and public/css/login.css.
set -eu

if [ $# -ne 2 ]; then
    echo "usage: $0 <version | path/to/src/webui/www> <out-dir>" >&2
    exit 1
fi

src=$1
out=$2
here=$(cd "$(dirname "$0")" && pwd)

if [ -e "$out" ] && [ -n "$(ls -A "$out" 2>/dev/null)" ]; then
    echo "$out already exists and is not empty" >&2
    exit 1
fi
mkdir -p "$out"

if [ -d "$src" ]; then
    www=$src
else
    tmp=$(mktemp -d)
    trap 'rm -rf "$tmp"' EXIT
    url="https://github.com/qbittorrent/qBittorrent/archive/refs/tags/release-$src.tar.gz"
    echo "Downloading $url"
    curl -fsSL "$url" | tar -xz -C "$tmp" "qBittorrent-release-$src/src/webui/www"
    www="$tmp/qBittorrent-release-$src/src/webui/www"
fi

for d in public private; do
    if [ ! -d "$www/$d" ]; then
        echo "$www/$d not found; expected qBittorrent's src/webui/www" >&2
        exit 1
    fi
    cp -R "$www/$d" "$out/"
done
# Files copied from a read-only location (e.g. the Nix store) keep its permissions
chmod -R u+w "$out"

cp "$here/css/ezqbit.css" "$out/private/css/"
cp "$here/css/ezqbit-login.css" "$out/public/css/"

prepend() {
    { printf '%s\n\n' "$2"; cat "$1"; } > "$1.tmp"
    mv "$1.tmp" "$1"
}
prepend "$out/private/css/style.css" '@import url("ezqbit.css");'
prepend "$out/public/css/login.css" '@import url("ezqbit-login.css");'

echo "Built $out"
