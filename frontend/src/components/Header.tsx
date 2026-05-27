'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface HeaderProps {
  lang: string;
}

/**
 * 다국어(ko/en/ja) 스위치 유닛을 탑재한 글로벌 상단 네비게이션 바입니다.
 * (클라이언트 컴포넌트 - path 탐색 및 라우트 대체 헬퍼 기동)
 */
export default function Header({ lang }: HeaderProps) {
  const pathname = usePathname();

  /**
   * [지능형 라우트 보존]: 사용자가 글 상세 페이지(예: /ko/posts/adsense)를 읽던 중
   * 영어(en) 버튼을 클릭하면, 메인 홈이 아닌 /en/posts/adsense 상세 페이지 번역본으로 동적 연동하여 워프시킵니다.
   */
  const getLanguageLink = (targetLang: string) => {
    if (!pathname) return `/${targetLang}`;
    const segments = pathname.split('/');
    // segments 구조: ['', 'ko', 'posts', 'slug'] -> index 1번이 로케일 코드
    if (segments.length > 1) {
      segments[1] = targetLang;
    }
    return segments.join('/');
  };

  // UI 언어 분기
  const navText = {
    ko: '전체 기사',
    en: 'Articles',
    ja: '記事一覧'
  }[lang as 'ko' | 'en' | 'ja'] || '전체 기사';

  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-200/10 bg-[#030712]/80 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        
        {/* 브랜드 로고 (클릭 시 현재 언어의 메인 홈으로 이동) */}
        <Link href={`/${lang}`} className="flex items-center gap-2">
          <span className="bg-gradient-to-r from-violet-400 via-indigo-400 to-cyan-400 bg-clip-text text-xl font-black tracking-tight text-transparent transition-transform hover:scale-105 duration-200">
            GoldenLog.
          </span>
        </Link>
        
        {/* 네비게이션 영역 */}
        <div className="flex items-center gap-6">
          <Link 
            href={`/${lang}`} 
            className="text-sm font-medium text-slate-300 hover:text-violet-300 transition-colors"
          >
            {navText}
          </Link>
          
          {/* [다국어 퀵 스위처]: 미니멀 네온 아우라 세그먼트 버튼 */}
          <div className="flex items-center gap-1 rounded-full bg-slate-950/80 border border-slate-800/80 p-1">
            {(['ko', 'en', 'ja'] as const).map((locale) => (
              <Link
                key={locale}
                href={getLanguageLink(locale)}
                className={`rounded-full px-2.5 py-0.5 text-[10px] font-bold uppercase transition-all duration-300 ${
                  lang === locale
                    ? 'bg-violet-600 text-white shadow-md shadow-violet-600/40' // 활성 언어: 보라색 발광
                    : 'text-slate-500 hover:text-slate-200'                      // 비활성 언어: 차분한 그레이
                }`}
              >
                {locale}
              </Link>
            ))}
          </div>
        </div>
        
      </div>
    </header>
  );
}
