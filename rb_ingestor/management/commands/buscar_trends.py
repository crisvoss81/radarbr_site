# rb_ingestor/management/commands/buscar_trends.py

import openai
import requests
import json
from pexels_api import API as PexelsAPI
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from django.core.files.base import ContentFile
from gnews import GNews
from dateutil.parser import parse
from rb_noticias.models import Noticia, Categoria
import re

def _salvar_imagem_de_url(noticia, url_imagem, nome_arquivo, credito_nome, credito_url=None):
    try:
        response_img = requests.get(url_imagem, timeout=15)
        if response_img.status_code == 200:
            noticia.imagem.save(nome_arquivo, ContentFile(response_img.content), save=False)
            noticia.imagem_credito = credito_nome
            if credito_url:
                noticia.imagem_fonte_url = credito_url
            return True
    except requests.exceptions.RequestException as e:
        print(f"Erro de download: {e}")
    return False

def buscar_imagem_pexels(noticia, termo_busca, api_key):
    print(f"  -> Buscando no Pexels com termo: '{termo_busca}'...")
    try:
        api = PexelsAPI(api_key)
        search_results = api.search(termo_busca, page=1, results_per_page=1)
        if search_results and search_results['photos']:
            foto_data = search_results['photos'][0]
            if _salvar_imagem_de_url(noticia, foto_data['src']['original'], f"{noticia.slug}.jpg", foto_data['photographer'], foto_data['photographer_url']):
                print(f'     -> Imagem encontrada em Pexels.')
                return True
        print('     -> Nenhuma imagem encontrada no Pexels.')
    except Exception as e:
        print(f'     -> Falha ao buscar no Pexels: {e}')
    return False

def buscar_imagem_unsplash(noticia, termo_busca, api_key):
    print(f"  -> Buscando no Unsplash com termo: '{termo_busca}'...")
    try:
        headers = {"Authorization": f"Client-ID {api_key}"}
        params = {"query": termo_busca, "per_page": 1, "lang": "pt"}
        response = requests.get("https://api.unsplash.com/search/photos", headers=headers, params=params, timeout=10)
        if response.status_code == 200 and response.json()['results']:
            resultado = response.json()['results'][0]
            if _salvar_imagem_de_url(noticia, resultado['urls']['regular'], f"{noticia.slug}.jpg", resultado['user']['name'], resultado['user']['links']['html']):
                print(f"     -> Imagem encontrada em Unsplash.")
                requests.get(resultado['links']['download_location'], headers=headers, timeout=5)
                return True
        print('     -> Nenhuma imagem encontrada no Unsplash.')
    except Exception as e:
        print(f'     -> Falha ao buscar no Unsplash: {e}')
    return False

def buscar_imagem_pixabay(noticia, termo_busca, api_key):
    print(f"  -> Buscando no Pixabay com termo: '{termo_busca}'...")
    try:
        params = {"key": api_key, "q": termo_busca, "per_page": 3, "lang": "pt", "safesearch": "true"}
        response = requests.get("https://pixabay.com/api/", params=params, timeout=10)
        if response.status_code == 200 and response.json()['hits']:
            resultado = response.json()['hits'][0]
            if _salvar_imagem_de_url(noticia, resultado['largeImageURL'], f"{noticia.slug}.jpg", resultado['user'], resultado['pageURL']):
                print(f"     -> Imagem encontrada em Pixabay.")
                return True
        print('     -> Nenhuma imagem encontrada no Pixabay.')
    except Exception as e:
        print(f'     -> Falha ao buscar no Pixabay: {e}')
    return False
    
def gerar_imagem_dalle(noticia, termo_busca, api_key):
    print(f"  -> Gerando imagem com DALL-E usando termo: '{termo_busca}'...")
    try:
        openai.api_key = api_key
        prompt_imagem = f"Uma foto jornalística de alta qualidade representando a seguinte notícia: '{termo_busca}'. Sem texto na imagem."
        response_dalle = openai.images.generate(model="dall-e-3", prompt=prompt_imagem, n=1, size="1024x1024", quality="standard")
        url_imagem = response_dalle.data[0].url
        if _salvar_imagem_de_url(noticia, url_imagem, f"{noticia.slug}.jpg", "Imagem gerada por IA (DALL-E 3)"):
            print('     -> Imagem gerada com DALL-E.')
            return True
    except Exception as e:
        print(f'     -> Falha ao gerar imagem com DALL-E: {e}')
    return False

