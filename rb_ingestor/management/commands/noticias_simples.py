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
            
            # Conteúdo SEO otimizado com tamanho padrão (700-1000 palavras)
            conteudo = f"""<p class="dek">{topico_data['dek']}</p>

{topico_data['conteudo']}

## Análise Detalhada

Os especialistas destacam que este tema tem ganhado cada vez mais relevância no cenário nacional. As mudanças observadas nos últimos meses indicam uma tendência consistente que merece atenção especial. Esta evolução tem sido acompanhada de perto por analistas e pesquisadores que estudam o impacto dessas transformações na sociedade brasileira.

### Impacto na Sociedade Brasileira

A população brasileira tem sentido diretamente os efeitos dessas transformações. Desde as grandes metrópoles até as cidades do interior, é possível observar mudanças significativas que afetam o dia a dia das pessoas. Estas alterações têm sido recebidas de forma positiva pela maioria da população, que vê nas mudanças uma oportunidade de melhoria na qualidade de vida.

### Perspectivas para o Futuro

As projeções indicam que esta tendência deve se manter nos próximos anos, com possíveis desenvolvimentos que podem trazer benefícios adicionais para o país. Os analistas são cautelosamente otimistas quanto ao futuro, destacando que o Brasil tem todas as condições necessárias para se consolidar como uma referência na área.

## Dados e Estatísticas

Os números mais recentes mostram uma evolução positiva em diversos indicadores relacionados ao tema. Esta melhoria tem sido observada de forma consistente ao longo dos últimos trimestres, demonstrando que não se trata de uma situação temporária, mas sim de uma tendência estrutural que deve perdurar.

### Principais Indicadores

- Crescimento sustentável nos principais setores relacionados ao tema
- Melhoria significativa nos indicadores de qualidade e eficiência
- Aumento consistente da confiança dos investidores nacionais e internacionais
- Fortalecimento das instituições relacionadas ao setor
- Crescimento do número de empresas que atuam na área
- Aumento da demanda por profissionais especializados

### Comparação Internacional

Quando comparado com outros países da região, o Brasil tem se destacado positivamente. Esta posição de destaque tem sido reconhecida por organismos internacionais especializados, que destacam a qualidade das iniciativas implementadas no país. O Brasil tem conseguido superar expectativas e se posicionar como um exemplo a ser seguido por outras nações.

## Impacto Econômico

O impacto econômico dessas mudanças tem sido significativo, com aumento na geração de empregos e crescimento do PIB em setores relacionados. As empresas que investiram na área têm registrado resultados positivos, o que tem incentivado novos investimentos e parcerias estratégicas.

### Geração de Empregos

O setor tem sido responsável pela criação de milhares de novos postos de trabalho em todo o país. Profissionais de diversas áreas têm encontrado oportunidades de crescimento e desenvolvimento profissional, contribuindo para a redução do desemprego e melhoria da qualidade de vida das famílias brasileiras.

### Investimentos e Parcerias

O aumento da confiança dos investidores tem resultado em novos aportes financeiros e parcerias estratégicas entre empresas nacionais e internacionais. Estas parcerias têm contribuído para o desenvolvimento tecnológico e a modernização dos processos produtivos.

## Perguntas Frequentes

### Como isso afeta o brasileiro comum?

O impacto na vida das pessoas é direto e positivo. As mudanças têm trazido benefícios concretos que podem ser observados no dia a dia da população, incluindo melhorias na qualidade dos serviços, redução de custos e aumento da eficiência em diversos setores.

### O que esperar nos próximos meses?

As projeções indicam continuidade da tendência positiva, com possíveis desenvolvimentos adicionais que podem trazer ainda mais benefícios. Os especialistas esperam que novos avanços sejam anunciados nos próximos meses, consolidando ainda mais a posição do Brasil na área.

### Existem riscos envolvidos?

Como em qualquer processo de transformação, existem desafios a serem enfrentados, mas os especialistas consideram que os benefícios superam significativamente os riscos. O país tem demonstrado capacidade de adaptação e superação dos obstáculos encontrados.

### Como o governo tem apoiado essas iniciativas?

O governo federal tem implementado políticas públicas que incentivam o desenvolvimento da área, incluindo programas de financiamento, redução de impostos e facilitação de processos burocráticos. Estas medidas têm contribuído para acelerar o crescimento do setor.

## Conclusão

Esta matéria foi desenvolvida com base em informações atualizadas e análises de especialistas da área. O RadarBR continua acompanhando os desdobramentos desta notícia e manterá os leitores informados sobre novos desenvolvimentos.

O cenário atual é promissor e indica que o Brasil está no caminho certo para se consolidar como uma referência na área. A continuidade das políticas públicas e o engajamento do setor privado serão fundamentais para manter o ritmo de crescimento observado.

Para mais informações sobre este e outros assuntos relevantes, acompanhe nossas atualizações diárias e mantenha-se sempre bem informado sobre os temas que mais importam para o Brasil."""
            
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
