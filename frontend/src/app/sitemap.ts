import { MetadataRoute } from 'next';
import postsData from '@/data/posts.json';

interface BlogPost {
  slug: string;
  date: string;
}

export default function sitemap(): MetadataRoute.Sitemap {
  const posts: BlogPost[] = postsData as BlogPost[];
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://blog-site-seven-weld.vercel.app';

  // 1. 핵심 기본 루트 페이지 설정
  const routes = [
    {
      url: baseUrl,
      lastModified: new Date(),
      changeFrequency: 'daily' as const,
      priority: 1.0,
    },
  ];

  // 2. 다국어 컴파일 기사 주소 자동 연동
  const postRoutes = posts.map((post) => ({
    url: `${baseUrl}/posts/${post.slug}`,
    lastModified: new Date(post.date),
    changeFrequency: 'weekly' as const,
    priority: 0.8,
  }));

  return [...routes, ...postRoutes];
}