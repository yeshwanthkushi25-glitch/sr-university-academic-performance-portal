"""
SR University Academic Performance Portal
Backward-compatible shim delegating to the industrial application factory (create_app).
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    print("🚀 SR University Academic Performance Portal running on http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)
