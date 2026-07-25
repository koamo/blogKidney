import Link from 'next/link';

export default function AuthorBio({ lang = 'ko' }: { lang?: string }) {
  return (
    <section data-lang={lang} aria-label="작성자 정보" className="mt-14 border-t border-[#d8e1dd] pt-7">
      <div className="flex gap-4">
        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded bg-[#dcefeb] text-sm font-bold text-[#176d68]">KL</div>
        <div>
          <h2 className="text-base font-bold text-[#17313a]">KidneyLife 운영자</h2>
          <p className="mt-2 text-sm leading-6 text-[#5b7076]">
            의료인이 아닌 개인 운영자가 공식 기관 자료와 원문을 일반 독자가 확인하기 쉽게 재구성합니다. 출처와 표현을 점검하지만 이는 의학 감수가 아니며, 전문 의료인의 감수가 있는 글만 감수자와 범위를 별도로 표시합니다.
          </p>
          <Link href={`/${lang}/about`} className="mt-3 inline-block text-sm font-semibold text-[#176d68] underline underline-offset-4">
            운영자와 편집 방식 확인
          </Link>
        </div>
      </div>
    </section>
  );
}
