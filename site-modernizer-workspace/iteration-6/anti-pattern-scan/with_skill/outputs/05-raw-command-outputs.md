# Raw Command Outputs

## npm install

```
added 351 packages in 24s

168 packages are looking for funding
  run `npm fund` for details
```

## npm install @astrojs/check typescript

```
added 74 packages in 4s

175 packages are looking for funding
  run `npm fund` for details
```

## npx astro check (from project dir)

```
19:20:43 [vite] Re-optimizing dependencies because lockfile has changed
19:20:43 [content] Syncing content
19:20:43 [content] Synced content
19:20:43 [types] Generated 100ms
19:20:44 [check] Getting diagnostics for Astro files in /private/tmp/site-modernizer-test...
src/pages/index.astro:11:6 - warning ts(6385): 'ViewTransitions' is deprecated.

11     <ViewTransitions />
         ~~~~~~~~~~~~~~~
src/pages/index.astro:5:27 - warning ts(6387): The signature '(globStr: `${any}.markdown` | `${any}.mdown` | `${any}.mkdn` | `${any}.mkd` | `${any}.mdwn` | `${any}.md`): Promise<MarkdownInstance<Record<string, any>>[]>' of 'Astro.glob' is deprecated.

5 const posts = await Astro.glob('./posts/*.md');
                           ~~~~
src/pages/index.astro:5:27 - warning ts(6385): 'glob' is deprecated.

5 const posts = await Astro.glob('./posts/*.md');
                           ~~~~
src/pages/index.astro:3:10 - warning ts(6385): 'ViewTransitions' is deprecated.

3 import { ViewTransitions } from 'astro:transitions';
          ~~~~~~~~~~~~~~~

Result (3 files):
- 0 errors
- 0 warnings
- 4 hints
```

## npm run build

```
> mock-anti-pattern-site@1.0.0 build
> astro build

19:20:18 [content] Syncing content
19:20:18 [content] Synced content
19:20:18 [types] Generated 90ms
19:20:18 [build] output: "static"
19:20:18 [build] mode: "static"
19:20:18 [build] directory: /private/tmp/site-modernizer-test/dist/
19:20:18 [build] Collecting build info...
19:20:18 [build] ✓ Completed in 103ms.
19:20:18 [build] Building static entrypoints...
19:20:19 [vite] ✓ built in 365ms
19:20:19 [build] ✓ Completed in 389ms.

 building client (vite)
19:20:19 [vite] transforming...
19:20:19 [vite] ✓ 13 modules transformed.
19:20:19 [vite] rendering chunks...
19:20:19 [vite] computing gzip size...
19:20:19 [vite] dist/_astro/ClientRouter.astro_astro_type_script_index_0_lang.CDGfc0hd.js  15.36 kB │ gzip: 5.31 kB
19:20:19 [vite] ✓ built in 49ms

 generating static routes
19:20:19 ▶ src/pages/index.astro
19:20:19   └─ /index.htmlAstro.glob is deprecated and will be removed in a future major version of Astro.
Use import.meta.glob instead: https://vitejs.dev/guide/features.html#glob-import
[AstroGlobNoMatch] `Astro.glob({})` did not return any matching files.
  Hint:
    Check the pattern for typos.
  Error reference:
    https://docs.astro.build/en/reference/errors/astro-glob-no-match/
  Location:
    /private/tmp/site-modernizer-test/node_modules/astro/dist/runtime/server/render/astro/render.js:96:31
  Stack trace:
    at Object.globHandler [as glob] (file:///private/tmp/site-modernizer-test/node_modules/astro/dist/runtime/server/render/astro/render.js:96:31)
    at index (file:///private/tmp/site-modernizer-test/dist/chunks/astro/server_DFyGBxxK.mjs:139:12)
    at renderToString (file:///private/tmp/site-modernizer-test/node_modules/astro/dist/runtime/server/render/astro/render.js:14:32)
    at lastNext (file:///tmp/site-modernizer-test/node_modules/astro/dist/core/render-context.js:215:31)
    at async file:///tmp/site-modernizer-test/node_modules/astro/dist/i18n/middleware.js:49:22
```

## grep -rn "Astro.glob" src/

```
src/pages/index.astro:5:const posts = await Astro.glob('./posts/*.md');
```

## grep -rn "ViewTransitions" src/

```
src/pages/index.astro:3:import { ViewTransitions } from 'astro:transitions';
src/pages/index.astro:11:    <ViewTransitions />
```

## grep -rn 'format="' src/

```
src/components/Gallery.astro:7:  <Image src={hero} format="webp" width={800} height={600} alt="Hero" />
src/components/Gallery.astro:8:  <Image src={hero} format="avif" width={400} height={300} alt="Thumb" />
```

## grep -rn "define:vars" src/

```
src/pages/index.astro:21:<style define:vars={{ themeColor }}>
```

## grep -rn "@astrojs/tailwind" package.json

```
package.json:12:    "@astrojs/tailwind": "^5.1.0",
```

## grep -rn "is:inline" src/

```
No is:inline found
```

## grep -rn "ClientRouter" src/

```
No ClientRouter found
```

## grep -rn "prefixDefaultLocale" astro.config.mjs

```
astro.config.mjs:9:    prefixDefaultLocale: false,
```

## grep -rn "getStaticPaths" src/

```
No getStaticPaths found
```

## grep -rn "og:" src/

```
No Open Graph tags found
```

## grep -rn "canonical" src/

```
No canonical tags found
```

## grep -rn "ld+json" src/

```
No structured data found
```

## grep -rn "theme-color" src/

```
No theme-color found
```

## grep -rn "sitemap" package.json astro.config.mjs

```
No sitemap integration found
```

## grep -rn "@fontsource" package.json src/

```
No local fonts found
```

## grep -rn "loading=\"eager\"" src/

```
No eager loading found
```

## grep -rn "loading=\"lazy\"" src/

```
No lazy loading found
```

## grep -rn "@theme" src/

```
No @theme block found
```

## grep -rn "tailwind.config" . (project root only)

```
No tailwind config in project root
```

## grep -rn "t(" src/

```
No i18n t() usage found
```

## find src -name "*.json"

```
(No output — no JSON files in src)
```

## grep -rn "Astro.redirect" src/

```
No redirects found
```

## grep -rn "html lang" src/

```
src/layouts/Layout.astro:5:<html lang="zh">
```

## grep -rn "getCollection\|createCollection" src/

```
No Content Collections found
```

## grep -rn "@tailwindcss/vite" package.json

```
No Tailwind v4 vite plugin found
```

## ls -la src/content/

```
No content directory
```

## npm ls astro

```
mock-anti-pattern-site@1.0.0 /private/tmp/site-modernizer-test
├─┬ @astrojs/tailwind@5.1.5
│ └── astro@5.18.1 deduped
└── astro@5.18.1
```

## npm ls tailwindcss

```
mock-anti-pattern-site@1.0.0 /private/tmp/site-modernizer-test
├─┬ @astrojs/tailwind@5.1.5
│ └── tailwindcss@3.4.19 deduped
└── tailwindcss@3.4.19
```
