import React from 'react';

export default function AuthorBio({ lang = 'ko' }: { lang?: string }) {
  const t = {
    name: 'KidneyLife',
    role: '신장 건강 정보 편집 노트',
    bio: '만성 콩팥병, 투석, 식이 관리와 관련된 공개 의학 정보를 일반 독자가 이해하기 쉬운 언어로 정리합니다. 모든 글은 진료를 대신하지 않으며 개인별 판단은 담당 의료진과 상의해야 합니다.',
  };

  return (
    <div data-lang={lang} className="mt-16 flex flex-col gap-4 border-t border-emerald-900/60 pt-8 sm:flex-row sm:items-start">
      <div className="flex h-14 w-14 flex-shrink-0 items-center justify-center rounded-lg bg-emerald-950 text-base font-bold text-emerald-200">
        KL
      </div>
      <div>
        <h4 className="mb-1 text-lg font-bold text-white">{t.name}</h4>
        <p className="mb-3 text-sm font-semibold text-emerald-300">{t.role}</p>
        <p className="text-sm leading-relaxed text-slate-300">{t.bio}</p>
      </div>
    </div>
  );
}
