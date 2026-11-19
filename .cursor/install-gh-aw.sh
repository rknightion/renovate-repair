#!/usr/bin/env bash
set -euo pipefail

version=${1:?gh-aw version required}
# Digests from https://github.com/github/gh-aw/releases/expanded_assets/v0.89.21
case "$version:$(uname -sm)" in
    'v0.89.21:Linux x86_64')
        asset=linux-amd64
        sha256=1c74ff5fc28b1891d32b67f4348a9b7f750946b6d4a721e909187a848868016b
        ;;
    'v0.89.21:Linux aarch64')
        asset=linux-arm64
        sha256=4e521be28bd45030e8165c8654ee69ea1d6830b4e0fdefdd020ab1a9b1dd19ae
        ;;
    *)
        printf 'No pinned gh-aw checksum for %s on %s\n' "$version" "$(uname -sm)" >&2
        exit 1
        ;;
esac

extension_dir=${XDG_DATA_HOME:-$HOME/.local/share}/gh/extensions/gh-aw
mkdir -p "$extension_dir"
cd "$extension_dir"
if [[ -x gh-aw ]] && printf '%s  gh-aw\n' "$sha256" | sha256sum --check --status; then
    exit 0
fi

staging=$(mktemp -d .install.XXXXXXXX)
trap 'rm -rf "$staging"' EXIT
curl -q -fsSL --proto '=https' --proto-redir '=https' --retry 3 \
    --output "$staging/gh-aw" "https://github.com/github/gh-aw/releases/download/$version/$asset"
printf '%s  %s/gh-aw\n' "$sha256" "$staging" | sha256sum --check
chmod 0755 "$staging/gh-aw"
mv -fT "$staging/gh-aw" gh-aw
