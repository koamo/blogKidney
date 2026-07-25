'use client';

export default function PrintButton() {
  return (
    <button
      type="button"
      onClick={() => window.print()}
      className="no-print inline-flex min-h-11 items-center justify-center rounded bg-[#176d68] px-5 py-3 text-sm font-bold text-white hover:bg-[#105653] focus:outline-none focus:ring-2 focus:ring-[#176d68] focus:ring-offset-2"
    >
      기록 양식 인쇄
    </button>
  );
}
