# Deployment Platforms for Astro Static Sites

Comprehensive deployment guides for major hosting platforms.

## Platform Comparison

| Platform | Auto CI/CD | Custom Domain | Edge CDN | Free Tier |
|----------|------------|---------------|----------|-----------|
| Netlify | Yes | Yes | Yes | 100GB/mo |
| Vercel | Yes | Yes | Yes | 100GB/mo |
| Cloudflare Pages | Yes | Yes | Yes | Unlimited |
| GitHub Pages | Manual | Yes | Via CDN | Unlimited |
| Firebase Hosting | Manual | Yes | Yes | 10GB/mo |
| AWS S3+CloudFront | Manual | Yes | Yes | Pay-as-go |

## Netlify

### Quick Setup

1. Push code to GitHub/GitLab
2. Connect repository in Netlify dashboard
3. Set build command: `npm run build`
4. Set publish directory: `dist`

### netlify.toml

```toml
[build]
  command = "npm run build"
  publish = "dist"

[build.environment]
  NODE_VERSION = "18"

# Redirects for SPA-style routing (if needed)
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

# Custom headers
[[headers]]
  for = "/*"
    [headers.values]
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"

# Trailing slashes
[build.processing]
  skip_processing = false
[build.processing.html]
  pretty_urls = true
```

### Environment Variables

Set in Netlify dashboard or `netlify.toml`:

```toml
[context.production.environment]
  API_URL = "https://api.example.com"

[context.deploy-preview.environment]
  API_URL = "https://staging-api.example.com"
```

## Vercel

### Quick Setup

1. Install Vercel CLI: `npm i -g vercel`
2. Run `vercel` in project root
3. Follow prompts to link/create project

### vercel.json

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "astro",
  "routes": [
    {
      "src": "/assets/(.*)",
      "headers": {
        "Cache-Control": "public, max-age=31536000, immutable"
      }
    }
  ],
  "trailingSlash": false
}
```

### Preview Deployments

Automatic for every PR. Access via unique URLs like:
`project-git-branch-username.vercel.app`

## Cloudflare Pages

### Quick Setup

1. Connect GitHub repo in Cloudflare dashboard
2. Set framework preset: Astro
3. Build command auto-detected

### Configuration

```toml
# wrangler.toml (optional)
name = "my-astro-site"
compatibility_date = "2024-01-01"

[site]
bucket = "./dist"
```

### Custom Headers

Create `public/_headers`:

```
/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff

/assets/*
  Cache-Control: public, max-age=31536000, immutable
```

## GitHub Pages

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm

      - run: npm ci
      - run: npm run build

      - uses: actions/upload-pages-artifact@v3
        with:
          path: dist

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/deploy-pages@v4
        id: deployment
```

### Astro Configuration for Subpath

```javascript
// astro.config.mjs
export default defineConfig({
  site: 'https://username.github.io',
  base: '/repository-name'
});
```

## Firebase Hosting

### Initial Setup

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login and initialize
firebase login
firebase init hosting
```

### firebase.json

```json
{
  "hosting": {
    "public": "dist",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ],
    "rewrites": [],
    "headers": [
      {
        "source": "/assets/**",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "public, max-age=31536000, immutable"
          }
        ]
      },
      {
        "source": "**",
        "headers": [
          {
            "key": "X-Frame-Options",
            "value": "DENY"
          }
        ]
      }
    ],
    "cleanUrls": true,
    "trailingSlash": false
  }
}
```

### Deploy Commands

```bash
# Build and deploy
npm run build
firebase deploy --only hosting

# Deploy to preview channel
firebase hosting:channel:deploy preview-name

# Deploy with custom site ID (multiple sites)
firebase deploy --only hosting:my-site-id
```

### GitHub Actions for Firebase

```yaml
# .github/workflows/firebase-deploy.yml
name: Deploy to Firebase

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm

      - run: npm ci
      - run: npm run build

      - uses: FirebaseExtended/action-hosting-deploy@v0
        with:
          repoToken: ${{ secrets.GITHUB_TOKEN }}
          firebaseServiceAccount: ${{ secrets.FIREBASE_SERVICE_ACCOUNT }}
          channelId: live
          projectId: your-project-id
```

### Multiple Sites

```json
{
  "hosting": [
    {
      "target": "main-site",
      "public": "dist",
      "ignore": ["firebase.json", "**/.*"]
    },
    {
      "target": "docs-site",
      "public": "docs/dist",
      "ignore": ["firebase.json", "**/.*"]
    }
  ]
}
```

```bash
firebase target:apply hosting main-site my-main-site
firebase target:apply hosting docs-site my-docs-site
firebase deploy --only hosting
```

## AWS S3 + CloudFront

### S3 Bucket Setup

```bash
# Create bucket
aws s3 mb s3://my-astro-site

