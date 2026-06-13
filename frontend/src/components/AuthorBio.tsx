import React from 'react';

export default function AuthorBio({ lang = 'ko' }: { lang?: string }) {
  const translations = {
    ko: {
      name: 'KidneyLog Research Team',
      role: '의학 데이터 스페셜리스트 & 신장 라이프 큐레이터',
      bio: '우리는 전 세계의 최신 신장내과 논문, 영양학 가이드라인, 의학 뉴스를 매일 분석하여 신장병 환우와 가족분들에게 가장 정확하고 따뜻한 정보를 전달합니다. "정확한 지식이 콩팥을 살린다"는 믿음 아래 연구합니다.',
      articles: '모든 작성 글 보기'
    },
    en: {
      name: 'KidneyLog Research Team',
      role: 'Medical Data Specialist & Renal Life Curator',
      bio: 'We analyze the latest nephrology papers, nutritional guidelines, and medical news globally every day to deliver the most accurate and compassionate information to kidney patients and their families. We believe that "Accurate knowledge saves kidneys."',
      articles: 'View all articles'
    },
    ja: {
      name: 'KidneyLog Research Team',
      role: '医学データスペシャリスト & 腎臓ライフキュレーター',
      bio: '私たちは毎日、世界中の最新の腎臓内科論文、栄養ガイドライン、医学ニュースを分析し、腎臓病患者やそのご家族に最も正確で温かい情報をお届けします。「正確な知識が腎臓を救う」という信念のもと研究を続けています。',
      articles: 'すべての記事を見る'
    }
  };

  const t = translations[lang as 'ko' | 'en' | 'ja'] || translations.ko;

  return (
    <div className="mt-16 pt-8 border-t border-slate-800/60 flex flex-col sm:flex-row gap-6 items-start">
      <div className="w-16 h-16 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-600 flex-shrink-0 flex items-center justify-center text-xl text-white font-black shadow-lg">
        KR
      </div>
      <div>
        <h4 className="text-lg font-bold text-white mb-1">{t.name}</h4>
        <p className="text-violet-400 text-sm font-semibold mb-3">{t.role}</p>
        <p className="text-slate-400 text-sm leading-relaxed mb-4">
          {t.bio}
        </p>
      </div>
    </div>
  );
}
