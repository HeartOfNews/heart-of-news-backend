'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import { format } from 'date-fns';
import { Article } from '@/types';
import api, { endpoints } from '@/lib/api';
import { ArrowLeftIcon, CalendarIcon, LinkIcon, ChartBarIcon } from '@heroicons/react/24/outline';

export default function ArticleDetailPage() {
  const params = useParams();
  const { id } = params;
  
  const [article, setArticle] = useState<Article | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    const fetchArticle = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        const response = await api.get<Article>(endpoints.articles.detail(id as string));
        setArticle(response.data);
      } catch (error: any) {
        console.error('Error fetching article:', error);
        setError(error.response?.data?.detail || 'Failed to fetch article. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };
    
    if (id) {
      fetchArticle();
    }
  }, [id]);
  
  // Determine bias color (red for right-leaning, blue for left-leaning, green for neutral)
  const getBiasColor = () => {
    if (!article?.bias_score) return 'bg-gray-300 dark:bg-gray-600';
    
    const politicalBias = article.bias_score.political_bias;
    if (politicalBias > 0.3) return 'bg-red-500';
    if (politicalBias < -0.3) return 'bg-blue-500';
    return 'bg-green-500';
  };
  
  const getBiasLabel = () => {
    if (!article?.bias_score) return 'Neutral';
    
    const politicalBias = article.bias_score.political_bias;
    if (politicalBias > 0.3) return 'Right-leaning';
    if (politicalBias < -0.3) return 'Left-leaning';
    return 'Neutral';
  };
  
  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }
  
  if (error || !article) {
    return (
      <div className="text-center py-10">
        <p className="text-destructive">{error || 'Article not found'}</p>
        <Link href="/articles" className="mt-4 inline-flex items-center text-primary">
          <ArrowLeftIcon className="h-4 w-4 mr-2" />
          Back to Articles
        </Link>
      </div>
    );
  }
  
  return (
    <div className="bg-background">
      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-6">
          <Link href="/articles" className="inline-flex items-center text-primary hover:underline">
            <ArrowLeftIcon className="h-4 w-4 mr-2" />
            Back to Articles
          </Link>
        </div>
        
        <article>
          {/* Article header */}
          <header className="mb-8">
            <h1 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl mb-4">
              {article.title}
            </h1>
            
            <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground mb-6">
              <div className="inline-flex items-center">
                <CalendarIcon className="h-4 w-4 mr-1.5" aria-hidden="true" />
                {format(new Date(article.published_at), 'MMMM d, yyyy')}
              </div>
              
              <div className="inline-flex items-center">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-secondary text-secondary-foreground">
                  {article.source.name}
                </span>
              </div>
              
              {article.categories.length > 0 && (
                <div className="inline-flex items-center flex-wrap gap-1">
                  {article.categories.map((category) => (
                    <span
                      key={category}
                      className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-muted text-muted-foreground"
                    >
                      {category}
                    </span>
                  ))}
                </div>
              )}
              
              <a
                href={article.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center text-primary hover:underline"
              >
                <LinkIcon className="h-4 w-4 mr-1.5" aria-hidden="true" />
                Original Source
              </a>
            </div>
            
            {/* Featured image */}
            {article.image_url && (
              <div className="relative h-64 sm:h-96 rounded-lg overflow-hidden mb-6">
                <Image
                  src={article.image_url}
                  alt={article.title}
                  fill
                  className="object-cover"
                />
              </div>
            )}
          </header>
          
          {/* Bias analysis */}
          {article.bias_score && (
            <div className="mb-8 p-4 border border-border rounded-lg bg-card">
              <h2 className="text-lg font-semibold mb-3 text-foreground flex items-center">
                <ChartBarIcon className="h-5 w-5 mr-2" />
                Bias Analysis
              </h2>
              
              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-muted-foreground">Political Bias</span>
                    <div className="flex items-center space-x-2">
                      <div className={`h-3 w-3 rounded-full ${getBiasColor()}`} />
                      <span className="text-sm">{getBiasLabel()}</span>
                    </div>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2.5">
                    <div
                      className={`h-2.5 rounded-full ${getBiasColor()}`}
                      style={{
                        width: '50%',
                        marginLeft: `${((article.bias_score.political_bias + 1) / 2) * 100}%`,
                        transform: 'translateX(-50%)',
                      }}
                    ></div>
                  </div>
                  <div className="flex justify-between text-xs text-muted-foreground mt-1">
                    <span>Left</span>
                    <span>Neutral</span>
                    <span>Right</span>
                  </div>
                </div>
                
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-muted-foreground">Emotional Tone</span>
                    <span className="text-sm">
                      {article.bias_score.emotional_tone < 0.3
                        ? 'Neutral'
                        : article.bias_score.emotional_tone < 0.6
                        ? 'Somewhat Emotional'
                        : 'Highly Emotional'}
                    </span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2.5">
                    <div
                      className="h-2.5 rounded-full bg-yellow-500"
                      style={{ width: `${article.bias_score.emotional_tone * 100}%` }}
                    ></div>
                  </div>
                </div>
                
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-muted-foreground">Overall Bias Score</span>
                    <span className="text-sm">
                      {(article.bias_score.overall_score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2.5">
                    <div
                      className="h-2.5 rounded-full bg-purple-500"
                      style={{ width: `${article.bias_score.overall_score * 100}%` }}
                    ></div>
                  </div>
                </div>
                
                {article.bias_score.propaganda_techniques.length > 0 && (
                  <div className="mt-3">
                    <span className="text-sm font-medium text-muted-foreground">Detected Propaganda Techniques:</span>
                    <ul className="mt-2 space-y-1">
                      {article.bias_score.propaganda_techniques.map((technique, index) => (
                        <li key={index} className="text-sm">
                          <span className="font-medium">{technique.name}:</span>{' '}
                          {technique.examples[0]}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}
          
          {/* Article content */}
          <div className="prose dark:prose-invert max-w-none">
            {/* Summary */}
            <div className="mb-6 text-lg italic border-l-4 border-primary pl-4 py-2">
              {article.summary}
            </div>
            
            {/* Main content - render as HTML */}
            <div dangerouslySetInnerHTML={{ __html: article.content }} />
            
            {/* Source link */}
            <div className="mt-8 pt-4 border-t border-border">
              <p className="text-muted-foreground">
                Source:{' '}
                <a
                  href={article.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary hover:underline"
                >
                  {article.source.name}
                </a>
              </p>
            </div>
          </div>
        </article>
      </div>
    </div>
  );
}