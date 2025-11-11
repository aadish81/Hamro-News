import React from 'react';
import type { NewsCart, Language } from '../types/news';
import './NewsCard.css';

interface NewsCardProps {
  news: NewsCart;
  onClick: (news: NewsCart) => void;
  language: Language;
}

const NewsCard: React.FC<NewsCardProps> = ({ news, onClick, language }) => {
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatSource = (sources: string[]): string => {
    if (!sources || sources.length === 0) return 'Unknown Source';
    return sources.join(', ');
  };

  const handleImageError = (e: React.SyntheticEvent<HTMLImageElement, Event>) => {
    e.currentTarget.src = '/placeholder-news.jpg';
  };

  return (
    <div className="news-card" onClick={() => onClick(news)}>
      <div className="news-image-container">
        <img 
          src={news.cover_image} 
          alt={news.title}
          className="news-image"
          onError={handleImageError}
        />
        <div className="news-category">{news.category}</div>
      </div>
      
      <div className="news-content">
        <h3 className="news-title">{news.title}</h3>
        
        <div className="news-meta">
          <div className="news-sources">
            <span className="source-icon">📰</span>
            {formatSource(news.source)}
          </div>
          <div className="news-date">
            <span className="date-icon">🕒</span>
            {formatDate(news.time_of_release)}
          </div>
        </div>
        
        <div className="news-language">
          <span className={`language-badge ${language}`}>
            {language === 'nepali' ? 'नेपाली' : 'English'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default NewsCard;