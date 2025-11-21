"""
Testes unitários para qa_core.github_integration
"""

import os
from unittest.mock import Mock, patch

import pytest
from github import GithubException
from github.Repository import Repository
from github.ContentFile import ContentFile

from qa_core.github_integration import GitHubIntegration, get_github_integration


class TestGitHubIntegration:
    """Testes para a classe GitHubIntegration."""

    def test_init_with_token(self):
        """Testa inicialização com token fornecido."""
        with patch("qa_core.github_integration.Github") as mock_github_class:
            mock_github = Mock()
            mock_user = Mock()
            mock_user.login = "test_user"
            mock_github.get_user.return_value = mock_user
            mock_github_class.return_value = mock_github

            integration = GitHubIntegration(token="test_token")
            assert integration.token == "test_token"
            assert integration.github == mock_github
            mock_github_class.assert_called_once_with("test_token")

    def test_init_with_env_token(self):
        """Testa inicialização usando token do ambiente."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "env_token"}):
            with patch("qa_core.github_integration.Github") as mock_github_class:
                mock_github = Mock()
                mock_user = Mock()
                mock_user.login = "test_user"
                mock_github.get_user.return_value = mock_user
                mock_github_class.return_value = mock_github

                integration = GitHubIntegration()
                assert integration.token == "env_token"
                mock_github_class.assert_called_once_with("env_token")

    def test_init_without_token(self):
        """Testa inicialização sem token (modo não autenticado)."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("qa_core.github_integration.Github") as mock_github_class:
                mock_github = Mock()
                mock_github_class.return_value = mock_github

                integration = GitHubIntegration()
                assert integration.token is None
                mock_github_class.assert_called_once_with()

    def test_init_auth_error(self):
        """Testa erro de autenticação."""
        with patch("qa_core.github_integration.Github") as mock_github_class:
            mock_github = Mock()
            mock_github.get_user.side_effect = GithubException(401, "Unauthorized")
            mock_github_class.return_value = mock_github

            with pytest.raises(ValueError, match="Erro na autenticação GitHub"):
                GitHubIntegration(token="invalid_token")

    def test_get_repository_success(self):
        """Testa obtenção bem-sucedida de repositório."""
        with patch("qa_core.github_integration.Github") as mock_github_class:
            mock_github = Mock()
            mock_repo = Mock(spec=Repository)
            mock_github.get_repo.return_value = mock_repo
            mock_github_class.return_value = mock_github

            integration = GitHubIntegration(token="test_token")
            result = integration.get_repository("owner/repo")

            assert result == mock_repo
            mock_github.get_repo.assert_called_once_with("owner/repo")

    def test_get_repository_invalid_format(self):
        """Testa erro com formato inválido de repositório."""
        with patch("qa_core.github_integration.Github") as mock_github_class:
            mock_github = Mock()
            mock_user = Mock()
            mock_user.login = "test_user"
            mock_github.get_user.return_value = mock_user
            mock_github_class.return_value = mock_github

            integration = GitHubIntegration(token="test_token")

            with pytest.raises(ValueError, match="Formato inválido"):
                integration.get_repository("invalid")

            with pytest.raises(ValueError, match="Formato inválido"):
                integration.get_repository("")

            with pytest.raises(ValueError, match="Formato inválido"):
                integration.get_repository(None)

    def test_get_repository_not_found(self):
        """Testa erro quando repositório não é encontrado."""
        with patch("qa_core.github_integration.Github") as mock_github_class:
            mock_github = Mock()
            error = GithubException(404, "Not Found")
            mock_github.get_repo.side_effect = error
            mock_github_class.return_value = mock_github

            integration = GitHubIntegration(token="test_token")

            with pytest.raises(ValueError, match="Repositório não encontrado"):
                integration.get_repository("owner/nonexistent")

    def test_get_repository_access_denied(self):
        """Testa erro de acesso negado."""
        with patch("qa_core.github_integration.Github") as mock_github_class:
            mock_github = Mock()
            mock_user = Mock()
            mock_user.login = "test_user"
            mock_github.get_user.return_value = mock_user
            # GithubException(status, data, headers) - status já é definido no construtor
            error = GithubException(403, {"message": "Forbidden"})
            mock_github.get_repo.side_effect = error
            mock_github_class.return_value = mock_github

            integration = GitHubIntegration(token="test_token")

            with pytest.raises(ValueError, match="Acesso negado"):
                integration.get_repository("owner/private-repo")

    def test_get_repository_other_error(self):
        """Testa outros erros ao acessar repositório."""
        with patch("qa_core.github_integration.Github") as mock_github_class:
            mock_github = Mock()
            mock_user = Mock()
            mock_user.login = "test_user"
            mock_github.get_user.return_value = mock_user
            error = GithubException(500, {"message": "Internal Server Error"})
            mock_github.get_repo.side_effect = error
            mock_github_class.return_value = mock_github

            integration = GitHubIntegration(token="test_token")

            with pytest.raises(ValueError, match="Erro ao acessar repositório"):
                integration.get_repository("owner/repo")

    def test_get_repository_info(self):
        """Testa obtenção de informações do repositório."""
        with patch("qa_core.github_integration.Github") as mock_github_class:
            mock_github = Mock()
            mock_repo = Mock(spec=Repository)
            mock_repo.name = "test-repo"
            mock_repo.full_name = "owner/test-repo"
            mock_repo.description = "Test repository"
            mock_repo.html_url = "https://github.com/owner/test-repo"
            mock_repo.language = "Python"
            mock_repo.stargazers_count = 10
            mock_repo.forks_count = 5
            mock_repo.private = False
            mock_repo.default_branch = "main"

            from datetime import datetime

            created_at = datetime(2023, 1, 1, 12, 0, 0)
            updated_at = datetime(2024, 1, 1, 12, 0, 0)
            mock_repo.created_at = created_at
            mock_repo.updated_at = updated_at

            mock_github.get_repo.return_value = mock_repo
            mock_github_class.return_value = mock_github

            integration = GitHubIntegration(token="test_token")
            info = integration.get_repository_info("owner/repo")

            assert info["name"] == "test-repo"
            assert info["full_name"] == "owner/test-repo"
            assert info["description"] == "Test repository"
            assert info["url"] == "https://github.com/owner/test-repo"
            assert info["language"] == "Python"
            assert info["stars"] == 10
            assert info["forks"] == 5
            assert info["is_private"] is False
            assert info["default_branch"] == "main"
            assert info["created_at"] == created_at.isoformat()
            assert info["updated_at"] == updated_at.isoformat()

    def test_get_repository_info_with_none_dates(self):
        """Testa obtenção de informações com datas None."""
        with patch("qa_core.github_integration.Github") as mock_github_class:
            mock_github = Mock()
            mock_repo = Mock(spec=Repository)
            mock_repo.name = "test-repo"
            mock_repo.full_name = "owner/test-repo"
            mock_repo.description = None
            mock_repo.html_url = "https://github.com/owner/test-repo"
            mock_repo.language = None
            mock_repo.stargazers_count = 0
            mock_repo.forks_count = 0
            mock_repo.private = False
            mock_repo.default_branch = "main"
            mock_repo.created_at = None
            mock_repo.updated_at = None

            mock_github.get_repo.return_value = mock_repo
            mock_github_class.return_value = mock_github

            integration = GitHubIntegration(token="test_token")
            info = integration.get_repository_info("owner/repo")

            assert info["created_at"] is None
            assert info["updated_at"] is None

    def test_get_file_content_success(self):
        """Testa obtenção de conteúdo de arquivo."""
        with patch("qa_core.github_integration.Github") as mock_github_class:
            mock_github = Mock()
            mock_repo = Mock(spec=Repository)
            mock_content = Mock(spec=ContentFile)
            mock_content.decoded_content = b"print('Hello, World!')"
            mock_repo.get_contents.return_value = mock_content
            mock_github.get_repo.return_value = mock_repo
            mock_github_class.return_value = mock_github

            integration = GitHubIntegration(token="test_token")
            content = integration.get_file_content("owner/repo", "test.py")

            assert content == "print('Hello, World!')"
            mock_repo.get_contents.assert_called_once_with("test.py")

    def test_get_file_content_with_branch(self):
        """Testa obtenção de conteúdo com branch específica."""
        with patch("qa_core.github_integration.Github") as mock_github_class:
            mock_github = Mock()
            mock_repo = Mock(spec=Repository)
            mock_content = Mock(spec=ContentFile)
            mock_content.decoded_content = b"print('dev')"
            mock_repo.get_contents.return_value = mock_content
            mock_github.get_repo.return_value = mock_repo
            mock_github_class.return_value = mock_github

            integration = GitHubIntegration(token="test_token")
            content = integration.get_file_content(
                "owner/repo", "test.py", branch="develop"
            )

            assert content == "print('dev')"
            mock_repo.get_contents.assert_called_once_with("test.py", ref="develop")

    def test_get_file_content_directory_error(self):
        """Testa erro quando caminho é um diretório."""
        with patch("qa_core.github_integration.Github") as mock_github_class:
            mock_github = Mock()
            mock_repo = Mock(spec=Repository)
            # Retorna uma lista (diretório) ao invés de ContentFile
            mock_repo.get_contents.return_value = [Mock()]
            mock_github.get_repo.return_value = mock_repo
            mock_github_class.return_value = mock_github

            integration = GitHubIntegration(token="test_token")

            with pytest.raises(ValueError, match="é um diretório, não um arquivo"):
                integration.get_file_content("owner/repo", "test_dir/")

    def test_get_file_content_not_found(self):
        """Testa erro quando arquivo não é encontrado."""
        with patch("qa_core.github_integration.Github") as mock_github_class:
            mock_github = Mock()
            mock_user = Mock()
            mock_user.login = "test_user"
            mock_github.get_user.return_value = mock_user
            mock_repo = Mock(spec=Repository)
            error = GithubException(404, {"message": "Not Found"})
            mock_repo.get_contents.side_effect = error
            mock_github.get_repo.return_value = mock_repo
            mock_github_class.return_value = mock_github

            integration = GitHubIntegration(token="test_token")

            with pytest.raises(ValueError, match="Arquivo não encontrado"):
                integration.get_file_content("owner/repo", "nonexistent.py")

    def test_get_file_content_other_error(self):
        """Testa outros erros ao ler arquivo."""
        with patch("qa_core.github_integration.Github") as mock_github_class:
            mock_github = Mock()
            mock_user = Mock()
            mock_user.login = "test_user"
            mock_github.get_user.return_value = mock_user
            mock_repo = Mock(spec=Repository)
            error = GithubException(500, {"message": "Internal Server Error"})
            mock_repo.get_contents.side_effect = error
            mock_github.get_repo.return_value = mock_repo
            mock_github_class.return_value = mock_github

            integration = GitHubIntegration(token="test_token")

            with pytest.raises(ValueError, match="Erro ao ler arquivo"):
                integration.get_file_content("owner/repo", "test.py")

    def test_list_files_empty_directory(self):
        """Testa listagem de arquivos em diretório vazio."""
        with patch("qa_core.github_integration.Github") as mock_github_class:
            mock_github = Mock()
            mock_repo = Mock(spec=Repository)
            mock_repo.get_contents.return_value = []
            mock_github.get_repo.return_value = mock_repo
            mock_github_class.return_value = mock_github

            integration = GitHubIntegration(token="test_token")
            files = integration.list_files("owner/repo", "empty_dir")

            assert files == []
            mock_repo.get_contents.assert_called_once_with("empty_dir")

    def test_list_files_with_files(self):
        """Testa listagem de arquivos."""
        with patch("qa_core.github_integration.Github") as mock_github_class:
            mock_github = Mock()
            mock_repo = Mock(spec=Repository)
            mock_file1 = Mock()
            mock_file1.type = "file"
            mock_file1.name = "test1.py"
            mock_file1.path = "test1.py"
            mock_file1.size = 100
            mock_file1.html_url = "https://github.com/owner/repo/blob/main/test1.py"

            mock_file2 = Mock()
            mock_file2.type = "file"
            mock_file2.name = "test2.py"
            mock_file2.path = "test2.py"
            mock_file2.size = 200
            mock_file2.html_url = "https://github.com/owner/repo/blob/main/test2.py"

            mock_repo.get_contents.return_value = [mock_file1, mock_file2]
            mock_github.get_repo.return_value = mock_repo
            mock_github_class.return_value = mock_github

            integration = GitHubIntegration(token="test_token")
            files = integration.list_files("owner/repo")

            assert len(files) == 2
            assert files[0]["name"] == "test1.py"
            assert files[1]["name"] == "test2.py"

    def test_list_files_with_directories(self):
        """Testa listagem incluindo diretórios."""
        with patch("qa_core.github_integration.Github") as mock_github_class:
            mock_github = Mock()
            mock_repo = Mock(spec=Repository)
            mock_dir = Mock()
            mock_dir.type = "dir"
            mock_dir.name = "subdir"
            mock_dir.path = "subdir"
            mock_dir.html_url = "https://github.com/owner/repo/tree/main/subdir"

            mock_repo.get_contents.return_value = [mock_dir]
            mock_github.get_repo.return_value = mock_repo
            mock_github_class.return_value = mock_github

            integration = GitHubIntegration(token="test_token")
            files = integration.list_files("owner/repo")

            assert len(files) == 1
            assert files[0]["name"] == "subdir"
            assert files[0]["type"] == "directory"

    def test_list_files_with_file_extensions_filter(self):
        """Testa listagem com filtro de extensões."""
        with patch("qa_core.github_integration.Github") as mock_github_class:
            mock_github = Mock()
            mock_repo = Mock(spec=Repository)
            mock_file1 = Mock()
            mock_file1.type = "file"
            mock_file1.name = "test.py"
            mock_file1.path = "test.py"
            mock_file1.size = 100
            mock_file1.html_url = "https://github.com/owner/repo/blob/main/test.py"

            mock_file2 = Mock()
            mock_file2.type = "file"
            mock_file2.name = "test.js"
            mock_file2.path = "test.js"
            mock_file2.size = 200
            mock_file2.html_url = "https://github.com/owner/repo/blob/main/test.js"

            mock_repo.get_contents.return_value = [mock_file1, mock_file2]
            mock_github.get_repo.return_value = mock_repo
            mock_github_class.return_value = mock_github

            integration = GitHubIntegration(token="test_token")
            files = integration.list_files("owner/repo", file_extensions=[".py"])

            assert len(files) == 1
            assert files[0]["name"] == "test.py"

    def test_list_files_single_file(self):
        """Testa listagem quando retorna um único arquivo (ContentFile)."""
        with patch("qa_core.github_integration.Github") as mock_github_class:
            mock_github = Mock()
            mock_repo = Mock(spec=Repository)
            mock_content = Mock(spec=ContentFile)
            mock_content.type = "file"
            mock_content.name = "single.py"
            mock_content.path = "single.py"
            mock_content.size = 50
            mock_content.html_url = "https://github.com/owner/repo/blob/main/single.py"

            mock_repo.get_contents.return_value = mock_content
            mock_github.get_repo.return_value = mock_repo
            mock_github_class.return_value = mock_github

            integration = GitHubIntegration(token="test_token")
            files = integration.list_files("owner/repo", "single.py")

            assert len(files) == 1
            assert files[0]["name"] == "single.py"

    def test_list_files_not_found(self):
        """Testa erro quando caminho não é encontrado."""
        with patch("qa_core.github_integration.Github") as mock_github_class:
            mock_github = Mock()
            mock_user = Mock()
            mock_user.login = "test_user"
            mock_github.get_user.return_value = mock_user
            mock_repo = Mock(spec=Repository)
            error = GithubException(404, {"message": "Not Found"})
            mock_repo.get_contents.side_effect = error
            mock_github.get_repo.return_value = mock_repo
            mock_github_class.return_value = mock_github

            integration = GitHubIntegration(token="test_token")

            with pytest.raises(ValueError, match="Caminho não encontrado"):
                integration.list_files("owner/repo", "nonexistent")

    def test_list_files_other_error(self):
        """Testa outros erros ao listar arquivos (linha 216)."""
        with patch("qa_core.github_integration.Github") as mock_github_class:
            mock_github = Mock()
            mock_user = Mock()
            mock_user.login = "test_user"
            mock_github.get_user.return_value = mock_user
            mock_repo = Mock(spec=Repository)
            # Erro diferente de 404 (ex: 500, 403, etc)
            error = GithubException(500, {"message": "Internal Server Error"})
            mock_repo.get_contents.side_effect = error
            mock_github.get_repo.return_value = mock_repo
            mock_github_class.return_value = mock_github

            integration = GitHubIntegration(token="test_token")

            with pytest.raises(ValueError, match="Erro ao listar arquivos"):
                integration.list_files("owner/repo", "path")

    def test_list_files_with_branch(self):
        """Testa listagem com branch específica."""
        with patch("qa_core.github_integration.Github") as mock_github_class:
            mock_github = Mock()
            mock_repo = Mock(spec=Repository)
            mock_repo.get_contents.return_value = []
            mock_github.get_repo.return_value = mock_repo
            mock_github_class.return_value = mock_github

            integration = GitHubIntegration(token="test_token")
            integration.list_files("owner/repo", branch="develop")

            mock_repo.get_contents.assert_called_once_with("", ref="develop")

    def test_get_repository_structure_success(self):
        """Testa obtenção da estrutura do repositório."""
        with patch("qa_core.github_integration.Github") as mock_github_class:
            mock_github = Mock()
            mock_repo = Mock(spec=Repository)

            mock_file = Mock()
            mock_file.type = "file"
            mock_file.name = "readme.md"
            mock_file.size = 100

            mock_dir_item = Mock()
            mock_dir_item.type = "file"
            mock_dir_item.name = "config.py"
            mock_dir_item.size = 200

            mock_subdir = Mock()
            mock_subdir.type = "dir"
            mock_subdir.name = "subdir"

            # Primeira chamada: raiz
            # Segunda chamada: subdir (mas retorna vazio para não complicar)
            mock_repo.get_contents.side_effect = [
                [mock_file, mock_subdir],  # Raiz
                [mock_dir_item],  # subdir
            ]

            mock_github.get_repo.return_value = mock_repo
            mock_github_class.return_value = mock_github

            integration = GitHubIntegration(token="test_token")
            structure = integration.get_repository_structure("owner/repo", max_depth=2)

            assert "readme.md" in structure
            assert "subdir" in structure
            assert structure["readme.md"]["type"] == "file"

    def test_get_repository_structure_max_depth(self):
        """Testa que max_depth é respeitado."""
        with patch("qa_core.github_integration.Github") as mock_github_class:
            mock_github = Mock()
            mock_user = Mock()
            mock_user.login = "test_user"
            mock_github.get_user.return_value = mock_user
            mock_repo = Mock(spec=Repository)

            mock_dir = Mock()
            mock_dir.type = "dir"
            mock_dir.name = "level1"

            # Com max_depth=0, ainda explora a raiz (depth=0), mas não os subdiretórios
            # Quando tentar explorar level1, depth será 1, que é > max_depth=0
            mock_repo.get_contents.side_effect = [
                [mock_dir],  # Primeira chamada (raiz)
                [],  # Chamada para level1 não acontece porque depth > max_depth
            ]
            mock_github.get_repo.return_value = mock_repo
            mock_github_class.return_value = mock_github

            integration = GitHubIntegration(token="test_token")
            structure = integration.get_repository_structure("owner/repo", max_depth=0)

            # Com max_depth=0, level1 é listado mas não explorado (fica vazio)
            assert "level1" in structure
            assert structure["level1"] == {}

    def test_get_repository_structure_with_branch(self):
        """Testa get_repository_structure com branch específica (linha 241)."""
        with patch("qa_core.github_integration.Github") as mock_github_class:
            mock_github = Mock()
            mock_user = Mock()
            mock_user.login = "test_user"
            mock_github.get_user.return_value = mock_user
            mock_repo = Mock(spec=Repository)

            mock_file = Mock()
            mock_file.type = "file"
            mock_file.name = "readme.md"
            mock_file.size = 100

            mock_repo.get_contents.return_value = [mock_file]
            mock_github.get_repo.return_value = mock_repo
            mock_github_class.return_value = mock_github

            integration = GitHubIntegration(token="test_token")
            structure = integration.get_repository_structure(
                "owner/repo", branch="develop"
            )

            # Verifica que get_contents foi chamado com ref
            assert mock_repo.get_contents.called
            # Verifica que estrutura foi retornada
            assert "readme.md" in structure

    def test_get_repository_structure_error_handling(self):
        """Testa que erros são tratados silenciosamente."""
        with patch("qa_core.github_integration.Github") as mock_github_class:
            mock_github = Mock()
            mock_repo = Mock(spec=Repository)

            error = GithubException(404, "Not Found")
            mock_repo.get_contents.side_effect = error

            mock_github.get_repo.return_value = mock_repo
            mock_github_class.return_value = mock_github

            integration = GitHubIntegration(token="test_token")
            structure = integration.get_repository_structure("owner/repo")

            # Deve retornar estrutura vazia quando há erro
            assert structure == {}

    def test_search_code_success(self):
        """Testa busca de código bem-sucedida."""
        with patch("qa_core.github_integration.Github") as mock_github_class:
            mock_github = Mock()
            mock_repo = Mock(spec=Repository)
            mock_github.get_repo.return_value = mock_repo

            mock_result1 = Mock()
            mock_result1.name = "test1.py"
            mock_result1.path = "test1.py"
            mock_result1.html_url = "https://github.com/owner/repo/blob/main/test1.py"
            mock_result1.repository.full_name = "owner/repo"

            mock_result2 = Mock()
            mock_result2.name = "test2.py"
            mock_result2.path = "test2.py"
            mock_result2.html_url = "https://github.com/owner/repo/blob/main/test2.py"
            mock_result2.repository.full_name = "owner/repo"

            mock_search_results = [mock_result1, mock_result2]
            mock_github.search_code.return_value = mock_search_results
            mock_github_class.return_value = mock_github

            integration = GitHubIntegration(token="test_token")
            results = integration.search_code("owner/repo", "def main")

            assert len(results) == 2
            assert results[0]["name"] == "test1.py"
            assert results[1]["name"] == "test2.py"
            mock_github.search_code.assert_called_once()
            call_args = mock_github.search_code.call_args[0][0]
            assert "def main" in call_args
            assert "repo:owner/repo" in call_args

    def test_search_code_with_language(self):
        """Testa busca de código com filtro de linguagem."""
        with patch("qa_core.github_integration.Github") as mock_github_class:
            mock_github = Mock()
            mock_repo = Mock(spec=Repository)
            mock_github.get_repo.return_value = mock_repo
            mock_github.search_code.return_value = []
            mock_github_class.return_value = mock_github

            integration = GitHubIntegration(token="test_token")
            integration.search_code("owner/repo", "def", language="python")

            call_args = mock_github.search_code.call_args[0][0]
            assert "language:python" in call_args

    def test_search_code_limit_results(self):
        """Testa que resultados são limitados a 10."""
        with patch("qa_core.github_integration.Github") as mock_github_class:
            mock_github = Mock()
            mock_repo = Mock(spec=Repository)
            mock_github.get_repo.return_value = mock_repo

            # Cria 15 resultados
            mock_results = []
            for i in range(15):
                mock_result = Mock()
                mock_result.name = f"test{i}.py"
                mock_result.path = f"test{i}.py"
                mock_result.html_url = (
                    f"https://github.com/owner/repo/blob/main/test{i}.py"
                )
                mock_result.repository.full_name = "owner/repo"
                mock_results.append(mock_result)

            mock_github.search_code.return_value = mock_results
            mock_github_class.return_value = mock_github

            integration = GitHubIntegration(token="test_token")
            results = integration.search_code("owner/repo", "def")

            assert len(results) == 10  # Limitado a 10

    def test_search_code_error(self):
        """Testa erro na busca de código."""
        with patch("qa_core.github_integration.Github") as mock_github_class:
            mock_github = Mock()
            mock_repo = Mock(spec=Repository)
            mock_github.get_repo.return_value = mock_repo

            error = GithubException(403, "Forbidden")
            mock_github.search_code.side_effect = error
            mock_github_class.return_value = mock_github

            integration = GitHubIntegration(token="test_token")

            with pytest.raises(ValueError, match="Erro na busca"):
                integration.search_code("owner/repo", "def")


class TestGetGitHubIntegration:
    """Testes para a função get_github_integration."""

    def test_get_github_integration_with_token(self):
        """Testa factory function com token configurado."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
            with patch(
                "qa_core.github_integration.GitHubIntegration"
            ) as mock_integration_class:
                mock_integration = Mock()
                mock_integration_class.return_value = mock_integration

                result = get_github_integration()

                assert result == mock_integration
                mock_integration_class.assert_called_once_with(token="test_token")

    def test_get_github_integration_without_token(self):
        """Testa factory function sem token."""
        with patch.dict(os.environ, {}, clear=True):
            with patch(
                "qa_core.github_integration.GitHubIntegration"
            ) as mock_integration_class:
                mock_integration = Mock()
                mock_integration_class.return_value = mock_integration

                result = get_github_integration()

                # A função permite uso sem token
                assert result == mock_integration
                mock_integration_class.assert_called_once_with(token=None)

    def test_get_github_integration_with_exception(self):
        """Testa factory function quando há exceção na criação."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "invalid_token"}):
            with patch(
                "qa_core.github_integration.GitHubIntegration"
            ) as mock_integration_class:
                mock_integration_class.side_effect = ValueError("Auth error")

                result = get_github_integration()

                assert result is None