# Enable static website hosting
aws s3 website s3://my-astro-site \
  --index-document index.html \
  --error-document 404.html

# Sync build output
aws s3 sync dist/ s3://my-astro-site --delete
```

### Bucket Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-astro-site/*"
    }
  ]
}
```

### CloudFront Distribution

Key settings:
- Origin: S3 bucket website endpoint
- Default root object: `index.html`
- Custom error response: 404 → /404.html
- Cache behavior: Use cache policy for static assets

### Invalidation on Deploy

```bash
aws cloudfront create-invalidation \
  --distribution-id E1234567890 \
  --paths "/*"
```

## GCS + Cloud CDN (GCP Alternative)

Alternative to Firebase Hosting using Google Cloud Storage with Cloud CDN.

### Setup

```bash
# Create bucket with uniform access
gsutil mb -l us-central1 gs://my-astro-site
gsutil uniformbucketlevelaccess set on gs://my-astro-site

# Enable public access
gsutil iam ch allUsers:objectViewer gs://my-astro-site

# Configure as static site
gsutil web set -m index.html -e 404.html gs://my-astro-site
```

### Deploy Script

```bash
# Build and sync
npm run build
gsutil -m rsync -r -d dist/ gs://my-astro-site

# Set cache headers for assets
gsutil -m setmeta -h "Cache-Control:public, max-age=31536000" \
  gs://my-astro-site/_astro/**
```

### Cloud CDN Setup

1. Create a backend bucket in Cloud Console
2. Point it to your GCS bucket
3. Create a load balancer with the backend bucket
4. Enable Cloud CDN on the backend bucket
5. Configure SSL certificate for HTTPS

```bash
# Invalidate CDN cache after deploy
gcloud compute url-maps invalidate-cdn-cache my-lb \
  --path "/*" --async
```

### When to Use GCS + CDN vs Firebase

| Scenario | Recommendation |
|----------|----------------|
| Simple static site | Firebase Hosting |
| Need fine-grained cache control | GCS + CDN |
| Already using GCP extensively | GCS + CDN |
| Want simplest setup | Firebase Hosting |
| Need custom CDN configuration | GCS + CDN |

## Common Issues and Solutions

### Trailing Slashes

```javascript
// astro.config.mjs
export default defineConfig({
  trailingSlash: 'always'  // or 'never' or 'ignore'
});
```

### Base Path for Subdirectory

```javascript
// astro.config.mjs
export default defineConfig({
  site: 'https://example.com',
  base: '/my-app'
});
```

Update all internal links:

```astro
<a href={`${import.meta.env.BASE_URL}about`}>About</a>
```

### 404 Handling

Most platforms need explicit 404 configuration:

1. Create `src/pages/404.astro`
2. Configure platform-specific redirects

### Build Failures

Common causes:
- Node version mismatch (use v18+)
- Missing environment variables
- Case-sensitive file systems (Linux vs macOS)
- Memory limits for large sites

### Asset Caching

For optimal performance, ensure assets have cache headers:

```javascript
// astro.config.mjs
export default defineConfig({
  build: {
    assets: '_assets'  // Prefixed directory for fingerprinted assets
  }
});
```

## Performance Optimization

### Pre-compression

```javascript
// astro.config.mjs
import compress from 'astro-compress';

export default defineConfig({
  integrations: [compress()]
});
```

### Image Optimization

```javascript
// astro.config.mjs
export default defineConfig({
  image: {
    service: {
      entrypoint: 'astro/assets/services/sharp'
    }
  }
});
```

### Prefetching

```javascript
// astro.config.mjs
export default defineConfig({
  prefetch: {
    prefetchAll: true,
    defaultStrategy: 'viewport'
  }
});
```
