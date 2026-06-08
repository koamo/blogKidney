import type { Metadata } from 'next';
import Link from 'next/link';
import { notFound } from 'next/navigation';
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
  content: string;
}

// Next.js 16+ 비동기 Params 컴포넌트 프롭스 규격 (언어 및 슬러그 동시 인자 수집)
interface PageProps {
  params: Promise<{
    lang: string;
    slug: string;
  }>;
}

/**
 * 1. [다차원 SSG 핵심]: 지원 언어(ko/en/ja)와 각 기사의 슬러그를 복합 맵핑하여
 *    총 3 x 3 = 9개의 물리 정적 HTML 상세 페이지를 선제 컴파일하는 로직
 */
export async function generateStaticParams() {
  const posts = postsData as BlogPost[];
  return posts.map((post) => ({
    lang: post.lang,
    slug: post.slug,
  }));
}

/**
 * 2. 각 국가 크롤러에게 언어별 메타태그를 동적으로 주입하는 글로벌 SEO 최적화 로직
 */
export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const resolvedParams = await params;
  const posts = postsData as BlogPost[];
  const post = posts.find(
    (p) => p.slug === resolvedParams.slug && p.lang === resolvedParams.lang
  );
  
  if (!post) {
    return {
      title: 'Not Found',
    };
  }
  
  return {
    title: post.title,
    description: post.description,
    keywords: post.tags,
    openGraph: {
      title: post.title,
      description: post.description,
      type: 'article',
      publishedTime: post.date,
      authors: ['GoldenLog'],
      tags: post.tags,
    },
  };
}

/**
 * 다국어 블로그 상세 기사 페이지 렌더러 컴포넌트입니다.
 */
export default async function PostDetailPage({ params }: PageProps) {
  const resolvedParams = await params;
  const lang = resolvedParams.lang || 'ko';
  const slug = resolvedParams.slug;
  
  // 1차 필터링: postsData에서 현재 접속 언어(lang)와 슬러그(slug)에 완벽하게 일치하는 기사 필터링
  const posts = postsData as BlogPost[];
  const post = posts.find((p) => p.slug === slug && p.lang === lang);
  
  if (!post) {
    notFound();
  }

  // 2차 다국어 번역 보조 문구 사전 (UI 다국어화)
  const translations = {
    ko: {
      back: '← 전체 아티클 목록으로',
      by: '작성자',
    },
    en: {
      back: '← Back to all articles',
      by: 'By',
    },
    ja: {
      back: '← 記事一覧に戻る',
      by: '著者',
    }
  };

  const t = translations[lang as 'ko' | 'en' | 'ja'] || translations.ko;
  
  return (
    <article className="mx-auto max-w-4xl px-6 py-12">
      
      {/* 럭셔리 트랜지션 뒤로가기 링크 (현재 접속 언어 목록으로 안전 백) */}
      <Link 
        href={`/${lang}`}
        className="inline-flex items-center gap-1.5 text-sm text-slate-400 hover:text-violet-400 transition-colors mb-8 group focus:outline-none"
      >
        <span className="inline-block transition-transform group-hover:-translate-x-1 duration-200">←</span>
        {t.back}
      </Link>

      {/* 기사 헤더 및 메타데이터 영역 */}
      <header className="mb-8 pb-8 border-b border-slate-800/60">
        
        {/* 태그 리스트 */}
        <div className="flex flex-wrap gap-2 mb-4">
          {post.tags.map((tag) => (
            <span 
              key={tag}
              className="rounded bg-violet-600/10 border border-violet-500/20 px-2.5 py-0.5 text-xs text-violet-300 font-semibold"
            >
              #{tag}
            </span>
          ))}
        </div>
        
        {/* 아티클 대형 헤드라인 */}
        <h1 className="text-3xl md:text-5xl font-black tracking-tight text-white mb-4 leading-tight font-['Outfit']">
          {post.title}
        </h1>
        
        {/* 날짜 및 작성자 표시 */}
        <div className="flex items-center gap-3 text-slate-500 text-sm">
          <span className="font-semibold text-slate-400">{t.by} GoldenLog</span>
          <span>·</span>
          <span>{post.date}</span>
        </div>
      </header>

      {/* [시각적 가치 증대] 본문 최상단에 썸네일 고화질 렌더링 (구글 애드센스 심사 통과 핵심 기법) */}
      {post.thumbnail && (
        <div className="w-full mb-10 overflow-hidden rounded-xl bg-slate-900 border border-slate-800">
          <img 
            src={post.thumbnail} 
            alt={post.title} 
            className="w-full h-[400px] object-cover opacity-90 hover:opacity-100 transition-opacity"
            loading="eager"
          />
        </div>
      )}

      {/* [수익화 장치 1] 기사 본문 상단 애드센스 배너 영역 */}
      <AdSenseUnit slot="2000000001" format="auto" />

      {/* [본문 렌더링] 마크다운 번역 HTML 및 수려한 타이포그래피 이식 */}
      <section 
        className="prose max-w-none my-12"
        dangerouslySetInnerHTML={{ __html: post.content }}
      />

      {/* [수익화 장치 2] 기사 본문 하단 애드센스 배너 영역 */}
      <AdSenseUnit slot="2000000002" format="auto" />
      
    </article>
  );
}
