import Link from 'next/link';
import Image from 'next/image';
import { Metadata } from 'next';
import AdSenseUnit from '@/components/AdSenseUnit';
// Next.js 빌드 시점에 수집되어 컴파일 완료된 posts.json 로드
import postsData from '@/data/posts.json';
interface BlogPost {
  title: string;
  date: string;
  description: string;
  tags: string[];
  thumbnail: string;
  slug: string;
  lang: string;
}
// Next.js 16+ 비동기 Params 컴포넌트 프롭스 규격
interface PageProps {
  params: Promise<{
    lang: string;
  }>;
}
/**
 * 1. 빌드 타임에 지원 언어 목록(/ko, /en, /ja)의 정적 라우팅 경로를 생성하는 로직
 */
export async function generateStaticParams() {
  return [
    { lang: 'ko' }
  ];
}
/**
 * 2. [추가 개선] 네이버 및 구글 검색 가이드라인 100% 충족을 위한
 *    각 다국어(ko, en, ja)별 고유의 페이지 제목과 요약 설명 동적 메타데이터 주입 로직
 */
export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const resolvedParams = await params;
  const lang = resolvedParams.lang || 'ko';
  const translations = {
    ko: {
      title: 'KidneyLife - 만성 콩팥병과 투석 생활 정보',
      description: '만성 콩팥병, 투석, 신장이식 관련 공개 자료를 환자와 가족이 이해하기 쉬운 언어로 정리하는 건강 정보 블로그입니다.'
    },
    en: {
      title: 'KidneyLife - Chronic Kidney Disease Diet & Health Blog',
      description: 'A professional media platform providing low sodium, low potassium, low phosphorus, and low protein diet guides and accurate renal health medical information for CKD patients.'
    },
    ja: {
      title: 'KidneyLife - 慢性腎臓病の食事療法と健康管理専門ブログ',
      description: '慢性腎臓病（慢性腎不全）、糸球体腎炎の患者のための低ナトリウム/低カリウム/低リン/低タンパクの4大食事管理ガイドと正しい腎臓健康医学情報を提供するメディアプラットフォームです。'
    }
  };
  const t = translations[lang as 'ko' | 'en' | 'ja'] || translations.ko;
  return {
    title: t.title,
    description: t.description,
    alternates: { canonical: `/${lang}` },
    openGraph: {
      title: t.title,
      description: t.description,
      url: `https://kidney-life.vercel.app/${lang}`,
      siteName: 'KidneyLife',
      locale: lang === 'ko' ? 'ko_KR' : lang === 'ja' ? 'ja_JP' : 'en_US',
      type: 'website',
      images: [
        {
          url: 'https://images.unsplash.com/photo-1498837167922-ddd27525d352?auto=format&fit=crop&w=800&q=80',
          width: 800,
          height: 600,
          alt: 'KidneyLife Healthy Diet and Healing Nature',
        },
      ],
    },
  };
}
/**
 * 다국어 블로그 메인 페이지 렌더링 컴포넌트입니다.
 */
