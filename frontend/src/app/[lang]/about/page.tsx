interface PageProps {
  params: Promise<{ lang: string }>;
}

export default async function AboutPage({ params }: PageProps) {
  await params;

  return (
    <div className="mx-auto max-w-3xl px-6 py-16 prose prose-invert">
      <h1>KidneyLife 소개</h1>
      <p>KidneyLife는 신장 건강과 만성 콩팥병 생활 관리 정보를 쉽게 풀어 쓰는 건강 정보 블로그입니다.</p>
      <p>글을 작성할 때는 공개된 자료와 제품 문서를 바탕으로 핵심 내용을 정리하고, 확인되지 않은 수치나 개인 경험은 사실처럼 쓰지 않는 것을 원칙으로 합니다.</p>
      <h2>운영 정보</h2>
      <ul>
        <li>사이트: https://kidney-life.vercel.app</li>
        <li>문의: contact@kidney-life.vercel.app</li>
        <li>운영 위치: Seoul, South Korea</li>
      </ul>
      <p className="text-sm text-slate-500">Last updated: July 2026</p>
    </div>
  );
}
