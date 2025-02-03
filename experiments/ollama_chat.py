import asyncio
from ollama import AsyncClient
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live
from rich.text import Text
from rich.style import Style

# Initialize rich console
console = Console()

async def chat_with_ollama(model: str, prompt: str) -> str:
    """
    Chat with an Ollama model with pretty formatting
    
    Args:
        model: Name of the Ollama model to use (e.g., 'llama2', 'mistral', 'codellama')
        prompt: The question or prompt to send to the model
    
    Returns:
        The model's response as a string
    """
    try:
        # Create an async client
        client = AsyncClient()
        
        # Create a text buffer for the response
        response_buffer = Text()
        
        # Create a panel for the response
        response_panel = Panel(
            response_buffer,
            title="[bold blue]AI Response",
            border_style="blue",
            padding=(1, 2),
            expand=True
        )
        
        # Use Live display for real-time updates
        with Live(response_panel, console=console, refresh_per_second=4) as live:
            async for response in await client.chat(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                stream=True
            ):
                if response.message:
                    # Append new content to the buffer
                    response_buffer.append(response.message.content)
                    # Update the panel with new content
                    live.update(response_panel)
        
        return "Response completed"
    
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        return f"Error: {str(e)}"

def print_header(model: str, prompt: str):
    """Print a nicely formatted header"""
    console.print("\n")
    console.print(Panel(
        f"[bold cyan]Model:[/bold cyan] {model}\n"
        f"[bold cyan]Prompt:[/bold cyan] {prompt}",
        title="[bold green]Chat Session",
        border_style="green",
        padding=(1, 2)
    ))
    console.print("\n")

async def main():
    parser = argparse.ArgumentParser(description='Chat with an Ollama model')
    parser.add_argument('--model', default='deepseek-r1:70b', help='Name of the Ollama model to use')
    parser.add_argument('--prompt', required=True, help='Question or prompt for the model')
    parser.add_argument('--markdown', action='store_true', help='Render response as markdown')
    
    args = parser.parse_args()
    
    # Clear the screen
    console.clear()
    
    # Print header
    print_header(args.model, args.prompt)
    
    # Get response
    await chat_with_ollama(args.model, args.prompt)
    
    # Add final newline
    console.print("\n")

if __name__ == "__main__":
    asyncio.run(main())
