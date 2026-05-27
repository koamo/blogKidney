import Script from 'next/script';

/**
 * 구글 애드센스 승인 및 자동 광고 연동을 위한 전역 스크립트 컴포넌트입니다.
 * NEXT_PUBLIC_ADSENSE_CLIENT_ID 환경변수가 존재하면 활용하고, 없을 시 기본 테스트 코드를 적용합니다.
 */
export default function AdSenseScript() {
  const adClientId = process.env.NEXT_PUBLIC_ADSENSE_CLIENT_ID || 'ca-pub-XXXXXXXXXXXXXXXX'; 

  // 구글 애드센스 공식 주입 스크립트 주소 호출
  return (
    <Script
      async
      src={`https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=${adClientId}`}
      crossOrigin="anonymous"
      strategy="afterInteractive" // 페이지 렌더링 완료 직후 안전하게 주입
    />
  );
}