class Command(BaseCommand):
    help = 'Busca notícias, gera conteúdo, imagens, classifica categorias e as publica.'

    def handle(self, *args, **options):
        try:
            openai_key = settings.OPENAI_API_KEY; pexels_key = settings.PEXELS_API_KEY
            unsplash_key = settings.UNSPLASH_API_KEY; pixabay_key = settings.PIXABAY_API_KEY
        except AttributeError as e:
            raise CommandError(f"A chave {e.name} não foi configurada no seu settings.py")

        self.stdout.write(self.style.NOTICE('Buscando categorias do banco de dados...'))
        lista_de_categorias = list(Categoria.objects.values_list('nome', flat=True))
        if not lista_de_categorias:
            raise CommandError("Nenhuma categoria encontrada. Cadastre algumas no Admin do Django.")
        lista_de_categorias_string = ", ".join(lista_de_categorias)
        self.stdout.write(f"Categorias encontradas: {lista_de_categorias_string}")

        self.stdout.write(self.style.NOTICE('Buscando notícias no Google News...'))
        gnews = GNews(language='pt', country='BR', period='1d')
        top_news = gnews.get_top_news()
        if not top_news: self.stdout.write(self.style.WARNING('Nenhuma notícia nova encontrada.')); return
        self.stdout.write(self.style.SUCCESS(f'Encontradas {len(top_news)} notícias. Processando...'))

        novas_noticias_processadas = 0
        for article in top_news:
            url_noticia = article['url']
            if Noticia.objects.filter(fonte_url=url_noticia).exists(): continue

            titulo_bruto = article['title']
            partes = titulo_bruto.rsplit(' - ', 1)
            titulo = partes[0].strip() if len(partes) == 2 else titulo_bruto
            if not titulo: self.stdout.write(self.style.WARNING(f'     -> Título inválido, pulando: "{titulo_bruto}"')); continue
            
            slug_base = slugify(titulo); slug_unico = slug_base; sufixo = 1
            while Noticia.objects.filter(slug=slug_unico).exists(): slug_unico = f"{slug_base}-{sufixo}"; sufixo += 1
            
            noticia = Noticia.objects.create(
                titulo=titulo, slug=slug_unico, publicado_em=parse(article['published date']),
                fonte_nome=article['publisher']['title'], fonte_url=url_noticia
            )
            self.stdout.write(f'\n-> Notícia base salva: "{titulo}"')

            try:
                self.stdout.write('  -> Gerando conteúdo e categoria com IA...')
                prompt_texto = f"""
                Sobre o tópico de notícia: '{noticia.titulo}', e dadas as seguintes categorias de site: [{lista_de_categorias_string}], por favor gere uma resposta em formato JSON contendo duas chaves:
                1. "artigo": contendo um artigo jornalístico completo e otimizado para SEO em português do Brasil, com no mínimo 400 palavras e subtítulos em markdown.
                2. "categoria": contendo o nome de UMA categoria da lista fornecida que melhor se encaixa no tópico.
                """
                
                # Lógica de Repetição (Retry)
                for tentativa in range(3):
                    try:
                        self.stdout.write(f'     -> Tentativa {tentativa + 1}/3...')
                        response = openai.chat.completions.create(
                            model="gpt-3.5-turbo", response_format={"type": "json_object"},
                            messages=[
                                {"role": "system", "content": "Você é um assistente que retorna respostas estritamente em formato JSON."},
                                {"role": "user", "content": prompt_texto}
                            ]
                        )
                        resultado_json = json.loads(response.choices[0].message.content.strip())
                        
                        artigo_ia = resultado_json.get('artigo')
                        conteudo_final = ""
                        if isinstance(artigo_ia, str):
                            conteudo_final = artigo_ia
                        elif isinstance(artigo_ia, dict):
                            # Lógica para montar o artigo a partir de um dicionário
                            partes = [artigo_ia.get('introducao', '')]
                            i = 1
                            while True:
                                sub = artigo_ia.get(f'subtitulo{i}')
                                cont = artigo_ia.get(f'conteudo{i}')
                                if sub and cont:
                                    partes.append(f"\n### {sub}\n")
                                    partes.append(cont)
                                    i += 1
                                else:
                                    break
                            conteudo_final = "\n".join(filter(None, partes))
                        
                        noticia.conteudo = conteudo_final.strip()
                        nome_categoria_ia = resultado_json.get('categoria', '')

                        if noticia.conteudo:
                            self.stdout.write(self.style.SUCCESS('     -> Conteúdo gerado.'))
                            if nome_categoria_ia:
                                categoria_obj = Categoria.objects.filter(nome__iexact=nome_categoria_ia).first()
                                if categoria_obj:
                                    noticia.categoria = categoria_obj
                                    self.stdout.write(f'     -> Categoria escolhida pela IA: "{nome_categoria_ia}"')
                            break # Sucesso, sai do loop de tentativas
                        else:
                            raise ValueError("JSON da IA incompleto ou não pôde ser montado.")
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'     -> Tentativa {tentativa + 1}/3 falhou: {e}'))
                        if tentativa == 2: # Última tentativa
                            raise # Re-lança a exceção final
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'     -> Falha final ao gerar conteúdo: {e}'))
                noticia.delete()
                continue

            termo_busca = noticia.titulo
            imagem_salva = False
            
            if not imagem_salva: imagem_salva = buscar_imagem_pexels(noticia, termo_busca, pexels_key)
            if not imagem_salva: imagem_salva = buscar_imagem_unsplash(noticia, termo_busca, unsplash_key)
            if not imagem_salva: imagem_salva = buscar_imagem_pixabay(noticia, termo_busca, pixabay_key)
            if not imagem_salva: imagem_salva = gerar_imagem_dalle(noticia, termo_busca, openai_key)

            noticia.status = Noticia.Status.PUBLICADO
            noticia.save()
            novas_noticias_processadas += 1
            self.stdout.write(self.style.SUCCESS('  -> Notícia finalizada e publicada!'))

        self.stdout.write(self.style.SUCCESS(f'\nProcesso finalizado. {novas_noticias_processadas} notícias novas foram publicadas.'))