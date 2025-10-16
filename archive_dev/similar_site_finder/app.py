# Aplicação Flask Principal - SimilarSiteFinder

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
import os
from datetime import datetime
import json
import threading
import time

# Importar módulos do projeto
from config import config
from models import db, Site, Contact, SearchSession, SearchFilter
from similarweb_api import SimilarWebAPI
from contact_extractor import ContactExtractor

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(config_name='default'):
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Inicializar extensões
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Inicializar APIs
    similarweb_api = SimilarWebAPI(
        api_key=app.config['SIMILARWEB_API_KEY'],
        base_url=app.config['SIMILARWEB_BASE_URL']
    )
    
    contact_extractor = ContactExtractor(
        timeout=app.config['CONTACT_EXTRACTION_TIMEOUT']
    )
    
    @app.route('/')
    def index():
        """Página principal"""
        return render_template('index.html')
    
    @app.route('/search', methods=['GET', 'POST'])
    def search():
        """Página de busca de sites similares"""
        if request.method == 'POST':
            data = request.get_json()
            reference_site = data.get('reference_site', '').strip()
            country = data.get('country', 'BR')
            max_results = int(data.get('max_results', 50))
            extract_contacts = data.get('extract_contacts', True)
            
            if not reference_site:
                return jsonify({'error': 'Site de referência é obrigatório'}), 400
            
            # Criar sessão de busca
            session = SearchSession(
                reference_site=reference_site,
                search_parameters={
                    'country': country,
                    'max_results': max_results,
                    'extract_contacts': extract_contacts
                },
                status='running'
            )
            db.session.add(session)
            db.session.commit()
            
            # Executar busca em background
            thread = threading.Thread(
                target=execute_search,
                args=(session.id, reference_site, country, max_results, extract_contacts)
            )
            thread.daemon = True
            thread.start()
            
            return jsonify({
                'success': True,
                'session_id': session.id,
                'message': 'Busca iniciada com sucesso'
            })
        
        # GET - Mostrar página de busca
        filters = SearchFilter.query.filter_by(is_active=True).all()
        return render_template('search.html', filters=filters)
    
    @app.route('/results/<int:session_id>')
    def results(session_id):
        """Página de resultados da busca"""
        session = SearchSession.query.get_or_404(session_id)
        sites = Site.query.filter_by(id=session.site_id).all() if session.site_id else []
        
        return render_template('results.html', session=session, sites=sites)
    
    @app.route('/api/search/status/<int:session_id>')
    def search_status(session_id):
        """API para verificar status da busca"""
        session = SearchSession.query.get_or_404(session_id)
        return jsonify(session.to_dict())
    
    @app.route('/api/sites')
    def api_sites():
        """API para listar sites"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category = request.args.get('category')
        country = request.args.get('country')
        status = request.args.get('status', 'active')
        
        query = Site.query.filter_by(status=status)
        
        if category:
            query = query.filter(Site.category.ilike(f'%{category}%'))
        if country:
            query = query.filter_by(country=country)
        
        sites = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'sites': [site.to_dict() for site in sites.items],
            'total': sites.total,
            'pages': sites.pages,
            'current_page': page
        })
    
    @app.route('/api/sites/<int:site_id>/contacts')
    def api_site_contacts(site_id):
        """API para obter contatos de um site"""
        site = Site.query.get_or_404(site_id)
        contacts = Contact.query.filter_by(site_id=site_id).all()
        
        return jsonify({
            'site': site.to_dict(),
            'contacts': [contact.to_dict() for contact in contacts]
        })
    
    @app.route('/sites')
    def sites_list():
        """Página de listagem de sites"""
        page = request.args.get('page', 1, type=int)
        category = request.args.get('category')
        country = request.args.get('country')
        search = request.args.get('search')
        
        query = Site.query.filter_by(status='active')
        
        if category:
            query = query.filter(Site.category.ilike(f'%{category}%'))
        if country:
            query = query.filter_by(country=country)
        if search:
            query = query.filter(
                Site.domain.ilike(f'%{search}%') |
                Site.title.ilike(f'%{search}%')
            )
        
        sites = query.paginate(
            page=page, per_page=20, error_out=False
        )
        
        categories = db.session.query(Site.category).distinct().all()
        countries = db.session.query(Site.country).distinct().all()
        
        return render_template('sites.html', 
                             sites=sites,
                             categories=[c[0] for c in categories if c[0]],
                             countries=[c[0] for c in countries if c[0]])
    
    @app.route('/site/<int:site_id>')
    def site_detail(site_id):
        """Página de detalhes de um site"""
        site = Site.query.get_or_404(site_id)
        contacts = Contact.query.filter_by(site_id=site_id).all()
        
        return render_template('site_detail.html', site=site, contacts=contacts)
    
    @app.route('/export')
    def export_data():
        """Exportar dados para Excel/CSV"""
        format_type = request.args.get('format', 'xlsx')
        category = request.args.get('category')
        country = request.args.get('country')
        
        query = Site.query.filter_by(status='active')
        
        if category:
            query = query.filter(Site.category.ilike(f'%{category}%'))
        if country:
            query = query.filter_by(country=country)
        
        sites = query.limit(10000).all()  # Limitar para evitar timeout
        
        if format_type == 'csv':
            return export_csv(sites)
        elif format_type == 'json':
            return export_json(sites)
        else:
            return export_excel(sites)
    
    @app.route('/filters')
    def filters_management():
        """Página de gerenciamento de filtros"""
        filters = SearchFilter.query.all()
        return render_template('filters.html', filters=filters)
    
    @app.route('/api/filters', methods=['POST'])
    def create_filter():
        """API para criar novo filtro"""
        data = request.get_json()
        
        filter_obj = SearchFilter(
            name=data['name'],
            description=data.get('description', ''),
            country=data.get('country'),
            category=data.get('category'),
            min_monthly_visits=data.get('min_monthly_visits'),
            max_monthly_visits=data.get('max_monthly_visits'),
            max_bounce_rate=data.get('max_bounce_rate'),
            min_pages_per_visit=data.get('min_pages_per_visit')
        )
        
        db.session.add(filter_obj)
        db.session.commit()
        
        return jsonify(filter_obj.to_dict())
    
    @app.route('/api/filters/<int:filter_id>', methods=['PUT', 'DELETE'])
    def manage_filter(filter_id):
        """API para editar ou deletar filtro"""
        filter_obj = SearchFilter.query.get_or_404(filter_id)
        
        if request.method == 'PUT':
            data = request.get_json()
            filter_obj.name = data.get('name', filter_obj.name)
            filter_obj.description = data.get('description', filter_obj.description)
            filter_obj.country = data.get('country', filter_obj.country)
            filter_obj.category = data.get('category', filter_obj.category)
            filter_obj.min_monthly_visits = data.get('min_monthly_visits', filter_obj.min_monthly_visits)
            filter_obj.max_monthly_visits = data.get('max_monthly_visits', filter_obj.max_monthly_visits)
            filter_obj.max_bounce_rate = data.get('max_bounce_rate', filter_obj.max_bounce_rate)
            filter_obj.min_pages_per_visit = data.get('min_pages_per_visit', filter_obj.min_pages_per_visit)
            filter_obj.is_active = data.get('is_active', filter_obj.is_active)
            
            db.session.commit()
            return jsonify(filter_obj.to_dict())
        
        elif request.method == 'DELETE':
            db.session.delete(filter_obj)
            db.session.commit()
            return jsonify({'success': True})
    
    @app.route('/dashboard')
    def dashboard():
        """Dashboard com estatísticas"""
        total_sites = Site.query.count()
        active_sites = Site.query.filter_by(status='active').count()
        total_contacts = Contact.query.count()
        whatsapp_contacts = Contact.query.filter_by(contact_type='whatsapp').count()
        
        recent_searches = SearchSession.query.order_by(
            SearchSession.started_at.desc()
        ).limit(10).all()
        
        stats = {
            'total_sites': total_sites,
            'active_sites': active_sites,
            'total_contacts': total_contacts,
            'whatsapp_contacts': whatsapp_contacts,
            'recent_searches': [s.to_dict() for s in recent_searches]
        }
        
        return render_template('dashboard.html', stats=stats)
    
    def execute_search(session_id, reference_site, country, max_results, extract_contacts):
        """Executa a busca de sites similares em background"""
        try:
            session = SearchSession.query.get(session_id)
            if not session:
                return
            
            logger.info(f"Iniciando busca para {reference_site}")
            
            # Buscar sites similares
            similar_sites = similarweb_api.get_similar_sites(
                domain=reference_site,
                country=country,
                limit=max_results
            )
            
            sites_found = 0
            new_sites = 0
            contacts_extracted = 0
            
            for site_data in similar_sites:
                try:
                    domain = site_data['domain']
                    
                    # Verificar se site já existe
                    existing_site = Site.query.filter_by(domain=domain).first()
                    
                    if existing_site:
                        # Atualizar métricas
                        existing_site.monthly_visits = site_data.get('monthly_visits')
                        existing_site.bounce_rate = site_data.get('bounce_rate')
                        existing_site.pages_per_visit = site_data.get('pages_per_visit')
                        existing_site.avg_visit_duration = site_data.get('avg_visit_duration')
                        existing_site.traffic_rank = site_data.get('traffic_rank')
                        existing_site.last_checked = datetime.utcnow()
                        existing_site.updated_at = datetime.utcnow()
                        
                        site = existing_site
                    else:
                        # Criar novo site
                        site = Site(
                            domain=domain,
                            url=site_data['url'],
                            title=site_data.get('title', ''),
                            description=site_data.get('description', ''),
                            category=site_data.get('category', ''),
                            country=country,
                            monthly_visits=site_data.get('monthly_visits'),
                            bounce_rate=site_data.get('bounce_rate'),
                            pages_per_visit=site_data.get('pages_per_visit'),
                            avg_visit_duration=site_data.get('avg_visit_duration'),
                            traffic_rank=site_data.get('traffic_rank'),
                            last_checked=datetime.utcnow()
                        )
                        db.session.add(site)
                        new_sites += 1
                    
                    sites_found += 1
                    
                    # Extrair contatos se solicitado
                    if extract_contacts and site.url:
                        try:
                            contact_result = contact_extractor.extract_contacts(site.url)
                            
                            if contact_result['success']:
                                for contact_data in contact_result['contacts']:
                                    # Verificar se contato já existe
                                    existing_contact = Contact.query.filter_by(
                                        site_id=site.id,
                                        contact_type=contact_data['type'],
                                        contact_value=contact_data['value']
                                    ).first()
                                    
                                    if not existing_contact:
                                        contact = Contact(
                                            site_id=site.id,
                                            contact_type=contact_data['type'],
                                            contact_value=contact_data['value'],
                                            contact_label=contact_data['label'],
                                            is_primary=contact_data.get('is_primary', False),
                                            extraction_method=contact_data['extraction_method'],
                                            confidence_score=contact_data['confidence']
                                        )
                                        db.session.add(contact)
                                        contacts_extracted += 1
                            
                        except Exception as e:
                            logger.error(f"Erro ao extrair contatos de {site.url}: {e}")
                    
                    # Commit a cada 10 sites para evitar perda de dados
                    if sites_found % 10 == 0:
                        db.session.commit()
                    
                except Exception as e:
                    logger.error(f"Erro ao processar site {site_data}: {e}")
                    continue
            
            # Finalizar sessão
            session.sites_found = sites_found
            session.new_sites = new_sites
            session.contacts_extracted = contacts_extracted
            session.status = 'completed'
            session.completed_at = datetime.utcnow()
            
            db.session.commit()
            
            logger.info(f"Busca concluída: {sites_found} sites, {new_sites} novos, {contacts_extracted} contatos")
            
        except Exception as e:
            logger.error(f"Erro na busca: {e}")
            session = SearchSession.query.get(session_id)
            if session:
                session.status = 'failed'
                session.error_message = str(e)
                session.completed_at = datetime.utcnow()
                db.session.commit()
    
    def export_csv(sites):
        """Exportar sites para CSV"""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Cabeçalho
        writer.writerow([
            'Domain', 'URL', 'Title', 'Category', 'Country',
            'Monthly Visits', 'Bounce Rate', 'Pages per Visit',
            'Avg Visit Duration', 'Traffic Rank', 'Status', 'Created At'
        ])
        
        # Dados
        for site in sites:
            writer.writerow([
                site.domain, site.url, site.title, site.category, site.country,
                site.monthly_visits, site.bounce_rate, site.pages_per_visit,
                site.avg_visit_duration, site.traffic_rank, site.status,
                site.created_at.strftime('%Y-%m-%d %H:%M:%S') if site.created_at else ''
            ])
        
        output.seek(0)
        
        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=sites.csv'}
        )
    
    def export_json(sites):
        """Exportar sites para JSON"""
        data = {
            'export_date': datetime.utcnow().isoformat(),
            'total_sites': len(sites),
            'sites': [site.to_dict() for site in sites]
        }
        
        from flask import Response
        return Response(
            json.dumps(data, indent=2, ensure_ascii=False),
            mimetype='application/json',
            headers={'Content-Disposition': 'attachment; filename=sites.json'}
        )
    
    def export_excel(sites):
        """Exportar sites para Excel"""
        import pandas as pd
        import io
        
        # Preparar dados
        data = []
        for site in sites:
            data.append({
                'Domain': site.domain,
                'URL': site.url,
                'Title': site.title,
                'Category': site.category,
                'Country': site.country,
                'Monthly Visits': site.monthly_visits,
                'Bounce Rate': site.bounce_rate,
                'Pages per Visit': site.pages_per_visit,
                'Avg Visit Duration': site.avg_visit_duration,
                'Traffic Rank': site.traffic_rank,
                'Status': site.status,
                'Created At': site.created_at.strftime('%Y-%m-%d %H:%M:%S') if site.created_at else ''
            })
        
        df = pd.DataFrame(data)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Sites', index=False)
        
        output.seek(0)
        
        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': 'attachment; filename=sites.xlsx'}
        )
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # Criar tabelas se não existirem
    with app.app_context():
        db.create_all()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
