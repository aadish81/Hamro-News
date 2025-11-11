import React from 'react';
import type { NewsCart, Language } from '../types/news';
import NewsCard from './NewsCard';
import './NewsGrid.css';

interface NewsGridProps {
  news: NewsCart[];
  onNewsClick: (news: NewsCart) => void;
  language: Language;
  isLoading: boolean;
//   currentSort: SortOption;
}

const NewsGrid: React.FC<NewsGridProps> = ({ 
  news, 
  onNewsClick, 
  language, 
  isLoading,

}) => {
  // Sort news based on current sort option
  const sortedNews = React.useMemo(() => {
    if (!news || news.length === 0) return [];
    
    return [...news].sort((a, b) => {
      const dateA = new Date(a.time_of_release).getTime();
      const dateB = new Date(b.time_of_release).getTime();
      
      return  dateA - dateB
    });
  }, [news]);

  if (isLoading) {
    return (
      <div className="news-grid-loading">
        <div className="loading-message">Loading news...</div>
      </div>
    );
  }

  if (!news || news.length === 0) {
    return (
      <div className="news-grid-empty">
        <div className="empty-message">
          <h3>No news available</h3>
          <p>There are no news items to display at the moment.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="news-grid">
      {sortedNews.map((newsItem) => (
        <NewsCard
          key={newsItem.id}
          news={newsItem}
          language={language}
          onClick={onNewsClick}
        />
      ))}
    </div>
  );
};

export default NewsGrid;