import os
import git
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import yaml


class ArticleManager:
    """Manages article projects, files, and git versioning."""
    
    def __init__(self, articles_dir: str = "writing_bot/articles"):
        """Initialize the article manager.
        
        Args:
            articles_dir: Directory containing all article projects
        """
        self.articles_dir = Path(articles_dir)
        self.articles_dir.mkdir(parents=True, exist_ok=True)
    
    def init_project(self, project_name: str) -> str:
        """Initialize a new article project.
        
        Args:
            project_name: Name of the project
            
        Returns:
            Path to the project directory
        """
        project_dir = self.articles_dir / project_name
        if project_dir.exists():
            raise ValueError(f"Project '{project_name}' already exists")
        
        # Create project directory
        project_dir.mkdir(parents=True)
        
        # Initialize git repository
        repo = git.Repo.init(project_dir)
        
        # Create initial files
        outline_path = project_dir / "outline.md"
        article_path = project_dir / "article.md"
        config_path = project_dir / "config.yaml"
        
        # Create outline template
        outline_content = f"""# {project_name.replace('_', ' ').title()} - Outline

## Introduction
- Hook
- Background
- Thesis statement

## Main Points
### Point 1
- Key idea
- Supporting evidence

### Point 2
- Key idea
- Supporting evidence

### Point 3
- Key idea
- Supporting evidence

## Conclusion
- Summary
- Call to action
"""
        
        # Create empty article file
        article_content = f"""# {project_name.replace('_', ' ').title()}

*Generated content will appear here as you expand your outline.*

"""
        
        # Create config file
        config = {
            'project_name': project_name,
            'created_date': str(Path().stat().st_ctime),
            'last_modified': str(Path().stat().st_mtime),
            'status': 'outline'
        }
        
        # Write files
        outline_path.write_text(outline_content)
        article_path.write_text(article_content)
        config_path.write_text(yaml.dump(config, default_flow_style=False))
        
        # Initial git commit
        repo.index.add(['outline.md', 'article.md', 'config.yaml'])
        repo.index.commit("Initial project setup")
        
        print(f"✅ Project '{project_name}' initialized successfully!")
        print(f"📁 Project directory: {project_dir}")
        print(f"📝 Edit outline.md to get started")
        
        return str(project_dir)
    
    def get_project_path(self, project_name: str) -> Path:
        """Get the path to a project directory.
        
        Args:
            project_name: Name of the project
            
        Returns:
            Path to the project directory
        """
        project_path = self.articles_dir / project_name
        if not project_path.exists():
            raise ValueError(f"Project '{project_name}' not found")
        return project_path
    
    def get_project_files(self, project_name: str) -> Dict[str, Path]:
        """Get the main files for a project.
        
        Args:
            project_name: Name of the project
            
        Returns:
            Dictionary with file paths
        """
        project_path = self.get_project_path(project_name)
        return {
            'outline': project_path / "outline.md",
            'article': project_path / "article.md",
            'config': project_path / "config.yaml"
        }
    
    def read_file(self, file_path: Path) -> str:
        """Read content from a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File content
        """
        return file_path.read_text()
    
    def write_file(self, file_path: Path, content: str) -> None:
        """Write content to a file.
        
        Args:
            file_path: Path to the file
            content: Content to write
        """
        file_path.write_text(content)
    
    def get_outline_sections(self, project_name: str) -> List[Tuple[str, str]]:
        """Get all sections from the outline.
        
        Args:
            project_name: Name of the project
            
        Returns:
            List of (section_name, section_content) tuples
        """
        files = self.get_project_files(project_name)
        outline_content = self.read_file(files['outline'])
        
        sections = []
        current_section = None
        current_content = []
        
        for line in outline_content.split('\n'):
            if line.startswith('### '):
                # Save previous section
                if current_section:
                    sections.append((current_section, '\n'.join(current_content).strip()))
                
                # Start new section
                current_section = line[4:].strip()
                current_content = []
            elif line.startswith('## ') and not line.startswith('### '):
                # Main section - skip for now
                continue
            elif current_section and line.strip():
                current_content.append(line)
        
        # Add last section
        if current_section:
            sections.append((current_section, '\n'.join(current_content).strip()))
        
        return sections
    
    def find_section_in_article(self, project_name: str, section_name: str) -> Optional[str]:
        """Find content for a specific section in the article.
        
        Args:
            project_name: Name of the project
            section_name: Name of the section to find
            
        Returns:
            Section content if found, None otherwise
        """
        files = self.get_project_files(project_name)
        article_content = self.read_file(files['article'])
        
        lines = article_content.split('\n')
        section_start = None
        section_end = None
        
        for i, line in enumerate(lines):
            if line.startswith(f'## {section_name}') or line.startswith(f'### {section_name}'):
                section_start = i + 1
                break
        
        if section_start is None:
            return None
        
        # Find end of section (next heading or end of file)
        for i in range(section_start, len(lines)):
            if lines[i].startswith('#') and i > section_start:
                section_end = i
                break
        
        if section_end is None:
            section_end = len(lines)
        
        return '\n'.join(lines[section_start:section_end]).strip()
    
    def update_article_section(self, project_name: str, section_name: str, content: str) -> None:
        """Update a specific section in the article.
        
        Args:
            project_name: Name of the project
            section_name: Name of the section to update
            content: New content for the section
        """
        files = self.get_project_files(project_name)
        article_content = self.read_file(files['article'])
        
        lines = article_content.split('\n')
        section_start = None
        section_end = None
        
        # Find section boundaries
        for i, line in enumerate(lines):
            if line.startswith(f'## {section_name}') or line.startswith(f'### {section_name}'):
                section_start = i + 1
                break
        
        if section_start is None:
            # Section doesn't exist, add it at the end
            lines.append(f'\n## {section_name}')
            lines.append(content)
        else:
            # Find end of existing section
            for i in range(section_start, len(lines)):
                if lines[i].startswith('#') and i > section_start:
                    section_end = i
                    break
            
            if section_end is None:
                section_end = len(lines)
            
            # Replace section content
            new_lines = lines[:section_start] + [content] + lines[section_end:]
            lines = new_lines
        
        # Write updated content
        self.write_file(files['article'], '\n'.join(lines))
    
    def commit_changes(self, project_name: str, message: str) -> None:
        """Commit changes to git.
        
        Args:
            project_name: Name of the project
            message: Commit message
        """
        project_path = self.get_project_path(project_name)
        repo = git.Repo(project_path)
        
        # Add all changes
        repo.index.add(['*'])
        
        # Commit
        repo.index.commit(message)
        print(f"✅ Changes committed: {message}")
    
    def get_status(self, project_name: str) -> Dict[str, any]:
        """Get project status and git history.
        
        Args:
            project_name: Name of the project
            
        Returns:
            Dictionary with status information
        """
        project_path = self.get_project_path(project_name)
        repo = git.Repo(project_path)
        
        # Get recent commits
        commits = []
        for commit in repo.iter_commits('main', max_count=5):
            commits.append({
                'hash': commit.hexsha[:8],
                'message': commit.message.strip(),
                'date': commit.committed_datetime.strftime('%Y-%m-%d %H:%M')
            })
        
        # Get file stats
        files = self.get_project_files(project_name)
        outline_size = files['outline'].stat().st_size
        article_size = files['article'].stat().st_size
        
        return {
            'project_name': project_name,
            'path': str(project_path),
            'recent_commits': commits,
            'outline_size': outline_size,
            'article_size': article_size,
            'last_commit': commits[0] if commits else None
        }
    
    def list_projects(self) -> List[str]:
        """List all available projects.
        
        Returns:
            List of project names
        """
        projects = []
        for item in self.articles_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                projects.append(item.name)
        return sorted(projects) 