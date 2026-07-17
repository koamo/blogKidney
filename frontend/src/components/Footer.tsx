import Link from 'next/link';

export default function Footer({ lang = 'ko' }: { lang?: string }) {
  return (
    <footer className="mt-auto w-full border-t border-[#d8e1dd] bg-white py-10">
      <div className="mx-auto max-w-6xl px-5">
        <div className="flex flex-col justify-between gap-5 md:flex-row md:items-start">
          <div>
            <p className="text-sm font-bold text-[#17313a]">KidneyLife</p>
            <p className="mt-2 max-w-xl text-xs leading-5 text-[#66787d]">
              공개된 공식 자료와 연구 원문을 바탕으로 신장 건강 정보를 정리합니다. 자료 편집 검토는 전문의의 의학적 감수를 뜻하지 않습니다.
            </p>
          </div>
          <nav aria-label="정책 문서" className="flex flex-wrap gap-x-4 gap-y-2 text-xs font-medium text-[#5a7076]">
            <Link href={`/${lang}/about`} className="hover:text-[#176d68]">소개</Link>
            <Link href={`/${lang}/editorial-policy`} className="hover:text-[#176d68]">편집·정정 원칙</Link>
            <Link href={`/${lang}/privacy`} className="hover:text-[#176d68]">개인정보처리방침</Link>
            <Link href={`/${lang}/terms`} className="hover:text-[#176d68]">이용약관</Link>
          </nav>
        </div>
        <p className="mt-7 border-t border-[#e3e9e6] pt-5 text-xs text-[#7a898d]">© 2026 KidneyLife. All rights reserved.</p>
      </div>
    </footer>
  );
}
