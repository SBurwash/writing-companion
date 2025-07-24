import click
import os
from .article_manager import ArticleManager
from .gemini_client import GeminiClient


def get_default_project(ctx):
    """Get the default project from environment variable or context."""
    return os.getenv('PROJECT_NAME') or ctx.obj.get('default_project')


@click.group()
@click.option('--api-key', envvar='GOOGLE_API_KEY', help='Google AI API key')
@click.option('--project', envvar='PROJECT_NAME', help='Default project name')
@click.pass_context
def cli(ctx, api_key, project):
    """Article Writing CLI - Write articles with Gemini AI and git versioning."""
    ctx.ensure_object(dict)
    ctx.obj['api_key'] = api_key
    ctx.obj['default_project'] = project
    
    # Initialize managers
    try:
        ctx.obj['article_manager'] = ArticleManager()
        if api_key:
            ctx.obj['gemini_client'] = GeminiClient(api_key)
        else:
            ctx.obj['gemini_client'] = None
    except Exception as e:
        click.echo(f"❌ Error initializing: {e}")
        ctx.exit(1)


@cli.command()
@click.argument('project_name')
@click.pass_context
def init(ctx, project_name):
    """Initialize a new article project."""
    try:
        article_manager = ctx.obj['article_manager']
        project_path = article_manager.init_project(project_name)
        click.echo(f"🎉 Project '{project_name}' created at: {project_path}")
    except ValueError as e:
        click.echo(f"❌ {e}")
        ctx.exit(1)


@cli.command()
@click.pass_context
def list(ctx):
    """List all available projects."""
    article_manager = ctx.obj['article_manager']
    projects = article_manager.list_projects()
    
    if not projects:
        click.echo("📝 No projects found. Create one with: writing-bot init <project_name>")
        return
    
    click.echo("📚 Available projects:")
    for project in projects:
        click.echo(f"  • {project}")


@cli.command()
@click.argument('section_name')
@click.argument('project_name', required=False)
@click.option('--context', help='Additional context for the section')
@click.pass_context
def expand(ctx, section_name, project_name, context):
    """Expand an outline section with Gemini AI."""
    # Use default project if not specified
    if not project_name:
        project_name = get_default_project(ctx)
        if not project_name:
            click.echo("❌ No project specified. Use --project option or set PROJECT_NAME environment variable.")
            ctx.exit(1)
    if not ctx.obj['gemini_client']:
        click.echo("❌ Gemini API key not configured. Set GOOGLE_API_KEY environment variable.")
        ctx.exit(1)
    
    try:
        article_manager = ctx.obj['article_manager']
        gemini_client = ctx.obj['gemini_client']
        
        # Get outline sections
        sections = article_manager.get_outline_sections(project_name)
        section_content = None
        
        for name, content in sections:
            if name.lower() == section_name.lower():
                section_content = content
                break
        
        if not section_content:
            click.echo(f"❌ Section '{section_name}' not found in outline.")
            click.echo("Available sections:")
            for name, _ in sections:
                click.echo(f"  • {name}")
            ctx.exit(1)
        
        # Get article context
        files = article_manager.get_project_files(project_name)
        article_context = article_manager.read_file(files['article'])
        
        click.echo(f"🤖 Expanding section '{section_name}' with Gemini...")
        
        # Generate content
        expanded_content = gemini_client.expand_section(
            outline_section=section_content,
            context=context or f"Article context: {article_context[:500]}..."
        )
        
        # Update article
        article_manager.update_article_section(project_name, section_name, expanded_content)
        
        click.echo(f"✅ Section '{section_name}' expanded successfully!")
        click.echo(f"📝 Content added to article.md")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        ctx.exit(1)


