import { MetadataRoute } from 'next';
import postsData from '@/data/posts.json';

interface BlogPost {
  slug: string;
  date: string;
  reviewedAt?: string;
  thumbnail?: string;
}

export default function sitemap(): MetadataRoute.Sitemap {
  const posts = postsData as BlogPost[];
  const baseUrl = (process.env.NEXT_PUBLIC_SITE_URL || 'https://kidney-life.vercel.app').replace(/\/$/, '');

  const staticRoutes = ['/ko', '/ko/archive', '/ko/about', '/ko/editorial-policy', '/ko/privacy', '/ko/terms'];

  const routes = staticRoutes.map((route) => ({
    url: `${baseUrl}${route}`,
    changeFrequency: 'weekly' as const,
    priority: route === '/ko' ? 1.0 : 0.6,
  }));

  const postRoutes = posts.map((post) => ({
    url: `${baseUrl}/ko/posts/${post.slug}`,
    lastModified: new Date(post.reviewedAt || post.date),
    changeFrequency: 'monthly' as const,
    priority: 0.8,
    images: post.thumbnail ? [new URL(post.thumbnail, baseUrl).toString()] : undefined,
  }));

  return [...routes, ...postRoutes];
}
