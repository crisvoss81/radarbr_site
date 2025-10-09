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
        
        # Tópicos com estrutura SEO otimizada
        topicos = [
            {
                "titulo": "Nova tecnologia revoluciona mercado brasileiro",
                "categoria": "Tecnologia",
                "dek": "Inovação tecnológica transforma cenário econômico nacional com oportunidades inéditas para empresas e consumidores brasileiros.",
                "conteudo": "Uma nova tecnologia está transformando o cenário econômico brasileiro, trazendo oportunidades inéditas para empresas e consumidores. Especialistas apontam que esta inovação pode gerar milhares de empregos nos próximos anos.\n\n### Impacto no Mercado Nacional\n\nA tecnologia emergente está revolucionando diversos setores da economia brasileira, desde a indústria até os serviços. Empresas de todos os portes estão se adaptando rapidamente às mudanças.\n\n### Perspectivas Futuras\n\nAnalistas projetam crescimento significativo nos próximos anos, com potencial para posicionar o Brasil como referência tecnológica na América Latina."
            },
            {
                "titulo": "Economia brasileira mostra sinais de recuperação",
                "categoria": "Economia",
                "dek": "Indicadores econômicos positivos sinalizam recuperação gradual da economia nacional com crescimento em setores estratégicos.",
                "conteudo": "Dados recentes indicam que a economia nacional está apresentando indicadores positivos, com crescimento em setores-chave. Analistas são otimistas quanto ao futuro econômico do país.\n\n### Principais Indicadores\n\nOs números mostram evolução positiva em áreas como produção industrial, consumo interno e investimentos privados.\n\n### Expectativas dos Especialistas\n\nEconomistas destacam a importância de manter políticas consistentes para sustentar o crescimento observado."
            },
            {
                "titulo": "Seleção brasileira se prepara para próximos jogos",
                "categoria": "Esportes",
                "dek": "Time nacional intensifica preparação para competições internacionais com foco em trabalho em equipe e dedicação dos atletas.",
                "conteudo": "A seleção nacional está intensificando os treinamentos para as próximas competições. O técnico destacou a importância do trabalho em equipe e da dedicação dos atletas.\n\n### Preparação Técnica\n\nA comissão técnica trabalha em estratégias específicas para cada adversário, aproveitando as características dos jogadores.\n\n### Expectativas da Torcida\n\nOs torcedores brasileiros aguardam com ansiedade os próximos jogos da seleção."
            },
            {
                "titulo": "Festival de cultura movimenta cidade brasileira",
                "categoria": "Cultura",
                "dek": "Evento cultural reúne artistas de todo o país promovendo diversidade e riqueza da cultura brasileira para milhares de visitantes.",
                "conteudo": "Um grande festival cultural está reunindo artistas de todo o país, promovendo a diversidade e a riqueza da cultura brasileira. O evento tem atraído milhares de visitantes.\n\n### Programação Diversificada\n\nO festival oferece uma ampla programação incluindo música, teatro, dança e artes visuais.\n\n### Impacto Cultural\n\nO evento contribui significativamente para a valorização e preservação da cultura nacional."
            },
            {
                "titulo": "Medidas políticas impactam população brasileira",
                "categoria": "Política",
                "dek": "Novas medidas governamentais anunciadas devem afetar diretamente a vida dos brasileiros com análises de especialistas sobre os impactos.",
                "conteudo": "Novas medidas governamentais foram anunciadas e devem afetar diretamente a vida dos brasileiros. Especialistas analisam os possíveis impactos dessas decisões.\n\n### Principais Mudanças\n\nAs medidas incluem alterações em áreas sensíveis como saúde, educação e previdência social.\n\n### Análise dos Especialistas\n\nEspecialistas em políticas públicas avaliam os possíveis efeitos das mudanças na sociedade brasileira."
            }
        ]
        
        criadas = 0
        num = options["num"]
        
        for i in range(num):
            topico_data = random.choice(topicos)
            
            # Título SEO-friendly (sem timestamp)
            titulo = topico_data['titulo']
            slug = slugify(titulo)[:180]
            
            # Verificar se já existe
            if Noticia.objects.filter(slug=slug).exists():
                print(f"AVISO Pulando: {titulo} (ja existe)")
                continue
            
            # Criar categoria específica se não existir
            cat_slug = slugify(topico_data['categoria'])[:140]
            categoria, created = Categoria.objects.get_or_create(
                slug=cat_slug,
                defaults={"nome": topico_data['categoria']}
            )
            
            if created:
                print(f"OK Categoria criada: {categoria.nome}")
            
            # Conteúdo SEO otimizado com estrutura adequada
            conteudo = f"""<p class="dek">{topico_data['dek']}</p>

{topico_data['conteudo']}

## Conclusão

Esta matéria foi desenvolvida com base em informações atualizadas e análises de especialistas da área. O RadarBR continua acompanhando os desdobramentos desta notícia.

Para mais informações sobre este e outros assuntos, acompanhe nossas atualizações diárias."""
            
            try:
                noticia = Noticia.objects.create(
                    titulo=titulo,
                    slug=slug,
                    conteudo=conteudo,
                    publicado_em=timezone.now(),
                    categoria=categoria,
                    fonte_url=f"seo-simples-{timezone.now().strftime('%Y%m%d-%H%M')}-{i}",
                    fonte_nome="RadarBR SEO",
                    status=1,
                    imagem_alt=f"Imagem relacionada a {topico_data['categoria'].lower()}"
                )
                
                # Buscar e adicionar imagem
                self._adicionar_imagem(noticia, topico_data['titulo'])
                
                criadas += 1
                print(f"OK Criado: {titulo} (Categoria: {categoria.nome})")
                
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
