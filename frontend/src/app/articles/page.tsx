'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { Article, ArticleListResponse, Source, SourceListResponse } from '@/types';
import ArticleCard from '@/components/features/ArticleCard';
import api, { endpoints } from '@/lib/api';
import { FunnelIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import { format } from 'date-fns';
import { useArticleUpdates } from '@/hooks/useArticleUpdates';
import NewArticlesNotification from '@/components/features/NewArticlesNotification';
import { useWebSocket } from '@/contexts/WebSocketContext';

export default function ArticlesPage() {
  const searchParams = useSearchParams();
  const initialQuery = searchParams?.get('q') || '';
  
  const { connectionStatus } = useWebSocket();
  
  const [sources, setSources] = useState<Source[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [totalArticles, setTotalArticles] = useState<number>(0);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [showFilters, setShowFilters] = useState<boolean>(false);
  
  // Filter states
  const [searchQuery, setSearchQuery] = useState<string>(initialQuery);
  const [selectedSource, setSelectedSource] = useState<string>('');
  const [dateFrom, setDateFrom] = useState<string>('');
  const [dateTo, setDateTo] = useState<string>('');
  
  // Pagination
  const pageSize = 12;
  const totalPages = Math.ceil(totalArticles / pageSize);
  
  // Use the real-time article updates hook
  const { 
    articles, 
    newArticleCount,
    showNewArticles,
    replaceArticles
  } = useArticleUpdates([]);
  
  // Load sources
  useEffect(() => {
    const fetchSources = async () => {
      try {
        const response = await api.get<SourceListResponse>(endpoints.sources.list);
        setSources(response.data.items);
      } catch (error) {
        console.error('Error fetching sources:', error);
      }
    };
    
    fetchSources();
  }, []);
  
  // Load articles
  useEffect(() => {
    const fetchArticles = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        const params = {
          page: currentPage,
          size: pageSize,
          ...(searchQuery && { query: searchQuery }),
          ...(selectedSource && { source_id: selectedSource }),
          ...(dateFrom && { date_from: dateFrom }),
          ...(dateTo && { date_to: dateTo }),
        };
        
        const response = await api.get<ArticleListResponse>(endpoints.articles.list, { params });
        replaceArticles(response.data.items);
        setTotalArticles(response.data.total);
      } catch (error: any) {
        console.error('Error fetching articles:', error);
        setError(error.response?.data?.detail || 'Failed to fetch articles. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchArticles();
  }, [currentPage, searchQuery, selectedSource, dateFrom, dateTo, replaceArticles]);
  
  // Handle search form submit
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage(1); // Reset to first page on new search
  };
  
  // Handle filter changes
  const applyFilters = () => {
    setCurrentPage(1); // Reset to first page on new filters
    setShowFilters(false);
  };
  
  // Reset filters
  const resetFilters = () => {
    setSelectedSource('');
    setDateFrom('');
    setDateTo('');
    setCurrentPage(1);
    setShowFilters(false);
  };
  
  // Function to load new articles
  const handleShowNewArticles = async () => {
    // First call the hook's function to reset the counter
    showNewArticles();
    
    // Then reload the articles from the beginning
    setCurrentPage(1);
  };
  
  return (
    <div className="bg-background">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold tracking-tight text-foreground">Latest News Articles</h1>
          <p className="mt-4 text-lg text-muted-foreground">
            Browse our collection of news articles from various sources, analyzed for bias and propaganda.
          </p>
          {connectionStatus === 'connected' && (
            <p className="mt-2 text-sm text-green-600 dark:text-green-400">
              <span className="inline-block h-2 w-2 rounded-full bg-green-500 mr-1"></span>
              Connected to real-time updates
            </p>
          )}
        </div>
        
        {/* New articles notification */}
        <NewArticlesNotification 
          count={newArticleCount} 
          onClick={handleShowNewArticles} 
        />
        
        {/* Search and filters */}
        <div className="mb-8">
          <div className="flex flex-col sm:flex-row gap-4 mb-4">
            <form onSubmit={handleSearch} className="flex-grow">
              <div className="relative rounded-md shadow-sm">
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                  <MagnifyingGlassIcon className="h-5 w-5 text-muted-foreground" aria-hidden="true" />
                </div>
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="block w-full rounded-md border-0 py-2 pl-10 text-foreground ring-1 ring-inset ring-border focus:ring-2 focus:ring-inset focus:ring-primary bg-background"
                  placeholder="Search articles..."
                />
                <button
                  type="submit"
                  className="absolute inset-y-0 right-0 flex items-center px-3 py-2 bg-primary text-primary-foreground rounded-r-md hover:bg-primary/90"
                >
                  Search
                </button>
              </div>
            </form>
            <button
              type="button"
              onClick={() => setShowFilters(!showFilters)}
              className="inline-flex items-center px-4 py-2 border border-border rounded-md bg-background text-foreground hover:bg-muted"
            >
              <FunnelIcon className="h-5 w-5 mr-2" aria-hidden="true" />
              Filters
            </button>
          </div>
          
          {/* Filters panel */}
          {showFilters && (
            <div className="mt-4 p-4 border border-border rounded-md bg-card">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label htmlFor="source" className="block text-sm font-medium text-foreground mb-1">
                    Source
                  </label>
                  <select
                    id="source"
                    value={selectedSource}
                    onChange={(e) => setSelectedSource(e.target.value)}
                    className="block w-full rounded-md border-0 py-2 text-foreground bg-background ring-1 ring-inset ring-border focus:ring-2 focus:ring-inset focus:ring-primary"
                  >
                    <option value="">All Sources</option>
                    {sources.map((source) => (
                      <option key={source.id} value={source.id}>
                        {source.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label htmlFor="date-from" className="block text-sm font-medium text-foreground mb-1">
                    From Date
                  </label>
                  <input
                    type="date"
                    id="date-from"
                    value={dateFrom}
                    onChange={(e) => setDateFrom(e.target.value)}
                    className="block w-full rounded-md border-0 py-2 text-foreground bg-background ring-1 ring-inset ring-border focus:ring-2 focus:ring-inset focus:ring-primary"
                  />
                </div>
                <div>
                  <label htmlFor="date-to" className="block text-sm font-medium text-foreground mb-1">
                    To Date
                  </label>
                  <input
                    type="date"
                    id="date-to"
                    value={dateTo}
                    onChange={(e) => setDateTo(e.target.value)}
                    className="block w-full rounded-md border-0 py-2 text-foreground bg-background ring-1 ring-inset ring-border focus:ring-2 focus:ring-inset focus:ring-primary"
                  />
                </div>
              </div>
              <div className="mt-4 flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={resetFilters}
                  className="px-4 py-2 border border-border rounded-md bg-background text-foreground hover:bg-muted"
                >
                  Reset
                </button>
                <button
                  type="button"
                  onClick={applyFilters}
                  className="px-4 py-2 rounded-md bg-primary text-primary-foreground hover:bg-primary/90"
                >
                  Apply Filters
                </button>
              </div>
            </div>
          )}
        </div>
        
        {/* Articles grid */}
        {isLoading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
          </div>
        ) : error ? (
          <div className="text-center py-10">
            <p className="text-destructive">{error}</p>
          </div>
        ) : articles.length === 0 ? (
          <div className="text-center py-10 border border-border rounded-md">
            <p className="text-muted-foreground">No articles found. Try different search terms or filters.</p>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {articles.map((article) => (
                <ArticleCard key={article.id} article={article} />
              ))}
            </div>
            
            {/* Pagination */}
            {totalPages > 1 && (
              <div className="mt-8 flex justify-center">
                <nav className="isolate inline-flex -space-x-px rounded-md shadow-sm">
                  <button
                    onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
                    disabled={currentPage === 1}
                    className="relative inline-flex items-center rounded-l-md px-2 py-2 text-muted-foreground ring-1 ring-inset ring-border hover:bg-muted disabled:opacity-50 disabled:hover:bg-transparent"
                  >
                    <span className="sr-only">Previous</span>
                    <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                      <path fillRule="evenodd" d="M12.79 5.23a.75.75 0 01-.02 1.06L8.832 10l3.938 3.71a.75.75 0 11-1.04 1.08l-4.5-4.25a.75.75 0 010-1.08l4.5-4.25a.75.75 0 011.06.02z" clipRule="evenodd" />
                    </svg>
                  </button>
                  
                  {Array.from({ length: totalPages }, (_, i) => i + 1)
                    .filter(page => {
                      // Show first, last, current, and pages around current
                      return page === 1 || page === totalPages || 
                        Math.abs(page - currentPage) <= 1;
                    })
                    .map((page, i, array) => {
                      // Add ellipsis if there are gaps
                      const prevPage = array[i - 1];
                      const showEllipsisBefore = prevPage && page - prevPage > 1;
                      
                      return (
                        <React.Fragment key={page}>
                          {showEllipsisBefore && (
                            <span className="relative inline-flex items-center px-4 py-2 text-sm font-semibold text-muted-foreground ring-1 ring-inset ring-border">
                              ...
                            </span>
                          )}
                          <button
                            onClick={() => setCurrentPage(page)}
                            className={`relative inline-flex items-center px-4 py-2 text-sm font-semibold ${
                              page === currentPage
                                ? 'bg-primary text-primary-foreground'
                                : 'text-foreground ring-1 ring-inset ring-border hover:bg-muted'
                            }`}
                          >
                            {page}
                          </button>
                        </React.Fragment>
                      );
                    })}
                  
                  <button
                    onClick={() => setCurrentPage((prev) => Math.min(prev + 1, totalPages))}
                    disabled={currentPage === totalPages}
                    className="relative inline-flex items-center rounded-r-md px-2 py-2 text-muted-foreground ring-1 ring-inset ring-border hover:bg-muted disabled:opacity-50 disabled:hover:bg-transparent"
                  >
                    <span className="sr-only">Next</span>
                    <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                      <path fillRule="evenodd" d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z" clipRule="evenodd" />
                    </svg>
                  </button>
                </nav>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}