Set WshShell = CreateObject("WScript.Shell")

' Change directory to script folder
strScriptPath = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\"))
WshShell.CurrentDirectory = strScriptPath

' Run FastAPI Backend silently (0 = hide window, false = do not wait for exit)
WshShell.Run "python -m uvicorn backend.api:app --host 127.0.0.1 --port 8000", 0, false

' Run User Streamlit App silently
WshShell.Run "python -m streamlit run user_app/app.py --server.port 8501 --server.headless true", 0, false

' Run Admin Streamlit App silently
WshShell.Run "python -m streamlit run admin_app/app.py --server.port 8502 --server.headless true", 0, false
