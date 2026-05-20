# Git Log

```
d4f9b0e fix(i18n): sync en/zh translations and remove hardcoded strings
2d144c3 init
```

## Diff Stats (source files only, excluding node_modules/dist/.astro)

```
 package-lock.json            | 5548 ++++++++++++++++++++++++++++++++++++++++++
 src/components/Hero.astro    |    8 +-
 src/components/Navbar.astro  |    8 +-
 src/content/i18n/en.json     |   13 +-
 src/content/i18n/zh.json     |    8 +-
 src/layouts/Layout.astro     |    4 +-
 src/pages/[lang]/index.astro |   11 +-
 7 files changed, 5581 insertions(+), 19 deletions(-)
```

Note: `package-lock.json` was generated during `npm install`. The meaningful i18n changes are in the 6 `src/` files with 19 lines deleted and 33 lines added.
