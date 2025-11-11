import  { useState, useEffect } from 'react';
import NewsGrid from './components/NewsGrid';
import NewsDetail from './components/NewsDetail';
import LanguageToggle from './components/LanguageToggle';
import LoadingSpinner from './components/LoadingSpinner';
import { newsAPI } from './services/api';
import type { NewsCart, NewsDetailResponse, Language } from './types/news';
import './App.css';

function App() {
  const [language, setLanguage] = useState<Language>('english');
  const [news, setNews] = useState<NewsCart[]>([]);
  const [selectedNews, setSelectedNews] = useState<NewsCart | null>(null);
  const [newsDetail, setNewsDetail] = useState<NewsDetailResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isLoadingDetail, setIsLoadingDetail] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch news based on selected language
  const fetchNews = async (selectedLanguage: Language): Promise<void> => {
    setIsLoading(true);
    setError(null);
    
    try {
      let newsData: NewsCart[];
      if (selectedLanguage === 'english') {
        newsData = await newsAPI.getEnglishNews();
      } else {
        newsData = await newsAPI.getNepaliNews();
      }
      setNews(newsData);
    } catch (err) {
      setError('Failed to fetch news. Please try again.');
      console.error('Error fetching news:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch news detail when a news card is clicked
  const fetchNewsDetail = async (newsItem: NewsCart): Promise<void> => {
    setIsLoadingDetail(true);
    setSelectedNews(newsItem);
    setError(null);
    
    try {
      let detailData: NewsDetailResponse;
      if (language === 'english') {
        detailData = await newsAPI.getEnglishDetail(newsItem.id);
      } else {
        detailData = await newsAPI.getNepaliDetail(newsItem.id);
      }
      setNewsDetail(detailData);
    } catch (err) {
      setError('Failed to fetch news details. Please try again.');
      console.error('Error fetching news detail:', err);
    } finally {
      setIsLoadingDetail(false);
    }
  };

  // Handle language change
  const handleLanguageChange = (newLanguage: Language): void => {
    setLanguage(newLanguage);
    setSelectedNews(null);
    setNewsDetail(null);
  };

  // Close news detail modal
  const handleCloseDetail = (): void => {
    setSelectedNews(null);
    setNewsDetail(null);
  };

  // Load news when language changes
  useEffect(() => {
    fetchNews(language);
  }, [language]);

  return (
    <div className="App">
      <header className="app-header">
        <h1>📰 News Portal</h1>
        <p>Stay updated with the latest news in your preferred language</p>
      </header>

      <main className="app-main">
        <LanguageToggle
          currentLanguage={language}
          onLanguageChange={handleLanguageChange}
          isLoading={isLoading}
        />

        {error && (
          <div className="error-message">
            ⚠️ {error}
            <button onClick={() => fetchNews(language)} className="retry-btn">
              Retry
            </button>
          </div>
        )}

        {isLoading ? (
          <LoadingSpinner size="large" />
        ) : (
          <NewsGrid
            news={news}
            onNewsClick={fetchNewsDetail}
            language={language}
            isLoading={isLoading}
          />
        )}

        {selectedNews && (
          <NewsDetail
            newsCart={selectedNews}
            newsDetail={newsDetail}
            onClose={handleCloseDetail}
            language={language}
          />
        )}

        {isLoadingDetail && (
          <div className="detail-loading">
            <LoadingSpinner size="medium" />
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>&copy; 2024 News Portal. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default App;