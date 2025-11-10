import React from "react";
import type { NewsCartRead } from "../types";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";

dayjs.extend(relativeTime);

interface NewsCardProps {
  news: NewsCartRead;
}

const NewsCard: React.FC<NewsCardProps> = ({ news }) => {
  const timeAgo = dayjs(news.time_of_release).fromNow();

  return (
    <div style={styles.card}>
      <img src={news.cover_image} alt={news.title} style={styles.image} />
      <div style={styles.content}>
        <h3 style={styles.title}>{news.title}</h3>
        <p style={styles.category}>Category: {news.category}</p>
        {news.source && news.source.length > 0 && (
          <p style={styles.source}>Source: {news.source.join(", ")}</p>
        )}
        <p style={styles.time}>Posted {timeAgo}</p>
      </div>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  card: {
    border: "1px solid #ddd",
    borderRadius: "10px",
    overflow: "hidden",
    marginBottom: "20px",
    display: "flex",
    flexDirection: "column",
    maxWidth: "400px",
    boxShadow: "0 2px 5px rgba(0,0,0,0.1)",
  },
  image: {
    width: "100%",
    height: "200px",
    objectFit: "cover",
  },
  content: { padding: "10px" },
  title: { fontSize: "1.2em", marginBottom: "5px" },
  category: { fontSize: "0.9em", color: "#555" },
  source: { fontSize: "0.85em", color: "#777" },
  time: { fontSize: "0.8em", color: "#999" },
};

export default NewsCard;
