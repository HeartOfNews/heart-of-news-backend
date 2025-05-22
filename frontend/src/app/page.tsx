'use client';

import Link from 'next/link';
import { ArrowRightIcon } from '@heroicons/react/24/outline';

export default function Home() {
  return (
    <div className="bg-background">
      {/* Hero section */}
      <div className="relative isolate overflow-hidden">
        <div className="mx-auto max-w-7xl px-6 py-24 sm:py-32 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h1 className="text-4xl font-bold tracking-tight text-foreground sm:text-6xl">
              News without bias or propaganda
            </h1>
            <p className="mt-6 text-lg leading-8 text-muted-foreground">
              Heart of News delivers information from multiple sources, analyzed by AI to detect and filter out bias and propaganda techniques, giving you a balanced view of world events.
            </p>
            <div className="mt-10 flex items-center justify-center gap-x-6">
              <Link
                href="/articles"
                className="rounded-md bg-primary px-3.5 py-2.5 text-sm font-semibold text-primary-foreground shadow-sm hover:bg-primary/90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
              >
                Browse Articles
              </Link>
              <Link href="/about" className="text-sm font-semibold leading-6 text-foreground group">
                Learn more <ArrowRightIcon className="inline h-4 w-4 transition group-hover:translate-x-1" />
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Features section */}
      <div className="mx-auto max-w-7xl px-6 lg:px-8 py-16 sm:py-24">
        <div className="mx-auto max-w-2xl lg:text-center">
          <h2 className="text-base font-semibold leading-7 text-primary">Unbiased Reporting</h2>
          <p className="mt-2 text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            Features that make a difference
          </p>
          <p className="mt-6 text-lg leading-8 text-muted-foreground">
            Heart of News uses advanced AI technology to analyze news articles from various sources, detecting and highlighting bias, emotional language, and propaganda techniques.
          </p>
        </div>
        <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-none">
          <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-16 lg:max-w-none lg:grid-cols-3">
            <div className="flex flex-col">
              <dt className="flex items-center gap-x-3 text-base font-semibold leading-7 text-foreground">
                <div className="h-10 w-10 flex items-center justify-center rounded-lg bg-primary">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6 text-primary-foreground">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v2.25m6.364.386-1.591 1.591M21 12h-2.25m-.386 6.364-1.591-1.591M12 18.75V21m-4.773-4.227-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0Z" />
                  </svg>
                </div>
                Bias Detection
              </dt>
              <dd className="mt-4 flex flex-auto flex-col text-base leading-7 text-muted-foreground">
                <p className="flex-auto">
                  Our AI analyzes news articles for political bias on a scale from left to right, helping you understand the perspective of the content.
                </p>
              </dd>
            </div>
            <div className="flex flex-col">
              <dt className="flex items-center gap-x-3 text-base font-semibold leading-7 text-foreground">
                <div className="h-10 w-10 flex items-center justify-center rounded-lg bg-primary">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6 text-primary-foreground">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166 2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a1.14 1.14 0 0 1 .865-.501 48.172 48.172 0 0 0 3.423-.379c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0 0 12 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018Z" />
                  </svg>
                </div>
                Emotional Language
              </dt>
              <dd className="mt-4 flex flex-auto flex-col text-base leading-7 text-muted-foreground">
                <p className="flex-auto">
                  We detect the use of emotional language and sensationalism in news articles, allowing you to focus on the facts rather than emotional manipulation.
                </p>
              </dd>
            </div>
            <div className="flex flex-col">
              <dt className="flex items-center gap-x-3 text-base font-semibold leading-7 text-foreground">
                <div className="h-10 w-10 flex items-center justify-center rounded-lg bg-primary">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6 text-primary-foreground">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 0 0-2.456 2.456ZM16.894 20.567 16.5 21.75l-.394-1.183a2.25 2.25 0 0 0-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 0 0 1.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 0 0 1.423 1.423l1.183.394-1.183.394a2.25 2.25 0 0 0-1.423 1.423Z" />
                  </svg>
                </div>
                Multi-source Analysis
              </dt>
              <dd className="mt-4 flex flex-auto flex-col text-base leading-7 text-muted-foreground">
                <p className="flex-auto">
                  We collect news from multiple sources, allowing you to compare different perspectives on the same story and form your own opinion.
                </p>
              </dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  );
}