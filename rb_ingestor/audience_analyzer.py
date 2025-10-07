# rb_ingestor/audience_analyzer.py
"""
Sistema de análise de audiência para otimizar conteúdo
"""
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count, Q
from django.apps import apps

class AudienceAnalyzer:
    def __init__(self):
        self.Noticia = apps.get_model("rb_noticias", "Noticia")
        self.Categoria = apps.get_model("rb_noticias", "Categoria")
    
    def analyze_performance(self, days: int = 30) -> Dict:
        """Analisa performance das notícias dos últimos dias"""
        start_date = timezone.now() - timedelta(days=days)
        
        # Análise por categoria
        category_performance = self.Noticia.objects.filter(
            publicado_em__gte=start_date
        ).values('categoria__nome').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Análise por palavras-chave nos títulos
        all_titles = self.Noticia.objects.filter(
            publicado_em__gte=start_date
        ).values_list('titulo', flat=True)
        
        keyword_analysis = self._analyze_keywords(all_titles)
        
        # Análise de horários de publicação
        time_analysis = self._analyze_publishing_times(start_date)
        
        return {
            "category_performance": list(category_performance),
            "keyword_analysis": keyword_analysis,
            "time_analysis": time_analysis,
            "total_articles": len(all_titles)
        }
    
    def _analyze_keywords(self, titles: List[str]) -> Dict:
        """Analisa palavras-chave mais frequentes nos títulos"""
        word_count = {}
        
        # Palavras-chave de alto engajamento
        high_engagement_words = [
            "como", "melhor", "dicas", "guia", "tutorial",
            "comparação", "análise", "opinião", "reviews",
            "passo a passo", "para iniciantes", "completo"
        ]
        
        for title in titles:
            words = title.lower().split()
            for word in words:
                # Limpar pontuação
                clean_word = ''.join(c for c in word if c.isalnum())
                if len(clean_word) > 3:  # Ignorar palavras muito curtas
                    word_count[clean_word] = word_count.get(clean_word, 0) + 1
        
        # Ordenar por frequência
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
        
        # Identificar palavras de alto engajamento
        high_engagement_found = []
        for word, count in sorted_words[:20]:
            if word in high_engagement_words:
                high_engagement_found.append({"word": word, "count": count})
        
        return {
            "top_keywords": sorted_words[:10],
            "high_engagement_words": high_engagement_found
        }
    
    def _analyze_publishing_times(self, start_date) -> Dict:
        """Analisa melhores horários para publicação"""
        articles_by_hour = {}
        
        articles = self.Noticia.objects.filter(
            publicado_em__gte=start_date
        ).values_list('publicado_em', flat=True)
        
        for published_time in articles:
            hour = published_time.hour
            articles_by_hour[hour] = articles_by_hour.get(hour, 0) + 1
        
        # Ordenar por frequência
        sorted_hours = sorted(articles_by_hour.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "best_hours": sorted_hours[:5],
            "hourly_distribution": articles_by_hour
        }
    
    def get_audience_insights(self) -> Dict:
        """Retorna insights sobre a audiência baseados nos dados"""
        performance = self.analyze_performance()
        
        insights = {
            "top_categories": [cat["categoria__nome"] for cat in performance["category_performance"][:3]],
            "trending_keywords": [kw[0] for kw in performance["keyword_analysis"]["top_keywords"][:5]],
            "best_publishing_hours": [hour[0] for hour in performance["time_analysis"]["best_hours"][:3]],
            "recommendations": self._generate_recommendations(performance)
        }
        
        return insights
    
    def _generate_recommendations(self, performance: Dict) -> List[str]:
        """Gera recomendações baseadas na análise de performance"""
        recommendations = []
        
        # Recomendações baseadas em categorias
        top_categories = performance["category_performance"][:3]
        if top_categories:
            recommendations.append(
                f"Foque mais em conteúdo de '{top_categories[0]['categoria__nome']}' "
                f"(categoria com melhor performance)"
            )
        
        # Recomendações baseadas em palavras-chave
        high_engagement = performance["keyword_analysis"]["high_engagement_words"]
        if high_engagement:
            recommendations.append(
                f"Use mais palavras-chave como '{high_engagement[0]['word']}' "
                f"nos títulos para aumentar engajamento"
            )
        
        # Recomendações baseadas em horários
        best_hours = performance["time_analysis"]["best_hours"][:3]
        if best_hours:
            recommendations.append(
                f"Publique mais conteúdo entre {best_hours[0][0]}:00h e {best_hours[-1][0]}:00h "
                f"(horários com melhor performance)"
            )
        
        return recommendations
    
    def predict_topic_success(self, topic: str) -> Dict:
        """Prediz o sucesso potencial de um tópico"""
        # Análise baseada em palavras-chave históricas
        performance = self.analyze_performance()
        
        topic_words = topic.lower().split()
        success_score = 0
        
        # Verificar se contém palavras-chave de alto engajamento
        high_engagement_words = [
            word["word"] for word in performance["keyword_analysis"]["high_engagement_words"]
        ]
        
        for word in topic_words:
            if word in high_engagement_words:
                success_score += 2
            elif word in [kw[0] for kw in performance["keyword_analysis"]["top_keywords"]]:
                success_score += 1
        
        # Análise de categoria
        category_score = 0
        for cat in performance["category_performance"]:
            if cat["categoria__nome"].lower() in topic.lower():
                category_score = cat["count"]
                break
        
        total_score = success_score + (category_score * 0.1)
        
        return {
            "topic": topic,
            "success_score": min(total_score, 10),  # Máximo 10
            "predicted_performance": "high" if total_score > 6 else "medium" if total_score > 3 else "low",
            "recommendations": self._get_topic_recommendations(topic, total_score)
        }
    
    def _get_topic_recommendations(self, topic: str, score: float) -> List[str]:
        """Gera recomendações específicas para um tópico"""
        recommendations = []
        
        if score < 3:
            recommendations.append("Considere adicionar palavras-chave de alto engajamento ao título")
            recommendations.append("Verifique se o tópico está alinhado com as categorias de melhor performance")
        
        if score > 6:
            recommendations.append("Este tópico tem alto potencial de sucesso")
            recommendations.append("Considere criar conteúdo relacionado para maximizar o alcance")
        
        return recommendations
