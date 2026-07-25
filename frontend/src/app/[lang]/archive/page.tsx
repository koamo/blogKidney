import Image from 'next/image';
import Link from 'next/link';
import type { Metadata } from 'next';
import postsData from '@/data/posts.json';

export const metadata: Metadata = {
  title: '전체 글',
  description: 'KidneyLife에 발행된 신장 검사, 만성 콩팥병, 투석과 이식 관련 글을 날짜순으로 확인합니다.',
  alternates: { canonical: '/ko/archive' },
};

interface BlogPost {
  title: string;
  date: string;
  description: string;
  thumbnail: string;
  slug: string;
  lang: string;
  contentType?: string;
  reviewedAt?: string;
}

interface PageProps {
  params: Promise<{ lang: string }>;
}

export async function generateStaticParams() {
  return [{ lang: 'ko' }];
}

function contentTypeLabel(contentType?: string) {
  if (contentType === 'patient-guide') return '환자 안내';
  if (contentType === 'reviewed-research') return '연구 검토';
  if (contentType === 'reference') return '참고 자료';
  return '건강 정보';
}

export default async function ArchivePage({ params }: PageProps) {
  const resolvedParams = await params;
  const lang = resolvedParams.lang || 'ko';
  const allPosts = postsData as BlogPost[];
  const posts = allPosts.filter((post) => post.lang === lang);

  return (
    <div className="mx-auto max-w-6xl px-5 py-12 md:py-16">
      <Link href={`/${lang}`} className="text-sm font-semibold text-[#176d68] underline underline-offset-4">← 홈으로</Link>
      <header className="mt-8 border-b border-[#d8e1dd] pb-8">
        <h1 className="text-3xl font-bold text-[#17313a] md:text-4xl">전체 글</h1>
        <p className="mt-4 max-w-2xl text-base leading-7 text-[#5b7076]">검사 기록, 진료 준비, 약·식사, 투석과 이식 관련 환자 안내를 발행일 순서로 확인할 수 있습니다. 모든 글에는 참고 자료, 작성 과정과 자료 검토일을 표시합니다.</p>
      </header>

      <div className="mt-9 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {posts.map((post) => (
          <article key={`${post.slug}-${post.lang}`} className="overflow-hidden rounded border border-[#d5dfda] bg-white">
            <Link href={`/${lang}/posts/${post.slug}`} className="group block h-full">
              <div className="relative aspect-[16/9] bg-[#e4ece8]">
                <Image src={post.thumbnail} alt={post.title} fill sizes="(max-width: 768px) 100vw, 33vw" className="object-cover" />
              </div>
              <div className="p-5">
                <div className="flex items-center justify-between gap-3 text-xs">
                  <span className="font-bold text-[#b05237]">{contentTypeLabel(post.contentType)}</span>
                  <time className="text-[#728388]">{post.date}</time>
                </div>
                <h2 className="mt-3 text-lg font-bold leading-7 text-[#17313a] group-hover:text-[#176d68]">{post.title}</h2>
                <p className="mt-3 line-clamp-3 text-sm leading-6 text-[#5b7076]">{post.description}</p>
                <p className="mt-4 text-xs text-[#728388]">자료 검토 {post.reviewedAt || post.date}</p>
              </div>
            </Link>
          </article>
        ))}
      </div>
    </div>
  );
}
