"""
SR University Academic Performance Portal - Server Entrypoint
Provides production WSGI entrypoint and local development runner.
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    print("🚀 SR University Academic Performance Portal running on http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)
