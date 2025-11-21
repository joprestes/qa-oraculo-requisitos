# ==========================================================
# github_integration.py — Integração com GitHub
# ==========================================================
# Este módulo permite conectar-se a repositórios do GitHub
# e analisar código diretamente, similar ao Codex.
#
# Funcionalidades:
#   - Seleção de repositório (owner/repo)
#   - Autenticação opcional via token
#   - Leitura de arquivos e estrutura do repositório
#   - Análise de código para contexto em User Stories
# ==========================================================

import os
from typing import Optional, Dict, List, Any
from github import Github, GithubException
from github.Repository import Repository
from github.ContentFile import ContentFile


class GitHubIntegration:
    """Classe para gerenciar integração com GitHub."""
    
    def __init__(self, token: Optional[str] = None):
        """
        Inicializa a integração com GitHub.
        
        Args:
            token: Token de autenticação do GitHub (opcional).
                   Se não fornecido, tenta usar GITHUB_TOKEN do ambiente.
        """
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.github = None
        self._authenticate()
    
    def _authenticate(self):
        """Autentica com GitHub usando token."""
        if self.token:
            try:
                self.github = Github(self.token)
                # Testa a autenticação
                self.github.get_user().login
            except GithubException as e:
                raise ValueError(f"Erro na autenticação GitHub: {e}")
        else:
            # Modo não autenticado (limitado a repositórios públicos)
            self.github = Github()
    
    def get_repository(self, repo_path: str) -> Repository:
        """
        Obtém um repositório do GitHub.
        
        Args:
            repo_path: Caminho do repositório no formato 'owner/repo'
                      Exemplo: 'joprestes/qa-oraculo-requisitos'
        
        Returns:
            Objeto Repository do PyGithub
        
        Raises:
            ValueError: Se o formato do caminho for inválido
            GithubException: Se o repositório não for encontrado
        """
        if not repo_path or "/" not in repo_path:
            raise ValueError(
                "Formato inválido. Use 'owner/repo' (ex: 'joprestes/qa-oraculo-requisitos')"
            )
        
        try:
            repo = self.github.get_repo(repo_path)
            return repo
        except GithubException as e:
            if e.status == 404:
                raise ValueError(f"Repositório não encontrado: {repo_path}")
            elif e.status == 403:
                raise ValueError(
                    "Acesso negado. Verifique se o repositório é público ou "
                    "se você tem permissão de acesso. Para repositórios privados, "
                    "configure GITHUB_TOKEN no arquivo .env"
                )
            else:
                raise ValueError(f"Erro ao acessar repositório: {e}")
    
    def get_repository_info(self, repo_path: str) -> Dict[str, Any]:
        """
        Obtém informações básicas sobre um repositório.
        
        Args:
            repo_path: Caminho do repositório no formato 'owner/repo'
        
        Returns:
            Dicionário com informações do repositório
        """
        repo = self.get_repository(repo_path)
        
        return {
            "name": repo.name,
            "full_name": repo.full_name,
            "description": repo.description,
            "url": repo.html_url,
            "language": repo.language,
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "is_private": repo.private,
            "default_branch": repo.default_branch,
            "created_at": repo.created_at.isoformat() if repo.created_at else None,
            "updated_at": repo.updated_at.isoformat() if repo.updated_at else None,
        }
    
    def get_file_content(
        self, 
        repo_path: str, 
        file_path: str, 
        branch: Optional[str] = None
    ) -> str:
        """
        Obtém o conteúdo de um arquivo do repositório.
        
        Args:
            repo_path: Caminho do repositório no formato 'owner/repo'
            file_path: Caminho do arquivo no repositório (ex: 'qa_core/app.py')
            branch: Branch específica (opcional, usa default se não fornecido)
        
        Returns:
            Conteúdo do arquivo como string
        """
        repo = self.get_repository(repo_path)
        
        try:
            if branch:
                contents = repo.get_contents(file_path, ref=branch)
            else:
                contents = repo.get_contents(file_path)
            
            if isinstance(contents, ContentFile):
                return contents.decoded_content.decode("utf-8")
            else:
                raise ValueError(f"'{file_path}' é um diretório, não um arquivo")
        except GithubException as e:
            if e.status == 404:
                raise ValueError(f"Arquivo não encontrado: {file_path}")
            else:
                raise ValueError(f"Erro ao ler arquivo: {e}")
    
    def list_files(
        self, 
        repo_path: str, 
        path: str = "", 
        branch: Optional[str] = None,
        file_extensions: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Lista arquivos em um diretório do repositório.
        
        Args:
            repo_path: Caminho do repositório no formato 'owner/repo'
            path: Caminho do diretório (vazio para raiz)
            branch: Branch específica (opcional)
            file_extensions: Lista de extensões para filtrar (ex: ['.py', '.js'])
        
        Returns:
            Lista de dicionários com informações dos arquivos
        """
        repo = self.get_repository(repo_path)
        
        try:
            if branch:
                contents = repo.get_contents(path, ref=branch)
            else:
                contents = repo.get_contents(path)
            
            files = []
            if isinstance(contents, list):
                for item in contents:
                    if item.type == "file":
                        if file_extensions:
                            if any(item.name.endswith(ext) for ext in file_extensions):
                                files.append({
                                    "name": item.name,
                                    "path": item.path,
                                    "size": item.size,
                                    "url": item.html_url,
                                })
                        else:
                            files.append({
                                "name": item.name,
                                "path": item.path,
                                "size": item.size,
                                "url": item.html_url,
                            })
                    elif item.type == "dir":
                        files.append({
                            "name": item.name,
                            "path": item.path,
                            "type": "directory",
                            "url": item.html_url,
                        })
            elif isinstance(contents, ContentFile):
                files.append({
                    "name": contents.name,
                    "path": contents.path,
                    "size": contents.size,
                    "url": contents.html_url,
                })
            
            return files
        except GithubException as e:
            if e.status == 404:
                raise ValueError(f"Caminho não encontrado: {path}")
            else:
                raise ValueError(f"Erro ao listar arquivos: {e}")
    
    def get_repository_structure(
        self, 
        repo_path: str, 
        branch: Optional[str] = None,
        max_depth: int = 3
    ) -> Dict[str, Any]:
        """
        Obtém a estrutura de diretórios do repositório.
        
        Args:
            repo_path: Caminho do repositório no formato 'owner/repo'
            branch: Branch específica (opcional)
            max_depth: Profundidade máxima para explorar
        
        Returns:
            Dicionário com estrutura de diretórios
        """
        def _explore_directory(repo: Repository, path: str, depth: int) -> Dict[str, Any]:
            if depth > max_depth:
                return {}
            
            try:
                if branch:
                    contents = repo.get_contents(path, ref=branch)
                else:
                    contents = repo.get_contents(path)
                
                structure = {}
                
                if isinstance(contents, list):
                    for item in contents:
                        if item.type == "dir":
                            structure[item.name] = _explore_directory(
                                repo, item.path, depth + 1
                            )
                        elif item.type == "file":
                            structure[item.name] = {
                                "type": "file",
                                "size": item.size,
                            }
                
                return structure
            except GithubException:
                return {}
        
        repo = self.get_repository(repo_path)
        return _explore_directory(repo, "", 0)
    
    def search_code(
        self, 
        repo_path: str, 
        query: str, 
        language: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca código no repositório.
        
        Args:
            repo_path: Caminho do repositório no formato 'owner/repo'
            query: Termo de busca
            language: Filtrar por linguagem (opcional)
        
        Returns:
            Lista de resultados da busca
        """
        _ = self.get_repository(repo_path)
        
        search_query = f"{query} repo:{repo_path}"
        if language:
            search_query += f" language:{language}"
        
        try:
            results = self.github.search_code(search_query)
            return [
                {
                    "name": result.name,
                    "path": result.path,
                    "url": result.html_url,
                    "repository": result.repository.full_name,
                }
                for result in results[:10]  # Limita a 10 resultados
            ]
        except GithubException as e:
            raise ValueError(f"Erro na busca: {e}")


def get_github_integration() -> Optional[GitHubIntegration]:
    """
    Factory function para criar instância de GitHubIntegration.
    
    Returns:
        Instância de GitHubIntegration ou None se não houver token configurado
    """
    token = os.getenv("GITHUB_TOKEN")
    if token or True:  # Permite uso sem token para repositórios públicos
        try:
            return GitHubIntegration(token=token)
        except Exception:
            return None
    return None

