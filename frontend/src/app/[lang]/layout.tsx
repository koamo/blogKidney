import type { Metadata } from 'next';
import { Outfit, Inter } from 'next/font/google';
import '../globals.css'; 
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import AdSenseScript from '@/components/AdSenseScript';

// Outfit 폰트 설정
const outfit = Outfit({
  subsets: ['latin'],
  variable: '--font-outfit',
  display: 'swap',
});

// Inter 폰트 설정
const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

export const metadata: Metadata = {
  title: {
    default: 'KidneyLife - 만성 콩팥병 식이요법 및 건강 가이드 전문 블로그',
    template: '%s | KidneyLife',
  },
  description: '만성 콩팥병(만성 신부전), 사구체신염 환우들을 위한 저나트륨/저칼륨/저인/저단백 4대 식단 관리 요령과 올바른 의학 건강 정보를 전달하는 프리미엄 정적 헬스 매거진입니다.',
  keywords: ['만성콩팥병', '콩팥병식단', '신장건강', '식이요법', '저염식', '저칼륨', 'KidneyLife'],
  authors: [{ name: 'KidneyLife' }],
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || 'https://kidney-life.vercel.app'), 
  
  // [보완 핵심]: 신장 건강 및 콩팥병 환우용 SNS 카드 공유 및 SEO Open Graph 최적화
  openGraph: {
    title: 'KidneyLife - 만성 콩팥병 식이요법 및 건강 가이드 전문 블로그',
    description: '만성 콩팥병(만성 신부전), 사구체신염 환우들을 위한 저나트륨/저칼륨/저인/저단백 4대 식단 관리 요령과 올바른 의학 건강 정보를 전달하는 프리미엄 정적 헬스 매거진입니다.',
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
  
  // [보안 공정]: 신규 블로그용 검색 소유권 인증은 깨끗하게 초기화하여 추후 신규 주소 발급 시 입력 대기
  verification: {
    google: '',
  },
  other: {
    // IT 블로그와 다른 고유 신장 블로그용 애드센스 승인/소유권을 위해 초기화 또는 추후 병합
    'google-adsense-account': 'ca-pub-7317136702675678', 
  },
};

// Next.js 16 글로벌 레이아웃용 Props 타입 정의
interface LayoutProps {
  children: React.ReactNode;
  params: Promise<{
    lang: string;
  }>;
}

/**
 * 신장 건강 다국어 정적 세그먼트 최상단에서 시작하는 전역 루트 레이아웃 컴포넌트입니다.
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
        {/* 구글 애드센스 전역 심사 스크립트 */}
        <AdSenseScript />
        
        {/* 상단 다국어 선택 스위처가 내장된 헤더 */}
        <Header lang={lang} />
        
        {/* 본문 콘텐츠 렌더링 영역 */}
        <main className="flex-grow">
          {children}
        </main>
        
        {/* 하단 푸터 */}
        <Footer />
      </body>
    </html>
  );
}