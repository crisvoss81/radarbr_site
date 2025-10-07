# GOOGLE ADSENSE CONFIGURATION
# Configuração dos códigos de anúncios do Google AdSense

# ID do cliente AdSense
ADSENSE_CLIENT_ID = "ca-pub-3913403142217011"

# Códigos de slots de anúncios (substitua pelos seus códigos reais)
ADSENSE_SLOTS = {
    # Home page
    "home_inline": "1234567890",           # Banner principal na home
    "home_between_cards": "1234567891",     # Banner entre cards na home
    
    # Páginas de notícias
    "post_header": "1234567892",           # Banner após título da notícia
    "post_image": "1234567893",            # Banner após imagem da notícia
    "post_content": "1234567894",          # Banner após conteúdo da notícia
    
    # Páginas de categoria
    "category_top": "1234567895",          # Banner no topo da categoria
    "category_bottom": "1234567896",       # Banner no final da categoria
    
    # Sidebar
    "sidebar_top": "1234567897",           # Banner no topo da sidebar
    "sidebar_middle": "1234567898",        # Banner no meio da sidebar
    "sidebar_bottom": "1234567899",        # Banner no final da sidebar
}

# Configurações de tamanho padrão
DEFAULT_AD_SIZES = {
    "leaderboard": (728, 90),      # Banner horizontal
    "rectangle": (300, 250),       # Retângulo médio
    "skyscraper": (160, 600),      # Banner vertical
    "mobile_banner": (320, 50),    # Banner mobile
}

# Configurações por dispositivo
RESPONSIVE_ADS = True
MOBILE_OPTIMIZED = True

# Configurações de exibição
AD_POLICY = {
    "max_ads_per_page": 5,         # Máximo de anúncios por página
    "min_content_length": 200,     # Conteúdo mínimo para exibir anúncios
    "respect_user_preferences": True,  # Respeitar preferências do usuário
}

# Instruções para configuração:
# 1. Acesse o Google AdSense
# 2. Crie unidades de anúncio para cada slot
# 3. Substitua os códigos "1234567890" pelos códigos reais
# 4. Teste em modo de desenvolvimento primeiro
# 5. Monitore performance no dashboard do AdSense
