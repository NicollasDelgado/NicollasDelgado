import requests
import os
from datetime import datetime

def get_featured_repos():
    """Busca repositórios em destaque do usuário"""
    repos = [
        "Todo-List", "Blog", "portfolio", "api-rest", "ecommerce",
        "calculadora", "jogo-memoria", "weather-app", "task-manager"
    ]
    
    featured_cards = []
    
    for repo_name in repos[:6]:  # Mostrar até 6 projetos
        try:
            # Verificar se o repositório existe
            response = requests.get(f'https://api.github.com/repos/NicollasDelgado/{repo_name}')
            if response.status_code == 200:
                repo_data = response.json()
                card = f"""
<a href="https://github.com/NicollasDelgado/{repo_name}">
  <img align="center" src="https://github-readme-stats.vercel.app/api/pin/?username=NicollasDelgado&repo={repo_name}&theme=tokyonight&hide_border=true&bg_color=0D1117&title_color=F85D7F&text_color=FFFFFF" />
</a>"""
                featured_cards.append(card)
        except:
            continue
    
    return featured_cards

def update_readme():
    """Atualiza a seção de projetos no README"""
    with open('README.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    featured_cards = get_featured_repos()
    
    # Gerar a nova seção de projetos
    projects_section = f"""
## 🚀 Meus Projetos

<div align="center">

### 💼 **Repositórios em Destaque**

{''.join(featured_cards)}

</div>

### 🔨 **O que estou construindo:**
- 📱 **Apps React Native** com Expo
- ⚛️ **Aplicações de Sites/App Webs** com React  
- 🎨 **Interfaces responsivas** com React e CSS
- 📝 **Aprendendo Utilizar** o Prisma
- 🔧 **Projetos full-stack** com Node.js

<br/>

---

## 🎯 Metas Atuais

- [x] ✅ **Dominar React básico**
- [x] ✅ **Aprender React Native** 
- [x] ✅ **Finalizar primeiros projetos mobile**
- [ ] 🚀 **Solidificar conhecimento em Node.js**
- [ ] 📚 **Iniciar estudos em Python**
- [ ] 🗄️ **Aprender back-end**
- [ ] 🤖 **Finalizar projetos de Arduino IDE**
- [ ] 💼 **Conseguir primeira oportunidade como dev**

*Última atualização: {datetime.now().strftime("%d/%m/%Y")}*

<br/>
"""
    
    # Encontrar e substituir a seção de projetos
    start_marker = "## 🚀 Meus Projetos"
    end_marker = "## 🎯 Metas Atuais"
    
    if start_marker in content and end_marker in content:
        start_index = content.find(start_marker)
        end_index = content.find(end_marker, start_index)
        
        new_content = content[:start_index] + projects_section + content[end_index:]
    else:
        # Fallback: adicionar no final
        new_content = content + f"\n\n<!-- Atualizado automaticamente em {datetime.now()} -->"
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("README atualizado com sucesso!")

if __name__ == "__main__":
    update_readme()
