import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
  site: 'https://tomjanus.github.io',
  base: '/water-skills',
  integrations: [
    starlight({
      title: 'water-skills',
      description: 'Agent skills for water science and engineering',
      logo: {
        src: './assets/banner.jpg',
        alt: 'water-skills',
      },
      sidebar: [
        {
          label: 'Home',
          items: [
            { label: 'Overview', link: '/' },
          ],
        },
        {
          label: 'Catalog',
          items: [
            { label: 'Skill catalog', link: '/catalog/' },
          ],
        },
        {
          label: 'Guides',
          items: [
            { label: 'Installation & use', link: '/guides/install/' },
            { label: 'Contribute without git', link: '/guides/contribute-without-git/' },
            { label: 'Contribute with git', link: '/guides/contribute-with-git/' },
            { label: 'Author a skill', link: '/guides/author-a-skill/' },
            { label: 'Review & lifecycle', link: '/guides/review-and-lifecycle/' },
            { label: 'Evaluate a skill', link: '/guides/evaluate/' },
            { label: 'Repository reference', link: '/guides/repository-reference/' },
          ],
        },
        {
          label: 'Tutorials',
          items: [
            { label: 'Tutorial index', link: '/tutorials/' },
            { label: '1 · What this repository is', link: '/tutorials/01-what-this-repo-is/' },
            { label: '2 · Use a skill', link: '/tutorials/02-use-a-skill/' },
            { label: '3 · Write knowledge, not documentation', link: '/tutorials/03-write-knowledge-not-docs/' },
            { label: '4 · Propose a skill without git', link: '/tutorials/04-propose-without-git/' },
            { label: '5 · Propose a skill with git', link: '/tutorials/05-propose-with-git/' },
            { label: '6 · How we know a skill works', link: '/tutorials/06-how-we-know-skill-works/' },
            { label: '7 · Review and lifecycle', link: '/tutorials/07-review-and-lifecycle/' },
            { label: '8 · Work with agents', link: '/tutorials/08-work-with-agents/' },
          ],
        },
      ],
      social: [
        { icon: 'discord', label: 'Discord', href: 'https://discord.gg/k49cHHrce' },
      ],
    }),
  ],
});
