import type { Metadata } from 'next';
import Link from 'next/link';
import PrintButton from '@/components/PrintButton';

export const metadata: Metadata = {
  title: '신장 진료 기록 양식',
  description: '검사 추세, 복용 약, 증상 변화와 진료 질문을 한곳에 기록해 의료진과 확인할 수 있는 인쇄용 양식입니다.',
  alternates: { canonical: '/ko/resources' },
};

interface PageProps {
  params: Promise<{ lang: string }>;
}

const blankRows = Array.from({ length: 5 }, (_, index) => index);

export default async function ResourcesPage({ params }: PageProps) {
  const { lang = 'ko' } = await params;

  return (
    <div className="mx-auto max-w-5xl px-5 py-10 md:py-14">
      <header className="no-print border-b border-[#d8e1dd] pb-8">
        <p className="text-xs font-bold text-[#176d68]">KIDNEYLIFE RECORD SHEETS</p>
        <h1 className="mt-4 text-3xl font-bold leading-tight text-[#17313a] md:text-4xl">신장 진료 기록 양식</h1>
        <p className="mt-4 max-w-3xl text-base leading-7 text-[#526970]">
          기억에 의존하기 어려운 검사 결과, 복용 약, 증상 변화와 진료 질문을 날짜별로 적는 빈 양식입니다.
          기록 자체가 진단을 대신하지 않으며, 목표 수치와 치료 결정은 담당 의료진과 확인해야 합니다.
        </p>
        <div className="mt-6 flex flex-wrap items-center gap-4">
          <PrintButton />
          <Link href={`/${lang}/archive`} className="text-sm font-semibold text-[#176d68] underline underline-offset-4">관련 안내 글 보기</Link>
        </div>
      </header>

      <nav aria-label="양식 바로가기" className="no-print my-8 flex flex-wrap gap-x-5 gap-y-3 text-sm font-semibold text-[#176d68]">
        <a href="#test-trend">검사 추세표</a>
        <a href="#medicine-list">약 목록</a>
        <a href="#appointment-questions">진료 질문지</a>
        <a href="#symptom-log">증상·체중 기록</a>
        <a href="#dialysis-comparison">투석 상담표</a>
      </nav>

      <div className="space-y-10 print:space-y-0">
        <section id="test-trend" className="print-sheet rounded border border-[#ccd9d4] bg-white p-5 md:p-7">
          <h2 className="text-xl font-bold text-[#17313a]">검사 결과 추세표</h2>
          <p className="mt-2 text-sm leading-6 text-[#5b7076]">같은 검사의 이전 값과 검사 당시 상황을 함께 기록합니다. 검사실마다 단위와 기준 범위가 다를 수 있으므로 결과지의 단위도 적어 두세요.</p>
          <div className="mt-5 overflow-x-auto">
            <table className="record-table min-w-[760px]">
              <thead><tr><th>검사일</th><th>크레아티닌</th><th>eGFR</th><th>UACR 또는 단백뇨</th><th>혈압</th><th>당시 변화·메모</th></tr></thead>
              <tbody>{blankRows.map((row) => <tr key={row}><td /><td /><td /><td /><td /><td /></tr>)}</tbody>
            </table>
          </div>
          <p className="mt-4 text-sm"><strong>다음 진료에서 물을 것:</strong> ____________________________________________________________________</p>
        </section>

        <section id="medicine-list" className="print-sheet rounded border border-[#ccd9d4] bg-white p-5 md:p-7">
          <h2 className="text-xl font-bold text-[#17313a]">복용 약·영양제 목록</h2>
          <p className="mt-2 text-sm leading-6 text-[#5b7076]">처방약뿐 아니라 진통제, 감기약, 한약과 건강기능식품도 포함합니다. 임의로 중단하지 말고 변경이 필요한지 의료진이나 약사에게 확인하세요.</p>
          <div className="mt-5 overflow-x-auto">
            <table className="record-table min-w-[760px]">
              <thead><tr><th>제품명·성분명</th><th>용량</th><th>횟수·시간</th><th>복용 목적</th><th>처방·구매처</th><th>확인할 점</th></tr></thead>
              <tbody>{blankRows.map((row) => <tr key={row}><td /><td /><td /><td /><td /><td /></tr>)}</tbody>
            </table>
          </div>
          <p className="mt-4 text-sm"><strong>알레르기·이상반응 경험:</strong> _________________________________________________________________</p>
        </section>

        <section id="appointment-questions" className="print-sheet rounded border border-[#ccd9d4] bg-white p-5 md:p-7">
          <h2 className="text-xl font-bold text-[#17313a]">진료 전 한 장 질문지</h2>
          <div className="mt-5 grid gap-5 md:grid-cols-2">
            <div className="record-box"><h3>지난 진료 뒤 달라진 점</h3><p>증상·식사·수면·활동:</p><div className="write-lines" /></div>
            <div className="record-box"><h3>가장 먼저 물을 질문 3개</h3><ol><li>________________________________</li><li>________________________________</li><li>________________________________</li></ol></div>
            <div className="record-box"><h3>검사와 치료 확인</h3><p>변한 검사값과 의미:</p><div className="write-lines" /></div>
            <div className="record-box"><h3>진료 후 기록</h3><p>다음 검사·예약·약 변경:</p><div className="write-lines" /></div>
          </div>
        </section>

        <section id="symptom-log" className="print-sheet rounded border border-[#ccd9d4] bg-white p-5 md:p-7">
          <h2 className="text-xl font-bold text-[#17313a]">증상·체중·혈압 기록표</h2>
          <p className="mt-2 text-sm leading-6 text-[#5b7076]">담당 의료진이 권한 항목과 시간대만 기록합니다. 수치 하나로 약이나 수분 섭취를 바꾸지 마세요.</p>
          <div className="mt-5 overflow-x-auto">
            <table className="record-table min-w-[760px]">
              <thead><tr><th>날짜·시간</th><th>체중</th><th>혈압·맥박</th><th>부종 위치·정도</th><th>숨참·피로 등</th><th>특이사항</th></tr></thead>
              <tbody>{blankRows.map((row) => <tr key={row}><td /><td /><td /><td /><td /><td /></tr>)}</tbody>
            </table>
          </div>
          <p className="mt-4 text-sm"><strong>병원에서 알려 준 연락 기준:</strong> ______________________________________________________________</p>
        </section>

        <section id="dialysis-comparison" className="print-sheet rounded border border-[#ccd9d4] bg-white p-5 md:p-7">
          <h2 className="text-xl font-bold text-[#17313a]">투석 방법 상담 기록표</h2>
          <p className="mt-2 text-sm leading-6 text-[#5b7076]">개인에게 가능한 치료인지 먼저 확인한 뒤, 이동·근무·가정 지원 같은 생활 조건을 함께 적습니다.</p>
          <div className="mt-5 overflow-x-auto">
            <table className="record-table min-w-[720px]">
              <thead><tr><th>확인 항목</th><th>혈액투석 메모</th><th>복막투석 메모</th><th>추가 질문</th></tr></thead>
              <tbody>
                {['의학적으로 가능한가', '시술·접근로 준비', '장소와 시간', '집에서 필요한 공간·지원', '교육과 비상 연락', '비용·이동·근무 조정'].map((label) => (
                  <tr key={label}><th>{label}</th><td /><td /><td /></tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>

      <aside className="no-print mt-10 rounded border border-[#d7dfdc] bg-[#eaf1ee] p-5 text-sm leading-6 text-[#405b63]">
        이 양식에는 주민등록번호나 불필요한 개인정보를 적지 마세요. 응급 증상이나 갑작스러운 악화가 의심되면 기록표를 채우는 것보다 의료기관의 안내를 먼저 따르세요.
      </aside>
    </div>
  );
}
