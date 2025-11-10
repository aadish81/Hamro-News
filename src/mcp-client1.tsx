import React, { useEffect, useState } from 'react';


// let toolResultJson: NewsItem[] = [];
// let forYou: NewsItem[] = [];
interface NewsItem {
  id: string;
  title: string;
  cover_image: string;
  source: string[];
  category: string;
  time_of_release:  string;
}

// const openai = new OpenAI({
//   apiKey: import.meta.env.VITE_AZURE_OPENAI_KEY,
//   baseURL: import.meta.env.VITE_AZURE_ENDPOINT,
//   defaultQuery: { "api-version": "2024-04-01-preview" },
//   dangerouslyAllowBrowser: true
// });

const NewsFilterComponent: React.FC = () => {
  const [categories, setCategories] = useState<string[]>([]);
  const [currentCategory, setCurrentCategory] = useState('');
  const [news, setNews] = useState<NewsItem[]>([]);
  const [dnews, setDnews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [language,setLanguage] = useState(false)
  const [error, setError] = useState('');
 
  let newsCarts:any;
let toolResultJson;
const getNews = async () => {
  setLoading(true);
  setError('');
  setNews([]);

  try {

      if (language === true){
       newsCarts = await fetch("http://127.0.0.1:8000/news-cart/nepali/")
      }
      else {
        newsCarts = await fetch("http://127.0.0.1:8000/news_carts/english/")
      }
   


    toolResultJson = await newsCarts.json();
    setDnews(toolResultJson);
    console.log("Fetched News Carts:", toolResultJson);
    console.log("Number of News Carts fetched:", toolResultJson.length);

  }
  catch (err: any) {
    setError(err.message);
  } finally {
    setLoading(false);
  }
}


  // Add category to the list
  const addCategory = () => {
    if (currentCategory.trim() && !categories.includes(currentCategory.trim())) {
      setCategories(prev => [...prev, currentCategory.trim()]);
      setCurrentCategory('');
      console.log('Added category:', currentCategory);
    }
  };

function getHoursDifference(targetDate: string | Date): string {
  const target = new Date(targetDate);
  const now = new Date();
  
  // Use UTC methods for consistent timezone handling
  const differenceMs = now.getTime() - target.getTime();
  const differenceHours = differenceMs / (1000 * 60 * 60);

  return Math.floor(differenceHours).toString();
}


  // Remove category from list
  const removeCategory = (categoryToRemove: string) => {
    setCategories(prev => prev.filter(cat => cat !== categoryToRemove));
  };

  // Call MCP prompt and then OpenAI with the prompt result


 
const getFilteredNews = async () => {
  if (categories.length === 0) {
    setError('Please add at least one category');
    return;
  }
  if (dnews .length === 0) {
    setError('No news data available. Please try again later.');
    return;
  }




  try {
    let forYou: NewsItem[] = [];
    for (const news of dnews) {
      for (const category of categories) {
        if (category.toLowerCase() === news.category.toLowerCase()) {
          forYou.push(news);
          continue
        }
      }
    }
    // console.log('Filtered News Carts:', forYou);
    console.log("length of forYou:", forYou.length);
    console.log("first item of forYou:", forYou[0]);
    setNews(forYou);

    
  } catch (err: any) {
    setError(err.message);
  } finally {
    setLoading(false);
  }
 }
  

  // Handle Enter key in category input
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      addCategory();
    }
  };

  const switchLanguage = () => {
    setLanguage((prev)=>(!prev))
  }
  useEffect(() => {

    getNews();
  }, [language]);

  return (
    <div className="max-w-6xl mx-auto p-6 flex flex-col gap-6 justify-end ">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">AI-Powered News Filter</h1>
        {/* <p className="text-gray-600 mt-2">Add categories → MCP Prompt → OpenAI → Get filtered news</p> */}
      </div>

      {/* Category Input */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Add News Categories
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              value={currentCategory}
              onChange={(e) => setCurrentCategory(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Enter a category (e.g., technology, sports)"
              className="flex-1 px-3 py-2 border text-black border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={addCategory}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Add
            </button>

          <button className='bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-400 focus:outline-none focus:ring-2 focus:ring-green-950'
          onClick={switchLanguage}>
            {language ? "Get in English":"Get in Nepali"}
          </button>
          </div>
        </div>

        {/* Selected Categories */}
        {categories.length > 0 && (
          <div className="mb-4">
            <h3 className="text-sm font-medium text-gray-700 mb-2">Selected Categories:</h3>
            <div className="flex flex-wrap gap-2">
              {categories.map((category) => (
                <span
                  key={category}
                  className="inline-flex items-center bg-blue-100 text-blue-800 text-sm px-3 py-1 rounded-full"
                >
                  {category}
                  <button
                    onClick={() => removeCategory(category)}
                    className="ml-2 text-blue-600 hover:text-blue-800 focus:outline-none"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Get News Button */}
        <button
          onClick={getFilteredNews}
          disabled={loading || categories.length === 0}
          className="w-full bg-green-600 text-white py-3 px-4 rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {loading ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Processing 
            </span>
          ) : (
            `Get AI-Filtered News (${categories.length} categories)`
          )}
        </button>

        {error && (
          <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            Error: {error}
          </div>
        )}
      </div>




      {/* News Display */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">
          Filtered News ({news.length} items)
        </h2>
        
        {news.length === 0 && !loading ? (
          <div className="text-center py-12 text-gray-500">
            { 'No news to display. Add categories and click "Get News"'}
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {news.map((item) => (
              <div key={item.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-lg transition-shadow">
                <img
                  src={item.cover_image}
                  alt={item.title}
                  className="w-full h-48 object-cover rounded-md mb-3"

                />
                
                <h3 className="text-lg font-semibold mb-2 line-clamp-2">{item.title}</h3>
                
                <div className="flex justify-between items-center mb-3">
                  <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                    {item.category}
                  </span>
                </div>

                {item.source && item.source.length > 0 && (
                  <div className="text-sm text-gray-600 mb-2">
                    <span className="font-medium">Sources:</span> {item.source.join(', ')}
                  </div>
                )}

                <div className="text-xs text-gray-500 border-t pt-2">
                  Time: {getHoursDifference(item.time_of_release)} hours ago
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default NewsFilterComponent;