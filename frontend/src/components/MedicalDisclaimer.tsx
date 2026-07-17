export default function MedicalDisclaimer({ lang = 'ko' }: { lang?: string }) {
  return (
    <aside data-lang={lang} aria-label="의료 정보 이용 안내" className="mb-10 rounded border border-[#d9c99a] bg-[#fffaf0] p-5">
      <h2 className="text-sm font-bold text-[#59491f]">의료 정보 이용 안내</h2>
      <p className="mt-2 text-sm leading-6 text-[#665b3e]">
        이 글은 일반적인 정보 제공을 위한 자료이며 개인의 진단이나 치료를 대신하지 않습니다. 약, 식사, 투석과 검사 일정은 담당 의료진과 상의해 결정하세요. 갑작스럽거나 심한 증상이 있으면 온라인 글보다 의료기관의 안내를 우선하세요.
      </p>
    </aside>
  );
}
