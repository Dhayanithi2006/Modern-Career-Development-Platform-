import asyncio
import httpx

async def main():
    async with httpx.AsyncClient() as client:
        # We simulate what the browser does on preflight and POST
        res = await client.options("http://localhost:8000/api/v1/assistant/sessions/1/messages", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "POST"})
        print("OPTIONS:", res.status_code, res.headers.get("access-control-allow-origin"))
        
        res = await client.post("http://localhost:8000/api/v1/assistant/sessions/1/messages", json={"content": "hello"}, headers={"Origin": "http://localhost:3000", "Authorization": "Bearer fake"})
        print("POST:", res.status_code, res.headers.get("access-control-allow-origin"))

asyncio.run(main())
