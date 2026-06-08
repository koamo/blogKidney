import React from 'react';

interface PageProps {
  params: Promise<{
    lang: string;
  }>;
}

export default async function AboutPage({ params }: PageProps) {
  const resolvedParams = await params;
  const lang = resolvedParams.lang || 'ko';

  return (
    <div className="mx-auto max-w-4xl px-6 py-16 prose prose-invert">
      <h1 className="text-3xl md:text-5xl font-black mb-8">About Us</h1>
      <p>
        Welcome to KidneyLog, a premium health and medical knowledge archive dedicated to kidney care.
      </p>
      <p>
        Our mission is to deliver the most valuable, up-to-date medical insights, nutritional guidelines, and practical daily tips to patients, caregivers, and health enthusiasts globally.
      </p>
      <p>
        We believe in the power of shared knowledge. Everything published here is curated to help you make informed decisions about your kidney health and well-being.
      </p>
      <h2>Contact Information</h2>
      <ul>
        <li>Email: admin@kidneylog.health</li>
        <li>Location: Seoul, South Korea</li>
      </ul>
      <p className="text-sm text-slate-500 mt-12">
        Last updated: June 2026
      </p>
    </div>
  );
}
