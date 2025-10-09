# rb_ingestor/management/commands/noticias_simples.py
"""
Comando ultra-simples para gerar notícias no Render
Sem dependências externas, apenas Django puro
"""
from django.core.management.base import BaseCommand
from django.apps import apps
from django.utils import timezone
from slugify import slugify
import random

class Command(BaseCommand):
    help = "Gerador ultra-simples de notícias"

    def add_arguments(self, parser):
        parser.add_argument("--num", type=int, default=3, help="Número de notícias")

    def handle(self, *args, **options):
        Noticia = apps.get_model("rb_noticias", "Noticia")
        Categoria = apps.get_model("rb_noticias", "Categoria")
        
        print("=== GERADOR ULTRA-SIMPLES ===")
        
        # Criar categoria se não existir
        cat, created = Categoria.objects.get_or_create(
            slug="geral",
            defaults={"nome": "Geral"}
        )
        
        if created:
            print(f"OK Categoria criada: {cat.nome}")
        
        # Tópicos com títulos mais realistas
        topicos = [
            {
                "titulo": "Nova tecnologia revoluciona mercado brasileiro",
                "conteudo": "Uma nova tecnologia está transformando o cenário econômico brasileiro, trazendo oportunidades inéditas para empresas e consumidores. Especialistas apontam que esta inovação pode gerar milhares de empregos nos próximos anos."
            },
            {
                "titulo": "Economia brasileira mostra sinais de recuperação",
                "conteudo": "Dados recentes indicam que a economia nacional está apresentando indicadores positivos, com crescimento em setores-chave. Analistas são otimistas quanto ao futuro econômico do país."
            },
            {
                "titulo": "Seleção brasileira se prepara para próximos jogos",
                "conteudo": "A seleção nacional está intensificando os treinamentos para as próximas competições. O técnico destacou a importância do trabalho em equipe e da dedicação dos atletas."
            },
            {
                "titulo": "Festival de cultura movimenta cidade brasileira",
                "conteudo": "Um grande festival cultural está reunindo artistas de todo o país, promovendo a diversidade e a riqueza da cultura brasileira. O evento tem atraído milhares de visitantes."
            },
            {
                "titulo": "Medidas políticas impactam população brasileira",
                "conteudo": "Novas medidas governamentais foram anunciadas e devem afetar diretamente a vida dos brasileiros. Especialistas analisam os possíveis impactos dessas decisões."
            },
            {
                "titulo": "Projetos ambientais ganham destaque no Brasil",
                "conteudo": "Iniciativas de preservação ambiental estão sendo implementadas em diversas regiões do país, demonstrando o compromisso com a sustentabilidade e o futuro do planeta."
            },
            {
                "titulo": "Educação brasileira recebe novos investimentos",
                "conteudo": "Recursos adicionais foram destinados para melhorar a qualidade da educação nacional, com foco em infraestrutura, capacitação de professores e tecnologia educacional."
            },
            {
                "titulo": "Sistema de saúde brasileiro implementa melhorias",
                "conteudo": "Novas tecnologias e protocolos estão sendo implementados no sistema de saúde público, visando melhorar o atendimento e a qualidade dos serviços oferecidos à população."
            },
            {
                "titulo": "Inovação tecnológica brasileira ganha reconhecimento",
                "conteudo": "Startups brasileiras estão desenvolvendo soluções inovadoras que chamam atenção internacionalmente, colocando o país em destaque no cenário tecnológico global."
            },
            {
                "titulo": "Turismo brasileiro registra crescimento significativo",
                "conteudo": "O setor turístico nacional está apresentando números positivos, com aumento no número de visitantes e receita. Destinos brasileiros estão sendo cada vez mais procurados."
            }
        ]
        
        criadas = 0
        num = options["num"]
        
        for i in range(num):
            topico_data = random.choice(topicos)
            timestamp = timezone.now().strftime('%d/%m %H:%M')
            titulo = f"{topico_data['titulo']} - {timestamp}"
            slug = slugify(titulo)[:180]
            
            # Verificar se já existe
            if Noticia.objects.filter(slug=slug).exists():
                print(f"AVISO Pulando: {titulo} (ja existe)")
                continue
            
            # Conteúdo em Markdown (formato correto para o filtro render_markdown)
            conteudo = f"""## {topico_data['titulo']}

{topico_data['conteudo']}

Esta matéria foi desenvolvida com base em informações atualizadas e análises de especialistas da área. O RadarBR continua acompanhando os desdobramentos desta notícia.

Para mais informações sobre este e outros assuntos, acompanhe nossas atualizações diárias.

*Publicado pelo RadarBR em {timestamp}*"""
            
            try:
                noticia = Noticia.objects.create(
                    titulo=titulo,
                    slug=slug,
                    conteudo=conteudo,
                    publicado_em=timezone.now(),
                    categoria=cat,
                    fonte_url=f"simples-{timezone.now().strftime('%Y%m%d-%H%M')}-{i}",
                    fonte_nome="RadarBR Simples",
                    status=1
                )
                
                # Buscar e adicionar imagem
                self._adicionar_imagem(noticia, topico_data['titulo'])
                
                criadas += 1
                print(f"OK Criado: {titulo}")
                
            except Exception as e:
                print(f"ERRO: {e}")
        
        print(f"\nCONCLUIDO: {criadas} noticias criadas")
        print(f"Total no sistema: {Noticia.objects.count()}")
    
    def _adicionar_imagem(self, noticia, titulo):
        """Busca e adiciona imagem à notícia"""
        try:
            from rb_ingestor.images_free import pick_image
            
            # Extrair palavra-chave do título para busca
            palavras_chave = titulo.lower().split()
            # Remover palavras comuns e pegar as mais relevantes
            palavras_relevantes = [p for p in palavras_chave if len(p) > 3 and p not in ['nova', 'brasileiro', 'brasileira', 'mercado', 'mostra', 'ganha', 'recebe', 'implementa', 'registra']]
            
            if palavras_relevantes:
                topico_busca = palavras_relevantes[0]  # Usar a primeira palavra relevante
            else:
                topico_busca = "tecnologia"  # Fallback
            
            # Buscar imagem gratuita
            image_info = pick_image(topico_busca)
            
            if image_info and image_info.get("url"):
                # Salvar URL da imagem diretamente
                noticia.imagem = image_info["url"]
                noticia.imagem_alt = f"Imagem relacionada a {topico_busca}"
                noticia.imagem_credito = image_info.get("credito", "Imagem gratuita")
                noticia.imagem_licenca = image_info.get("licenca", "CC")
                noticia.imagem_fonte_url = image_info.get("fonte_url", image_info["url"])
                noticia.save()
                
                print(f"OK Imagem adicionada: {topico_busca}")
            else:
                print(f"AVISO Nenhuma imagem encontrada para: {topico_busca}")
                
        except Exception as e:
            print(f"AVISO Erro ao buscar imagem para {titulo}: {e}")
