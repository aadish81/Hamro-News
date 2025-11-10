import React, { useState } from 'react';
import OpenAI from 'openai';
import { useMcp } from 'use-mcp/react'

interface NewsItem {
  id: string;
  title: string;
  cover_image: string;
  source: string[];
  category: string;
  time_of_release:  string;
}

const openai = new OpenAI({
  apiKey: import.meta.env.VITE_AZURE_OPENAI_KEY,
  baseURL: import.meta.env.VITE_AZURE_ENDPOINT,
  defaultQuery: { "api-version": "2024-04-01-preview" },
  dangerouslyAllowBrowser: true
});

const NewsFilterComponent: React.FC = () => {
  const [categories, setCategories] = useState<string[]>([]);
  const [currentCategory, setCurrentCategory] = useState('');
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [aiResponse, setAiResponse] = useState('');

  let promptText;
  const {state, getPrompt ,tools, callTool} = useMcp({
  url: import.meta.env.VITE_MCP_SERVER,
  clientName: "hamro-news-mcp-server", 
  autoReconnect: true,
});

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
  
  const differenceMs = now.getTime() - target.getTime();
  const differenceHours = differenceMs / (1000 * 60 * 60);

  return Math.floor(differenceHours).toString(); // Returns whole hours
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

    setLoading(true);
    setError('');
    setAiResponse('');
    setNews([]);

    try {
      console.log(categories);
    // Step 1: Call MCP prompt to get the filtering instructions
    const promptResponse = await getPrompt('filter-news-by-preferences', {
          categoriesJson: JSON.stringify(categories)
        });
    

      promptText =promptResponse.messages[0]?.content;
      console.log('MCP Prompt Result:', promptText);


      if (!promptText) {
        throw new Error('No prompt text received from MCP server');
      }
    } catch (err: any) {
      setError('Error getting prompt from MCP: ' + err.message);
      setLoading(false);
      return;
    }
      try{

      if (typeof promptText !== "string") {
        promptText = JSON.stringify(promptText);
}
      // Step 2: Pass the MCP prompt result to OpenAI
      const completion =  await openai.chat.completions.create({
        model: "gpt-4.1",
        messages: [
          {
            role: "system",
            content: promptText
          }
        ],
          tools:tools.map((t) => ({
          type: "function",
          function: {
            name: t.name,
            description: t.description,
            parameters: t.inputSchema || { type: "object" },
          },
        }))
      });

      const choice = completion.choices[0];
      const toolCall = choice.message.tool_calls?.[0]
      console.log('OpenAI called the tool:', toolCall);

      if (toolCall && toolCall.type === 'function') {
        // LLM decided to call a tool
        const { arguments: rawArgs, name } = toolCall.function;
        const tool_call_id = toolCall.id;
        let parsedArgs: any = {};
        try {
          parsedArgs = JSON.parse(rawArgs);
        } catch {
          parsedArgs = {};
        }

        const toolResult = await callTool(name, parsedArgs);

        const followup = await openai.chat.completions.create({
          model: "gpt-4.1",
          messages: [
            {role:"system", content: promptText},
            { role: "assistant", tool_calls: [toolCall] },
            { 
              role: "tool",
              content: JSON.stringify(toolResult),
              tool_call_id: tool_call_id  },
          ],
        });
        console.log('OpenAI Follow-up Response:', followup);
        const aiMessage = (followup.choices[0].message.content || "")
        .replace(/[*_~#>]/g, "")
        .trim();

      





      setAiResponse(aiMessage || '');

      // Step 3: Extract and parse news data from AI response
      if (aiMessage) {
        try {
          // Try to find JSON in the AI response
          const jsonMatch = aiMessage.match(/\[.*\]/s);
          if (jsonMatch) {
            const newsData = JSON.parse(jsonMatch[0]);
            setNews(newsData);
            console.log('useState News Data:', news );
            console.log('Parsed News Data:', newsData);
          } else {
            // If no JSON found, the AI might have summarized instead
            setNews([]);
          }
        } catch (parseError) {
          console.log('AI returned summary instead of JSON data');
          // AI returned a summary, not JSON data
          setNews([]);
        }
      }
    }

    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };



  // Handle Enter key in category input
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      addCategory();
    }
  };

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
              Processing with AI...
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

      {/* AI Response */}
      {aiResponse && (
        <div className="bg-yellow-50 rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">AI Analysis</h2>
          <div className="bg-white p-4 rounded border">
            <p className="text-gray-700 whitespace-pre-wrap">{aiResponse}</p>
          </div>
        </div>
      )}

      {/* News Display */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">
          Filtered News ({news.length} items)
        </h2>
        
        {news.length === 0 && !loading ? (
          <div className="text-center py-12 text-gray-500">
            {aiResponse ? 'AI provided analysis but no structured news data' : 'No news to display. Add categories and click "Get News"'}
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {news.map((item) => (
              <div key={item.title} className="border border-gray-200 rounded-lg p-4 hover:shadow-lg transition-shadow">
                <img
                  src={item.coverimage}
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
                  Time: {getHoursDifference(item.timeofrelease)} hours ago
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