@cli.command()
@click.argument('section_name')
@click.argument('instruction')
@click.argument('project_name', required=False)
@click.pass_context
def rewrite(ctx, section_name, instruction, project_name):
    # Use default project if not specified
    if not project_name:
        project_name = get_default_project(ctx)
        if not project_name:
            click.echo("❌ No project specified. Use --project option or set PROJECT_NAME environment variable.")
            ctx.exit(1)
    if not ctx.obj['gemini_client']:
        click.echo("❌ Gemini API key not configured. Set GOOGLE_API_KEY environment variable.")
        ctx.exit(1)
    
    try:
        article_manager = ctx.obj['article_manager']
        gemini_client = ctx.obj['gemini_client']
        
        # Find existing content
        existing_content = article_manager.find_section_in_article(project_name, section_name)
        
        if not existing_content:
            click.echo(f"❌ Section '{section_name}' not found in article.")
            click.echo("Use 'expand' command first to create content.")
            ctx.exit(1)
        
        click.echo(f"🤖 Rewriting section '{section_name}' with instruction: '{instruction}'")
        
        # Rewrite content
        rewritten_content = gemini_client.rewrite_content(existing_content, instruction)
        
        # Update article
        article_manager.update_article_section(project_name, section_name, rewritten_content)
        
        click.echo(f"✅ Section '{section_name}' rewritten successfully!")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        ctx.exit(1)


@cli.command()
@click.argument('topic')
@click.pass_context
def research(ctx, topic):
    """Get research and facts about a topic."""
    if not ctx.obj['gemini_client']:
        click.echo("❌ Gemini API key not configured. Set GOOGLE_API_KEY environment variable.")
        ctx.exit(1)
    
    try:
        gemini_client = ctx.obj['gemini_client']
        
        click.echo(f"🔍 Researching topic: '{topic}'")
        
        # Get research
        research_content = gemini_client.research_topic(topic)
        
        click.echo("\n📊 Research Results:")
        click.echo("=" * 50)
        click.echo(research_content)
        click.echo("=" * 50)
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        ctx.exit(1)


@cli.command()
@click.argument('section_name')
@click.argument('project_name', required=False)
@click.option('--style-notes', help='Specific style preferences')
@click.pass_context
def improve(ctx, section_name, project_name, style_notes):
    # Use default project if not specified
    if not project_name:
        project_name = get_default_project(ctx)
        if not project_name:
            click.echo("❌ No project specified. Use --project option or set PROJECT_NAME environment variable.")
            ctx.exit(1)
    if not ctx.obj['gemini_client']:
        click.echo("❌ Gemini API key not configured. Set GOOGLE_API_KEY environment variable.")
        ctx.exit(1)
    
    try:
        article_manager = ctx.obj['article_manager']
        gemini_client = ctx.obj['gemini_client']
        
        # Find existing content
        existing_content = article_manager.find_section_in_article(project_name, section_name)
        
        if not existing_content:
            click.echo(f"❌ Section '{section_name}' not found in article.")
            click.echo("Use 'expand' command first to create content.")
            ctx.exit(1)
        
        click.echo(f"✨ Improving style of section '{section_name}'")
        
        # Improve content
        improved_content = gemini_client.improve_style(existing_content, style_notes)
        
        # Update article
        article_manager.update_article_section(project_name, section_name, improved_content)
        
        click.echo(f"✅ Section '{section_name}' style improved successfully!")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        ctx.exit(1)


@cli.command()
@click.argument('project_name', required=False)
@click.pass_context
def status(ctx, project_name):
    # Use default project if not specified
    if not project_name:
        project_name = get_default_project(ctx)
        if not project_name:
            click.echo("❌ No project specified. Use --project option or set PROJECT_NAME environment variable.")
            ctx.exit(1)
    try:
        article_manager = ctx.obj['article_manager']
        status_info = article_manager.get_status(project_name)
        
        click.echo(f"📊 Project Status: {status_info['project_name']}")
        click.echo(f"📁 Path: {status_info['path']}")
        click.echo(f"📝 Outline size: {status_info['outline_size']} bytes")
        click.echo(f"📄 Article size: {status_info['article_size']} bytes")
        
        if status_info['last_commit']:
            click.echo(f"🔄 Last commit: {status_info['last_commit']['message']} ({status_info['last_commit']['date']})")
        
        click.echo("\n📜 Recent commits:")
        for commit in status_info['recent_commits']:
            click.echo(f"  {commit['hash']} - {commit['message']} ({commit['date']})")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        ctx.exit(1)


