#!/usr/bin/env python3
import os
import requests
from datetime import datetime
from collections import Counter

# Configurações
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
USERNAME = os.environ.get('GITHUB_REPOSITORY_OWNER', 'NicollasDelgado')
README_PATH = 'README.md'

headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

def get_user_stats():
    """Busca estatísticas do usuário"""
    url = f'https://api.github.com/users/{USERNAME}'
    response = requests.get(url, headers=headers)
    return response.json()

def get_repositories():
    """Busca todos os repositórios públicos"""
    repos = []
    page = 1
    while True:
        url = f'https://api.github.com/users/{USERNAME}/repos?per_page=100&page={page}&sort=updated'
        response = requests.get(url, headers=headers)
        data = response.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos

def get_language_stats(repos):
    """Calcula estatísticas de linguagens"""
    language_bytes = Counter()
    
    for repo in repos:
        if repo['fork']:
            continue
        
        lang_url = repo['languages_url']
        response = requests.get(lang_url, headers=headers)
        if response.status_code == 200:
            languages = response.json()
            for lang, bytes_count in languages.items():
                language_bytes[lang] += bytes_count
    
    total_bytes = sum(language_bytes.values())
    if total_bytes == 0:
        return {}
    
    language_percentages = {
        lang: (bytes_count / total_bytes * 100) 
        for lang, bytes_count in language_bytes.items()
    }
    
    return dict(language_percentages.most_common(10))

def get_featured_projects(repos):
    """Seleciona projetos em destaque (exclui o profile repo)"""
    featured = [r for r in repos if not r['fork'] and r['name'] != USERNAME]
    featured.sort(
        key=lambda x: (x['stargazers_count'], x['forks_count'], x['updated_at']),
        reverse=True
    )
    return featured[:4]

def create_language_bar(languages):
    """Cria barra de progresso visual com as principais linguagens"""
    if not languages:
        return "Nenhuma linguagem detectada ainda."
    
    bar_length = 25
    bars = []
    
    # Pega apenas as top 5 para exibir na barra
    top_langs = dict(list(languages.items())[:5])
    
    for lang, percentage in top_langs.items():
        filled = int((percentage / 100) * bar_length)
        bar = '█' * filled + '░' * (bar_length - filled)
        bars.append(f"{lang:<15} {bar} {percentage:.1f}%")
    
    return '\n'.join(bars)

def generate_projects_section(projects):
    """Gera cards de projetos em destaque mantendo o estilo visual"""
    if not projects:
        return '<div align="center">\n\n*Nenhum projeto público encontrado ainda*\n\n</div>\n\n'
    
    section = '<div align="center">\n\n### 💼 **Repositórios em Destaque**\n  \n'
    
    # Pega os 2 primeiros para cards grandes
    for i in range(0, min(2, len(projects))):
        repo = projects[i]
        section += f'<a href="{repo["html_url"]}"> \n'
        section += f'  <img align="center" src="https://github-readme-stats.vercel.app/api/pin/?username={USERNAME}&repo={repo["name"]}&theme=tokyonight&hide_border=true&bg_color=0D1117&title_color=F85D7F&text_color=FFFFFF" />\n'
        section += '</a>'
    
    section += '\n</div>\n\n'
    return section

def generate_detailed_stats(user_data, repos, languages):
    """Gera estatísticas detalhadas em texto"""
    total_repos = len([r for r in repos if not r['fork']])
    total_stars = sum(r['stargazers_count'] for r in repos if not r['fork'])
    total_forks = sum(r['forks_count'] for r in repos if not r['fork'])
    followers = user_data.get('followers', 0)
    following = user_data.get('following', 0)
    
    section = "### 📊 **Estatísticas Detalhadas**\n\n"
    section += "```text\n"
    section += f"📦 Repositórios Públicos: {total_repos}\n"
    section += f"⭐ Total de Stars:        {total_stars}\n"
    section += f"🍴 Total de Forks:        {total_forks}\n"
    section += f"👥 Seguidores:            {followers}\n"
    section += f"👤 Seguindo:              {following}\n"
    section += "```\n\n"
    
    if languages:
        section += "### 🔥 **Linguagens Mais Usadas (% de código)**\n\n"
        section += "```text\n"
        section += create_language_bar(languages)
        section += "\n```\n\n"
    
    return section

def update_readme():
    """Atualiza o README.md mantendo o estilo atual"""
    print("🔍 Buscando dados do GitHub...")
    
    # Busca dados
    user_data = get_user_stats()
    repos = get_repositories()
    languages = get_language_stats(repos)
    featured = get_featured_projects(repos)
    
    print(f"✅ Encontrados {len(repos)} repositórios")
    print(f"✅ Top linguagens: {', '.join(list(languages.keys())[:5])}")
    print(f"✅ Projetos em destaque: {len(featured)}")
    
    # Lê README atual
    with open(README_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Markers para identificar seções auto-geradas
    stats_marker = "<!-- AUTO-STATS -->"
    projects_marker = "<!-- AUTO-PROJECTS -->"
    
    # Timestamp
    timestamp = f"*🔄 Última atualização automática: {datetime.now().strftime('%d/%m/%Y às %H:%M')} (horário de Brasília)*\n\n"
    
    # Gera seções
    stats_content = generate_detailed_stats(user_data, repos, languages)
    projects_content = generate_projects_section(featured)
    
    # Atualiza seção de estatísticas detalhadas
    if stats_marker in content:
        parts = content.split(stats_marker)
        if len(parts) >= 3:
            # Substitui o conteúdo entre os dois markers
            content = f"{parts[0]}{stats_marker}\n\n{stats_content}{timestamp}{stats_marker}{parts[2]}"
        else:
            print("⚠️ Marker de stats encontrado apenas uma vez, adicionando segundo marker")
            content = content.replace(stats_marker, f"{stats_marker}\n\n{stats_content}{timestamp}{stats_marker}\n\n")
    else:
        print("ℹ️ Marker de stats não encontrado, não será atualizado")
    
    # Atualiza seção de projetos
    if projects_marker in content:
        parts = content.split(projects_marker)
        if len(parts) >= 3:
            content = f"{parts[0]}{projects_marker}\n\n{projects_content}{projects_marker}{parts[2]}"
        else:
            print("⚠️ Marker de projetos encontrado apenas uma vez, adicionando segundo marker")
            content = content.replace(projects_marker, f"{projects_marker}\n\n{projects_content}{projects_marker}\n\n")
    else:
        print("ℹ️ Marker de projetos não encontrado, não será atualizado")
    
    # Salva README atualizado
    with open(README_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ README.md atualizado com sucesso!")

if __name__ == '__main__':
    update_readme()
