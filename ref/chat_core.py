# 레전드레전드
import os
import asyncio
from typing import Any
from dotenv import load_dotenv
from dataclasses import dataclass, field

from google import genai
from google.genai import types
from google.genai.types import Content, Part

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

@dataclass
class Chat:
    history = []
    system_prompt: str = """
    너는 MySQL 마스터 어시스턴트다.
    너의 임무는 사용할 수 있는 도구들을 이용해 SQL 쿼리를 실행하고, 그 결과를 사용자에게 전달하는 것이다.
    [MCP 규칙] MCP 도구가 제공되면, 쿼리를 설명하지 말고 즉시 function_call을 호출해라.
    """
    history.append(Content(role="user", parts=[Part(text=system_prompt)]))

    def __init__(self, client):
        self.client = client

    async def process_query(self, session: ClientSession, query: str):

        # Get tools from MCP session and convert to Gemini Tool objects
        mcp_tools = await session.list_tools()
        tools = [
            types.Tool(
                function_declarations=[
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": {
                            k: v
                            for k, v in tool.inputSchema.items()
                            if k not in ["additionalProperties", "$schema"]
                        },
                    }
                ]
            )
            for tool in mcp_tools.tools
        ]

        self.history.append(Content(role="user", parts=[Part(text=query)]))

        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=self.history,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    tools=tools,
                ),
            )

            # Gemini가 함수 호출을 요구하는지 확인
            for part in response.candidates[0].content.parts:
                if hasattr(part, "function_call"):
                    fn = part.function_call
                    if fn is None:
                        # print("No function call received from Gemini. Responding with text only.")
                        # print(response.candidates[0].content.parts[0].text)
                        continue
                    tool_result = await session.call_tool(fn.name, fn.args)
                    text_result = tool_result.content[0].text if isinstance(tool_result.content, list) else tool_result.content
                    # print(text_result)

                    self.history.append(
                        Content(role="model", parts=[Part(text=text_result)])
                    )
                    self.history.append(
                        Content(role="user",parts=[Part(text="자연어로 답을 설명해줘.")])
                    )

                    response = self.client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=self.history,
                        config=types.GenerateContentConfig(
                            temperature=0.5,
                        ),
                    )
        except Exception as e:
                print("🔥 Gemini 처리 중 에러 발생:", e)

        print("response:",response.text)
        self.history.append(Content(role="user", parts=[Part(text=query)]))

    async def chat_loop(self, session: ClientSession):
        while True:
            query = input("\nQuery: ").strip()
            await self.process_query(session, query)

    async def run(self,server_params):
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                await self.chat_loop(session)

# chat = Chat()
# asyncio.run(chat.run(server_params))
