// import React, { useState } from 'react';
// import OpenAI from 'openai';
// import { useMcp } from 'use-mcp/react'

// interface NewsItem {
//   id: string;
//   title: string;
//   cover_image: string;
//   source: string[];
//   category: string;
//   time_of_release:  string;
// }

// const openai = new OpenAI({
//   apiKey: import.meta.env.VITE_AZURE_OPENAI_KEY,
//   baseURL: import.meta.env.VITE_AZURE_ENDPOINT,
//   defaultQuery: { "api-version": "2024-04-01-preview" },
//   dangerouslyAllowBrowser: true
// });

// const NewsFilterComponent: React.FC = () => {
//   const [categories, setCategories] = useState<string[]>([]);
//   const [currentCategory, setCurrentCategory] = useState('');
//   const [news, setNews] = useState<NewsItem[]>([]);
//   const [loading, setLoading] = useState(false);
//   const [error, setError] = useState('');
//   const [aiResponse, setAiResponse] = useState('');


//   const news_portal = ['https://english.onlinekhabar.com/feed','https://english.ratopati.com/rss','https://en.setopati.com/']

// //   let promptText;
//   const {state,tools, callTool} = useMcp({
//   url: import.meta.env.VITE_MCP_SERVER,
//   clientName: "hamro-news-mcp-server", 
//   autoReconnect: true,
// });

//   // Add category to the list
//   const addCategory = () => {
//     if (currentCategory && !categories.includes(currentCategory)) {
//       setCategories(prev => [...prev, currentCategory]);
//       setCurrentCategory('');
//       console.log('Added category:', currentCategory);
//     }
//   };




//   const removeCategory = (categoryToRemove: string) => {
//     setCategories(prev => prev.filter(cat => cat !== categoryToRemove));
//   };

//   // Call MCP prompt and then OpenAI with the prompt result
//   const getFilteredNews = async () => {
//     if (categories.length === 0) {
//       setError('Please add at least one category');
//       return;
//     }
//     let flag = true
//     setLoading(true);
//     setError('');
//     setAiResponse('');
//     setNews([]);

//     let i = 0;
//     do{

//       try{


      
//       // Step 2: Pass the MCP prompt result to OpenAI
//       const completion =  await openai.chat.completions.create({
//         model: "gpt-4.1",
//         messages: [
//           {
//             role: "system",
//             content: import.meta.env.VITE_MCP_SEARCH_PROMPT1
//           },
//           {role:"user",content:`If you think you need to call mcp tool then only use  ${news_portal[i]} else ignore it `}
//         ],
//           tools:tools.map((t) => ({
//           type: "function",
//           function: {
//             name: t.name,
//             description: t.description,
//             parameters: t.inputSchema || { type: "object" },
//           },
//         }))
//       });

//       const choice = completion.choices[0];
//       const toolCall = choice.message.tool_calls?.[0]
//       console.log('OpenAI called the tool:', toolCall);

//       if (toolCall && toolCall.type === 'function') {
//         // LLM decided to call a tool
//         const { arguments: rawArgs, name } = toolCall.function;
//         const tool_call_id = toolCall.id;
//         let parsedArgs: any = {};
//         try {
//           parsedArgs = JSON.parse(rawArgs);
//         } catch {
//           parsedArgs = {};
//         }

//         const toolResult = await callTool(name, parsedArgs);
//         if(!toolResult){
//           flag = false
//         }

//         const followup = await openai.chat.completions.create({
//           model: "gpt-4.1",
//           messages: [
//             {role:"system", content: import.meta.env.VITE_MCP_SEARCH_PROMPT },
//             {role:"user",content:`${categories}`},
//             { role: "assistant", tool_calls: [toolCall] },
//             { 
//               role: "tool",
//               content: JSON.stringify(toolResult),
//               tool_call_id: tool_call_id  },
//           ],
//         });
//         console.log('OpenAI Follow-up Response:', followup);
//         const aiMessage = (followup.choices[0].message.content )
//         .replace(/[*_~#>]/g, "")
//         .trim();
//         if (aiMessage != "null"){
//           setAiResponse(aiMessage || '');
//           flag  = false 
//         }
      






//     }

//     } catch (err: any) {
//       setError(err.message);
//     } finally {
//       setLoading(false);
//     }
//       i = i + 1
//   }while(flag == true && i < news_portal.length)

// }



//   const handleKeyPress = (e: React.KeyboardEvent) => {
//     if (e.key === 'Enter') {
//       addCategory();
//     }
//   };

//   return (
//     <div className="max-w-6xl mx-auto p-6 flex flex-col gap-6 justify-end ">
//       {/* Header */}
//       <div className="text-center mb-8">
//         <h1 className="text-3xl font-bold text-gray-900">Get the images for news</h1>
//         {/* <p className="text-gray-600 mt-2">Add categories → MCP Prompt → OpenAI → Get filtered news</p> */}
//       </div>

//       {/* Category Input */}
//       <div className="bg-white rounded-lg shadow-md p-6 mb-6">
//         *<div className="mb-4">
//            <label className="block text-sm font-medium text-gray-700 mb-2">
//             Add Context
//           </label> 
//           <div className="flex gap-2">
//             <input
//               type="text"
//               value={currentCategory}
//               onChange={(e) => setCurrentCategory(e.target.value)}
//               onKeyPress={handleKeyPress}
//               placeholder="Enter context"
//               className="flex-1 px-3 py-2 border text-black border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
//             />
//             <button
//               onClick={addCategory}
//               className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
//             >
//               Add
//             </button>
//           </div>
//         </div>

//         {/* Selected Categories */}
//         {categories.length > 0 && (
//           <div className="mb-4">
//             <h3 className="text-sm font-medium text-gray-700 mb-2">Selected Context</h3>
//             <div className="flex flex-wrap gap-2">
//               {categories.map((category) => (
//                 <span
//                   key={category}
//                   className="inline-flex items-center bg-blue-100 text-blue-800 text-sm px-3 py-1 rounded-full"
//                 > 
//                   {categories}
//                   <button
//                     onClick={() => removeCategory(category)}
//                     className="ml-2 text-blue-600 hover:text-blue-800 focus:outline-none"
//                   >
//                     ×
//                   </button> 
//                 </span>
//               ))}
//             </div>
//           </div>
//         )}

//         {/* Get News Button */}
//         <button
//           onClick={getFilteredNews}
//           disabled={loading }
//           className="w-full bg-amber-700 text-white py-3 px-4 rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
//         >
//           {loading ? (
//             <span className="flex items-center justify-center">
//               <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
//                 <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
//                 <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
//               </svg>
//               Processing with AI...
//             </span>
//           ) : (
//             `Get Image URL`
//           )}
//         </button>

//         {error && (
//           <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
//             Error: {error}
//           </div>
//         )}
//       </div>

//       {/* AI Response */}
//       {aiResponse && (
//         <div className="bg-yellow-50 rounded-lg shadow-md p-6 mb-6">
//           <h2 className="text-xl font-bold text-gray-900 mb-4">AI Analysis</h2>
//           <div className="bg-white p-4 rounded border">
//             <p className="text-gray-700 whitespace-pre-wrap">{aiResponse}</p>
//           </div>
//         </div>
//       )}

//     </div>
//   );
// };

// export default NewsFilterComponent;