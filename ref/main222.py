# test_mySQL_BOT.py
import os
import asyncio
import logging
from dotenv import load_dotenv

from google import genai
from google.genai import types
from google.genai.types import Content, Part

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 환경 변수 로드
load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASS = os.getenv("MYSQL_PASS")
MYSQL_DB = os.getenv("MYSQL_DB")

client = genai.Client(api_key=GOOGLE_API_KEY)

# 서버 파라미터 설정
server_params = StdioServerParameters(
    command="npx",
    args=[
        "-y",
        "@benborla29/mcp-server-mysql"
    ],
    env={
        "MYSQL_HOST": MYSQL_HOST,
        "MYSQL_PORT": MYSQL_PORT,
        "MYSQL_USER": MYSQL_USER,
        "MYSQL_PASS": MYSQL_PASS,
        "MYSQL_DB": MYSQL_DB,
        "ALLOW_INSERT_OPERATION": "False",
        "ALLOW_UPDATE_OPERATION": "False",
        "ALLOW_DELETE_OPERATION": "False",
        "PATH": "C:\\Program Files\\nodejs",
        "NODE_PATH": "C:\\Users\\jhwoo\\AppData\\Roaming\\npm\\node_modules",
        "DEBUG": "true"
    }
)

#----------------------------------------------------------------------------------------------------

# 자동 재시도 및 오류 처리 함수
async def safe_call_tool(session, function_call, user_input, tools):
    """안전한 MCP 호출 함수, 에러 발생 시 재시도 및 다른 방법을 시도."""
    try:
        result = await session.call_tool(function_call.name, arguments=function_call.args)
        tool_output = result.content[0].text

        # 결과가 비었거나 의미 없는 결과일 경우
        if not tool_output.strip() or len(tool_output.strip()) < 10:
            raise ValueError("빈 결과 또는 의미 없는 결과가 반환되었습니다.")

        return tool_output

    except Exception as e:
        # 오류가 발생하면 모델에게 피드백
        error_feedback = f"Error Ocurred:\n{str(e)}"

        error_feedback2 = f"""
        [MCP 규칙] 너는 MCP 도구가 제공되면 직접 쿼리 설명하지 않는다다.
        필요하다면 function_call을 호출해서 답을 알려줘.
        위 명령어는 실패하였으므로, 다시는 사용하지 않는다.
        사용자 질문에 답변하기 위해 테이블 구조나 column을 다시 조회하거나 다른 테이블을 조회하는 query를 사용할 것.
        사용자 질문: {user_input}"""

        print("\n⚠️ 모델에게 에러 피드백 전달 중...\n")

        # Gemini에게 자연어로 답을 요청
        retry_response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                Content(role="user", parts=[Part(text=user_input)]),
                Content(role="model", parts=[Part(function_call=function_call.model_dump())]),
                Content(role="model", parts=[Part(text=error_feedback)]),
                Content(role="user", parts=[Part(text=error_feedback2)])
            ],
            config=types.GenerateContentConfig(
                temperature=0.5,
                tools=tools
            )
        )

        # retry_suggestion = retry_response.text.strip()
        # print("\n⚡ 모델 제안:", retry_response)

        # 모델이 제시한 방법으로 재시도
        if retry_response.candidates[0].content.parts[0].function_call:
            modified_function_call = retry_response.candidates[0].content.parts[0].function_call
            print("modified:", modified_function_call)

            return await safe_call_tool(session, modified_function_call, user_input, tools)

        return retry_response.text


# 메인 실행 함수
async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            
            # 세션 초기화
            await session.initialize()
            
            # MCP 도구 목록을 불러옴
            mcp_tools = await session.list_tools()
            tools = [
                types.Tool(
                    function_declarations=[{
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": {
                            k: v for k, v in tool.inputSchema.items() if k not in ["additionalProperties", "$schema"]
                        },
                    }]
                ) for tool in mcp_tools.tools
            ]
            
            #------------------------------------------------------------------------------------------

            while True:
                # 사용자 입력 받기
                user_input = input("input: ")
                prompt = f"""
                [MCP 규칙] 너는 MCP 도구가 제공되면 직접 쿼리 설명하지 않는다.
                필요하다면 function_call을 호출해서 답을 알려줘.
                사용자 질문: {user_input}"""

                # 모델에 질문 전달
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.3,    
                        tools=tools,
                    ),
                )

                # 함수 호출 존재 여부 확인
                if response.candidates[0].content.parts[0].function_call:
                    function_call = response.candidates[0].content.parts[0].function_call
                    # print("Function call:", function_call)

                    # MCP 도구 실행 및 결과 처리
                    tool_output = await safe_call_tool(session, function_call, user_input, tools)
                    # print(tool_output)

                    # Gemini에게 자연어로 답을 요청
                    followup = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=[
                            Content(role="user", parts=[Part(text=prompt)]),
                            Content(role="model", parts=[Part(function_call=function_call.model_dump())]),
                            Content(role="model", parts=[Part(text=tool_output)]),
                            Content(role="user", parts=[Part(text="위 결과를 요약해서 사용자에게 설명해줘. 꼭 자연어로. 테이블이면 칼럼 설명도 간단히.")])
                        ],
                        config=types.GenerateContentConfig(
                            temperature=0.0
                        )
                    )

                    print("Final response:", followup.text.strip())
                else:
                    print("No function call found in the response.")
                    print(response.text)


# asyncio 이벤트 루프 시작
asyncio.run(run())
