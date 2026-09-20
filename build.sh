#!/bin/sh
# Собирает index.html для GitHub Pages из src/app.html (исходник артефакта без <html>/<head>).
set -e
cd "$(dirname "$0")"
TITLE=$(sed -n 's:.*<title>\(.*\)</title>.*:\1:p' src/app.html | head -1)
{
cat <<HEAD
<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#F6F7F9" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#13161C" media="(prefers-color-scheme: dark)">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="$TITLE">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icon.svg" type="image/svg+xml">
<link rel="icon" href="icon-192.png" type="image/png" sizes="192x192">
<link rel="apple-touch-icon" href="icon-180.png">
<title>$TITLE</title>
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}[hidden]{display:none!important}</style>
</head>
<body>
HEAD
sed '/<title>.*<\/title>/d' src/app.html
cat <<FOOT
</body>
</html>
FOOT
} > index.html
echo "built index.html ($(wc -c < index.html) bytes)"
