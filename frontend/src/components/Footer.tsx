/**
 * 블로그의 글로벌 하단 푸터 컴포넌트입니다.
 * 차분한 무채색 계열 다크 테마를 기반으로 전문적인 저작권 정보 및 약관 링크를 제공합니다.
 */
export default function Footer() {
  return (
    <footer className="w-full border-t border-slate-200/5 bg-slate-950/60 py-10 mt-auto">
      <div className="mx-auto max-w-6xl px-6 flex flex-col md:flex-row items-center justify-between gap-4 text-center md:text-left">
        
        {/* 저작권 및 블로그 브랜딩 정보 */}
        <div>
          <p className="text-sm font-semibold text-slate-400">GoldenLog. 개인 지식 아카이브</p>
          <p className="text-xs text-slate-500 mt-1">
            © 2026 GoldenLog. All rights reserved. Powered by Next.js 16 (App Router) & Python 3.12.
          </p>
        </div>
        
        {/* 부가 정책 링크 (구글 애드센스 심사관들이 블로그의 규정 준수 여부를 판단할 때 유용) */}
        <div className="flex gap-4 text-xs text-slate-500">
          <a href="/ko/about" className="hover:text-slate-300 transition-colors">
            소개 (About)
          </a>
          <span>·</span>
          <a href="/ko/privacy" className="hover:text-slate-300 transition-colors">
            개인정보처리방침
          </a>
          <span>·</span>
          <a href="/ko/terms" className="hover:text-slate-300 transition-colors">
            이용약관
          </a>
        </div>
      </div>
    </footer>
  );
}
