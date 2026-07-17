import Script from 'next/script';

export default function AdSenseScript() {
  const enabled = process.env.NEXT_PUBLIC_ADSENSE_ENABLED === 'true';
  const adClientId = process.env.NEXT_PUBLIC_ADSENSE_CLIENT_ID;

  if (!enabled || !adClientId) {
    return null;
  }

  return (
    <Script
      async
      src={`https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=${adClientId}`}
      crossOrigin="anonymous"
      strategy="afterInteractive"
    />
  );
}
