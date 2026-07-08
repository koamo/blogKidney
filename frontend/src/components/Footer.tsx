import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="mt-auto w-full border-t border-slate-200/5 bg-slate-950/60 py-10">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-6 text-center md:flex-row md:text-left">
        <div>
          <p className="text-sm font-semibold text-slate-400">KidneyLife. 신장 건강 정보 노트</p>
          <p className="mt-1 text-xs text-slate-500">© 2026 KidneyLife. All rights reserved.</p>
        </div>
        <nav aria-label="정책 문서" className="flex gap-4 text-xs text-slate-500">
          <Link href="/ko/about" className="transition-colors hover:text-slate-300">소개</Link>
          <span aria-hidden="true">·</span>
          <Link href="/ko/privacy" className="transition-colors hover:text-slate-300">개인정보처리방침</Link>
          <span aria-hidden="true">·</span>
          <Link href="/ko/terms" className="transition-colors hover:text-slate-300">이용약관</Link>
        </nav>
      </div>
    </footer>
  );
}
