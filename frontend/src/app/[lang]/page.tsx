import Link from 'next/link';
import AdSenseUnit from '@/components/AdSenseUnit';
// Next.js 내부 데이터 저장소에 파이썬이 다국어 번역 적재해 놓은 posts.json 로드
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
 * 1. 빌드 타임에 지원 언어 목록(/ko, /en, /ja)을 정적 라우트 주소로 선제 생성하는 로직
 */
export async function generateStaticParams() {
  return [
    { lang: 'ko' },
    { lang: 'en' },
    { lang: 'ja' }
  ];
}

/**
 * 다국어 블로그 홈 페이지 렌더러 컴포넌트입니다.
 */
export default async function Home({ params }: PageProps) {
  const resolvedParams = await params;
  const lang = resolvedParams.lang || 'ko';
  
  // 1차 필터링: postsData 데이터베이스에서 현재 라우트 언어 스펙에 부합하는 글만 추출
  const allPosts: BlogPost[] = postsData as BlogPost[];
  const posts = allPosts.filter((post) => post.lang === lang);

  // 2차 다국어 번역 딕셔너리 (i18n) 설정 - 레이아웃 핵심 텍스트 자동 대응
  const translations = {
    ko: {
      badge: '✨ 프리미엄 지식 아카이브',
      welcome: '지식의 가치를 더하는 공간,',
      description: '수익형 구글 애드센스 심사를 한 번에 통과하기 위한 최적의 기술 세팅 위에, 엄선된 IT 실무 기술 지식과 스마트한 시간 관리 팁, 그리고 자기계발 노하우를 깊이 있게 기록합니다.',
      latest: '최신 발행 아티클',
      total: `총 ${posts.length}개 발행됨`,
      readMore: '자세히 보기',
    },
    en: {
      badge: '✨ Premium Knowledge Archive',
      welcome: 'A space that adds value to knowledge,',
      description: 'Built on top of an optimized technical configuration engineered to pass the profitable Google AdSense audit at once, we catalog in-depth IT engineering insights, smart time management methodologies, and practical self-improvement philosophies.',
      latest: 'Latest Publications',
      total: `Total ${posts.length} articles published`,
      readMore: 'Read Article',
    },
    ja: {
      badge: '✨ プレミアム知識アーカイブ',
      welcome: '知識の価値を高める空間、',
      description: '収益型Googleアドセンス審査を一発で通過するための最適な技術設定の上に、厳選されたIT実務技術知識とスマートな時間管理のコツ、そして自己開発のノウハウを深く記録します。',
      latest: '最新の発行記事',
      total: `合計 ${posts.length} 個の記事`,
      readMore: '詳細を見る',
    }
  };

  const t = translations[lang as 'ko' | 'en' | 'ja'] || translations.ko;

  return (
    <div className="mx-auto max-w-6xl px-6 py-12">
      
      {/* 럭셔리 네온 아우라 히어로 섹션 */}
      <section className="relative overflow-hidden rounded-3xl bg-[#090d16]/80 border border-slate-800/60 p-8 md:p-12 mb-16 text-center md:text-left">
        <div className="absolute top-0 right-0 w-80 h-80 bg-violet-600/10 rounded-full blur-3xl -z-10" />
        <div className="absolute bottom-0 left-0 w-60 h-60 bg-cyan-600/10 rounded-full blur-3xl -z-10" />
        
        <span className="inline-block rounded-full bg-violet-500/10 border border-violet-500/20 px-4 py-1 text-xs font-semibold text-violet-300 mb-4">
          {t.badge}
        </span>
        
        <h1 className="text-3xl md:text-5xl font-extrabold tracking-tight text-white mb-4 leading-tight">
          {t.welcome} <br className="hidden md:inline"/>
          <span className="bg-gradient-to-r from-violet-400 via-indigo-400 to-cyan-400 bg-clip-text text-transparent">
            GoldenLog
          </span>
        </h1>
        
        <p className="text-slate-400 max-w-2xl text-base md:text-lg leading-relaxed">
          {t.description}
        </p>
      </section>

      {/* 타이틀 및 발행 현황 영역 */}
      <div className="flex items-center justify-between mb-8">
        <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2 font-['Outfit']">
          {t.latest}
          <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
        </h2>
        <span className="text-xs text-slate-500 font-medium">{t.total}</span>
      </div>

      {/* 포스팅 카드 그리드 레이아웃 (반응형 3열 구성) */}
      <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
        {posts.map((post) => (
          <article 
            key={`${post.slug}-${post.lang}`}
            className="group relative flex flex-col overflow-hidden rounded-2xl border border-slate-800/60 bg-[#070b12]/60 transition-all duration-300 hover:-translate-y-1.5 hover:border-violet-500/40 hover:shadow-2xl hover:shadow-violet-600/5"
          >
            {/* 카드 상단 썸네일 장식 영역 */}
            <div className="relative h-48 w-full bg-gradient-to-br from-[#0c1220] via-[#080d16] to-[#04080e] flex items-center justify-center p-6 border-b border-slate-800/40">
              <div className="absolute top-0 right-0 w-24 h-24 bg-violet-500/5 rounded-full blur-xl transition-all group-hover:bg-violet-500/15" />
              <span className="text-4xl text-violet-400 group-hover:scale-110 transition-transform duration-300 filter drop-shadow-[0_4px_6px_rgba(139,92,246,0.2)]">
                📝
              </span>
            </div>

            {/* 카드 하단 텍스트 상세 영역 */}
            <div className="flex flex-grow flex-col p-6">
              <span className="text-xs text-slate-500 font-semibold mb-2">{post.date}</span>
              
              <h3 className="text-xl font-bold text-slate-100 group-hover:text-violet-400 transition-colors duration-200 line-clamp-2 mb-2">
                {/* 다국어 URL 구조에 맞추어 /[lang]/posts/[slug] 로 링크 전환 */}
                <Link href={`/${lang}/posts/${post.slug}`} className="focus:outline-none">
                  {post.title}
                </Link>
              </h3>
              
              <p className="text-slate-400 text-sm leading-relaxed line-clamp-3 mb-4">
                {post.description}
              </p>

              {/* 개별 태그 목록 */}
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

      {/* 사이트 메인 홈 하단 디스플레이 광고 슬롯 */}
      <div className="mt-24">
        <AdSenseUnit slot="1000000001" format="auto" />
      </div>
    </div>
  );
}
