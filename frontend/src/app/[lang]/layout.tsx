import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import '../globals.css';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import AdSenseScript from '@/components/AdSenseScript';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

export const metadata: Metadata = {
  title: {
    default: 'KidneyLife - 신장 건강과 투석 생활 정보',
    template: '%s | KidneyLife',
  },
  description: '신장 검사, 만성 콩팥병, 투석과 이식 관련 공개 자료를 환자와 가족이 확인하기 쉽게 정리하는 건강 정보 블로그입니다.',
  keywords: ['콩팥병', '만성콩팥병', '신장검사', '투석', '신장이식', '환자교육', 'KidneyLife'],
  authors: [{ name: 'KidneyLife 자료 편집부' }],
  creator: 'KidneyLife 자료 편집부',
  publisher: 'KidneyLife',
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || 'https://kidney-life.vercel.app'),
  alternates: { canonical: '/ko' },
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
  openGraph: {
    title: 'KidneyLife - 신장 건강과 투석 생활 정보',
    description: '공식 자료와 원문을 바탕으로 신장 건강 정보를 차분하게 정리합니다.',
    url: '/ko',
    siteName: 'KidneyLife',
    locale: 'ko_KR',
    type: 'website',
  },
  verification: {
    google: 'bGXWFZLkGtDdZACKeIEY5pQB87_7TK1-UatjnGobEkk',
  },
  other: {
    'google-adsense-account': 'ca-pub-7317136702675678',
    'naver-site-verification': '5454dce125cdb9bd0167f950be749faf191a9cf8',
  },
};

interface LayoutProps {
  children: React.ReactNode;
  params: Promise<{ lang: string }>;
}

export default async function RootLayout({ children, params }: LayoutProps) {
  const resolvedParams = await params;
  const lang = resolvedParams.lang || 'ko';

  return (
    <html lang={lang} className={inter.variable}>
      <body className="flex min-h-screen flex-col bg-[#f4f7f5] text-[#17313a] antialiased">
        <AdSenseScript />
        <Header lang={lang} />
        <main className="flex-grow">{children}</main>
        <Footer lang={lang} />
      </body>
    </html>
  );
}
