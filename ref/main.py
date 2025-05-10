# test_mySQL_BOT.py
import os
import asyncio
from dotenv import load_dotenv

from google import genai
from google.genai import types
from google.genai.types import Content, Part

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
MYSQL_HOST=os.getenv("MYSQL_HOST")
MYSQL_PORT=os.getenv("MYSQL_PORT")
MYSQL_USER=os.getenv("MYSQL_USER")
MYSQL_PASS=os.getenv("MYSQL_PASS")
MYSQL_DB=os.getenv("MYSQL_DB")

client = genai.Client(api_key=GOOGLE_API_KEY)

# Create server parameters for stdio connection
server_params = StdioServerParameters(
      command = "npx",
      args = [
        "-y",
        "@benborla29/mcp-server-mysql"
      ],
      env = {
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

#------------------------------------------------------------------------------------

async def safe_call_tool(session, function_call,prompt, tools):
    """안전한 MCP 호출 함수, 에러 발생 시 재시도 및 다른 방법을 시도."""
    # MCP tool 실행
    try:
        # MCP 도구 호출 시도
        result = await session.call_tool(
            function_call.name, arguments=function_call.args
        )
        return result.content[0].text

    except Exception as e:
        # 에러 메시지를 출력하고
        print("도구 호출 중 오류 발생:", str(e))

        # 모델에게 에러 내용을 다시 질문해보자
        # error_feedback = f"Error Ocuured!\n{str(e)}"
        print("\n⚠️ 모델에게 에러 피드백 전달 중...\n")

        # 새로운 프롬프트로 오류 피드백 전달
        retry_response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=str(function_call.model_dump())+'\n'+f"result:{str(e)}"+'\n'+prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,  # 좀 더 안정적으로
                tools=tools
            ),
        )

        # 모델이 제시한 방법으로 재시도
        if retry_response.candidates[0].content.parts[0].function_call:
            modified_function_call = retry_response.candidates[0].content.parts[0].function_call
            print("modified:", modified_function_call)

            return await safe_call_tool(session, modified_function_call, prompt, tools)


async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection between client and server
            await session.initialize()

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
            while True:
                user_input = input("input:")
                prompt = f"""
                [MCP 규칙] 너는 MCP 도구가 제공되면 직접 쿼리 설명하지 말고 function_call을 호출해.
                사용자 질문: {user_input}""" 

                # Send request to the model with MCP function declarations
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.3,
                        tools=tools,
                    ),
                )

                # Check for a function call
                if response.candidates[0].content.parts[0].function_call:
                    function_call = response.candidates[0].content.parts[0].function_call
                    print("Function call:", function_call)

                    # MCP tool 실행
                    tool_output = await safe_call_tool(session, function_call,prompt, tools)
                    # try:
                    #     # MCP 도구 호출 시도
                    #     result = await session.call_tool(
                    #         function_call.name, arguments=function_call.args
                    #     )
                    #     tool_output = result.content[0].text
                    #     print(tool_output)

                    # except Exception as e:
                    #     # 에러 메시지를 출력하고
                    #     print("도구 호출 중 오류 발생:", str(e))
                    #     print(tool_output)

                    #     # 모델에게 에러 내용을 다시 질문해보자
                    #     error_feedback = f"이 쿼리를 실행하려 했는데 오류가 났어:\n{str(e)}\n이유가 뭘까?"
                    #     print("\n⚠️ 모델에게 에러 피드백 전달 중...\n")

                    #     # 새로운 프롬프트로 오류 피드백 전달
                    #     retry_response = client.models.generate_content(
                    #         model="gemini-2.0-flash",
                    #         contents=error_feedback,
                    #         config=types.GenerateContentConfig(
                    #             temperature=0.2,  # 좀 더 안정적으로
                    #             tools=tools
                    #         ),
                    #     )

                    #     print(retry_response.text)


                    # Gemini한테 자연어로 대답하게 요청
                    followup = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=[
                            Content(role="user", parts=[Part(text=prompt)]),
                            Content(role="model", parts=[Part(function_call=function_call.model_dump())]),
                            Content(role="model", parts=[Part(text=tool_output)]),  # or Part(function_response=...) if applicable
                            Content(role="user", parts=[Part(text="답을 알려줘.")])  # 여기가 핵심

                        ],
                        config=types.GenerateContentConfig(
                            temperature=0.5
                        )
                    )

                    print("Final response:", followup.text)
                else:
                    print("No function call found in the response.")
                    print(response.text)


# Start the asyncio event loop and run the main function
asyncio.run(run())