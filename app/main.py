from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

from app.data import loader
from app.audit import ppc, seo
from app.ai import recommendations as rec_engine

load_dotenv()

app = FastAPI(title="Komacut Growth Audit", docs_url="/docs")

_templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

# Module-level cache for audit results so /chat and /export can use them
_audit_cache: dict | None = None


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return _templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/audit/run")
async def audit_run():
    global _audit_cache
    try:
        data = loader.load()
        ppc_findings = ppc.run(data)
        seo_findings = seo.run(data)
        _audit_cache = {"ppc": ppc_findings, "seo": seo_findings}
        return _audit_cache
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/audit/recommendations")
async def audit_recommendations():
    if _audit_cache is None:
        raise HTTPException(status_code=400, detail="Run /audit/run first")
    try:
        recs = rec_engine.generate(_audit_cache["ppc"], _audit_cache["seo"])
        return {"recommendations": recs}
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