export default async function Home({ params }: PageProps) {
  const resolvedParams = await params;
  const lang = resolvedParams.lang || 'ko';
  // 1. postsData 데이터베이스에서 현재 접속된 언어 스펙에 부합하는 글만 추출
  const allPosts: BlogPost[] = postsData as BlogPost[];
  const posts = allPosts.filter((post) => post.lang === lang);
  // [프리미엄 포털 구조] 최신 1개는 Featured, 그 다음 9개는 Recent로 분리
  const featuredPost = posts[0];
  const recentPosts = posts.slice(1, 10);
  // 2. 다국어 텍스트 번역 딕셔너리 (i18n) 설정
  const translations = {
    ko: {
      badge: '신장 건강 정보 노트',
      welcome: '신장 건강 정보를 차분히 정리하는 공간,',
      description: '만성 콩팥병, 투석, 신장이식 관련 자료를 쉽게 풀어 쓰되 치료와 식사 조정은 개인 상태에 따라 다르다는 점을 함께 안내합니다.',
      latest: '최근 건강 정보',
      total: `총 ${posts.length}개 발행됨`,
      readMore: '자세히 보기',
      featured: '추천 글',
      viewAll: '모든 글 보기'
    },
    en: {
      badge: '✨ Renal Health Notes',
      welcome: 'A space that adds value to kidney health,',
      description: 'Built on top of an optimized medical channel, we catalog low sodium, low potassium, low phosphorus, and low protein diet guides and clinical renal care insights for CKD patients.',
      latest: 'Latest Medical Reports',
      total: `Total ${posts.length} articles published`,
      readMore: 'Read Article',
      featured: 'Featured Column',
      viewAll: 'View All Columns →'
    },
    ja: {
      badge: '✨ プレミアム腎臓健康アーカイブ',
      welcome: '腎臓の健康と食事の価値を高める空間、',
      description: '低ナトリウム/低カリウム/低リン/低タンパクの4大食事管理ガイドと正しい腎臓健康医学情報を深く記録し、患者とその家族に最適化されたコンテンツをお届けします。',
      latest: '最新の医学記事一覧',
      total: `合計 ${posts.length} 件の記事`,
      readMore: '詳細を見る',
      featured: '🔥 おすすめの医学コラム',
      viewAll: 'すべてのコラムを見る →'
    }
  };
  const t = translations[lang as 'ko' | 'en' | 'ja'] || translations.ko;
  return (
    <div className="mx-auto max-w-6xl px-6 py-12">
      {/* 히어로 환영 섹션 */}
      <section className="relative overflow-hidden rounded-3xl bg-[#090d16]/80 border border-slate-800/60 p-8 md:p-12 mb-16 text-center md:text-left">
        <div className="absolute top-0 right-0 w-80 h-80 bg-violet-600/10 rounded-full blur-3xl -z-10" />
        <div className="absolute bottom-0 left-0 w-60 h-60 bg-cyan-600/10 rounded-full blur-3xl -z-10" />
        <span className="inline-block rounded-full bg-violet-500/10 border border-violet-500/20 px-4 py-1 text-xs font-semibold text-violet-300 mb-4">
          {t.badge}
        </span>
        <h1 className="text-3xl md:text-5xl font-extrabold tracking-tight text-white mb-4 leading-tight">
          {t.welcome} <br className="hidden md:inline"/>
          <span className="bg-gradient-to-r from-violet-400 via-indigo-400 to-cyan-400 bg-clip-text text-transparent">
            KidneyLife
          </span>
        </h1>
        <p className="text-slate-400 max-w-2xl text-base md:text-lg leading-relaxed">
          {t.description}
        </p>
      </section>
      {/* [Featured Post] 대형 썸네일 추천 기사 (애드센스 구조 최적화) */}
      {featuredPost && (
        <div className="mb-20">
          <h2 className="text-xl font-bold tracking-tight text-violet-400 flex items-center gap-2 mb-6 font-['Outfit']">
            {t.featured}
          </h2>
          <Link href={`/${lang}/posts/${featuredPost.slug}`} className="group relative flex flex-col md:flex-row overflow-hidden rounded-3xl border border-slate-800/80 bg-[#070b12]/80 transition-all duration-300 hover:border-violet-500/40 hover:shadow-2xl hover:shadow-violet-600/10">
            {/* Featured 이미지 */}
            <div className="w-full md:w-1/2 h-64 md:h-auto bg-slate-900 relative overflow-hidden">
              {featuredPost.thumbnail ? (
                <Image src={featuredPost.thumbnail} alt={featuredPost.title} fill priority sizes="(max-width: 768px) 100vw, 50vw" className="object-cover opacity-80 group-hover:opacity-100 transition-opacity duration-500 group-hover:scale-105" />
              ) : (
                <div className="absolute inset-0 bg-gradient-to-br from-violet-900/40 to-cyan-900/20 flex items-center justify-center">
                  <span className="text-6xl filter drop-shadow-lg">✨</span>
                </div>
              )}
            </div>
            {/* Featured 내용 */}
            <div className="w-full md:w-1/2 p-8 md:p-12 flex flex-col justify-center">
              <span className="text-sm text-slate-500 font-semibold mb-3">{featuredPost.date}</span>
              <h3 className="text-3xl font-extrabold text-white group-hover:text-violet-400 transition-colors duration-200 mb-4 leading-tight">
                {featuredPost.title}
              </h3>
              <p className="text-slate-400 text-base leading-relaxed line-clamp-3 mb-6">
                {featuredPost.description}
              </p>
              <div className="flex flex-wrap gap-2 mt-auto">
                {featuredPost.tags.map((tag) => (
                  <span key={tag} className="rounded bg-violet-600/20 border border-violet-500/30 px-3 py-1 text-xs text-violet-300 font-semibold">
                    #{tag}
                  </span>
                ))}
              </div>
            </div>
          </Link>
        </div>
      )}
      {/* 최신 포스트 현황 타이틀 영역 */}
      <div className="flex items-center justify-between mb-8 pb-4 border-b border-slate-800">
        <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2 font-['Outfit']">
          {t.latest}
          <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
        </h2>
        <span className="text-xs text-slate-500 font-medium">{t.total}</span>
      </div>
      {/* 포스트 카드 반응형 3열 레이아웃 (최신 9개만 노출) */}
      <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
        {recentPosts.map((post) => (
          <article
            key={`${post.slug}-${post.lang}`}
            className="group relative flex flex-col overflow-hidden rounded-2xl border border-slate-800/60 bg-[#070b12]/60 transition-all duration-300 hover:-translate-y-1.5 hover:border-violet-500/40 hover:shadow-2xl hover:shadow-violet-600/5"
          >
            {/* 카드 상단 고화질 unsplash 기사 썸네일 이미지 실시간 연동 (시각적 WOW 효과 극대화) */}
            <div className="relative h-48 w-full overflow-hidden border-b border-slate-800/40 bg-slate-900">
              <Image src={post.thumbnail} alt={post.title} fill sizes="(max-width: 768px) 100vw, 33vw" className="object-cover opacity-80 group-hover:opacity-100 transition-all duration-500 group-hover:scale-105" />
              <div className="absolute inset-0 bg-gradient-to-t from-[#070b12] to-transparent opacity-60" />
            </div>
            {/* 카드 하단 데이터 필드 영역 */}
            <div className="flex flex-grow flex-col p-6">
              <span className="text-xs text-slate-500 font-semibold mb-2">{post.date}</span>
              <h3 className="text-xl font-bold text-slate-100 group-hover:text-violet-400 transition-colors duration-200 line-clamp-2 mb-2 font-['Outfit']">
                <Link href={`/${lang}/posts/${post.slug}`} className="focus:outline-none">
                  {post.title}
                </Link>
              </h3>
              <p className="text-slate-400 text-sm leading-relaxed line-clamp-3 mb-4">
                {post.description}
              </p>
              {/* 태그 영역 */}
              <div className="mt-auto flex flex-wrap gap-1.5">
                {post.tags.map((tag) => (
                  <span
                    key={tag}
                    className="rounded bg-slate-800/40 border border-slate-800/80 px-2.5 py-0.5 text-xs text-slate-400"
                  >
                    #{tag}
                  </span>
                ))}
              </div>
            </div>
          </article>
        ))}
      </div>
      {/* [아카이브 링크] 모든 기사 보기 버튼 */}
      <div className="mt-12 flex justify-center">
        <Link
          href={`/${lang}/archive`}
          className="inline-flex items-center justify-center px-8 py-3 text-sm font-bold text-white bg-slate-800 hover:bg-violet-600 rounded-full transition-colors duration-300 shadow-lg shadow-black/50"
        >
          {t.viewAll}
        </Link>
      </div>
      {/* 구글 애드센스 피드용 인피드 광고 슬롯 */}
      <div className="mt-24">
        <AdSenseUnit slot="1000000001" format="auto" />
      </div>
    </div>
  );
}
