'use client';

import { useEffect, useRef } from 'react';

interface AdSenseUnitProps {
  slot: string; // 애드센스 대시보드에서 생성한 광고 슬롯 ID
  format?: 'auto' | 'fluid' | 'rectangle';
  responsive?: 'true' | 'false';
  style?: React.CSSProperties;
}

/**
 * 포스팅 중간 및 하단에 직접 배치할 수 있는 구글 애드센스 맞춤형 광고 유닛 컴포넌트입니다.
 * 광고 로딩 중에 발생할 수 있는 레이아웃 밀림(Layout Shift) 현상을 최소화합니다.
 */
export default function AdSenseUnit({
  slot,
  format = 'auto',
  responsive = 'true',
  style = { display: 'block' },
}: AdSenseUnitProps) {
  const initialized = useRef(false);

  useEffect(() => {
    // 윈도우 환경 및 중복 초기화 방지 필터링
    if (typeof window !== 'undefined' && !initialized.current) {
      try {
        // @ts-ignore
        (window.adsbygoogle = window.adsbygoogle || []).push({});
        initialized.current = true;
      } catch (e) {
        console.error('[AdSense] 광고 로드 실패:', e);
      }
    }
  }, []);

  const adClientId = process.env.NEXT_PUBLIC_ADSENSE_CLIENT_ID || 'ca-pub-XXXXXXXXXXXXXXXX';

  return (
    <div className="my-10 w-full flex flex-col items-center justify-center">
      {/* 구글 애드센스 공식 주입 마크업 구조 */}
      <div className="w-full max-w-4xl overflow-hidden rounded-xl border border-dashed border-slate-800/40 bg-slate-900/10 p-3 dark:border-slate-700/40 dark:bg-white/[0.02]">
        <ins
          className="adsbygoogle"
          style={style}
          data-ad-client={adClientId}
          data-ad-slot={slot}
          data-ad-format={format}
          data-full-width-responsive={responsive}
        />
      </div>
      
      {/* 개발 또는 검토 단계에서 광고 영역이 있음을 보여주는 보조 캡션 */}
      <span className="mt-2 text-[10px] tracking-wider text-slate-500/60 uppercase dark:text-slate-400/30">
        Google Sponsored Ad Area
      </span>
    </div>
  );
}
