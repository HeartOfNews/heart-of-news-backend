'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { MagnifyingGlassIcon, PlusIcon, TrashIcon, PencilIcon } from '@heroicons/react/24/outline';
import { Article } from '@/types';
import api, { endpoints } from '@/lib/api';

export default function AdminArticlesPage() {
  const router = useRouter();
  const [articles, setArticles] = useState<Article[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [selectedArticles, setSelectedArticles] = useState<string[]>([]);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    fetchArticles();
  }, [currentPage, searchQuery]);

  const fetchArticles = async () => {
    setIsLoading(true);
    try {
      const params = {
        page: currentPage,
        size: 10,
        ...(searchQuery && { query: searchQuery }),
      };

      // In a real implementation, this would call the API
      // For now, we'll simulate a response
      setTimeout(() => {
        const mockArticles = Array(10)
          .fill(0)
          .map((_, index) => ({
            id: `${index + 1 + (currentPage - 1) * 10}`,
            title: `Article ${index + 1 + (currentPage - 1) * 10} ${
              searchQuery ? `matching "${searchQuery}"` : ''
            }`,
            summary: 'This is a summary of the article...',
            content: '<p>Article content</p>',
            url: 'https://example.com',
            published_at: new Date().toISOString(),
            source_id: '1',
            source: {
              id: '1',
              name: 'Example Source',
              url: 'https://example.com',
              is_active: true,
              reliability_score: 0.8,
              bias_score: 0.2,
            },
            categories: ['Politics', 'Economy'],
          }));

        setArticles(mockArticles);
        setTotalPages(5); // Mock total pages
        setIsLoading(false);
      }, 500);
    } catch (error) {
      console.error('Error fetching articles:', error);
      setIsLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchArticles();
  };

  const handleSelectAll = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.checked) {
      setSelectedArticles(articles.map((article) => article.id));
    } else {
      setSelectedArticles([]);
    }
  };

  const handleSelectArticle = (id: string) => {
    if (selectedArticles.includes(id)) {
      setSelectedArticles(selectedArticles.filter((articleId) => articleId !== id));
    } else {
      setSelectedArticles([...selectedArticles, id]);
    }
  };

  const handleDeleteSelected = async () => {
    if (selectedArticles.length === 0) return;

    if (window.confirm(`Are you sure you want to delete ${selectedArticles.length} articles?`)) {
      setIsDeleting(true);
      try {
        // In a real implementation, this would call the API
        // await Promise.all(selectedArticles.map((id) => api.delete(endpoints.articles.detail(id))));
        
        // For now, just simulate a delay
        await new Promise((resolve) => setTimeout(resolve, 1000));
        
        // Remove deleted articles from the list
        setArticles(articles.filter((article) => !selectedArticles.includes(article.id)));
        setSelectedArticles([]);
        
        alert('Articles deleted successfully');
      } catch (error) {
        console.error('Error deleting articles:', error);
        alert('Failed to delete articles');
      } finally {
        setIsDeleting(false);
      }
    }
  };

  return (
    <div>
      <div className="mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Articles</h1>
          <p className="text-muted-foreground">Manage articles published on the platform</p>
        </div>
        <Link
          href="/admin/articles/new"
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary hover:bg-primary/90"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          Add Article
        </Link>
      </div>

      <div className="bg-card rounded-lg shadow-sm border border-border overflow-hidden">
        {/* Search and filters */}
        <div className="p-4 border-b border-border">
          <form onSubmit={handleSearch} className="flex gap-2">
            <div className="relative flex-grow">
              <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                <MagnifyingGlassIcon className="h-5 w-5 text-muted-foreground" />
              </div>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="block w-full rounded-md border-0 py-2 pl-10 text-foreground ring-1 ring-inset ring-border focus:ring-2 focus:ring-inset focus:ring-primary bg-background"
                placeholder="Search articles..."
              />
            </div>
            <button
              type="submit"
              className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
            >
              Search
            </button>
          </form>
        </div>

        {/* Bulk actions */}
        {selectedArticles.length > 0 && (
          <div className="bg-muted p-4 flex items-center gap-4 border-b border-border">
            <span className="text-sm font-medium">
              {selectedArticles.length} article{selectedArticles.length === 1 ? '' : 's'} selected
            </span>
            <button
              type="button"
              onClick={handleDeleteSelected}
              disabled={isDeleting}
              className="inline-flex items-center px-3 py-1.5 border border-transparent rounded-md text-sm font-medium text-white bg-destructive hover:bg-destructive/90 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <TrashIcon className="h-4 w-4 mr-2" />
              {isDeleting ? 'Deleting...' : 'Delete Selected'}
            </button>
          </div>
        )}

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-border">
            <thead className="bg-muted">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  <input
                    type="checkbox"
                    checked={selectedArticles.length === articles.length && articles.length > 0}
                    onChange={handleSelectAll}
                    className="h-4 w-4 rounded border-border text-primary focus:ring-primary"
                  />
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Title
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Source
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Categories
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Published At
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-card divide-y divide-border">
              {isLoading ? (
                <tr>
                  <td colSpan={6} className="px-6 py-4 text-center">
                    <div className="flex justify-center">
                      <div className="animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-primary"></div>
                    </div>
                  </td>
                </tr>
              ) : articles.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-4 text-center">
                    <p className="text-muted-foreground">No articles found</p>
                  </td>
                </tr>
              ) : (
                articles.map((article) => (
                  <tr key={article.id} className="hover:bg-muted/50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <input
                        type="checkbox"
                        checked={selectedArticles.includes(article.id)}
                        onChange={() => handleSelectArticle(article.id)}
                        className="h-4 w-4 rounded border-border text-primary focus:ring-primary"
                      />
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm font-medium">{article.title}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-secondary text-secondary-foreground">
                        {article.source.name}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-wrap gap-1">
                        {article.categories.map((category) => (
                          <span
                            key={category}
                            className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-muted text-muted-foreground"
                          >
                            {category}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">
                      {new Date(article.published_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => router.push(`/admin/articles/${article.id}`)}
                          className="text-primary hover:text-primary/80"
                        >
                          <PencilIcon className="h-5 w-5" />
                          <span className="sr-only">Edit</span>
                        </button>
                        <button
                          onClick={() => {
                            if (window.confirm('Are you sure you want to delete this article?')) {
                              // In a real implementation, this would call the API
                              setArticles(articles.filter((a) => a.id !== article.id));
                            }
                          }}
                          className="text-destructive hover:text-destructive/80"
                        >
                          <TrashIcon className="h-5 w-5" />
                          <span className="sr-only">Delete</span>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="px-6 py-4 border-t border-border flex items-center justify-between">
          <div className="text-sm text-muted-foreground">
            Showing page {currentPage} of {totalPages}
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
              disabled={currentPage === 1 || isLoading}
              className="px-3 py-1 rounded border border-border bg-card text-foreground hover:bg-muted disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <button
              onClick={() => setCurrentPage((prev) => Math.min(prev + 1, totalPages))}
              disabled={currentPage === totalPages || isLoading}
              className="px-3 py-1 rounded border border-border bg-card text-foreground hover:bg-muted disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}