@cli.command()
@click.argument('message')
@click.argument('project_name', required=False)
@click.pass_context
def commit(ctx, message, project_name):
    # Use default project if not specified
    if not project_name:
        project_name = get_default_project(ctx)
        if not project_name:
            click.echo("❌ No project specified. Use --project option or set PROJECT_NAME environment variable.")
            ctx.exit(1)
    try:
        article_manager = ctx.obj['article_manager']
        article_manager.commit_changes(project_name, message)
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        ctx.exit(1)


@cli.command()
@click.argument('project_name', required=False)
@click.pass_context
def outline(ctx, project_name):
    # Use default project if not specified
    if not project_name:
        project_name = get_default_project(ctx)
        if not project_name:
            click.echo("❌ No project specified. Use --project option or set PROJECT_NAME environment variable.")
            ctx.exit(1)
    try:
        article_manager = ctx.obj['article_manager']
        files = article_manager.get_project_files(project_name)
        outline_content = article_manager.read_file(files['outline'])
        
        click.echo(f"📋 Outline for '{project_name}':")
        click.echo("=" * 50)
        click.echo(outline_content)
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        ctx.exit(1)


@cli.command()
@click.argument('project_name', required=False)
@click.pass_context
def article(ctx, project_name):
    # Use default project if not specified
    if not project_name:
        project_name = get_default_project(ctx)
        if not project_name:
            click.echo("❌ No project specified. Use --project option or set PROJECT_NAME environment variable.")
            ctx.exit(1)
    try:
        article_manager = ctx.obj['article_manager']
        files = article_manager.get_project_files(project_name)
        article_content = article_manager.read_file(files['article'])
        
        click.echo(f"📄 Article content for '{project_name}':")
        click.echo("=" * 50)
        click.echo(article_content)
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        ctx.exit(1)


@cli.command()
@click.argument('request', nargs=-1)
@click.option('--project_name', required=False)
@click.pass_context
def review(ctx, request, project_name):
    # Use default project if not specified
    if not project_name:
        project_name = get_default_project(ctx)
        if not project_name:
            click.echo("❌ No project specified. Use --project option or set PROJECT_NAME environment variable.")
            ctx.exit(1)
    if not ctx.obj['gemini_client']:
        click.echo("❌ Gemini API key not configured. Set GOOGLE_API_KEY environment variable.")
        ctx.exit(1)
    print(project_name)
    print(get_default_project(ctx))
    try:
        print(project_name)
        print("here")
        article_manager = ctx.obj['article_manager']
        print("here2")
        gemini_client = ctx.obj['gemini_client']
        print("here3")
        files = article_manager.get_project_files(project_name)
        print("here4")
        outline_content = article_manager.read_file(files['outline'])
        print("here5")
        article_content = article_manager.read_file(files['article'])
        print("here6")
        request_text = " ".join(request)
        print(request_text)
        if not request_text.strip():
            click.echo("❌ Please provide a review request. Examples:")
            click.echo("  • review my outline")
            click.echo("  • give feedback on structure")
            click.echo("  • check for gaps in my content")
            click.echo("  • suggest improvements")
            ctx.exit(1)
        click.echo(f"🔍 Reviewing '{project_name}' with request: '{request_text}'")
        click.echo("🤖 Analyzing with Gemini...")
        feedback = gemini_client.review_with_context(
            request=request_text,
            outline_content=outline_content,
            article_content=article_content,
            project_name=project_name
        )
        click.echo("\n📋 Review Feedback:")
        click.echo("=" * 60)
        click.echo(feedback)
        click.echo("=" * 60)
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        ctx.exit(1)


def main():
    """Main entry point."""
    cli() 
