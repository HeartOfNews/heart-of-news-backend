import { useState, useEffect, useCallback } from 'react';
import { useWebSocketMessage } from './useWebSocketMessage';
import { Article } from '@/types';

interface ArticleUpdateMessage {
  action: 'new' | 'update' | 'delete';
  article: Article;
}

export function useArticleUpdates(initialArticles: Article[] = []) {
  const [articles, setArticles] = useState<Article[]>(initialArticles);
  const [newArticleCount, setNewArticleCount] = useState(0);
  const { lastData, isConnected } = useWebSocketMessage<ArticleUpdateMessage>('article');

  // Process new article updates
  useEffect(() => {
    if (lastData && isConnected) {
      const { action, article } = lastData;
      
      switch (action) {
        case 'new':
          // If we have the show new articles button active, increment the counter
          // instead of immediately adding to the list
          if (newArticleCount > 0) {
            setNewArticleCount(prev => prev + 1);
          } else {
            setArticles(prev => [article, ...prev]);
          }
          break;
          
        case 'update':
          setArticles(prev => 
            prev.map(a => a.id === article.id ? { ...a, ...article } : a)
          );
          break;
          
        case 'delete':
          setArticles(prev => prev.filter(a => a.id !== article.id));
          break;
      }
    }
  }, [lastData, isConnected, newArticleCount]);

  // Function to show the new articles that have been accumulated
  const showNewArticles = useCallback(() => {
    if (newArticleCount > 0) {
      // This would typically make a request to get the new articles
      // But for simplicity, we'll just reset the counter
      setNewArticleCount(0);
    }
  }, [newArticleCount]);

  // Function to add new articles to the list
  const addArticles = useCallback((newArticles: Article[]) => {
    setArticles(prev => [...newArticles, ...prev]);
  }, []);

  // Function to replace all articles (e.g., on initial load or filter change)
  const replaceArticles = useCallback((newArticles: Article[]) => {
    setArticles(newArticles);
    setNewArticleCount(0);
  }, []);

  return {
    articles,
    newArticleCount,
    showNewArticles,
    addArticles,
    replaceArticles,
    isConnected
  };
}