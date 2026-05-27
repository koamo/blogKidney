import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const PUBLIC_FILE = /\.(.*)$/;
const locales = ['ko', 'en', 'ja'];
const defaultLocale = 'ko';

/**
 * 전 세계 사용자의 브라우저 언어를 실시간 분석하여 최적의 번역 페이지로 순간 리다이렉트하는 글로벌 미들웨어입니다.
 */
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // [보완 핵심]: 정적 자산, 썸네일 이미지 및 SEO 필수 파일(sitemap/robots)은 미들웨어 적용에서 완전히 예외 통과
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/api') ||
    pathname.startsWith('/images') ||
    pathname === '/favicon.ico' ||
    pathname === '/sitemap.xml' ||
    pathname === '/robots.txt' ||
    PUBLIC_FILE.test(pathname)
  ) {
    return NextResponse.next();
  }

  // 이미 URL 세그먼트에 지원하는 언어 코드(/ko, /en, /ja)가 명시되어 있다면 미들웨어 추가 처리 생략
  const pathnameHasLocale = locales.some(
    (locale) => pathname.startsWith(`/${locale}/`) || pathname === `/${locale}`
  );

  if (pathnameHasLocale) {
    return NextResponse.next();
  }

  // 사용자의 브라우저 선호 언어 목록(Accept-Language) 추출 및 파싱
  const acceptLanguage = request.headers.get('accept-language') || '';
  let detectedLocale = defaultLocale;

  if (acceptLanguage) {
    // 브라우저 가중치 순서대로 분해 파싱 (예: en-US,en;q=0.9,ko-KR;q=0.8)
    const preferredLanguages = acceptLanguage
      .split(',')
      .map((lang) => lang.split(';')[0].trim().toLowerCase());

    for (const lang of preferredLanguages) {
      if (lang.startsWith('ko')) {
        detectedLocale = 'ko';
        break;
      }
      if (lang.startsWith('en')) {
        detectedLocale = 'en';
        break;
      }
      if (lang.startsWith('ja')) {
        detectedLocale = 'ja';
        break;
      }
    }
  }

  // 적절한 다국어 경로(/ko, /en, /ja)를 주입한 하위 동적 주소로 즉시 리다이렉트 실행
  request.nextUrl.pathname = `/${detectedLocale}${pathname}`;
  return NextResponse.redirect(request.nextUrl);
}

/**
 * 미들웨어가 스캔할 경로 범위 설정 (시스템 및 정적 자산 영역은 사전 완전 배제)
 */
export const config = {
  matcher: ['/((?!api|_next/static|_next/image|images|favicon.ico|sitemap.xml|robots.txt).*)'],
};
