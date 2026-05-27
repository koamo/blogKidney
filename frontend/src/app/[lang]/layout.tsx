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
    default: 'KidneyLife - 만성 콩팥병 식이요법 및 건강관리 전문 블로그',
    template: '%s | KidneyLife',
  },
  description: '만성 콩팥병(만성 신부전), 사구체신염 환우를 위한 저나트륨/저칼륨/저인/저단백 4대 식단 조절 가이드와 올바른 신장 건강 의학 정보를 제공하는 미디어 플랫폼입니다.',
  keywords: ['콩팥병', '만성콩팥병식단', '신장건강', '식이요법', '저염식', '저칼륨', 'KidneyLife'],
  authors: [{ name: 'KidneyLife' }],
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || 'https://kidney-life.vercel.app'), 
  
  // [소셜 미디어 공유 최적화]: 신장 건강 및 만성 콩팥병 환우 SNS 카카오톡 및 페이스북 공유 SEO Open Graph 고도화
  openGraph: {
    title: 'KidneyLife - 만성 콩팥병 식이요법 및 건강관리 전문 블로그',
    description: '만성 콩팥병(만성 신부전), 사구체신염 환우를 위한 저나트륨/저칼륨/저인/저단백 4대 식단 조절 가이드와 올바른 신장 건강 의학 정보를 제공하는 미디어 플랫폼입니다.',
    url: 'https://kidney-life.vercel.app',
    siteName: 'KidneyLife',
    locale: 'ko_KR',
    type: 'website',
    images: [
      {
        url: 'https://images.unsplash.com/photo-1498837167922-ddd27525d352?auto=format&fit=crop&w=800&q=80',
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
