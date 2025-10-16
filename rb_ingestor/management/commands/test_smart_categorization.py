# rb_ingestor/management/commands/test_smart_categorization.py
"""
Comando para testar o sistema inteligente de categorização
"""
from django.core.management.base import BaseCommand
from rb_ingestor.smart_categorizer import SmartCategorizer

class Command(BaseCommand):
    help = "Testa o sistema inteligente de categorização"

    def handle(self, *args, **options):
        self.stdout.write("=== TESTE DO SISTEMA INTELIGENTE DE CATEGORIZAÇÃO ===")
        
        categorizer = SmartCategorizer()
        
        # Casos de teste
        test_cases = [
            {
                "title": "Lula anuncia novo pacote econômico para o Brasil",
                "content": "O presidente Lula anunciou hoje um novo pacote de medidas econômicas para estimular o crescimento do país. As medidas incluem redução de impostos e investimentos em infraestrutura.",
                "topic": "política econômica",
                "expected": "política"
            },
            {
                "title": "Dólar sobe 2% após decisão do Banco Central",
                "content": "A moeda americana registrou alta de 2% hoje após o Banco Central manter a taxa Selic. Economistas analisam o impacto na inflação e no mercado brasileiro.",
                "topic": "economia",
                "expected": "economia"
            },
            {
                "title": "Flamengo vence o Corinthians por 3x1 no Maracanã",
                "content": "O Flamengo venceu o Corinthians por 3x1 hoje no Maracanã. Gabriel Barbosa marcou dois gols e Pedro fechou a contagem. O time carioca segue na liderança do Brasileirão.",
                "topic": "futebol",
                "expected": "esportes"
            },
            {
                "title": "Nova vacina contra COVID-19 é aprovada pela Anvisa",
                "content": "A Anvisa aprovou hoje uma nova vacina contra COVID-19 para uso no Brasil. A vacina será distribuída pelo SUS e deve começar a ser aplicada em dezembro.",
                "topic": "saúde",
                "expected": "saúde"
            },
            {
                "title": "Startup brasileira desenvolve IA para diagnóstico médico",
                "content": "Uma startup brasileira desenvolveu uma inteligência artificial capaz de diagnosticar doenças com 95% de precisão. A tecnologia será integrada ao SUS.",
                "topic": "tecnologia",
                "expected": "tecnologia"
            },
            {
                "title": "Desmatamento na Amazônia aumenta 15% em 2024",
                "content": "O desmatamento na Amazônia aumentou 15% em 2024, segundo dados do INPE. Ambientalistas alertam para os riscos climáticos e pedem ações urgentes.",
                "topic": "meio ambiente",
                "expected": "meio ambiente"
            }
        ]
        
        self.stdout.write("\n🧪 EXECUTANDO TESTES:")
        
        correct_predictions = 0
        total_tests = len(test_cases)
        
        for i, test_case in enumerate(test_cases, 1):
            title = test_case["title"]
            content = test_case["content"]
            topic = test_case["topic"]
            expected = test_case["expected"]
            
            # Categorizar
            predicted = categorizer.categorize_content(title, content, topic)
            confidence = categorizer.get_category_confidence(title, content, topic)
            
            # Verificar se está correto
            is_correct = predicted == expected
            if is_correct:
                correct_predictions += 1
                status = "✅"
            else:
                status = "❌"
            
            self.stdout.write(f"\n{status} Teste {i}:")
            self.stdout.write(f"   Título: {title}")
            self.stdout.write(f"   Esperado: {expected}")
            self.stdout.write(f"   Predito: {predicted}")
            self.stdout.write(f"   Confiança: {confidence:.2f}")
        
        # Resultados
        accuracy = (correct_predictions / total_tests) * 100
        
        self.stdout.write(f"\n📊 RESULTADOS:")
        self.stdout.write(f"   Acertos: {correct_predictions}/{total_tests}")
        self.stdout.write(f"   Precisão: {accuracy:.1f}%")
        
        if accuracy >= 80:
            self.stdout.write("🎉 Excelente! Sistema funcionando muito bem!")
        elif accuracy >= 60:
            self.stdout.write("👍 Bom! Sistema funcionando bem.")
        else:
            self.stdout.write("⚠ Precisa melhorar! Verificar padrões.")
        
        self.stdout.write("\n=== FIM DOS TESTES ===")

