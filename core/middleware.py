import sys
from django.conf import settings
from django.http import HttpResponse
from django.template import Template, Context
from django.utils.timezone import now
from gopher.services import get_random_header


class BrowserCheckMiddleware:
    """
    Middleware that checks for a 'd_sensor' cookie.
    If missing, it returns a lightweight HTML page that sets the cookie via JS and reloads.
    This filters out dumb bots/scrapers that don't execute JS.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.whitelist_paths = [
            "/static/",
            "/robots.txt",
            "/favicon.ico",
        ]
        if hasattr(settings, "BROWSER_CHECK_WHITELIST_PATHS"):
            self.whitelist_paths.extend(settings.BROWSER_CHECK_WHITELIST_PATHS)

    def __call__(self, request):
        # Bypass for django tests or command-line runs
        is_testing = getattr(settings, "TESTING", False) or (
            len(sys.argv) > 1 and sys.argv[1] == "test"
        )
        if is_testing:
            return self.get_response(request)

        path = request.path_info

        # 1. Bypass whitelist
        for w in self.whitelist_paths:
            if path.startswith(w) or path == w:
                return self.get_response(request)

        # 2. Check for cookie
        if "d_sensor" in request.COOKIES:
            return self.get_response(request)

        # 3. Serve Challenge Page (Gopher theme-aware)
        current_theme = "green"
        if hasattr(request, "session"):
            current_theme = request.session.get("theme", "green")

        # Select colors based on theme to match go4hive styling
        if current_theme == "amber":
            text_color = "#ffb000"
            dim_color = "#a37200"
            highlight_color = "#3b2a00"
        elif current_theme == "white":
            text_color = "#e0e0e0"
            dim_color = "#888888"
            highlight_color = "#333333"
        else:  # green/default
            text_color = "#00ff41"
            dim_color = "#008f11"
            highlight_color = "#003b00"

        # Fetch random ASCII art header
        try:
            ascii_art = get_random_header()
        except Exception:
            ascii_art = r"""  ____  ___    _  _     _   _ _____     _______
 / ___|/ _ \  | || |   | | | |_ _\ \   / / ____|
| |  _| | | | | || |_  | |_| || | \ \ / /|  _|
| |_| | |_| | |__   _| |  _  || |  \ V / | |___
 \____|\\___/     |_|   |_| |_|___|  \_/  |_____|"""

        html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Go4Hive Security Check</title>
    <style>
        :root {
            --bg-color: #0c0c0c;
            --text-color: {{ text_color }};
            --dim-color: {{ dim_color }};
            --highlight-color: {{ highlight_color }};
            --font-family: 'Courier New', Courier, monospace;
        }
        body {
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: var(--font-family);
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            box-sizing: border-box;
            overflow: hidden;
            position: relative;
        }
        /* Scanline effect */
        body::before {
            content: " ";
            display: block;
            position: fixed;
            top: 0;
            left: 0;
            bottom: 0;
            right: 0;
            background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.15) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.03), rgba(0, 255, 0, 0.01), rgba(0, 0, 255, 0.03));
            z-index: 1000;
            background-size: 100% 4px, 3px 100%;
            pointer-events: none;
        }
        .container {
            border: 1px solid var(--text-color);
            padding: 30px;
            background-color: #121212;
            max-width: 600px;
            width: 100%;
            box-shadow: 0 0 15px var(--text-color);
            box-sizing: border-box;
        }
        .header-art {
            color: var(--text-color);
            margin-bottom: 20px;
            text-align: center;
        }
        pre {
            white-space: pre-wrap;
            word-wrap: break-word;
            font-size: 0.9em;
            margin: 0;
        }
        .header-art pre {
            white-space: pre;
            font-size: 0.8em;
            display: inline-block;
            text-align: left;
        }
        .status-box {
            border: 1px dashed var(--dim-color);
            padding: 15px;
            margin: 20px 0;
            background-color: var(--highlight-color);
        }
        .cursor {
            display: inline-block;
            width: 10px;
            height: 1.2em;
            background-color: var(--text-color);
            vertical-align: middle;
            animation: blink 1s step-start infinite;
        }
        @keyframes blink {
            50% { opacity: 0; }
        }
        .progress-bar {
            width: 100%;
            background-color: var(--highlight-color);
            border: 1px solid var(--dim-color);
            height: 10px;
            margin-top: 10px;
            position: relative;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background-color: var(--text-color);
            width: 0%;
            transition: width 2s linear;
        }
    </style>
    <script>
        // Set the cookie via JS. max-age=3600 matches ecobank's 1 hour limit.
        document.cookie = "d_sensor=" + Date.now() + "; path=/; max-age=3600; SameSite=Lax";
        window.onload = function() {
            var fill = document.querySelector('.progress-fill');
            if (fill) {
                setTimeout(function() {
                    fill.style.width = '100%';
                }, 100);
            }
            setTimeout(function() {
                window.location.reload();
            }, 2000);
        };
    </script>
</head>
<body>
    <div class="container">
        <div class="header-art">
            <pre>{{ ascii_art }}</pre>
            <div style="font-size: 0.8em; margin-top: 5px; color: var(--dim-color);">
                --- A GOPHER-LIKE INTERFACE FOR HIVE BLOCKCHAIN ---
            </div>
        </div>

        <div style="text-align: center; font-weight: bold; margin-bottom: 10px;">
            [ SYSTEM ] SECURITY CHALLENGE
        </div>

        <div class="status-box">
            <pre>VERIFYING USER BROWSER<span class="cursor"></span>
STATUS: TESTING JAVASCRIPT CAPABILITIES...
ACTION: RESOLVING CHALLENGE TO SET D_SENSOR COOKIE
REDIRECTING IN 2 SECONDS...</pre>
        </div>

        <div class="progress-bar">
            <div class="progress-fill"></div>
        </div>

        <div style="font-size: 0.8em; color: var(--dim-color); text-align: center; margin-top: 15px;">
            Go4Hive Anti-Scrape Protection | Date: {{ current_time }} UTC
        </div>
    </div>
</body>
</html>"""

        context = {
            "text_color": text_color,
            "dim_color": dim_color,
            "highlight_color": highlight_color,
            "ascii_art": ascii_art,
            "current_time": now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        t = Template(html_template)
        c = Context(context)
        html = t.render(c)

        return HttpResponse(html, content_type="text/html")
