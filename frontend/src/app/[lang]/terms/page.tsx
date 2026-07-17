import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: '이용약관',
  description: 'KidneyLife 건강 정보의 이용 범위와 의학적 책임 한계를 안내합니다.',
  alternates: { canonical: '/ko/terms' },
};

interface PageProps {
  params: Promise<{ lang: string }>;
}

export default async function TermsPage({ params }: PageProps) {
  await params;

  return (
    <div className="prose mx-auto max-w-3xl px-5 py-12 md:py-16">
      <h1>이용약관</h1>
      <p>KidneyLife의 콘텐츠는 일반 정보 제공을 목적으로 합니다. 글의 내용을 그대로 적용하기 전에 각자의 상황과 최신 자료를 함께 확인해 주세요.</p>
      <h2>콘텐츠 이용</h2>
      <p>사이트의 글, 이미지, 편집 문구는 저작권의 보호를 받을 수 있습니다. 개인 학습 목적의 링크 공유는 가능하지만, 무단 복제와 재배포는 허용하지 않습니다.</p>
      <h2>면책</h2>
      <p>외부 서비스, 제품, 정책은 시간이 지나며 변경될 수 있습니다. 본 사이트는 정보의 정확성을 높이기 위해 노력하지만 모든 결과를 보장하지 않습니다.</p>
      <p className="text-sm text-[#718287]">최종 갱신: 2026년 7월 18일</p>
    </div>
  );
}
