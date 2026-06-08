import React from 'react';

interface PageProps {
  params: Promise<{
    lang: string;
  }>;
}

export default async function TermsPage({ params }: PageProps) {
  const resolvedParams = await params;
  const lang = resolvedParams.lang || 'ko';

  return (
    <div className="mx-auto max-w-4xl px-6 py-16 prose prose-invert">
      <h1 className="text-3xl md:text-5xl font-black mb-8">Terms of Service</h1>
      <p>
        Welcome to KidneyLog. By accessing this website, we assume you accept these terms and conditions. Do not continue to use KidneyLog if you do not agree to take all of the terms and conditions stated on this page.
      </p>

      <h2>1. License</h2>
      <p>
        Unless otherwise stated, KidneyLog and/or its licensors own the intellectual property rights for all material on KidneyLog. All intellectual property rights are reserved. You may access this from KidneyLog for your own personal use subjected to restrictions set in these terms and conditions.
      </p>

      <h2>2. User Content</h2>
      <p>
        In these Website Standard Terms and Conditions, "Your Content" shall mean any audio, video text, images or other material you choose to display on this Website. By displaying Your Content, you grant KidneyLog a non-exclusive, worldwide irrevocable, sub licensable license to use, reproduce, adapt, publish, translate and distribute it in any and all media.
      </p>

      <h2>3. Disclaimer</h2>
      <p>
        To the maximum extent permitted by applicable law, we exclude all representations, warranties and conditions relating to our website and the use of this website. This site is for informational purposes only and does not substitute professional medical advice.
      </p>

      <p className="text-sm text-slate-500 mt-12">
        Last updated: June 2026
      </p>
    </div>
  );
}
