# Try to import FastAPI app
try:
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    sys.path.insert(0, os.path.join(current_dir, 'backend'))
    
    from backend.main import app
    
    # Configure for larger file uploads
    import uvicorn
    from uvicorn.middleware.wsgi import WSGIMiddleware
    
    application = app
    
except Exception as e:
    print(f"Failed to import FastAPI app: {e}")
    
    # Fallback WSGI app
    def application(environ, start_response):
        status = '200 OK'
        headers = [('Content-Type', 'application/json')]
        start_response(status, headers)
        return [b'{"message": "CuraNet Basic WSGI is working!", "status": "success"}']