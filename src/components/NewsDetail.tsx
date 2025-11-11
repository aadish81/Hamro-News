import React from 'react';
import type { NewsCart, NewsDetailResponse, Language } from '../types/news';
import './NewsDetail.css';

interface NewsDetailProps {
  newsCart: NewsCart;
  newsDetail: NewsDetailResponse | null;
  onClose: () => void;
  language: Language;
}

const NewsDetail: React.FC<NewsDetailProps> = ({ 
  newsCart, 
  newsDetail, 
  onClose, 
  language 
}) => {
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatSource = (sources: string[]): string => {
    if (!sources || sources.length === 0) return 'Unknown Source';
    return sources.join(', ');
  };

  if (!newsDetail) return null;

  return (
    <div className="news-detail-overlay" onClick={onClose}>
      <div className="news-detail-modal" onClick={(e) => e.stopPropagation()}>
        <button className="close-button" onClick={onClose}>×</button>
        
        <div className="detail-header">
          <div className="detail-image-container">
            <img 
              src={newsCart.cover_image} 
              alt={newsCart.title}
              className="detail-image"
            />
            <div className="detail-category">{newsCart.category}</div>
          </div>
          
          <div className="detail-title-section">
            <h1 className="detail-title">{newsCart.title}</h1>
            
            <div className="detail-meta">
              <div className="meta-item">
                <span className="meta-icon">📰</span>
                <span>{formatSource(newsCart.source)}</span>
              </div>
              
              <div className="meta-item">
                <span className="meta-icon">🕒</span>
                <span>{formatDate(newsCart.time_of_release)}</span>
              </div>
              
              <div className="meta-item">
                <span className="meta-icon">🌐</span>
                <span className={`language-tag ${language}`}>
                  {language === 'nepali' ? 'नेपाली' : 'English'}
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <div className="detail-content">
          <div className="description-section">
            <h3>News Description</h3>
            <div className="description-text">
              {newsDetail.description.split('\n').map((paragraph, index) => (
                <p key={index}>{paragraph}</p>
              ))}
            </div>
          </div>
        </div>
        
        <div className="detail-footer">
          <button className="back-button" onClick={onClose}>
            ← Back to News
          </button>
        </div>
      </div>
    </div>
  );
};

export default NewsDetail;