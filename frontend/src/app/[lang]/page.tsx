import Link from 'next/link';
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
    { lang: 'ko' },
    { lang: 'en' },
    { lang: 'ja' }
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
      title: 'KidneyLife - 만성 콩팥병 식이요법 및 건강관리 전문 블로그',
      description: '만성 콩팥병(만성 신부전), 사구체신염 환우를 위한 저나트륨/저칼륨/저인/저단백 4대 식단 조절 가이드와 올바른 신장 건강 의학 정보를 제공하는 미디어 플랫폼입니다.'
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

  // 2. 다국어 텍스트 번역 딕셔너리 (i18n) 설정
  const translations = {
    ko: {
      badge: '✨ 프리미엄 신장 아카이브',
      welcome: '신장 건강의 가치를 전하는 공간,',
      description: '구글 애드센스 승인을 통과한 최적의 의학 채널로, 저나트륨/저칼륨/저인/저단백 4대 영양 조절 식이 원칙과 만성 콩팥병 홈케어 관리 요령을 전문적이고 깊이 있게 전해 드립니다.',
      latest: '최신 의학 컬럼 리포트',
      total: `총 ${posts.length}개 발행됨`,
      readMore: '자세히 보기',
    },
    en: {
      badge: '✨ Premium Renal Health Archive',
      welcome: 'A space that adds value to kidney health,',
      description: 'Built on top of an optimized medical channel, we catalog low sodium, low potassium, low phosphorus, and low protein diet guides and clinical renal care insights for CKD patients.',
      latest: 'Latest Medical Reports',
      total: `Total ${posts.length} articles published`,
      readMore: 'Read Article',
    },
    ja: {
      badge: '✨ プレミアム腎臓健康アーカイブ',
      welcome: '腎臓の健康と食事の価値を高める空間、',
      description: '低ナトリウム/低カリウム/低リン/低タンパクの4大食事管理ガイドと正しい腎臓健康医学情報を深く記録し、患者とその家族に最適化されたコンテンツをお届けします。',
      latest: '最新の医学記事一覧',
      total: `合計 ${posts.length} 件の記事`,
      readMore: '詳細を見る',
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

      {/* 최신 포스트 현황 타이틀 영역 */}
      <div className="flex items-center justify-between mb-8">
        <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2 font-['Outfit']">
          {t.latest}
          <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
        </h2>
        <span className="text-xs text-slate-500 font-medium">{t.total}</span>
      </div>

      {/* 포스트 카드 반응형 3열 레이아웃 */}
      <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
        {posts.map((post) => (
          <article 
            key={`${post.slug}-${post.lang}`}
            className="group relative flex flex-col overflow-hidden rounded-2xl border border-slate-800/60 bg-[#070b12]/60 transition-all duration-300 hover:-translate-y-1.5 hover:border-violet-500/40 hover:shadow-2xl hover:shadow-violet-600/5"
          >
            {/* 카드 상단 고화질 unsplash 기사 썸네일 이미지 실시간 연동 (시각적 WOW 효과 극대화) */}
            <div className="relative h-48 w-full overflow-hidden border-b border-slate-800/40 bg-slate-900">
              <img 
                src={post.thumbnail} 
                alt={post.title}
                className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                loading="lazy"
              />
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

      {/* 구글 애드센스 피드용 인피드 광고 슬롯 */}
      <div className="mt-24">
        <AdSenseUnit slot="1000000001" format="auto" />
      </div>
    </div>
  );
}
