# rb_ingestor/writing_styles.py
"""
Sistema de estilos de escrita para geração de artigos
"""
import random
from typing import Dict, List

class WritingStyleManager:
    """Gerencia diferentes estilos de escrita para artigos"""
    
    def __init__(self):
        self.styles = {
            'jornalistico': {
                'name': 'Jornalístico Clássico',
                'description': 'Tom formal e imparcial, linguagem direta e objetiva',
                'characteristics': [
                    'Use linguagem formal e respeitosa',
                    'Mantenha tom imparcial e objetivo',
                    'Foque em fatos e dados concretos',
                    'Estrutura tradicional de notícia',
                    'Evite opiniões pessoais',
                    'Use terceira pessoa'
                ],
                'tone': 'formal',
                'perspective': 'third_person'
            },
            'natural': {
                'name': 'Natural/Conversacional',
                'description': 'Tom amigável e acessível, como uma conversa',
                'characteristics': [
                    'Use linguagem amigável e acessível',
                    'Explique conceitos complexos de forma simples',
                    'Como se estivesse conversando com o leitor',
                    'Use exemplos práticos e cotidianos',
                    'Mantenha tom respeitoso mas próximo',
                    'Evite jargões técnicos desnecessários'
                ],
                'tone': 'friendly',
                'perspective': 'second_person'
            },
            'tecnico': {
                'name': 'Técnico/Analítico',
                'description': 'Linguagem especializada com análise profunda',
                'characteristics': [
                    'Use terminologia técnica quando apropriado',
                    'Faça análises detalhadas e profundas',
                    'Foque em dados, estatísticas e evidências',
                    'Use linguagem mais formal e precisa',
                    'Inclua contexto histórico e comparativo',
                    'Mantenha rigor científico'
                ],
                'tone': 'analytical',
                'perspective': 'third_person'
            },
            'sarcastico': {
                'name': 'Sarcástico/Inteligente',
                'description': 'Tom crítico mas inteligente, com ironia sutil',
                'characteristics': [
                    'Use ironia sutil sem alterar os fatos',
                    'Faça comentários perspicazes e inteligentes',
                    'Mantenha seriedade quando necessário',
                    'Use humor inteligente, não ofensivo',
                    'Seja crítico mas construtivo',
                    'Nunca distorça informações importantes'
                ],
                'tone': 'critical',
                'perspective': 'third_person'
            },
            'explicativo': {
                'name': 'Explicativo/Didático',
                'description': 'Foco em ensinar e explicar conceitos',
                'characteristics': [
                    'Explique passo a passo os conceitos',
                    'Use linguagem educativa e clara',
                    'Quebre conceitos complexos em partes simples',
                    'Use analogias e exemplos práticos',
                    'Mantenha tom paciente e didático',
                    'Foque no aprendizado do leitor'
                ],
                'tone': 'educational',
                'perspective': 'second_person'
            },
            'dinamico': {
                'name': 'Dinâmico/Moderno',
                'description': 'Linguagem jovem e atual, ritmo acelerado',
                'characteristics': [
                    'Use linguagem contemporânea e dinâmica',
                    'Mantenha ritmo acelerado e envolvente',
                    'Use expressões modernas quando apropriado',
                    'Seja energético mas informativo',
                    'Conecte com audiência jovem',
                    'Mantenha relevância atual'
                ],
                'tone': 'energetic',
                'perspective': 'second_person'
            }
        }
    
    def get_random_style(self) -> str:
        """Retorna um estilo aleatório"""
        return random.choice(list(self.styles.keys()))
    
    def get_style_info(self, style_key: str) -> Dict:
        """Retorna informações sobre um estilo específico"""
        return self.styles.get(style_key, {})
    
    def get_all_styles(self) -> List[str]:
        """Retorna lista de todos os estilos disponíveis"""
        return list(self.styles.keys())
    
    def create_style_prompt(self, style_key: str, topic: str, min_words: int) -> str:
        """Cria prompt específico para o estilo escolhido"""
        style = self.styles.get(style_key, self.styles['jornalistico'])
        
        prompt = f"""
ESTILO DE ESCRITA: {style['name']}
DESCRIÇÃO: {style['description']}

CARACTERÍSTICAS OBRIGATÓRIAS:
"""
        
        for char in style['characteristics']:
            prompt += f"• {char}\n"
        
        prompt += f"""
INSTRUÇÕES ESPECÍFICAS:
- Tópico: {topic}
- Palavras mínimas: {min_words}
- Tom: {style['tone']}
- Perspectiva: {style['perspective']}
- NÃO altere fatos ou informações importantes
- Mantenha precisão jornalística
- Use exatamente 2 subtítulos H2
- Conteúdo em português brasileiro

IMPORTANTE: Adapte o estilo mas mantenha a veracidade dos fatos!
"""
        
        return prompt

# Instância global para uso nos comandos
writing_style_manager = WritingStyleManager()
