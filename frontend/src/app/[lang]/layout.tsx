import type { Metadata } from 'next';
import { Outfit, Inter } from 'next/font/google';
import '../globals.css';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import AdSenseScript from '@/components/AdSenseScript';
// Outfit 폰트 설정 (Next.js 폰트 최적화)
const outfit = Outfit({
  subsets: ['latin'],
  variable: '--font-outfit',
  display: 'swap',
});
// Inter 폰트 설정 (Next.js 폰트 최적화)
const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});
export const metadata: Metadata = {
  title: {
    default: 'KidneyLife - 신장 건강과 만성 콩팥병 생활 관리',
    template: '%s | KidneyLife',
  },
  // [네이버 80자 최적화]: 공백 포함 76자로 구성하여 서치어드바이저의 가독성 경고를 완벽하게 방어
  description: '만성 콩팥병, 복막투석, 신장 건강 식단 정보를 일반 독자가 이해하기 쉽게 정리하는 건강 정보 블로그입니다.',
  keywords: ['콩팥병', '만성콩팥병식단', '신장건강', '식이요법', '저염식', '저칼륨', 'KidneyLife'],
  authors: [{ name: 'KidneyLife' }],
  creator: 'KidneyLife',
  publisher: 'KidneyLife',
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || 'https://kidney-life.vercel.app'),
  alternates: {
    canonical: '/ko',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-snippet': -1,
      'max-image-preview': 'large',
      'max-video-preview': -1,
    },
  },
// [소셜 미디어 공유 최적화]: SNS 공유 SEO Open Graph 고도화 및 76자 설명 주입
  openGraph: {
    title: 'KidneyLife - 신장 건강과 만성 콩팥병 생활 관리',
    description: '만성 콩팥병, 복막투석, 신장 건강 식단 정보를 일반 독자가 이해하기 쉽게 정리하는 건강 정보 블로그입니다.',
    url: '/ko',
    siteName: 'KidneyLife',
    locale: 'ko_KR',
    type: 'website',
    images: [
      {
        url: '/ko',
        width: 800,
        height: 600,
        alt: 'KidneyLife Healthy Diet and Healing Nature',
      },
    ],
  },
  // [구글 검색 노출]: 구글 서치 콘솔 등록을 위한 소유권 인증 고유키 설정
  verification: {
    google: 'bGXWFZLkGtDdZACKeIEY5pQB87_7TK1-UatjnGobEkk',
  },
  other: {
    // 구글 애드센스 승인 신청을 위한 계정 확인 고유 키 연동
    'google-adsense-account': 'ca-pub-7317136702675678',
    // 네이버 서치어드바이저 등록을 위한 사이트 소유권 확인 고유 키 연동
    'naver-site-verification': '5454dce125cdb9bd0167f950be749faf191a9cf8',
  },
};
// Next.js 16 App Router용 전역 Props 타입 설정
interface LayoutProps {
  children: React.ReactNode;
  params: Promise<{
    lang: string;
  }>;
}
/**
 * 신장건강 정보 포털의 전역 루트 레이아웃 컴포넌트입니다.
 */
export default async function RootLayout({
  children,
  params,
}: LayoutProps) {
  const resolvedParams = await params;
  const lang = resolvedParams.lang || 'ko';
  return (
    <html lang={lang} className={`${outfit.variable} ${inter.variable}`}>
      <body className="flex min-h-screen flex-col bg-[#031b15] text-emerald-50 antialiased">
        {/* 구글 애드센스 자동 광고 주입 스크립트 */}
        <AdSenseScript />
        {/* 공통 상단 네비게이션 헤더 */}
        <Header lang={lang} />
        {/* 본문 콘텐츠 영역 */}
        <main className="flex-grow">
          {children}
        </main>
        {/* 공통 하단 푸터 */}
        <Footer />
      </body>
    </html>
  );
}
