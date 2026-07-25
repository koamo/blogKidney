import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const PUBLIC_FILE = /\.(.*)$/;
const locales = ['ko'];
const defaultLocale = 'ko';

/**
 * 사용자 요청을 한국어(/ko) 경로로 라우팅하고, 기존 다국어 URL 트래픽을 안전하게 리다이렉트하는 SEO 보존형 미들웨어입니다.
 */
export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // [보완 핵심]: 정적 자산, 썸네일 이미지 및 SEO 필수 파일(sitemap/robots)은 미들웨어 적용에서 완전히 예외 통과
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/api') ||
    pathname.startsWith('/images') ||
    pathname === '/favicon.ico' ||
    pathname === '/sitemap.xml' ||
    pathname === '/robots.txt' ||
    pathname === '/ads.txt' ||
    PUBLIC_FILE.test(pathname)
  ) {
    return NextResponse.next();
  }

  // [SEO 보완]: 기존 다국어 주소(/en, /ja) 접근 시 자동으로 한국어(/ko) 경로로 리다이렉션하여 404 및 SEO 지수 하락 방지
  const unsupportedLocales = ['en', 'ja'];
  for (const locale of unsupportedLocales) {
    if (pathname.startsWith(`/${locale}/`)) {
      request.nextUrl.pathname = pathname.replace(`/${locale}/`, '/ko/');
      return NextResponse.redirect(request.nextUrl);
    } else if (pathname === `/${locale}`) {
      request.nextUrl.pathname = '/ko';
      return NextResponse.redirect(request.nextUrl);
    }
  }

  // 이미 URL 세그먼트에 지원하는 언어 코드(/ko)가 명시되어 있다면 미들웨어 추가 처리 생략
  const pathnameHasLocale = locales.some(
    (locale) => pathname.startsWith(`/${locale}/`) || pathname === `/${locale}`
  );

  if (pathnameHasLocale) {
    return NextResponse.next();
  }

  // 기본적으로 한국어(/ko) 경로로 리다이렉트 실행
  request.nextUrl.pathname = `/${defaultLocale}${pathname}`;
  return NextResponse.redirect(request.nextUrl);
}

/**
 * 미들웨어가 스캔할 경로 범위 설정 (시스템 및 정적 자산 영역은 사전 완전 배제)
 */
export const config = {
  matcher: ['/((?!api|_next/static|_next/image|images|favicon.ico|sitemap.xml|robots.txt|ads.txt).*)'],
};
