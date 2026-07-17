import Image from 'next/image';
import Link from 'next/link';
import type { Metadata } from 'next';
import AdSenseUnit from '@/components/AdSenseUnit';
import postsData from '@/data/posts.json';

interface BlogPost {
  title: string;
  date: string;
  description: string;
  tags: string[];
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

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const resolvedParams = await params;
  const lang = resolvedParams.lang || 'ko';

  return {
    title: '신장 건강과 투석 생활 정보',
    description: '신장 검사, 만성 콩팥병, 투석과 이식 관련 공식 자료를 환자와 가족이 확인하기 쉬운 언어로 정리합니다.',
    alternates: { canonical: `/${lang}` },
    openGraph: {
      title: 'KidneyLife - 신장 건강과 투석 생활 정보',
      description: '공식 자료와 연구 원문을 바탕으로 신장 건강 정보를 차분하게 정리합니다.',
      url: `/${lang}`,
      siteName: 'KidneyLife',
      locale: 'ko_KR',
      type: 'website',
    },
  };
}

function contentTypeLabel(contentType?: string) {
  if (contentType === 'patient-guide') return '환자 안내';
  if (contentType === 'reviewed-research') return '연구 검토';
  if (contentType === 'reference') return '참고 자료';
  return '건강 정보';
}

export default async function Home({ params }: PageProps) {
  const resolvedParams = await params;
  const lang = resolvedParams.lang || 'ko';
  const allPosts = postsData as BlogPost[];
  const posts = allPosts.filter((post) => post.lang === lang);
  const featuredPost = posts[0];
  const recentPosts = posts.slice(1, 7);

  return (
    <div>
      <section className="border-b border-[#d8e1dd] bg-white">
        <div className="mx-auto max-w-6xl px-5 py-12 md:py-16">
          <p className="text-xs font-bold text-[#176d68]">KIDNEYLIFE EVIDENCE NOTE</p>
          <h1 className="mt-4 max-w-3xl text-3xl font-bold leading-tight text-[#17313a] md:text-5xl">
            신장 건강과 투석 생활 정보
          </h1>
          <p className="mt-5 max-w-3xl text-base leading-7 text-[#526970] md:text-lg">
            검사표를 읽고 진료 질문을 준비하는 방법부터 투석·이식 연구의 적용 범위까지, 공식 자료와 원문을 바탕으로 정리합니다.
          </p>
          <div className="mt-7 flex flex-wrap gap-4 text-sm font-semibold">
            <Link href={`/${lang}/archive`} className="rounded bg-[#176d68] px-5 py-3 text-white hover:bg-[#105653]">전체 글 보기</Link>
            <Link href={`/${lang}/editorial-policy`} className="px-1 py-3 text-[#176d68] underline underline-offset-4">자료를 검토하는 방법</Link>
          </div>
        </div>
      </section>

      <section aria-label="사이트 이용 안내" className="border-b border-[#d8e1dd] bg-[#eaf1ee]">
        <div className="mx-auto grid max-w-6xl gap-5 px-5 py-6 text-sm text-[#405b63] md:grid-cols-3">
          <p><strong className="text-[#17313a]">출처 우선</strong><br />공식 기관과 연구 원문 링크를 함께 표시합니다.</p>
          <p><strong className="text-[#17313a]">적용 범위 구분</strong><br />동물실험, 관찰자료, 임상시험을 같은 근거로 다루지 않습니다.</p>
          <p><strong className="text-[#17313a]">진료 대체 아님</strong><br />개인별 약·식사·치료는 담당 의료진과 확인해야 합니다.</p>
        </div>
      </section>

      <div className="mx-auto max-w-6xl px-5 py-12">
        {featuredPost && (
          <section aria-labelledby="featured-heading" className="mb-14">
            <div className="mb-5 flex items-end justify-between gap-4">
              <h2 id="featured-heading" className="text-xl font-bold text-[#17313a]">먼저 읽을 글</h2>
              <span className="text-xs text-[#728388]">자료 검토 {featuredPost.reviewedAt || featuredPost.date}</span>
            </div>
            <Link href={`/${lang}/posts/${featuredPost.slug}`} className="group grid overflow-hidden rounded border border-[#d5dfda] bg-white md:grid-cols-[0.9fr_1.1fr]">
              <div className="relative aspect-[16/10] bg-[#e4ece8] md:aspect-auto md:min-h-80">
                <Image src={featuredPost.thumbnail} alt={featuredPost.title} fill priority sizes="(max-width: 768px) 100vw, 45vw" className="object-cover" />
              </div>
              <div className="flex flex-col justify-center p-7 md:p-10">
                <p className="text-xs font-bold text-[#b05237]">{contentTypeLabel(featuredPost.contentType)}</p>
                <h3 className="mt-3 text-2xl font-bold leading-snug text-[#17313a] group-hover:text-[#176d68] md:text-3xl">{featuredPost.title}</h3>
                <p className="mt-4 text-sm leading-7 text-[#526970] md:text-base">{featuredPost.description}</p>
                <p className="mt-6 text-sm font-semibold text-[#176d68]">글 읽기 →</p>
              </div>
            </Link>
          </section>
        )}

        <section aria-labelledby="recent-heading">
          <div className="mb-6 flex items-center justify-between border-b border-[#d8e1dd] pb-4">
            <h2 id="recent-heading" className="text-xl font-bold text-[#17313a]">최근 발행 글</h2>
            <span className="text-xs font-medium text-[#728388]">총 {posts.length}편</span>
          </div>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {recentPosts.map((post) => (
              <article key={`${post.slug}-${post.lang}`} className="overflow-hidden rounded border border-[#d5dfda] bg-white">
                <Link href={`/${lang}/posts/${post.slug}`} className="group block">
                  <div className="relative aspect-[16/9] bg-[#e4ece8]">
                    <Image src={post.thumbnail} alt={post.title} fill sizes="(max-width: 768px) 100vw, 33vw" className="object-cover" />
                  </div>
                  <div className="p-5">
                    <div className="flex items-center justify-between gap-3 text-xs">
                      <span className="font-bold text-[#b05237]">{contentTypeLabel(post.contentType)}</span>
                      <time className="text-[#728388]">{post.date}</time>
                    </div>
                    <h3 className="mt-3 text-lg font-bold leading-7 text-[#17313a] group-hover:text-[#176d68]">{post.title}</h3>
                    <p className="mt-3 line-clamp-3 text-sm leading-6 text-[#5b7076]">{post.description}</p>
                  </div>
                </Link>
              </article>
            ))}
          </div>
          <div className="mt-9 text-center">
            <Link href={`/${lang}/archive`} className="inline-flex rounded border border-[#176d68] px-5 py-3 text-sm font-bold text-[#176d68] hover:bg-[#e8f2ef]">발행 글 전체 보기</Link>
          </div>
        </section>

        <AdSenseUnit slot="1000000001" format="auto" />
      </div>
    </div>
  );
}
