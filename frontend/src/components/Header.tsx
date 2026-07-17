import Link from 'next/link';

interface HeaderProps {
  lang: string;
}

export default function Header({ lang = 'ko' }: HeaderProps) {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-[#d8e1dd] bg-white/95 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between gap-4 px-5">
        <Link href={`/${lang}`} className="flex min-w-0 items-center gap-2 text-[#17313a]">
          <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded bg-[#176d68] text-xs font-bold text-white">KL</span>
          <span className="truncate text-base font-bold">KidneyLife</span>
        </Link>
        <nav aria-label="주요 메뉴" className="flex items-center gap-4 text-xs font-semibold text-[#4e656c] sm:gap-6 sm:text-sm">
          <Link href={`/${lang}/archive`} className="hover:text-[#176d68]">전체 글</Link>
          <Link href={`/${lang}/about`} className="hover:text-[#176d68]">소개</Link>
          <Link href={`/${lang}/editorial-policy`} className="hover:text-[#176d68]">편집 원칙</Link>
        </nav>
      </div>
    </header>
  );
}
