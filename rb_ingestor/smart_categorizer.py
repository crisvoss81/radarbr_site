# rb_ingestor/smart_categorizer.py
"""
Sistema inteligente de categorização baseado no conteúdo gerado
"""
import re
from collections import defaultdict
from django.conf import settings

class SmartCategorizer:
    """Sistema inteligente de categorização baseado no conteúdo"""
    
    def __init__(self):
        # Dicionário semântico expandido para cada categoria
        self.category_patterns = {
            "política": {
                "keywords": [
                    "política", "governo", "eleições", "presidente", "lula", "bolsonaro", 
                    "congresso", "ministro", "democracia", "eleitoral", "partido", "candidato",
                    "votação", "urna", "eleitor", "mandato", "gestão", "administração",
                    "poder", "estado", "federal", "municipal", "estadual", "prefeito",
                    "governador", "senador", "deputado", "vereador", "câmara", "senado",
                    "anuncia", "anunciou", "declara", "declarou", "pacote"  # Ações políticas
                ],
                "context_patterns": [
                    r"governo\s+(federal|estadual|municipal)",
                    r"(eleições|votação)\s+(municipais|estaduais|federais)",
                    r"(presidente|governador|prefeito)\s+(da|do|de)",
                    r"(congresso|senado|câmara)\s+(nacional|federal)",
                    r"(partido|político)\s+(brasileiro|nacional)",
                    r"(democracia|democrático)\s+(brasileira|nacional)"
                ],
                "weight": 1.0
            },
            "economia": {
                "keywords": [
                    "economia", "mercado", "inflação", "dólar", "real", "investimento", 
                    "finanças", "banco", "crédito", "bolsa", "ações", "pib", "desemprego",
                    "crescimento", "recessão", "crise", "recuperação", "produtividade",
                    "exportação", "importação", "balança", "comercial", "fiscal",
                    "monetária", "política", "cambial", "taxa", "juros", "selic"
                ],
                "context_patterns": [
                    r"(economia|mercado)\s+(brasileira|nacional)",
                    r"(inflação|dólar|real)\s+(sobe|desce|estável)",
                    r"(pib|produto interno bruto)",
                    r"(bolsa|ações)\s+(de valores|brasileira)",
                    r"(banco central|bcb|selic)",
                    r"(crescimento|recessão)\s+(econômico|da economia)"
                ],
                "weight": 1.0
            },
            "esportes": {
                "keywords": [
                    "esportes", "futebol", "copa", "mundial", "brasileirão", "atletismo", 
                    "jogos", "competição", "campeonato", "jogador", "time", "clube",
                    "estádio", "torcida", "gol", "vitória", "derrota", "empate",
                    "técnico", "treinador", "atleta", "medalha", "olimpíada", "copa do mundo",
                    "marca", "goleia", "partida", "jogo", "memphis", "malta"  # Palavras específicas de futebol
                ],
                "context_patterns": [
                    r"(futebol|futebolista)\s+(brasileiro|nacional)",
                    r"(brasileirão|campeonato brasileiro)",
                    r"(copa do mundo|mundial)\s+(de futebol)",
                    r"(time|clube)\s+(brasileiro|de futebol)",
                    r"(jogador|atleta)\s+(brasileiro|profissional)",
                    r"(estádio|arena)\s+(brasileira|nacional)"
                ],
                "weight": 1.0
            },
            "saúde": {
                "keywords": [
                    "saúde", "medicina", "hospital", "vacina", "covid", "coronavírus", 
                    "tratamento", "médico", "doença", "epidemia", "pandemia", "sintomas",
                    "diagnóstico", "cura", "prevenção", "sistema", "público", "sus",
                    "enfermagem", "enfermeiro", "cirurgia", "medicamento", "farmacêutico"
                ],
                "context_patterns": [
                    r"(saúde|sistema de saúde)\s+(pública|brasileira)",
                    r"(hospital|unidade de saúde)\s+(público|municipal)",
                    r"(sus|sistema único de saúde)",
                    r"(vacina|vacinação)\s+(contra|para)",
                    r"(doença|epidemia)\s+(no brasil|brasileira)",
                    r"(médico|enfermeiro)\s+(brasileiro|do sus)"
                ],
                "weight": 1.0
            },
            "meio ambiente": {
                "keywords": [
                    "meio ambiente", "sustentabilidade", "natureza", "clima", "ecologia", 
                    "verde", "energia", "poluição", "desmatamento", "aquecimento", "global",
                    "floresta", "amazônia", "biodiversidade", "recursos", "naturais",
                    "conservação", "preservação", "ambiental", "carbono", "emissões",
                    "pescaria", "pesca", "traira", "peixe", "rio", "lago", "água", "aquático"
                ],
                "context_patterns": [
                    r"(meio ambiente|ambiental)\s+(brasileiro|nacional)",
                    r"(amazônia|floresta amazônica)",
                    r"(desmatamento|desflorestamento)\s+(na amazônia)",
                    r"(sustentabilidade|sustentável)\s+(brasileira)",
                    r"(energia|renovável)\s+(no brasil)",
                    r"(poluição|contaminação)\s+(ambiental|do ar)"
                ],
                "weight": 1.0
            },
            "tecnologia": {
                "keywords": [
                    "tecnologia", "digital", "ia", "inteligência artificial", "chatgpt", 
                    "app", "software", "blockchain", "crypto", "bitcoin", "startup", 
                    "inovação", "digital", "internet", "smartphone", "computador",
                    "programação", "desenvolvedor", "dados", "big data", "cloud", "nuvem",
                    "desenvolve", "desenvolveu", "criou", "criada", "algoritmo", "sistema"
                ],
                "context_patterns": [
                    r"(tecnologia|digital)\s+(brasileira|nacional)",
                    r"(startup|empresa de tecnologia)\s+(brasileira)",
                    r"(inteligência artificial|ia)\s+(no brasil)",
                    r"(app|aplicativo)\s+(brasileiro|nacional)",
                    r"(software|programa)\s+(brasileiro|desenvolvido)",
                    r"(inovação|inovador)\s+(tecnológica|digital)"
                ],
                "weight": 1.0  # Peso normal para tecnologia
            },
            "mundo": {
                "keywords": [
                    "china", "eua", "estados unidos", "europa", "internacional", "global", "mundial", 
                    "país", "nação", "estrangeiro", "guerra", "conflito", "onu", "oriente médio", "oriente medio",
                    "organização", "mundial", "tratado", "acordo", "internacional",
                    "exportação", "importação", "comércio", "exterior", "diplomacia",
                    "holanda", "holandês", "holandesa", "países baixos", "américa", "europa",
                    "frança", "alemão", "alemã", "italiano", "italiana", "espanhol", "espanhola",
                    "israel", "palestina", "gaza", "cisjordânia", "hamas", "hezbollah", "ucrânia", "russia"
                ],
                "context_patterns": [
                    r"(china|estados unidos|eua|israel|ucrânia|rússia|russia)\s+(.*)",
                    r"(europa|união europeia)\s+(.*)",
                    r"(guerra|conflito)\s+(internacional|mundial|israel|gaza|ucr[aâ]nia)",
                    r"(onu|organização das nações unidas)",
                    r"(comércio|relações)\s+(internacionais|exteriores)",
                    r"(acordo|tratado)\s+(internacional|mundial)"
                ],
                "weight": 1.4
            },
            "lazer": {
                "keywords": [
                    "lazer", "hobby", "hobbies", "entretenimento", "diversão", "recreação",
                    "pescaria", "pesca", "caça", "camping", "trilha", "escalada", "surf",
                    "natação", "ciclismo", "corrida", "caminhada", "viagem", "turismo",
                    "férias", "ferias", "descanso", "relaxamento", "praia", "montanha",
                    "traira", "peixe", "rio", "lago", "pesqueiro", "pesque-pague"
                ],
                "context_patterns": [
                    r"(pescaria|pesca)\s+(de|da|do)",
                    r"(hobby|hobbies)\s+(brasileiro|nacional)",
                    r"(lazer|entretenimento)\s+(no brasil)",
                    r"(férias|ferias)\s+(brasileiras|no brasil)"
                ],
                "weight": 1.0
            },
            "brasil": {
                "keywords": [
                    "brasil", "brasileiro", "brasileira", "nacional", "federal", 
                    "estadual", "municipal", "governo federal", "república", "federação",
                    "constituição", "democracia", "cidadão", "brasileiro", "sociedade"
                ],
                "context_patterns": [
                    r"(brasil|brasileiro)\s+(é|tem|possui)",
                    r"(governo federal|república federativa)",
                    r"(sociedade|população)\s+(brasileira)",
                    r"(cidadão|brasileiro)\s+(tem direito)",
                    r"(constituição|lei)\s+(brasileira|federal)",
                    r"(democracia|democrático)\s+(brasileira)"
                ],
                "weight": 0.3  # Peso muito reduzido para ser usado apenas como último fallback
            }
        }
    
    def categorize_content(self, title, content, topic=""):
        """
        Categoriza conteúdo baseado em análise inteligente do texto completo
        """
        # Combinar todo o texto para análise
        full_text = f"{title} {content} {topic}".lower()
        
        # Remover tags HTML para análise de texto limpo
        clean_text = re.sub(r'<[^>]+>', ' ', full_text)
        
        category_scores = defaultdict(float)
        
        # Analisar cada categoria
        for category, patterns in self.category_patterns.items():
            score = 0
            
            # 1. Pontuação por palavras-chave (peso 1.0)
            keyword_matches = 0
            for keyword in patterns["keywords"]:
                if keyword in clean_text:
                    keyword_matches += 1
                    # Dar mais peso para palavras mais específicas
                    if len(keyword.split()) > 1:  # Frases têm mais peso
                        score += 2.0
                    else:
                        score += 1.0
            
            # 2. Pontuação por padrões contextuais (peso 2.0)
            context_matches = 0
            for pattern in patterns["context_patterns"]:
                if re.search(pattern, clean_text, re.IGNORECASE):
                    context_matches += 1
                    score += 3.0  # Padrões contextuais têm muito mais peso
            
            # 3. Pontuação por densidade de palavras-chave
            if keyword_matches > 0:
                density_score = keyword_matches / len(patterns["keywords"])
                score += density_score * 5.0
            
            # 4. Aplicar peso da categoria
            score *= patterns["weight"]
            
            category_scores[category] = score
        
        # Encontrar categoria com maior pontuação
        if category_scores:
            # Regra: se mencionar países estrangeiros e não mencionar Brasil, favorecer "mundo"
            foreign_markers = ["israel", "gaza", "palestina", "ucrânia", "rússia", "china", "eua", "estados unidos", "europa"]
            mentions_foreign = any(m in clean_text for m in foreign_markers)
            mentions_brazil = ("brasil" in clean_text or "brasileir" in clean_text)

            if mentions_foreign and not mentions_brazil:
                category_scores["mundo"] *= 1.5

            best_category = max(category_scores.items(), key=lambda x: x[1])
            
            # Só retornar se a pontuação for significativa (> 2.0)
            if best_category[1] > 2.0:
                return best_category[0]
        
        # Fallback para "brasil" se nenhuma categoria tiver pontuação suficiente
        return "brasil"
    
    def get_category_confidence(self, title, content, topic=""):
        """
        Retorna a confiança da categorização (0.0 a 1.0)
        """
        full_text = f"{title} {content} {topic}".lower()
        clean_text = re.sub(r'<[^>]+>', ' ', full_text)
        
        category_scores = defaultdict(float)
        
        for category, patterns in self.category_patterns.items():
            score = 0
            
            for keyword in patterns["keywords"]:
                if keyword in clean_text:
                    if len(keyword.split()) > 1:
                        score += 2.0
                    else:
                        score += 1.0
            
            for pattern in patterns["context_patterns"]:
                if re.search(pattern, clean_text, re.IGNORECASE):
                    score += 3.0
            
            score *= patterns["weight"]
            category_scores[category] = score
        
        if category_scores:
            best_score = max(category_scores.values())
            total_score = sum(category_scores.values())
            
            if total_score > 0:
                return best_score / total_score
        
        return 0.0
