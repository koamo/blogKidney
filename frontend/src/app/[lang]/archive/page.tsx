import Link from 'next/link';
import Image from 'next/image';
import type { Metadata } from 'next';
import AdSenseUnit from '@/components/AdSenseUnit';
import postsData from '@/data/posts.json';

export const metadata: Metadata = {
  title: '전체 글',
  description: 'KidneyLife에 발행된 만성 콩팥병, 투석, 신장이식 관련 글을 날짜순으로 확인합니다.',
  alternates: { canonical: '/ko/archive' },
};

interface BlogPost {
  title: string;
  date: string;
  description: string;
  tags: string[];
  thumbnail: string;
  slug: string;
  lang: string;
}

interface PageProps {
  params: Promise<{
    lang: string;
  }>;
}

export async function generateStaticParams() {
  return [
    { lang: 'ko' }
  ];
}

export default async function ArchivePage({ params }: PageProps) {
  const resolvedParams = await params;
  const lang = resolvedParams.lang || 'ko';

  const allPosts: BlogPost[] = postsData as BlogPost[];
  const posts = allPosts.filter((post) => post.lang === lang);

  const translations = {
    ko: {
      title: '모든 칼럼 보관소',
      description: 'KidneyLife의 모든 의학 전문 칼럼과 건강 가이드를 이곳에서 확인하세요.',
      back: '← 메인으로 돌아가기'
    },
    en: {
      title: 'All Columns Archive',
      description: 'Find all medical columns and health guides from KidneyLife here.',
      back: '← Back to Home'
    },
    ja: {
      title: 'すべてのコラムアーカイブ',
      description: 'KidneyLifeのすべての医学専門コラムと健康ガイドをここで確認してください。',
      back: '← ホームに戻る'
    }
  };

  const t = translations[lang as 'ko' | 'en' | 'ja'] || translations.ko;

  return (
    <div className="mx-auto max-w-6xl px-6 py-12">
      <Link
        href={`/${lang}`}
        className="inline-flex items-center gap-1.5 text-sm text-slate-400 hover:text-violet-400 transition-colors mb-8 group focus:outline-none"
      >
        <span className="inline-block transition-transform group-hover:-translate-x-1 duration-200">←</span>
        {t.back}
      </Link>

      <header className="mb-12 pb-8 border-b border-slate-800/60">
        <h1 className="text-3xl md:text-5xl font-black tracking-tight text-white mb-4 leading-tight">
          {t.title}
        </h1>
        <p className="text-slate-400 text-lg">
          {t.description}
        </p>
      </header>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 lg:gap-8">
        {posts.map((post) => (
          <Link href={`/${lang}/posts/${post.slug}`} key={`${post.slug}-${post.lang}`} className="group flex flex-col overflow-hidden rounded-2xl border border-slate-800 bg-[#070b12] hover:border-violet-500/30 transition-all duration-300">
            <div className="h-40 bg-slate-900 relative overflow-hidden">
              {post.thumbnail ? (
                <Image src={post.thumbnail} alt={post.title} fill sizes="(max-width: 768px) 100vw, 33vw" className="object-cover opacity-70 group-hover:opacity-100 transition-opacity duration-300 group-hover:scale-105" />
              ) : (
                <div className="absolute inset-0 bg-gradient-to-br from-[#0c1220] to-[#04080e] flex items-center justify-center">
                  <span className="text-3xl filter drop-shadow-md opacity-50">글</span>
                </div>
              )}
            </div>
            <div className="p-5 flex flex-col flex-grow">
              <span className="text-[10px] text-slate-500 font-bold mb-2 uppercase tracking-wider">{post.date}</span>
              <h3 className="text-lg font-bold text-slate-200 group-hover:text-violet-400 transition-colors line-clamp-2 mb-2 leading-snug">
                {post.title}
              </h3>
              <p className="text-sm text-slate-400 line-clamp-2 mb-4 flex-grow">
                {post.description}
              </p>
            </div>
          </Link>
        ))}
      </div>

      <div className="mt-16 pt-8 border-t border-slate-800">
        <AdSenseUnit slot="1000000002" format="auto" />
      </div>
    </div>
  );
}
