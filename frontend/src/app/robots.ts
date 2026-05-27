import { MetadataRoute } from 'next';

/**
 * 구글 및 전 세계 검색엔진 크롤러봇에게 사이트 크롤링 정책을 동적으로 가이드하는 robots.txt 파일 생성기입니다.
 */
export default function robots(): MetadataRoute.Robots {
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://blog-site-seven-weld.vercel.app';
  
  return {
    rules: {
      userAgent: '*',     // 모든 검색 로봇 지정
      allow: '/',         // 사이트 전체 영역 크롤링 허용 (애드센스 승인 보장)
      disallow: '/private/', // 비공개 시스템 영역 차단
    },
    sitemap: `${baseUrl}/sitemap.xml`, // 사이트맵 실제 경로 자동 맵핑
  };
}