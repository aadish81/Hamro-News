import React from 'react';
import type { NewsCart, Language } from '../types/news';
import NewsCard from './NewsCard';
import './NewsGrid.css';

interface NewsGridProps {
  news: NewsCart[];
  onNewsClick: (news: NewsCart) => void;
  language: Language;
  isLoading: boolean;
}

const NewsGrid: React.FC<NewsGridProps> = ({ 
  news, 
  onNewsClick, 
  language, 
  isLoading 
}) => {
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
      {news.map((newsItem) => (
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