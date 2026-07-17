import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: '개인정보처리방침',
  description: 'KidneyLife의 개인정보 처리 및 광고·분석 도구 사용 기준을 안내합니다.',
  alternates: { canonical: '/ko/privacy' },
};

interface PageProps {
  params: Promise<{ lang: string }>;
}

export default async function PrivacyPage({ params }: PageProps) {
  await params;
  const contactEmail = process.env.NEXT_PUBLIC_CONTACT_EMAIL || 'admin@goldenlog.tech';

  return (
    <div className="prose mx-auto max-w-3xl px-5 py-12 md:py-16">
      <h1>개인정보처리방침</h1>
      <p>KidneyLife는 사이트 운영, 보안, 통계 분석, 광고 제공을 위해 필요한 최소한의 정보를 처리할 수 있습니다.</p>
      <h2>수집될 수 있는 정보</h2>
      <p>방문 로그, 브라우저 정보, 접속 시간, 참조 URL, 쿠키 정보가 수집될 수 있으며, 이는 개인을 직접 식별하기 위한 목적으로 사용하지 않습니다.</p>
      <h2>쿠키와 광고</h2>
      <p>본 사이트는 Google AdSense 등 제3자 광고 서비스를 사용할 수 있습니다. Google은 광고 제공을 위해 쿠키를 사용할 수 있으며, 사용자는 브라우저 설정이나 Google 광고 설정에서 맞춤 광고를 관리할 수 있습니다.</p>
      <h2>문의</h2>
      <p>개인정보 관련 문의는 <a href={`mailto:${contactEmail}`}>{contactEmail}</a>로 연락해 주세요.</p>
      <p className="text-sm text-[#718287]">최종 갱신: 2026년 7월 18일</p>
    </div>
  );
}
