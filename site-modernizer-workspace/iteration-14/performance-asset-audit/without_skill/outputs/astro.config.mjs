import { defineConfig } from 'astro/config';

export default defineConfig({
  output: 'static',
  integrations: [],
  image: {
    service: {
      entrypoint: 'astro/assets/services/sharp',
      config: {
        limitInputPixels: false,
      },
    },
  },
});
