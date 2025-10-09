# rb_ingestor/management/commands/monitor_performance.py
"""
Sistema de monitoramento de performance da automação
Analisa dados e gera relatórios para otimização
"""
import os
import sys
import django
from django.core.management.base import BaseCommand
from django.apps import apps
from django.utils import timezone
from datetime import datetime, timedelta
import json

class Command(BaseCommand):
    help = "Monitora performance do sistema de automação"

    def add_arguments(self, parser):
        parser.add_argument("--period", choices=['1h', '6h', '24h', '7d'], default='24h',
                          help="Período de análise")
        parser.add_argument("--export", action="store_true", help="Exportar dados para JSON")

    def handle(self, *args, **options):
        Noticia = apps.get_model("rb_noticias", "Noticia")
        Categoria = apps.get_model("rb_noticias", "Categoria")
        
        self.stdout.write("=== MONITOR DE PERFORMANCE ===")
        
        # Determinar período
        period_map = {
            '1h': timedelta(hours=1),
            '6h': timedelta(hours=6),
            '24h': timedelta(days=1),
            '7d': timedelta(days=7)
        }
        
        period_delta = period_map[options["period"]]
        start_time = timezone.now() - period_delta
        
        # Análise de dados
        analysis = self._analyze_performance(start_time, Noticia, Categoria)
        
        # Exibir relatório
        self._display_report(analysis, options["period"])
        
        # Exportar se solicitado
        if options["export"]:
            self._export_data(analysis, options["period"])

    def _analyze_performance(self, start_time, Noticia, Categoria):
        """Analisa performance do sistema"""
        
        # Dados básicos
        total_news = Noticia.objects.count()
        period_news = Noticia.objects.filter(publicado_em__gte=start_time)
        period_count = period_news.count()
        
        # Análise por categoria
        category_stats = {}
        for news in period_news:
            cat_name = news.categoria.nome if news.categoria else "Sem categoria"
            if cat_name not in category_stats:
                category_stats[cat_name] = {"count": 0, "titles": []}
            category_stats[cat_name]["count"] += 1
            category_stats[cat_name]["titles"].append(news.titulo)
        
        # Análise por horário
        hour_stats = {}
        for news in period_news:
            hour = news.publicado_em.hour
            hour_stats[hour] = hour_stats.get(hour, 0) + 1
        
        # Análise por dia da semana
        weekday_stats = {}
        for news in period_news:
            weekday = news.publicado_em.weekday()
            weekday_names = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
            weekday_name = weekday_names[weekday]
            weekday_stats[weekday_name] = weekday_stats.get(weekday_name, 0) + 1
        
        # Análise de fontes
        source_stats = {}
        for news in period_news:
            source = news.fonte_nome or "Desconhecida"
            source_stats[source] = source_stats.get(source, 0) + 1
        
        # Calcular métricas
        avg_per_hour = period_count / (period_delta.total_seconds() / 3600) if period_delta.total_seconds() > 0 else 0
        
        return {
            "period": {
                "start": start_time,
                "end": timezone.now(),
                "duration": str(period_delta)
            },
            "metrics": {
                "total_news": total_news,
                "period_news": period_count,
                "avg_per_hour": round(avg_per_hour, 2)
            },
            "category_stats": category_stats,
            "hour_stats": hour_stats,
            "weekday_stats": weekday_stats,
            "source_stats": source_stats
        }

    def _display_report(self, analysis, period):
        """Exibe relatório de performance"""
        
        self.stdout.write(f"\n📊 RELATÓRIO DE PERFORMANCE - {period.upper()}")
        self.stdout.write(f"Período: {analysis['period']['start'].strftime('%d/%m %H:%M')} até {analysis['period']['end'].strftime('%d/%m %H:%M')}")
        
        # Métricas principais
        metrics = analysis["metrics"]
        self.stdout.write(f"\n📈 MÉTRICAS PRINCIPAIS:")
        self.stdout.write(f"Total de notícias: {metrics['total_news']}")
        self.stdout.write(f"Notícias no período: {metrics['period_news']}")
        self.stdout.write(f"Média por hora: {metrics['avg_per_hour']}")
        
        # Top categorias
        if analysis["category_stats"]:
            self.stdout.write(f"\n🏆 TOP CATEGORIAS:")
            sorted_cats = sorted(analysis["category_stats"].items(), key=lambda x: x[1]["count"], reverse=True)
            for cat, data in sorted_cats[:5]:
                self.stdout.write(f"  {cat}: {data['count']} notícias")
        
        # Melhores horários
        if analysis["hour_stats"]:
            self.stdout.write(f"\n⏰ MELHORES HORÁRIOS:")
            sorted_hours = sorted(analysis["hour_stats"].items(), key=lambda x: x[1], reverse=True)
            for hour, count in sorted_hours[:5]:
                self.stdout.write(f"  {hour:02d}h: {count} notícias")
        
        # Performance por dia da semana
        if analysis["weekday_stats"]:
            self.stdout.write(f"\n📅 PERFORMANCE POR DIA:")
            sorted_weekdays = sorted(analysis["weekday_stats"].items(), key=lambda x: x[1], reverse=True)
            for day, count in sorted_weekdays:
                self.stdout.write(f"  {day}: {count} notícias")
        
        # Fontes mais ativas
        if analysis["source_stats"]:
            self.stdout.write(f"\n🔗 FONTES MAIS ATIVAS:")
            sorted_sources = sorted(analysis["source_stats"].items(), key=lambda x: x[1], reverse=True)
            for source, count in sorted_sources[:5]:
                self.stdout.write(f"  {source}: {count} notícias")
        
        # Recomendações
        self._generate_recommendations(analysis)

    def _generate_recommendations(self, analysis):
        """Gera recomendações baseadas na análise"""
        
        self.stdout.write(f"\n💡 RECOMENDAÇÕES:")
        
        # Recomendação de categoria
        if analysis["category_stats"]:
            best_category = max(analysis["category_stats"].items(), key=lambda x: x[1]["count"])
            self.stdout.write(f"✅ Focar mais em: {best_category[0]} (melhor performance)")
        
        # Recomendação de horário
        if analysis["hour_stats"]:
            best_hours = sorted(analysis["hour_stats"].items(), key=lambda x: x[1], reverse=True)[:3]
            hours_str = ", ".join([f"{h[0]:02d}h" for h in best_hours])
            self.stdout.write(f"✅ Melhores horários para publicação: {hours_str}")
        
        # Recomendação de volume
        avg_per_hour = analysis["metrics"]["avg_per_hour"]
        if avg_per_hour < 0.5:
            self.stdout.write("⚠️ Volume baixo - considerar aumentar frequência")
        elif avg_per_hour > 2:
            self.stdout.write("⚠️ Volume alto - considerar otimizar qualidade")
        else:
            self.stdout.write("✅ Volume adequado - manter estratégia atual")
        
        # Recomendação de diversificação
        if len(analysis["category_stats"]) < 3:
            self.stdout.write("⚠️ Pouca diversificação - expandir categorias")
        else:
            self.stdout.write("✅ Boa diversificação de categorias")

    def _export_data(self, analysis, period):
        """Exporta dados para arquivo JSON"""
        
        filename = f"performance_report_{period}_{timezone.now().strftime('%Y%m%d_%H%M')}.json"
        
        # Preparar dados para exportação
        export_data = {
            "timestamp": timezone.now().isoformat(),
            "period": period,
            "analysis": analysis
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
            
            self.stdout.write(f"\n📁 Dados exportados para: {filename}")
            
        except Exception as e:
            self.stdout.write(f"\n❌ Erro ao exportar dados: {e}")
