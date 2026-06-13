'use client';

import React from 'react';

export default function MedicalDisclaimer({ lang = 'ko' }: { lang?: string }) {
  const translations = {
    ko: {
      title: '⚠️ 의학적 책임 한계 고지 (Medical Disclaimer)',
      content: '본 블로그에서 제공하는 모든 정보는 일반적인 건강 및 영양 지식 전달을 목적으로 하며, 전문적인 의학적 진단, 진료, 혹은 치료를 대신할 수 없습니다. 신장 질환 및 관련 건강 문제에 대한 결정은 반드시 담당 전문의(신장내과 등)와의 상담을 통해 이루어져야 합니다. 본 사이트의 정보에만 의존하여 발생하는 어떠한 결과에 대해서도 책임을 지지 않습니다.'
    },
    en: {
      title: '⚠️ Medical Disclaimer',
      content: 'All information provided on this blog is for general health and nutritional educational purposes only, and does not substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition. Do not disregard professional medical advice or delay in seeking it because of something you have read on this website.'
    },
    ja: {
      title: '⚠️ 免責事項（Medical Disclaimer）',
      content: 'このブログで提供されるすべての情報は、一般的な健康および栄養知識の伝達を目的としており、専門的な医学的診断や治療の代わりになるものではありません。腎臓疾患や健康に関する決定は、必ず専門医にご相談ください。本サイトの情報のみに依存して生じたいかなる結果についても責任を負いません。'
    }
  };

  const t = translations[lang as 'ko' | 'en' | 'ja'] || translations.ko;

  return (
    <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-5 mb-10">
      <h3 className="text-red-400 font-bold text-sm mb-2">{t.title}</h3>
      <p className="text-red-200/80 text-xs leading-relaxed">
        {t.content}
      </p>
    </div>
  );
}
