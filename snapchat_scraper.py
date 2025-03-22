import requests
import re
import json
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.traceback import install

install()
console = Console()


def fetch_snapchat_data(username):
    url = f'https://www.snapchat.com/add/{username}/'
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }
    responses = requests.get(url, headers=headers)
    responses.raise_for_status()
    return responses.text

def extract_json_data(html_content):
    regexp = r'<script\s*id="__NEXT_DATA__"\s*type="application/json">([^<]+)</script>'
    match = re.findall(regexp, html_content)
    if match:
        return json.loads(match[0])
    else:
        raise ValueError("No JSON data found in the HTML content.")

def process_stories(stories):
    if not stories:
        console.print("[bold red]There are no stories to display.[/bold red]")
        return

    table = Table(title="Snapchat Stories", title_style="bold cyan")
    table.add_column("Date", justify="center", style="bold yellow")
    table.add_column("Media Type", justify="center", style="bold magenta")
    table.add_column("URL", justify="left", style="bold green")

    for story in stories:
        try:
            timestamp = datetime.fromtimestamp(int(story['timestampInSec']['value']))
            media_type = "Video" if story['snapMediaType'] else "Image"
            url = story['snapUrls']['mediaUrl']
            table.add_row(str(timestamp), media_type, url)
        except KeyError as e:
            console.print(f"[bold red]Missing data in the story: {e}[/bold red]")

    console.print(table)

def main():
    try:
        username = console.input("[bold blue]Snapchat Username: [/bold blue]")
        html_content = fetch_snapchat_data(username)
        json_data = extract_json_data(html_content)
        if 'props' in json_data and 'pageProps' in json_data['props']:
            page_props = json_data['props']['pageProps']


            if 'story' in page_props and page_props['story']:
                console.print(f"Username: {page_props['userProfile']['publicProfileInfo']['username']}",style='red')

                stories = page_props['story']['snapList']
                process_stories(stories)
            else:
                console.print("[bold red]There are no stories for this user.[/bold red]")

    except requests.RequestException as e:
        console.print(f"Network error: {e}", style="bold red")
    except ValueError as e:
        console.print(f"[bold red]Processing error: {e}[/bold red]")
    except KeyError as e:
        console.print(f"[bold red]Missing expected data in JSON: {e}[/bold red]")

if __name__ == "__main__":
    main()




