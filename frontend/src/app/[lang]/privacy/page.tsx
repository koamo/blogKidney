import React from 'react';

interface PageProps {
  params: Promise<{
    lang: string;
  }>;
}

export default async function PrivacyPage({ params }: PageProps) {
  const resolvedParams = await params;
  const lang = resolvedParams.lang || 'ko';

  return (
    <div className="mx-auto max-w-4xl px-6 py-16 prose prose-invert">
      <h1 className="text-3xl md:text-5xl font-black mb-8">Privacy Policy</h1>
      <p>
        At KidneyLog, accessible from our website, one of our main priorities is the privacy of our visitors. This Privacy Policy document contains types of information that is collected and recorded by KidneyLog and how we use it.
      </p>
      
      <h2>1. Log Files</h2>
      <p>
        KidneyLog follows a standard procedure of using log files. These files log visitors when they visit websites. The information collected includes internet protocol (IP) addresses, browser type, Internet Service Provider (ISP), date and time stamp, and referring/exit pages. These are not linked to any information that is personally identifiable.
      </p>

      <h2>2. Cookies and Web Beacons</h2>
      <p>
        Like any other website, KidneyLog uses "cookies". These cookies are used to store information including visitors' preferences, and the pages on the website that the visitor accessed or visited. The information is used to optimize the users' experience by customizing our web page content based on visitors' browser type and/or other information.
      </p>

      <h2>3. Google DoubleClick DART Cookie</h2>
      <p>
        Google is one of a third-party vendor on our site. It also uses cookies, known as DART cookies, to serve ads to our site visitors based upon their visit to our site and other sites on the internet. However, visitors may choose to decline the use of DART cookies by visiting the Google ad and content network Privacy Policy at the following URL: <a href="https://policies.google.com/technologies/ads">https://policies.google.com/technologies/ads</a>
      </p>

      <h2>4. Consent</h2>
      <p>
        By using our website, you hereby consent to our Privacy Policy and agree to its Terms and Conditions.
      </p>

      <p className="text-sm text-slate-500 mt-12">
        Last updated: June 2026
      </p>
    </div>
  );
}
