# i18n Sync Audit Summary

## Translation Key Alignment

All translation keys are aligned between `en.json` and `zh.json`.

## Hardcoded Chinese Strings Detected

These components contain hardcoded Chinese text and should be refactored to use i18n keys:

- `src/components/Navbar.astro:5`: `<a href="/">首页</a>`
- `src/components/Navbar.astro:6`: `<a href="/about/">关于我们</a>`
- `src/components/Navbar.astro:7`: `<span>当前语言: {lang}</span>`
- `src/components/Hero.astro:5`: `<h1>{lang === 'zh' ? '欢迎' : 'Welcome'}</h1>`
- `src/components/Hero.astro:6`: `<p>这是一个演示网站</p>`
- `src/components/Hero.astro:7`: `<button>立即开始</button>`
- `src/pages/[lang]/index.astro:12`: `<Layout title={lang === 'zh' ? '演示站点' : 'Demo Site'}>`
- `src/pages/[lang]/index.astro:15`: `<footer>保留所有权利 © 2024</footer>`
