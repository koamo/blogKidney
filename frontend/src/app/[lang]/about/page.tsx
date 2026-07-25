import type { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: '소개',
  description: 'KidneyLife의 운영 주체, 콘텐츠 범위, 자료 검토 방식과 의료 정보의 한계를 안내합니다.',
  alternates: { canonical: '/ko/about' },
};

interface PageProps {
  params: Promise<{ lang: string }>;
}

export default async function AboutPage({ params }: PageProps) {
  const { lang = 'ko' } = await params;
  const contactEmail = process.env.NEXT_PUBLIC_CONTACT_EMAIL || 'admin@goldenlog.tech';

  return (
    <div className="prose mx-auto max-w-3xl px-5 py-12 md:py-16">
      <h1>KidneyLife 소개</h1>
      <p>KidneyLife는 의료인이 아닌 개인 운영자가 관리하는 신장 건강 정보 블로그입니다. 신장 검사, 만성 콩팥병, 투석과 이식에 관한 공개 자료를 환자와 가족이 진료 전에 확인하기 쉬운 언어로 재구성합니다.</p>

      <h2>무엇을 제공하나요</h2>
      <p>공식 기관의 환자 안내와 연구 원문을 우선해 검사표를 읽는 방법, 진료 전에 준비할 질문, 새로운 연구의 적용 범위를 설명합니다. 단순 번역이나 RSS 요약에 머물지 않도록 독자가 실제로 확인할 항목과 자료의 한계를 함께 적습니다.</p>

      <h2>의료진 감수와 자료 검토는 다릅니다</h2>
      <p>사이트에 표시된 “출처 및 표현 점검”은 운영자가 원문 링크, 수치, 연구 단계와 과장 표현을 확인했다는 뜻입니다. 의사나 임상영양사의 전문적인 의학 감수를 뜻하지 않습니다. 향후 의료인의 감수가 이뤄진 글은 감수자, 자격과 검토 범위를 해당 글에 별도로 표시합니다.</p>

      <h2>AI 도구를 어떻게 사용하나요</h2>
      <p>일부 글은 자료 후보를 정리하거나 초안 구조를 잡을 때 AI 도구의 도움을 받습니다. 공개 전에는 운영자가 공식 원문을 다시 열어 출처와 수치를 대조하고, 문장과 구성을 직접 고칩니다. 각 글 상단의 “작성 과정”에서 AI 보조 여부와 사람의 검토 범위를 확인할 수 있습니다. 자동 수집한 RSS 요약은 공개 글로 바로 전환하지 않습니다.</p>

      <h2>운영 및 문의</h2>
      <ul>
        <li>작성·운영 주체: KidneyLife 개인 운영자(의료인 아님)</li>
        <li>운영 언어: 한국어</li>
        <li>콘텐츠 문의·정정 요청: <a href={`mailto:${contactEmail}`}>{contactEmail}</a></li>
      </ul>
      <p>정정 요청에는 해당 글 주소, 문제가 된 문장과 확인 가능한 근거를 함께 보내 주세요. 검토 결과에 따라 본문과 자료 검토일을 갱신합니다.</p>

      <p><Link href={`/${lang}/editorial-policy`}>편집·정정 원칙 자세히 보기</Link></p>
      <p className="text-sm text-[#718287]">최종 갱신: 2026년 7월 25일</p>
    </div>
  );
}
