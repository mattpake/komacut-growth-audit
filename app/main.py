import os
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, Response, RedirectResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

from app.data import loader
from app.audit import ppc, seo
from app.ai import recommendations as rec_engine, chat as chat_engine
from app.auth import ubersuggest_oauth as ub_oauth
from app.export import xlsx as xlsx_builder
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []

load_dotenv()

app = FastAPI(title="Komacut Growth Audit", docs_url="/docs")

_templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

# Module-level cache for audit results so /chat and /export can use them
_audit_cache: dict | None = None


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return _templates.TemplateResponse(request, "index.html")


@app.get("/health")
async def health():
    return {"status": "ok"}


def _callback_uri() -> str:
    base = os.environ.get("APP_BASE_URL", "http://localhost:8000").rstrip("/")
    return f"{base}/auth/ubersuggest/callback"


@app.get("/auth/ubersuggest/connect")
async def ubersuggest_connect():
    try:
        url = ub_oauth.build_auth_url(_callback_uri())
        return RedirectResponse(url)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Could not reach Ubersuggest OAuth: {e}")


@app.get("/auth/ubersuggest/callback")
async def ubersuggest_callback(code: str = "", state: str = "", error: str = ""):
    if error:
        return RedirectResponse("/?ubersuggest=error")
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code or state")
    try:
        ub_oauth.exchange_code(code, state)
        return RedirectResponse("/?ubersuggest=connected")
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.get("/auth/ubersuggest/status")
async def ubersuggest_status():
    return {"connected": ub_oauth.is_connected()}


@app.post("/auth/ubersuggest/disconnect")
async def ubersuggest_disconnect():
    ub_oauth.disconnect()
    return {"connected": False}


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


@app.get("/export/xlsx")
async def export_xlsx():
    if _audit_cache is None:
        raise HTTPException(status_code=400, detail="Run /audit/run first")
    try:
        data = xlsx_builder.build(_audit_cache["ppc"], _audit_cache["seo"])
        return Response(
            content=data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=komacut_growth_audit.xlsx"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
async def chat(req: ChatRequest):
    if _audit_cache is None:
        raise HTTPException(status_code=400, detail="Run /audit/run first")
    try:
        answer = chat_engine.reply(req.message, _audit_cache, req.history)
        return {"reply": answer}
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
