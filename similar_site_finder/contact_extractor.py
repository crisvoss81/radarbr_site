# Extrator de Contatos - Priorizando WhatsApp Comercial

import re
import requests
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Optional, Tuple
import phonenumbers
from phonenumbers import carrier, geocoder
import time
import json

logger = logging.getLogger(__name__)

class ContactExtractor:
    """Classe para extrair contatos de sites, priorizando WhatsApp comercial"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Padrões de regex para diferentes tipos de contato
        self.whatsapp_patterns = [
            r'whatsapp[:\s]*(\+?[\d\s\-\(\)]{10,})',
            r'wa\.me/(\d+)',
            r'api\.whatsapp\.com/send\?phone=(\d+)',
            r'(\+?55[\d\s\-\(\)]{10,})',  # Números brasileiros
            r'(\+?[\d\s\-\(\)]{10,})\s*\(whatsapp\)',
            r'whatsapp.*?(\d{2,3}[\d\s\-\(\)]{8,})',
        ]
        
        self.email_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            r'mailto:([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
        ]
        
        self.phone_patterns = [
            r'(\+?55[\s\-]?\(?[1-9]{2}\)?[\s\-]?[\d]{4,5}[\s\-]?[\d]{4})',  # Brasil
            r'(\+?[\d\s\-\(\)]{10,})',
            r'tel:(\+?[\d\s\-\(\)]{10,})',
            r'phone[:\s]*(\+?[\d\s\-\(\)]{10,})',
            r'telefone[:\s]*(\+?[\d\s\-\(\)]{10,})',
        ]
        
        # Palavras-chave que indicam contato comercial
        self.commercial_keywords = [
            'comercial', 'vendas', 'sales', 'marketing', 'atendimento',
            'suporte', 'support', 'contato', 'contact', 'fale conosco',
            'orcamento', 'orçamento', 'quote', 'proposta', 'negocios',
            'business', 'empresa', 'company', 'servicos', 'services'
        ]
        
        # Seletores CSS comuns para seções de contato
        self.contact_selectors = [
            'footer', '.footer', '#footer',
            '.contact', '#contact', '.contato', '#contato',
            '.footer-contact', '.contact-info', '.contact-details',
            '.header-contact', '.top-contact', '.main-contact',
            '[class*="contact"]', '[id*="contact"]',
            '[class*="contato"]', '[id*="contato"]',
            '.social', '.social-media', '.social-links',
            '.whatsapp', '.wa', '.zap'
        ]
    
    def extract_contacts(self, url: str) -> Dict:
        """
        Extrai todos os contatos de um site
        
        Args:
            url: URL do site
            
        Returns:
            Dicionário com contatos encontrados organizados por tipo
        """
        try:
            logger.info(f"Extraindo contatos de: {url}")
            
            # Fazer requisição para o site
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extrair diferentes tipos de contato
            contacts = {
                'whatsapp': self._extract_whatsapp_contacts(soup, url),
                'emails': self._extract_emails(soup, url),
                'phones': self._extract_phones(soup, url),
                'social_media': self._extract_social_media(soup, url)
            }
            
            # Processar e validar contatos
            processed_contacts = self._process_contacts(contacts, url)
            
            logger.info(f"Encontrados {len(processed_contacts)} contatos")
            return {
                'success': True,
                'contacts': processed_contacts,
                'total_contacts': len(processed_contacts),
                'source_url': url
            }
            
        except Exception as e:
            logger.error(f"Erro ao extrair contatos de {url}: {e}")
            return {
                'success': False,
                'contacts': [],
                'total_contacts': 0,
                'error': str(e),
                'source_url': url
            }
    
    def _extract_whatsapp_contacts(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extrai contatos do WhatsApp com prioridade para comerciais"""
        whatsapp_contacts = []
        
        try:
            # Buscar em links do WhatsApp
            whatsapp_links = soup.find_all('a', href=re.compile(r'whatsapp|wa\.me|api\.whatsapp'))
            
            for link in whatsapp_links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                # Extrair número do link
                phone_match = re.search(r'(\+?[\d\s\-\(\)]{10,})', href)
                if phone_match:
                    phone = self._clean_phone(phone_match.group(1))
                    if phone:
                        contact = {
                            'type': 'whatsapp',
                            'value': phone,
                            'label': self._determine_contact_label(text, link),
                            'confidence': self._calculate_confidence(text, link, 'whatsapp'),
                            'extraction_method': 'link',
                            'context': text
                        }
                        whatsapp_contacts.append(contact)
            
            # Buscar números de telefone que podem ser WhatsApp
            phone_elements = soup.find_all(text=re.compile(r'whatsapp|wa\.me', re.IGNORECASE))
            
            for element in phone_elements:
                parent = element.parent
                if parent:
                    text = parent.get_text(strip=True)
                    
                    # Procurar números próximos ao texto WhatsApp
                    phone_match = re.search(r'(\+?[\d\s\-\(\)]{10,})', text)
                    if phone_match:
                        phone = self._clean_phone(phone_match.group(1))
                        if phone:
                            contact = {
                                'type': 'whatsapp',
                                'value': phone,
                                'label': self._determine_contact_label(text, parent),
                                'confidence': self._calculate_confidence(text, parent, 'whatsapp'),
                                'extraction_method': 'text',
                                'context': text
                            }
                            whatsapp_contacts.append(contact)
            
            # Buscar em seções específicas de contato
            for selector in self.contact_selectors:
                contact_sections = soup.select(selector)
                for section in contact_sections:
                    section_text = section.get_text()
                    
                    # Procurar padrões de WhatsApp na seção
                    for pattern in self.whatsapp_patterns:
                        matches = re.finditer(pattern, section_text, re.IGNORECASE)
                        for match in matches:
                            phone = self._clean_phone(match.group(1))
                            if phone:
                                contact = {
                                    'type': 'whatsapp',
                                    'value': phone,
                                    'label': self._determine_contact_label(section_text, section),
                                    'confidence': self._calculate_confidence(section_text, section, 'whatsapp'),
                                    'extraction_method': 'section',
                                    'context': section_text[:200]
                                }
                                whatsapp_contacts.append(contact)
            
            # Remover duplicatas e ordenar por confiança
            whatsapp_contacts = self._remove_duplicates(whatsapp_contacts)
            whatsapp_contacts.sort(key=lambda x: x['confidence'], reverse=True)
            
            return whatsapp_contacts
            
        except Exception as e:
            logger.error(f"Erro ao extrair WhatsApp: {e}")
            return []
    
    def _extract_emails(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extrai emails do site"""
        emails = []
        
        try:
            # Buscar em links mailto
            mailto_links = soup.find_all('a', href=re.compile(r'^mailto:'))
            
            for link in mailto_links:
                href = link.get('href', '')
                email_match = re.search(r'mailto:([^?]+)', href)
                if email_match:
                    email = email_match.group(1).strip()
                    contact = {
                        'type': 'email',
                        'value': email,
                        'label': self._determine_contact_label(link.get_text(), link),
                        'confidence': self._calculate_confidence(link.get_text(), link, 'email'),
                        'extraction_method': 'mailto',
                        'context': link.get_text(strip=True)
                    }
                    emails.append(contact)
            
            # Buscar emails no texto
            text_content = soup.get_text()
            for pattern in self.email_patterns:
                matches = re.finditer(pattern, text_content, re.IGNORECASE)
                for match in matches:
                    email = match.group(1) if len(match.groups()) > 0 else match.group(0)
                    email = email.strip()
                    
                    # Validar email básico
                    if '@' in email and '.' in email.split('@')[1]:
                        contact = {
                            'type': 'email',
                            'value': email,
                            'label': self._determine_contact_label(text_content, None),
                            'confidence': self._calculate_confidence(text_content, None, 'email'),
                            'extraction_method': 'text',
                            'context': text_content[max(0, match.start()-50):match.end()+50]
                        }
                        emails.append(contact)
            
            # Remover duplicatas
            emails = self._remove_duplicates(emails)
            emails.sort(key=lambda x: x['confidence'], reverse=True)
            
            return emails
            
        except Exception as e:
            logger.error(f"Erro ao extrair emails: {e}")
            return []
    
    def _extract_phones(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extrai números de telefone do site"""
        phones = []
        
        try:
            # Buscar em links tel
            tel_links = soup.find_all('a', href=re.compile(r'^tel:'))
            
            for link in tel_links:
                href = link.get('href', '')
                phone_match = re.search(r'tel:(\+?[\d\s\-\(\)]+)', href)
                if phone_match:
                    phone = self._clean_phone(phone_match.group(1))
                    if phone:
                        contact = {
                            'type': 'phone',
                            'value': phone,
                            'label': self._determine_contact_label(link.get_text(), link),
                            'confidence': self._calculate_confidence(link.get_text(), link, 'phone'),
                            'extraction_method': 'tel_link',
                            'context': link.get_text(strip=True)
                        }
                        phones.append(contact)
            
            # Buscar números no texto
            text_content = soup.get_text()
            for pattern in self.phone_patterns:
                matches = re.finditer(pattern, text_content)
                for match in matches:
                    phone = self._clean_phone(match.group(1))
                    if phone:
                        contact = {
                            'type': 'phone',
                            'value': phone,
                            'label': self._determine_contact_label(text_content, None),
                            'confidence': self._calculate_confidence(text_content, None, 'phone'),
                            'extraction_method': 'text',
                            'context': text_content[max(0, match.start()-50):match.end()+50]
                        }
                        phones.append(contact)
            
            # Remover duplicatas
            phones = self._remove_duplicates(phones)
            phones.sort(key=lambda x: x['confidence'], reverse=True)
            
            return phones
            
        except Exception as e:
            logger.error(f"Erro ao extrair telefones: {e}")
            return []
    
    def _extract_social_media(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extrai links de redes sociais"""
        social_contacts = []
        
        try:
            social_patterns = {
                'facebook': r'facebook\.com/[^/\s]+',
                'instagram': r'instagram\.com/[^/\s]+',
                'linkedin': r'linkedin\.com/[^/\s]+',
                'twitter': r'twitter\.com/[^/\s]+',
                'youtube': r'youtube\.com/[^/\s]+',
                'tiktok': r'tiktok\.com/@[^/\s]+'
            }
            
            # Buscar em links
            all_links = soup.find_all('a', href=True)
            
            for link in all_links:
                href = link.get('href', '')
                
                for platform, pattern in social_patterns.items():
                    if re.search(pattern, href, re.IGNORECASE):
                        contact = {
                            'type': 'social_media',
                            'value': href,
                            'label': platform,
                            'confidence': 0.8,
                            'extraction_method': 'link',
                            'context': link.get_text(strip=True)
                        }
                        social_contacts.append(contact)
                        break
            
            return social_contacts
            
        except Exception as e:
            logger.error(f"Erro ao extrair redes sociais: {e}")
            return []
    
    def _clean_phone(self, phone: str) -> Optional[str]:
        """Limpa e valida um número de telefone"""
        try:
            if not phone:
                return None
            
            # Remover caracteres não numéricos exceto +
            cleaned = re.sub(r'[^\d+]', '', phone)
            
            # Adicionar +55 se for número brasileiro sem código do país
            if cleaned.startswith('55') and len(cleaned) >= 12:
                cleaned = '+' + cleaned
            elif cleaned.startswith('11') and len(cleaned) == 10:
                cleaned = '+55' + cleaned
            elif not cleaned.startswith('+') and len(cleaned) >= 10:
                cleaned = '+55' + cleaned
            
            # Validar com phonenumbers
            try:
                parsed = phonenumbers.parse(cleaned, None)
                if phonenumbers.is_valid_number(parsed):
                    return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
            except:
                pass
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao limpar telefone {phone}: {e}")
            return None
    
    def _determine_contact_label(self, text: str, element) -> str:
        """Determina o tipo de contato baseado no contexto"""
        if not text:
            return 'geral'
        
        text_lower = text.lower()
        
        # Verificar palavras-chave comerciais
        for keyword in self.commercial_keywords:
            if keyword in text_lower:
                return 'comercial'
        
        # Verificar contexto específico
        if any(word in text_lower for word in ['vendas', 'sales', 'comercial']):
            return 'comercial'
        elif any(word in text_lower for word in ['suporte', 'support', 'atendimento']):
            return 'suporte'
        elif any(word in text_lower for word in ['marketing', 'promocao', 'promoção']):
            return 'marketing'
        
        return 'geral'
    
    def _calculate_confidence(self, text: str, element, contact_type: str) -> float:
        """Calcula a confiança na extração do contato"""
        confidence = 0.5  # Base
        
        if not text:
            return confidence
        
        text_lower = text.lower()
        
        # Aumentar confiança para contatos comerciais
        if any(keyword in text_lower for keyword in self.commercial_keywords):
            confidence += 0.3
        
        # Aumentar confiança para WhatsApp
        if contact_type == 'whatsapp':
            confidence += 0.2
            if 'whatsapp' in text_lower:
                confidence += 0.1
        
        # Aumentar confiança para elementos específicos
        if element:
            if element.name == 'a' and element.get('href'):
                confidence += 0.1
            if 'contact' in element.get('class', []) or 'contato' in element.get('class', []):
                confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _remove_duplicates(self, contacts: List[Dict]) -> List[Dict]:
        """Remove contatos duplicados"""
        seen = set()
        unique_contacts = []
        
        for contact in contacts:
            key = f"{contact['type']}:{contact['value']}"
            if key not in seen:
                seen.add(key)
                unique_contacts.append(contact)
        
        return unique_contacts
    
    def _process_contacts(self, contacts: Dict, url: str) -> List[Dict]:
        """Processa e organiza todos os contatos encontrados"""
        processed = []
        
        # Priorizar WhatsApp comercial
        whatsapp_contacts = contacts.get('whatsapp', [])
        for contact in whatsapp_contacts:
            if contact['label'] == 'comercial':
                contact['is_primary'] = True
                processed.append(contact)
        
        # Adicionar outros WhatsApp
        for contact in whatsapp_contacts:
            if contact['label'] != 'comercial':
                contact['is_primary'] = False
                processed.append(contact)
        
        # Adicionar emails comerciais
        emails = contacts.get('emails', [])
        for contact in emails:
            if contact['label'] == 'comercial':
                contact['is_primary'] = True
                processed.append(contact)
        
        # Adicionar outros emails
        for contact in emails:
            if contact['label'] != 'comercial':
                contact['is_primary'] = False
                processed.append(contact)
        
        # Adicionar telefones comerciais
        phones = contacts.get('phones', [])
        for contact in phones:
            if contact['label'] == 'comercial':
                contact['is_primary'] = True
                processed.append(contact)
        
        # Adicionar outros telefones
        for contact in phones:
            if contact['label'] != 'comercial':
                contact['is_primary'] = False
                processed.append(contact)
        
        # Adicionar redes sociais
        social_media = contacts.get('social_media', [])
        for contact in social_media:
            contact['is_primary'] = False
            processed.append(contact)
        
        return processed
