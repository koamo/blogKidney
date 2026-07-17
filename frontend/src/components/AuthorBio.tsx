import Link from 'next/link';

export default function AuthorBio({ lang = 'ko' }: { lang?: string }) {
  return (
    <section data-lang={lang} aria-label="작성자 정보" className="mt-14 border-t border-[#d8e1dd] pt-7">
      <div className="flex gap-4">
        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded bg-[#dcefeb] text-sm font-bold text-[#176d68]">KL</div>
        <div>
          <h2 className="text-base font-bold text-[#17313a]">KidneyLife 자료 편집부</h2>
          <p className="mt-2 text-sm leading-6 text-[#5b7076]">
            공식 기관 자료와 연구 원문을 일반 독자가 확인하기 쉽게 재구성합니다. 자료 편집부는 의료기관이 아니며, 전문의 감수가 있는 글은 감수자와 범위를 별도로 표시합니다.
          </p>
          <Link href={`/${lang}/editorial-policy`} className="mt-3 inline-block text-sm font-semibold text-[#176d68] underline underline-offset-4">
            편집·정정 원칙 확인
          </Link>
        </div>
      </div>
    </section>
  );
}
