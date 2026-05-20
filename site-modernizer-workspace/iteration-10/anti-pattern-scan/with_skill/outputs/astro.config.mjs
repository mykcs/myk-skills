import { defineConfig } from 'astro/config';

export default defineConfig({
  output: 'static',
  integrations: [],
  i18n: {
    locales: ['en', 'zh'],
    defaultLocale: 'zh',
    prefixDefaultLocale: false,
  },
});
