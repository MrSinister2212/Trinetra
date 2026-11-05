# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['trinetra_desktop.py'],
    pathex=['D:/VSCODES/Trinetra/backend'],
    binaries=[],
    datas=[('backend/app/modules/data/sites.json', 'app/modules/data'), ('backend/app/modules/data/darkweb_blocklist.json', 'app/modules/data'), ('backend/app/reporting/templates', 'app/reporting/templates'), ('frontend/dist', 'dist')],
    hiddenimports=['uvicorn', 'uvicorn.logging', 'uvicorn.loops', 'uvicorn.loops.auto', 'uvicorn.protocols', 'uvicorn.protocols.http', 'uvicorn.protocols.http.auto', 'uvicorn.protocols.websockets', 'uvicorn.protocols.websockets.auto', 'uvicorn.lifespans', 'uvicorn.lifespans.on', 'aiosqlite', 'greenlet', 'greenlet._greenlet', 'sqlalchemy.dialects.sqlite', 'xhtml2pdf', 'reportlab', 'docx', 'phonenumbers', 'PIL', 'networkx', 'fastapi', 'starlette', 'dns.resolver', 'webview', 'webview.platforms.winforms', 'clr', 'pythonnet', 'jose', 'passlib', 'bcrypt', 'app.routes.ai_routes', 'app.ai.copilot', 'app.ai.llm_engine', 'app.modules.location'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Trinetra',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Trinetra',
)
