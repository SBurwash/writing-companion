import click
import os
from .article_manager import ArticleManager
from .gemini_client import GeminiClient
from .session_manager import SessionManager
from .conversation_workflow import ConversationWorkflow


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
@click.argument('project_name', required=False)
@click.pass_context
def status(ctx, project_name):
    """Show project status and git history."""
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
    """Commit changes with a custom message."""
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
@click.argument('request', nargs=-1)
@click.option('--project', required=False)
@click.pass_context
def review(ctx, request, project):
    """Review your project with free-form requests and context."""
    # Use default project if not specified
    if not project:
        project = get_default_project(ctx)
        if not project:
            click.echo("❌ No project specified. Use --project option or set PROJECT_NAME environment variable.")
            ctx.exit(1)
    
    if not ctx.obj['gemini_client']:
        click.echo("❌ Gemini API key not configured. Set GOOGLE_API_KEY environment variable.")
        ctx.exit(1)
    
    try:
        article_manager = ctx.obj['article_manager']
        gemini_client = ctx.obj['gemini_client']
        
        files = article_manager.get_project_files(project)
        outline_content = article_manager.read_file(files['outline'])
        article_content = article_manager.read_file(files['article'])
        request_text = " ".join(request)
        
        if not request_text.strip():
            click.echo("❌ Please provide a review request. Examples:")
            click.echo("  • review my outline")
            click.echo("  • give feedback on structure")
            click.echo("  • check for gaps in my content")
            click.echo("  • suggest improvements")
            ctx.exit(1)
        
        click.echo(f"🔍 Reviewing '{project}' with request: '{request_text}'")
        click.echo("🤖 Analyzing with Gemini...")
        
        feedback = gemini_client.review_with_context(
            request=request_text,
            outline_content=outline_content,
            article_content=article_content,
            project_name=project
        )
        
        click.echo("\n📋 Review Feedback:")
        click.echo("=" * 60)
        click.echo(feedback)
        click.echo("=" * 60)
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        ctx.exit(1)


@cli.command()
@click.argument('project_name', required=False)
@click.pass_context
def chat(ctx, project_name):
    """Start a conversational session with the writing assistant."""
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
        
        # Get project path and initialize session manager
        project_path = article_manager.get_project_path(project_name)
        session_manager = SessionManager(project_path)
        
        # Initialize conversation workflow
        workflow = ConversationWorkflow(session_manager, article_manager, project_name)
        
        click.echo(f"🤖 Starting conversation session for project: {project_name}")
        click.echo("💬 Type your messages below. Type 'quit' or 'exit' to end the session.")
        click.echo("=" * 60)
        
        # Show current context
        context = session_manager.get_context_summary()
        if context:
            click.echo("📋 Current context:")
            click.echo(context)
            click.echo("=" * 60)
        
        # Start conversation loop
        while True:
            try:
                # Get user input
                user_input = click.prompt("\n💭 You", type=str)
                
                # Check for exit commands
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    click.echo("👋 Ending conversation session. Goodbye!")
                    break
                
                if not user_input.strip():
                    continue
                
                # Run the workflow
                click.echo("🤖 Processing...")
                result = workflow.run(user_input)
                
                # Display response
                if result.get("assistant_response"):
                    click.echo(f"\n🤖 Assistant: {result['assistant_response']}")
                
                # Show any updates
                if result.get("outline_updated"):
                    click.echo("✅ Outline has been updated!")
                
            except KeyboardInterrupt:
                click.echo("\n👋 Session interrupted. Goodbye!")
                break
            except Exception as e:
                click.echo(f"❌ Error in conversation: {e}")
                continue
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        ctx.exit(1)


def main():
    """Main entry point."""
    cli() 
