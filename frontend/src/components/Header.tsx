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
export default function Header({ lang = 'ko' }: HeaderProps) {
  const navHome = '홈';
  const navArchive = '모든 칼럼';

  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-200/10 bg-[#030712]/80 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        
        {/* 브랜드 로고 (클릭 시 현재 언어의 메인 홈으로 이동) */}
        <Link href={`/${lang}`} className="flex items-center gap-2">
          {/* 생명력과 정화를 상징하는 블루-그린-퍼플 그라데이션 타이포그래피 */}
          <span className="bg-gradient-to-r from-violet-400 via-indigo-400 to-cyan-400 bg-clip-text text-xl font-black tracking-tight text-transparent transition-transform hover:scale-105 duration-200">
            KidneyLife.
          </span>
        </Link>
        
        {/* 네비게이션 영역 */}
        <div className="flex items-center gap-6">
          <Link 
            href={`/${lang}`} 
            className="text-sm font-medium text-slate-300 hover:text-violet-300 transition-colors"
          >
            {navHome}
          </Link>
          <Link 
            href={`/${lang}/archive`} 
            className="text-sm font-medium text-slate-300 hover:text-violet-300 transition-colors"
          >
            {navArchive}
          </Link>
        </div>
        
      </div>
    </header>
  );
}
