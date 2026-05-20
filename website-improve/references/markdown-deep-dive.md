# Markdown Deep Dive for Astro

Advanced patterns for Markdown and MDX content in Astro static sites.

## Static Markdown Rendering

Astro treats Markdown as build-time content with zero runtime cost:

- Parsed and transformed to HTML during build
- Excellent SEO out of the box
- Full control over layout and styling
- Clean separation of content and presentation

## Content Collection Best Practices

### Schema Patterns

```typescript
// src/content/config.ts
import { defineCollection, z, reference } from "astro:content";

export const collections = {
  // Blog with author references
  blog: defineCollection({
    schema: z.object({
      title: z.string(),
      description: z.string(),
      pubDate: z.coerce.date(),
      updatedDate: z.coerce.date().optional(),
      heroImage: z.string().optional(),
      author: reference('authors'),  // Reference another collection
      tags: z.array(z.string()).default([]),
      draft: z.boolean().default(false)
    })
  }),

  // Authors collection
  authors: defineCollection({
    schema: z.object({
      name: z.string(),
      avatar: z.string(),
      bio: z.string()
    })
  }),

  // Documentation with ordering
  docs: defineCollection({
    schema: z.object({
      title: z.string(),
      description: z.string().optional(),
      sidebar: z.object({
        order: z.number(),
        label: z.string().optional()
      }).optional()
    })
  })
};
```

### Filtering Collections

```astro
---
import { getCollection } from "astro:content";

// Filter out drafts in production
const publishedPosts = await getCollection('blog', ({ data }) => {
  return import.meta.env.PROD ? data.draft !== true : true;
});

// Sort by date
const sortedPosts = publishedPosts.sort(
  (a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf()
);

// Filter by tag
const rustPosts = await getCollection('blog', ({ data }) => {
  return data.tags.includes('rust');
});
---
```

## Advanced Code Block Features

### Shiki Configuration Options

```javascript
// astro.config.mjs
export default defineConfig({
  markdown: {
    shikiConfig: {
      // Available themes: https://shiki.style/themes
      theme: 'github-dark',
      // Or use dual themes for light/dark mode
      themes: {
        light: 'github-light',
        dark: 'github-dark'
      },
      // Enable word wrap
      wrap: true,
      // Add custom languages
      langs: []
    }
  }
});
```

### Line Highlighting Syntax

```markdown
<!-- Highlight lines 2-4 -->
```js {2-4}
const a = 1;
const b = 2;
const c = 3;
const d = 4;
```

<!-- Highlight with markers -->
```js {2} ins={3} del={4}
const original = 1;
const modified = 2;  // highlighted
const added = 3;     // green (inserted)
const removed = 4;   // red (deleted)
```
```

### Code Block Titles

```markdown
```js title="src/utils/helper.js"
export function helper() {
  return 'Hello';
}
```
```

## MDX Integration

Install and configure:

```bash
npx astro add mdx
```

```javascript
// astro.config.mjs
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';

export default defineConfig({
  integrations: [mdx()]
});
```

### Using Components in MDX

```mdx
---
title: My Article
---
import Callout from '../components/Callout.astro';
import CodeDemo from '../components/CodeDemo.jsx';

# {frontmatter.title}

<Callout type="warning">
  This is an important warning!
</Callout>

Here's an interactive demo:

<CodeDemo client:visible />
```

### Component Mapping

Override default HTML elements:

```astro
---
// src/pages/blog/[slug].astro
import { getEntry } from 'astro:content';
import CustomHeading from '../components/CustomHeading.astro';
import CustomCode from '../components/CustomCode.astro';

const { slug } = Astro.params;
const post = await getEntry('blog', slug);
const { Content } = await post.render();
---

<Content components={{
  h1: CustomHeading,
  h2: CustomHeading,
  pre: CustomCode
}} />
```

## Remark and Rehype Plugins

### Common Plugin Setup

```javascript
// astro.config.mjs
import { defineConfig } from 'astro/config';
import remarkToc from 'remark-toc';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import rehypeSlug from 'rehype-slug';
import rehypeAutolinkHeadings from 'rehype-autolink-headings';

export default defineConfig({
  markdown: {
    remarkPlugins: [
      remarkToc,
      remarkMath
    ],
    rehypePlugins: [
      rehypeSlug,
      [rehypeAutolinkHeadings, { behavior: 'wrap' }],
      rehypeKatex
    ]
  }
});
```

### Reading Time Plugin

```javascript
// plugins/remark-reading-time.mjs
import getReadingTime from 'reading-time';
import { toString } from 'mdast-util-to-string';

export function remarkReadingTime() {
  return function (tree, { data }) {
    const textOnPage = toString(tree);
    const readingTime = getReadingTime(textOnPage);
    data.astro.frontmatter.minutesRead = readingTime.text;
  };
}
```

```javascript
// astro.config.mjs
import { remarkReadingTime } from './plugins/remark-reading-time.mjs';

export default defineConfig({
  markdown: {
    remarkPlugins: [remarkReadingTime]
  }
});
```

## Table of Contents Generation

### Manual Approach

```astro
---
import { getEntry } from 'astro:content';

const post = await getEntry('blog', 'my-post');
const { Content, headings } = await post.render();

// headings is an array of { depth, slug, text }
---

<nav class="toc">
  <h2>On This Page</h2>
  <ul>
    {headings
      .filter(h => h.depth <= 3)
      .map(h => (
        <li style={`margin-left: ${(h.depth - 2) * 1rem}`}>
          <a href={`#${h.slug}`}>{h.text}</a>
        </li>
      ))
    }
  </ul>
</nav>

<article>
  <Content />
</article>
```

## Images in Markdown

### Local Images with Optimization

```markdown
<!-- Use relative paths for optimization -->
![Alt text](./hero.png)

<!-- Or import in MDX -->
import heroImage from './hero.png';

<img src={heroImage.src} alt="Hero" />
```

### Remote Images

```javascript
// astro.config.mjs
export default defineConfig({
  image: {
    domains: ['images.unsplash.com'],
    remotePatterns: [{ protocol: 'https' }]
  }
});
```

```astro
---
import { Image } from 'astro:assets';
---

<Image
  src="https://images.unsplash.com/photo-..."
  alt="Description"
  width={800}
  height={600}
/>
```

## Custom Frontmatter Fields

Access custom fields in rendered content:

```markdown
---
title: My Post
customField: Special Value
---
```

```astro
---
const post = await getEntry('blog', 'my-post');
console.log(post.data.customField); // "Special Value"
---
```

## Performance Considerations

1. **Build-time only**: All Markdown processing happens at build
2. **No runtime parsing**: Output is pure HTML
3. **Syntax highlighting**: Pre-computed, no client-side JS
4. **Lazy loading**: Use `loading="lazy"` for images
5. **Content caching**: Astro caches processed Markdown between builds

## Troubleshooting Markdown Issues

**Frontmatter validation errors:**
```bash
astro check  # Shows detailed schema errors
```

**Code block not highlighting:**
- Ensure language tag is specified: \`\`\`javascript
- Check theme is properly configured

**MDX components not rendering:**
- Verify component is imported at top of file
- Check component path is correct
- Ensure MDX integration is installed

**Slow builds with many Markdown files:**
- Consider incremental builds
- Use `content.config.ts` type generation caching
