import React, { useEffect, useState } from "react";
import axios from "axios";
import NewsCard from "./components/NewsCard";
import type { NewsCartRead } from "./types";

const App: React.FC = () => {
  const [newsList, setNewsList] = useState<NewsCartRead[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchNews = async () => {
      try {
        const res = await axios.get<NewsCartRead[]>(
          "https://hamro-news.onrender.com/news-carts/english/"
        );
        setNewsList(res.data);
      } catch (err) {
        console.error("Error fetching news:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchNews();
  }, []);

  if (loading) return <p>Loading news...</p>;

  return (
    <div style={styles.container}>
      <h1 style={styles.header}>📰 English News Feed</h1>
      <div style={styles.grid}>
        {newsList.map((news) => (
          <NewsCard key={news.id} news={news} />
        ))}
      </div>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    padding: "20px",
    fontFamily: "sans-serif",
  },
  header: {
    textAlign: "center",
    marginBottom: "30px",
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(350px, 1fr))",
    gap: "20px",
    justifyItems: "center",
  },
};

export default App;
