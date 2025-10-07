# rb_ingestor/trending_analyzer.py
"""
Sistema inteligente de análise de tendências para aumentar audiência
"""
import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from django.utils import timezone

class TrendingAnalyzer:
    def __init__(self):
        self.google_trends_api = "https://trends.google.com/trends/api/dailytrends"
        self.reddit_api = "https://www.reddit.com/r/brasil/hot.json"
        self.twitter_trends_api = "https://api.twitter.com/1.1/trends/place.json"
        
    def get_google_trends_br(self) -> List[Dict]:
        """Busca trending topics do Google Trends Brasil"""
        try:
            # Simulação de busca em Google Trends (API real requer autenticação)
            # Em produção, usar biblioteca como pytrends
            trending_topics = [
                {"topic": "eleições 2026", "search_volume": "high", "category": "política"},
                {"topic": "copa do mundo 2026", "search_volume": "high", "category": "esportes"},
                {"topic": "inflação Brasil", "search_volume": "medium", "category": "economia"},
                {"topic": "ChatGPT Brasil", "search_volume": "high", "category": "tecnologia"},
                {"topic": "crise hídrica", "search_volume": "medium", "category": "meio ambiente"},
            ]
            return trending_topics
        except Exception:
            return []
    
    def get_reddit_trending(self) -> List[Dict]:
        """Busca posts populares do Reddit Brasil"""
        try:
            headers = {'User-Agent': 'RadarBR/1.0'}
            response = requests.get(self.reddit_api, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                posts = []
                for post in data.get('data', {}).get('children', [])[:10]:
                    post_data = post.get('data', {})
                    posts.append({
                        "title": post_data.get('title', ''),
                        "score": post_data.get('score', 0),
                        "subreddit": post_data.get('subreddit', ''),
                        "url": post_data.get('url', '')
                    })
                return posts
            else:
                return []
        except Exception as e:
            print(f"Erro ao buscar Reddit: {e}")
            return []
    
    def analyze_keyword_potential(self, topic: str) -> Dict:
        """Analisa o potencial de audiência de um tópico"""
        # Simulação de análise de palavras-chave
        # Em produção, integrar com Google Keyword Planner ou SEMrush
        
        high_volume_keywords = [
            "como fazer", "melhor", "preço", "comparação", "dicas",
            "guia", "tutorial", "reviews", "opinião", "análise"
        ]
        
        commercial_keywords = [
            "comprar", "venda", "oferta", "desconto", "promoção",
            "loja", "preço", "barato", "caro", "vale a pena"
        ]
        
        informational_keywords = [
            "o que é", "como funciona", "por que", "quando", "onde",
            "quem", "história", "origem", "significado"
        ]
        
        topic_lower = topic.lower()
        
        # Análise de intenção
        if any(kw in topic_lower for kw in commercial_keywords):
            intent = "commercial"
            potential_score = 8
        elif any(kw in topic_lower for kw in informational_keywords):
            intent = "informational"
            potential_score = 9
        elif any(kw in topic_lower for kw in high_volume_keywords):
            intent = "high_volume"
            potential_score = 7
        else:
            intent = "general"
            potential_score = 5
        
        return {
            "intent": intent,
            "potential_score": potential_score,
            "estimated_traffic": self._estimate_traffic(topic, intent),
            "competition": self._estimate_competition(topic)
        }
    
    def _estimate_traffic(self, topic: str, intent: str) -> str:
        """Estima tráfego potencial baseado no tópico e intenção"""
        if intent == "informational":
            return "high"
        elif intent == "commercial":
            return "medium"
        elif intent == "high_volume":
            return "high"
        else:
            return "low"
    
    def _estimate_competition(self, topic: str) -> str:
        """Estima competição para o tópico"""
        high_competition_keywords = ["notícias", "atual", "hoje", "agora"]
        if any(kw in topic.lower() for kw in high_competition_keywords):
            return "high"
        return "medium"
    
    def get_optimized_topics(self, limit: int = 5) -> List[Dict]:
        """Retorna tópicos otimizados para audiência"""
        all_topics = []
        
        # Buscar trending topics
        google_trends = self.get_google_trends_br()
        reddit_trending = self.get_reddit_trending()
        
        # Processar Google Trends
        if google_trends:
            for trend in google_trends:
                analysis = self.analyze_keyword_potential(trend["topic"])
                all_topics.append({
                    "topic": trend["topic"],
                    "source": "google_trends",
                    "category": trend["category"],
                    "search_volume": trend["search_volume"],
                    "analysis": analysis,
                    "priority": analysis["potential_score"]
                })
        
        # Processar Reddit
        if reddit_trending:
            for post in reddit_trending[:5]:
                analysis = self.analyze_keyword_potential(post["title"])
                all_topics.append({
                    "topic": post["title"],
                    "source": "reddit",
                    "category": "geral",
                    "search_volume": "medium",
                    "analysis": analysis,
                    "priority": analysis["potential_score"]
                })
        
        # Ordenar por prioridade e retornar os melhores
        all_topics.sort(key=lambda x: x["priority"], reverse=True)
        return all_topics[:limit]
    
    def get_seasonal_topics(self) -> List[str]:
        """Retorna tópicos sazonais baseados na data atual"""
        now = datetime.now()
        month = now.month
        
        seasonal_topics = {
            1: ["ano novo", "férias janeiro", "carnaval"],
            2: ["carnaval", "volta às aulas", "imposto de renda"],
            3: ["páscoa", "outono", "dia da mulher"],
            4: ["dia do trabalho", "tiradentes", "abril"],
            5: ["dia das mães", "maio", "inverno"],
            6: ["festas juninas", "são joão", "junho"],
            7: ["férias julho", "inverno", "julho"],
            8: ["dia dos pais", "agosto", "inverno"],
            9: ["primavera", "setembro", "independência"],
            10: ["outubro", "eleições", "halloween"],
            11: ["novembro", "black friday", "consciência negra"],
            12: ["natal", "ano novo", "dezembro", "férias"]
        }
        
        return seasonal_topics.get(month, [])
    
    def get_long_tail_keywords(self, base_topic: str) -> List[str]:
        """Gera palavras-chave de cauda longa para um tópico base"""
        modifiers = [
            "como fazer", "melhor", "dicas", "guia completo",
            "tutorial", "passo a passo", "para iniciantes",
            "comparação", "análise", "opinião", "reviews"
        ]
        
        long_tail = []
        for modifier in modifiers:
            long_tail.append(f"{modifier} {base_topic}")
            long_tail.append(f"{base_topic} {modifier}")
        
        return long_tail[:5]  # Retorna apenas os 5 melhores
