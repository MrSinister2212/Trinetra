import os
import re
import json
import base64
from typing import List, Dict, Any, Optional, Tuple
import httpx

class LLMEngine:
    """
    TRINETRA Multi-Provider Artificial Intelligence Engine.
    
    Provides true generative Artificial Intelligence for OSINT investigations:
    - Online Cloud LLMs: Google Gemini (1.5 Flash/Pro), OpenAI (GPT-4o, GPT-4o-mini)
    - Local & Air-Gapped LLMs: Ollama (Llama 3, Mistral, Qwen, Llava)
    - Multimodal Vision AI: Visual geolocation clues, architectural style, road signage, OCR
    - Interactive Copilot Chat: Real-time intelligence inquiry & hypothesis testing
    - Defensible Citation Enforcement: Strict adherence to evidence Finding IDs [fnd_id]
    """

    def __init__(
        self,
        gemini_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        ollama_url: Optional[str] = "http://localhost:11434",
        preferred_model: Optional[str] = None
    ):
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.ollama_url = ollama_url or os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.preferred_model = preferred_model

    def update_keys(self, gemini_key: Optional[str] = None, openai_key: Optional[str] = None, ollama_url: Optional[str] = None):
        if gemini_key is not None:
            self.gemini_api_key = gemini_key.strip()
        if openai_key is not None:
            self.openai_api_key = openai_key.strip()
        if ollama_url is not None:
            self.ollama_url = ollama_url.strip()

    async def get_status(self) -> Dict[str, Any]:
        """
        Checks which AI providers and models are active and available.
        """
        ollama_active = False
        ollama_models = []
        try:
            async with httpx.AsyncClient(timeout=1.5) as client:
                res = await client.get(f"{self.ollama_url}/api/tags")
                if res.status_code == 200:
                    ollama_active = True
                    tags_data = res.json()
                    ollama_models = [m.get("name") for m in tags_data.get("models", [])]
        except Exception:
            ollama_active = False

        active_provider = "offline_heuristic"
        if self.gemini_api_key:
            active_provider = "gemini"
        elif self.openai_api_key:
            active_provider = "openai"
        elif ollama_active and len(ollama_models) > 0:
            active_provider = "ollama"

        return {
            "active_provider": active_provider,
            "gemini_available": bool(self.gemini_api_key),
            "openai_available": bool(self.openai_api_key),
            "ollama_available": ollama_active,
            "ollama_url": self.ollama_url,
            "ollama_models": ollama_models
        }

    # ==========================================
    # 1. TEXT GENERATION & COPILOT CHAT
    # ==========================================

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 1500) -> Tuple[str, str]:
        """
        Generates text using the best available configured LLM.
        Returns: (response_text, provider_name)
        """
        # Try Gemini first
        if self.gemini_api_key:
            try:
                text = await self._call_gemini_text(prompt, system_prompt)
                return text, "Google Gemini"
            except Exception as e:
                pass

        # Try OpenAI
        if self.openai_api_key:
            try:
                text = await self._call_openai_text(prompt, system_prompt, max_tokens)
                return text, "OpenAI GPT-4"
            except Exception as e:
                pass

        # Try Local Ollama
        try:
            status = await self.get_status()
            if status["ollama_available"]:
                model = self.preferred_model or (status["ollama_models"][0] if status["ollama_models"] else "llama3")
                text = await self._call_ollama_text(prompt, system_prompt, model)
                return text, f"Ollama ({model})"
        except Exception:
            pass

        return "", "offline"

    async def _call_gemini_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        model = self.preferred_model or "gemini-1.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.gemini_api_key}"
        
        full_content = prompt
        if system_prompt:
            full_content = f"{system_prompt}\n\nUser Query:\n{prompt}"

        payload = {
            "contents": [{"parts": [{"text": full_content}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 2048}
        }

        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
            raise RuntimeError(f"Gemini API error ({resp.status_code}): {resp.text}")

    async def _call_openai_text(self, prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 1500) -> str:
        model = self.preferred_model or "gpt-4o-mini"
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": max_tokens
        }

        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"].strip()
            raise RuntimeError(f"OpenAI API error ({resp.status_code}): {resp.text}")

    async def _call_ollama_text(self, prompt: str, system_prompt: Optional[str], model: str) -> str:
        url = f"{self.ollama_url}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "system": system_prompt or "",
            "stream": False,
            "options": {"temperature": 0.2}
        }
        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                return resp.json().get("response", "").strip()
            raise RuntimeError(f"Ollama API error: {resp.text}")

    # ==========================================
    # 2. MULTIMODAL AI VISION ANALYSIS
    # ==========================================

    async def analyze_image_vision(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg",
        target_name: str = "Uploaded Image"
    ) -> Dict[str, Any]:
        """
        Executes true Multimodal Vision AI for image geolocation and OSINT.
        Extracts:
        - Geolocation clues (architecture, road markings, signage languages, flora)
        - OCR text transcription
        - Object/entity recognition
        - Digital tampering / AI-generation indicators
        """
        vision_prompt = """
You are the TRINETRA Senior OSINT Visual Intelligence & Geolocation Analyst.
Examine this image with deep forensic rigor for open-source intelligence clues:

1. GEOLOCATION & REGIONAL CLUES:
   - Visible architectural styles, building materials, window/roof design
   - Street furniture, road lane markings, traffic light design, driving side (left/right)
   - Utility poles, electrical transformers, power socket types
   - Landscape, vegetation, terrain, sun shadow angle / time of day estimation
   - Languages, scripts, country domain names (.fr, .uk, etc.), telephone area codes
   - Most probable country, region, or city with confidence reasoning

2. VISIBLE TEXT & OCR EXTRACTION:
   - Transcribe ALL visible text, road signs, store names, vehicle plates, logos, badges, slogans.

3. FORENSIC & INTEGRITY ASSESSMENT:
   - Identify whether the image exhibits signs of AI generation (e.g. Midjourney/Stable Diffusion artifacting, unnatural textures, anatomy anomalies, garbled text) or digital compositing.

Format your analysis concisely with clear sections:
- Estimated Location / Country: [Estimation with Confidence %]
- Key Geolocation Indicators: [Bullet points]
- Transcribed Text (OCR): [List of text extracted]
- Forensic Integrity & Manipulation Assessment: [Verdict]
"""
        # 1. Try Gemini Vision
        if self.gemini_api_key:
            try:
                model = "gemini-1.5-flash"
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.gemini_api_key}"
                b64_img = base64.b64encode(image_bytes).decode("utf-8")
                
                payload = {
                    "contents": [{
                        "parts": [
                            {"text": vision_prompt},
                            {"inlineData": {"mimeType": mime_type, "data": b64_img}}
                        ]
                    }],
                    "generationConfig": {"temperature": 0.2, "maxOutputTokens": 2048}
                }
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        analysis_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                        return {
                            "success": True,
                            "provider": "Google Gemini Vision AI",
                            "analysis": analysis_text
                        }
            except Exception as e:
                pass

        # 2. Try OpenAI Vision (GPT-4o)
        if self.openai_api_key:
            try:
                b64_img = base64.b64encode(image_bytes).decode("utf-8")
                url = "https://api.openai.com/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": "gpt-4o-mini",
                    "messages": [{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": vision_prompt},
                            {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{b64_img}"}}
                        ]
                    }],
                    "max_tokens": 1500
                }
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.post(url, json=payload, headers=headers)
                    if resp.status_code == 200:
                        analysis_text = resp.json()["choices"][0]["message"]["content"].strip()
                        return {
                            "success": True,
                            "provider": "OpenAI GPT-4o Vision",
                            "analysis": analysis_text
                        }
            except Exception:
                pass

        # 3. Try Local Ollama Vision (llava or llama3.2-vision)
        try:
            status = await self.get_status()
            if status["ollama_available"]:
                vision_models = [m for m in status["ollama_models"] if "llava" in m.lower() or "vision" in m.lower()]
                if vision_models:
                    model = vision_models[0]
                    b64_img = base64.b64encode(image_bytes).decode("utf-8")
                    url = f"{self.ollama_url}/api/generate"
                    payload = {
                        "model": model,
                        "prompt": vision_prompt,
                        "images": [b64_img],
                        "stream": False
                    }
                    async with httpx.AsyncClient(timeout=60.0) as client:
                        resp = await client.post(url, json=payload)
                        if resp.status_code == 200:
                            return {
                                "success": True,
                                "provider": f"Local Ollama ({model})",
                                "analysis": resp.json().get("response", "").strip()
                            }
        except Exception:
            pass

        return {
            "success": False,
            "provider": "Offline",
            "analysis": "No vision-capable Artificial Intelligence API configured. Configure a Google Gemini API key, OpenAI API key, or run Ollama with 'llava' locally for visual geolocation and deep forensic scene analysis."
        }

    # ==========================================
    # 3. INTERACTIVE INVESTIGATOR COPILOT CHAT
    # ==========================================

    async def chat_with_copilot(
        self,
        user_query: str,
        findings: List[Dict[str, Any]],
        case_info: Optional[Dict[str, Any]] = None,
        history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Interactive OSINT conversational assistant.
        Uses findings context and case parameters to answer investigator questions,
        uncover hidden connections, and recommend high-value next steps.
        """
        case_title = case_info.get("title", "Active Investigation") if case_info else "Active Investigation"
        findings_context = "\n".join([
            f"- [{f.get('id')}] [{f.get('module', '').upper()}] Source: {f.get('source')} | Target: {f.get('target')} | Evidence: {f.get('evidence_snippet')} | Confidence: {round(float(f.get('confidence', 0.5))*100)}%"
            for f in findings[:40]
        ])

        system_prompt = f"""
You are the TRINETRA OSINT Intelligence Analyst Copilot.
You assist human intelligence analysts, journalists, and cybersecurity investigators.
Case Dossier: {case_title}

EVIDENCE BASE ({len(findings)} Findings):
{findings_context if findings_context else "No findings collected yet."}

OPERATIONAL DOCTRINE:
1. Always cite Finding IDs in brackets (e.g. [fnd_123]) when making claims grounded in collected evidence.
2. If the user asks about location or identity, synthesize clues from username habits, email domain infrastructure, phone numbering allocations, and image GPS/EXIF.
3. Be professional, analytical, objective, and hypothesis-driven. Clearly distinguish verified facts from speculative leads.
4. When suggesting next steps, provide specific actionable OSINT techniques and queries.
"""
        response_text, provider = await self.generate_text(user_query, system_prompt, max_tokens=1500)
        if not response_text:
            response_text = (
                f"Analyst Copilot initialized in offline mode. {len(findings)} findings are indexed in memory. "
                "To enable deep neural reasoning and natural language conversational intelligence, configure a Gemini or OpenAI API key, or launch Ollama locally on port 11434."
            )

        return {
            "response": response_text,
            "provider": provider,
            "findings_referenced": len(findings)
        }

# Global Singleton Instance
ai_engine = LLMEngine()
