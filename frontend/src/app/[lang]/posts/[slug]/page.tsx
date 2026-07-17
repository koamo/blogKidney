import type { Metadata } from 'next';
import Image from 'next/image';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import AdSenseUnit from '@/components/AdSenseUnit';
import AuthorBio from '@/components/AuthorBio';
import MedicalDisclaimer from '@/components/MedicalDisclaimer';
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
  contentType?: string;
  editorialValue?: string;
  sourceName?: string;
  sourceTitle?: string;
  sourceUrl?: string;
  sourcePublishedAt?: string;
  primarySourceName?: string;
  primarySourceTitle?: string;
  primarySourceUrl?: string;
  reviewedBy?: string;
  reviewedAt?: string;
}

interface PageProps {
  params: Promise<{ lang: string; slug: string }>;
}

export async function generateStaticParams() {
  const posts = postsData as BlogPost[];
  return posts.map((post) => ({ lang: post.lang, slug: post.slug }));
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const resolvedParams = await params;
  const posts = postsData as BlogPost[];
  const post = posts.find((item) => item.slug === resolvedParams.slug && item.lang === resolvedParams.lang);

  if (!post) return { title: '글을 찾을 수 없습니다' };

  const canonicalPath = `/${resolvedParams.lang}/posts/${post.slug}`;
  return {
    title: post.title,
    description: post.description,
    alternates: { canonical: canonicalPath },
    keywords: post.tags,
    authors: [{ name: 'KidneyLife 자료 편집부' }],
    openGraph: {
      title: post.title,
      description: post.description,
      url: canonicalPath,
      type: 'article',
      publishedTime: post.date,
      modifiedTime: post.reviewedAt || post.date,
      authors: ['KidneyLife 자료 편집부'],
      tags: post.tags,
      images: post.thumbnail ? [{ url: post.thumbnail, alt: post.title }] : undefined,
    },
  };
}

function contentTypeLabel(contentType?: string) {
  if (contentType === 'patient-guide') return '환자 안내';
  if (contentType === 'reviewed-research') return '연구 검토';
  if (contentType === 'reference') return '참고 자료';
  return '건강 정보';
}

export default async function PostDetailPage({ params }: PageProps) {
  const resolvedParams = await params;
  const lang = resolvedParams.lang || 'ko';
  const posts = postsData as BlogPost[];
  const post = posts.find((item) => item.slug === resolvedParams.slug && item.lang === lang);
  if (!post) notFound();

  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://kidney-life.vercel.app';
  const articleUrl = new URL(`/${lang}/posts/${post.slug}`, baseUrl).toString();
  const citations = [post.primarySourceUrl, post.sourceUrl].filter(Boolean);
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'BlogPosting',
    headline: post.title,
    description: post.description,
    datePublished: post.date,
    dateModified: post.reviewedAt || post.date,
    inLanguage: 'ko-KR',
    mainEntityOfPage: articleUrl,
    image: post.thumbnail || undefined,
    author: { '@type': 'Organization', name: 'KidneyLife 자료 편집부' },
    publisher: { '@type': 'Organization', name: 'KidneyLife' },
    citation: citations.length ? citations : undefined,
  };

  return (
    <article className="mx-auto max-w-3xl px-5 py-10 md:py-14">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, '\\u003c') }} />
      <Link href={`/${lang}/archive`} className="text-sm font-semibold text-[#176d68] underline underline-offset-4">← 전체 글</Link>

      <header className="mt-8 border-b border-[#d8e1dd] pb-8">
        <p className="text-xs font-bold text-[#b05237]">{contentTypeLabel(post.contentType)}</p>
        <h1 className="mt-4 text-3xl font-bold leading-tight text-[#17313a] md:text-4xl">{post.title}</h1>
        <p className="mt-5 text-base leading-7 text-[#5b7076]">{post.description}</p>
        <dl className="mt-6 grid gap-2 text-sm text-[#66797e] sm:grid-cols-2">
          <div><dt className="inline font-semibold text-[#304b53]">발행 </dt><dd className="inline">{post.date}</dd></div>
          <div><dt className="inline font-semibold text-[#304b53]">자료 검토 </dt><dd className="inline">{post.reviewedAt || post.date}</dd></div>
          <div><dt className="inline font-semibold text-[#304b53]">작성 </dt><dd className="inline">KidneyLife 자료 편집부</dd></div>
          <div><dt className="inline font-semibold text-[#304b53]">검토 </dt><dd className="inline">{post.reviewedBy || 'KidneyLife 자료 편집부'} · 자료 및 출처</dd></div>
        </dl>
      </header>

      {post.editorialValue && (
        <aside className="mt-7 rounded border border-[#cbded8] bg-[#eaf3f0] p-5">
          <h2 className="text-sm font-bold text-[#174f4d]">이 글에서 보완한 점</h2>
          <p className="mt-2 text-sm leading-6 text-[#42615f]">{post.editorialValue}</p>
        </aside>
      )}

      {post.thumbnail && (
        <div className="relative mt-8 aspect-[16/9] overflow-hidden rounded border border-[#d5dfda] bg-[#e4ece8]">
          <Image src={post.thumbnail} alt={post.title} fill priority sizes="(max-width: 768px) 100vw, 768px" className="object-cover" />
        </div>
      )}

      <div className="mt-9"><MedicalDisclaimer lang={lang} /></div>

      <section className="prose max-w-none" dangerouslySetInnerHTML={{ __html: post.content }} />

      {(post.primarySourceUrl || post.sourceUrl) && (
        <section aria-labelledby="source-details" className="mt-12 rounded border border-[#d5dfda] bg-white p-5">
          <h2 id="source-details" className="text-base font-bold text-[#17313a]">출처 메타정보</h2>
          <ul className="mt-3 space-y-3 text-sm leading-6 text-[#526970]">
            {post.primarySourceUrl && (
              <li><strong className="text-[#304b53]">1차 자료:</strong> <a href={post.primarySourceUrl} target="_blank" rel="noreferrer" className="font-semibold text-[#176d68] underline underline-offset-4">{post.primarySourceTitle || post.primarySourceName || '원문 확인'}</a></li>
            )}
            {post.sourceUrl && (
              <li><strong className="text-[#304b53]">정리 기준 자료:</strong> <a href={post.sourceUrl} target="_blank" rel="noreferrer" className="font-semibold text-[#176d68] underline underline-offset-4">{post.sourceTitle || post.sourceName || '자료 확인'}</a></li>
            )}
          </ul>
        </section>
      )}

      <AuthorBio lang={lang} />
      <AdSenseUnit slot="2000000002" format="auto" />
    </article>
  );
}
