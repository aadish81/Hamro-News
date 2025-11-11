import React from 'react';
import type { Language } from '../types/news';
import './LanguageToggle.css';

interface LanguageToggleProps {
  currentLanguage: Language;
  onLanguageChange: (language: Language) => void;
  isLoading: boolean;
}

const LanguageToggle: React.FC<LanguageToggleProps> = ({ 
  currentLanguage, 
  onLanguageChange, 
  isLoading 
}) => {
  return (
    <div className="language-toggle">
      <h2 className="toggle-title">News Language</h2>
      <div className="toggle-buttons">
        <button
          className={`toggle-btn ${currentLanguage === 'english' ? 'active' : ''}`}
          onClick={() => onLanguageChange('english')}
          disabled={isLoading}
        >
          <span className="flag">🇺🇸</span>
          English News
        </button>
        
        <button
          className={`toggle-btn ${currentLanguage === 'nepali' ? 'active' : ''}`}
          onClick={() => onLanguageChange('nepali')}
          disabled={isLoading}
        >
          <span className="flag">🇳🇵</span>
          नेपाली समाचार
        </button>
      </div>
    </div>
  );
};

export default LanguageToggle;