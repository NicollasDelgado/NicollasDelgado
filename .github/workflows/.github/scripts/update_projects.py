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
        if repo['fork']:  # Ignora forks
            continue
        
        lang_url = repo['languages_url']
        response = requests.get(lang_url, headers=headers)
        if response.status_code == 200:
            languages = response.json()
            for lang, bytes_count in languages.items():
                language_bytes[lang] += bytes_count
    
    total_bytes = sum(language_bytes.values())
    language_percentages = {
        lang: (bytes_count / total_bytes * 100) 
        for lang, bytes_count in language_bytes.items()
    }
    
    return dict(language_percentages.most_common(5))

def get_featured_projects(repos):
    """Seleciona projetos em destaque"""
    # Filtra e ordena por estrelas, forks e atualização
    featured = [r for r in repos if not r['fork']]
    featured.sort(
        key=lambda x: (x['stargazers_count'], x['forks_count'], x['updated_at']),
        reverse=True
    )
    return featured[:6]  # Top 6 projetos

def create_language_bar(languages):
    """Cria barra de progresso visual para linguagens"""
    bar_length = 25
    bars = []
    
    for lang, percentage in languages.items():
        filled = int((percentage / 100) * bar_length)
        bar = '█' * filled + '░' * (bar_length - filled)
        bars.append(f"{lang:<15} {bar} {percentage:.1f}%")
    
    return '\n'.join(bars)

def generate_projects_section(projects):
    """Gera seção de projetos em Markdown"""
    section = "## 🚀 Meus Projetos em Destaque\n\n"
    
    for i, repo in enumerate(projects, 1):
        name = repo['name']
        description = repo['description'] or 'Sem descrição'
        stars = repo['stargazers_count']
        forks = repo['forks_count']
        language = repo['language'] or 'N/A'
        url = repo['html_url']
        
        # Emoji baseado na linguagem
        lang_emoji = {
            'JavaScript': '🟨', 'Python': '🐍', 'Java': '☕',
            'HTML': '🌐', 'CSS': '🎨', 'TypeScript': '🔷',
            'PHP': '🐘', 'C++': '⚡', 'C': '🔧'
        }
        emoji = lang_emoji.get(language, '📁')
        
        section += f"### {i}. [{name}]({url}) {emoji}\n"
        section += f"**{description}**\n\n"
        section += f"- 🌟 Stars: {stars} | 🍴 Forks: {forks} | 💻 Linguagem: {language}\n\n"
    
    return section

def generate_stats_section(user_data, repos, languages):
    """Gera seção de estatísticas"""
    total_repos = len([r for r in repos if not r['fork']])
    total_stars = sum(r['stargazers_count'] for r in repos if not r['fork'])
    total_forks = sum(r['forks_count'] for r in repos if not r['fork'])
    followers = user_data.get('followers', 0)
    
    section = "## 📊 Estatísticas GitHub\n\n"
    section += f"![GitHub Stats](https://github-readme-stats.vercel.app/api?username={USERNAME}&show_icons=true&theme=radical&count_private=true)\n\n"
    section += f"![Top Langs](https://github-readme-stats.vercel.app/api/top-langs/?username={USERNAME}&layout=compact&theme=radical&langs_count=8)\n\n"
    
    section += "### 📈 Resumo Geral\n\n"
    section += f"- 📦 **Repositórios Públicos:** {total_repos}\n"
    section += f"- ⭐ **Total de Stars:** {total_stars}\n"
    section += f"- 🍴 **Total de Forks:** {total_forks}\n"
    section += f"- 👥 **Seguidores:** {followers}\n\n"
    
    section += "### 🔥 Linguagens Mais Usadas\n\n"
    section += "```text\n"
    section += create_language_bar(languages)
    section += "\n```\n\n"
    
    return section

def generate_activity_section():
    """Gera seção de atividade recente"""
    section = "## 📅 Atividade Recente\n\n"
    section += f"![GitHub Activity Graph](https://github-readme-activity-graph.vercel.app/graph?username={USERNAME}&theme=react-dark&hide_border=true)\n\n"
    section += f"![GitHub Streak](https://github-readme-streak-stats.herokuapp.com/?user={USERNAME}&theme=radical&hide_border=true)\n\n"
    return section

def update_readme():
    """Atualiza o README.md"""
    print("🔍 Buscando dados do GitHub...")
    
    # Busca dados
    user_data = get_user_stats()
    repos = get_repositories()
    languages = get_language_stats(repos)
    featured = get_featured_projects(repos)
    
    print(f"✅ Encontrados {len(repos)} repositórios")
    print(f"✅ Top linguagens: {', '.join(languages.keys())}")
    
    # Lê README atual
    with open(README_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Markers para identificar seções auto-geradas
    stats_start = "<!-- STATS:START -->"
    stats_end = "<!-- STATS:END -->"
    projects_start = "<!-- PROJECTS:START -->"
    projects_end = "<!-- PROJECTS:END -->"
    activity_start = "<!-- ACTIVITY:START -->"
    activity_end = "<!-- ACTIVITY:END -->"
    
    # Gera novo conteúdo
    stats_section = generate_stats_section(user_data, repos, languages)
    projects_section = generate_projects_section(featured)
    activity_section = generate_activity_section()
    
    # Adiciona timestamp
    timestamp = f"*Última atualização: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}*\n\n"
    
    # Substitui ou adiciona seções
    if stats_start in content and stats_end in content:
        before = content.split(stats_start)[0]
        after = content.split(stats_end)[1]
        content = f"{before}{stats_start}\n{stats_section}{timestamp}{stats_end}{after}"
    
    if projects_start in content and projects_end in content:
        before = content.split(projects_start)[0]
        after = content.split(projects_end)[1]
        content = f"{before}{projects_start}\n{projects_section}{projects_end}{after}"
    
    if activity_start in content and activity_end in content:
        before = content.split(activity_start)[0]
        after = content.split(activity_end)[1]
        content = f"{before}{activity_start}\n{activity_section}{activity_end}{after}"
    
    # Salva README atualizado
    with open(README_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ README.md atualizado com sucesso!")
    print(f"📊 {len(featured)} projetos em destaque")
    print(f"🔥 {len(languages)} linguagens principais")

if __name__ == '__main__':
    update_readme()
