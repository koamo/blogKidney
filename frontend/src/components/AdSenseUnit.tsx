'use client';

import { useEffect, useRef } from 'react';

interface AdSenseUnitProps {
  slot: string;
  format?: 'auto' | 'fluid' | 'rectangle';
  responsive?: 'true' | 'false';
  style?: React.CSSProperties;
}

export default function AdSenseUnit({
  slot,
  format = 'auto',
  responsive = 'true',
  style = { display: 'block' },
}: AdSenseUnitProps) {
  const initialized = useRef(false);
  const enabled = process.env.NEXT_PUBLIC_ADSENSE_ENABLED === 'true';
  const adClientId = process.env.NEXT_PUBLIC_ADSENSE_CLIENT_ID;

  useEffect(() => {
    if (!enabled || !adClientId || initialized.current || typeof window === 'undefined') {
      return;
    }
    try {
      // @ts-expect-error adsbygoogle is injected by the AdSense script
      (window.adsbygoogle = window.adsbygoogle || []).push({});
      initialized.current = true;
    } catch (error) {
      console.error('[AdSense] 광고 로드 실패:', error);
    }
  }, [adClientId, enabled]);

  if (!enabled || !adClientId) {
    return null;
  }

  return (
    <div className="my-12 w-full border-y border-[#e1e8e4] py-5">
      <p className="mb-2 text-center text-[10px] font-semibold text-[#879397]">광고</p>
      <ins
        className="adsbygoogle"
        style={style}
        data-ad-client={adClientId}
        data-ad-slot={slot}
        data-ad-format={format}
        data-full-width-responsive={responsive}
      />
    </div>
  );
}
