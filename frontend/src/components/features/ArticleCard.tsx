'use client';

import { Article } from '@/types';
import Link from 'next/link';
import Image from 'next/image';
import { format } from 'date-fns';
import { CalendarIcon, ChartBarIcon } from '@heroicons/react/24/outline';

interface ArticleCardProps {
  article: Article;
  showBiasIndicator?: boolean;
}

export default function ArticleCard({ article, showBiasIndicator = true }: ArticleCardProps) {
  const { id, title, summary, published_at, source, image_url, bias_score } = article;
  
  // Format date
  const formattedDate = format(new Date(published_at), 'MMM d, yyyy');
  
  // Determine bias color (red for right-leaning, blue for left-leaning, green for neutral)
  const getBiasColor = () => {
    if (!bias_score) return 'bg-gray-300 dark:bg-gray-600';
    
    const politicalBias = bias_score.political_bias;
    if (politicalBias > 0.3) return 'bg-red-500';
    if (politicalBias < -0.3) return 'bg-blue-500';
    return 'bg-green-500';
  };
  
  return (
    <div className="flex flex-col overflow-hidden rounded-lg shadow-md bg-card">
      <div className="flex-shrink-0 relative h-48">
        {image_url ? (
          <Image
            src={image_url}
            alt={title}
            fill
            className="object-cover"
          />
        ) : (
          <div className="w-full h-full bg-muted flex items-center justify-center">
            <span className="text-muted-foreground">No image available</span>
          </div>
        )}
      </div>
      <div className="flex flex-1 flex-col justify-between p-6">
        <div className="flex-1">
          <div className="flex items-center space-x-2 text-xs mb-2">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-secondary text-secondary-foreground">
              {source.name}
            </span>
            {showBiasIndicator && bias_score && (
              <div className="flex items-center space-x-1">
                <div className={`h-2 w-2 rounded-full ${getBiasColor()}`} />
                <span className="text-muted-foreground text-xs">
                  {bias_score.political_bias > 0.3 
                    ? 'Right-leaning' 
                    : bias_score.political_bias < -0.3 
                      ? 'Left-leaning' 
                      : 'Neutral'}
                </span>
              </div>
            )}
          </div>
          <Link href={`/articles/${id}`} className="block mt-2">
            <h3 className="text-xl font-semibold text-foreground hover:underline">{title}</h3>
            <p className="mt-3 text-base text-muted-foreground line-clamp-3">{summary}</p>
          </Link>
        </div>
        <div className="mt-6 flex items-center">
          <div className="flex space-x-4 text-sm text-muted-foreground">
            <span className="inline-flex items-center">
              <CalendarIcon className="h-4 w-4 mr-1.5" aria-hidden="true" />
              {formattedDate}
            </span>
            {bias_score && (
              <span className="inline-flex items-center">
                <ChartBarIcon className="h-4 w-4 mr-1.5" aria-hidden="true" />
                {`Bias: ${(bias_score.overall_score * 100).toFixed(0)}%`}
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}