import uvicorn
import webbrowser
import threading
import time

def on_startup():
    # Wait 2 seconds for the FastAPI server to fully start
    time.sleep(2) 
    
    # Automatically open the browser
    webbrowser.open("http://127.0.0.1:8000/docs")

if __name__ == "__main__":
    # Run startup tasks in a background thread
    threading.Thread(target=on_startup).start()
    
    # Run Uvicorn server
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
