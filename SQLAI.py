import os
import re
import sys
import shutil
import asyncio
import pymysql

from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, pyqtSignal, QObject, pyqtSlot

from google import genai
from google.genai import types
from google.genai.types import Content, Part

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from ui_SQLAI import Ui_MainWindow
from dotenv import load_dotenv, set_key

system_prompt: str = """
    너는 MySQL 마스터 어시스턴트다.
    너의 임무는 사용할 수 있는 도구들을 이용해 SQL 쿼리를 실행하고, 그 결과를 사용자에게 전달하는 것이다.
    [MCP 규칙] MCP 도구가 제공되면, 쿼리를 설명하지 말고 즉시 function_call을 호출해라.
    """

dotenv_path = ".env"

# 대화 처리 관련 클래스 (chat_core.py)
class ChatCore(QObject):
    update_message_signal = pyqtSignal(str)
    process_query_signal = pyqtSignal(str)  # 쿼리 전달 시그널
  
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.history = []
        self.history.append(Content(role="user", parts=[Part(text=system_prompt)]))

    async def handle_query(self, query: str):
        # Get tools from MCP session and convert to Gemini Tool objects
        mcp_tools = await self.session.list_tools()
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
        print("Query:", query)

        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=self.history,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    tools=tools,
                ),
            )

            # candidates[0] 안의 content가 리스트일 수도 있음
            content = response.candidates[0].content
            if isinstance(content, list):
                parts = content
            else:
                parts = content.parts if hasattr(content, "parts") else []

            for part in parts:
                if hasattr(part, "function_call"):
                    fn = part.function_call
                    if fn is None:
                        continue
                    tool_result = await self.session.call_tool(fn.name, fn.args)
                    text_result = (
                        tool_result.content[0].text if isinstance(tool_result.content, list) else tool_result.content
                    )

                    self.history.append(Content(role="model", parts=[Part(text=text_result)]))
                    self.history.append(Content(role="user", parts=[Part(text="자연어로 답을 설명해줘.")]))
                    
                    response = self.client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=self.history,
                        config=types.GenerateContentConfig(
                            temperature=0.5,
                        ),
                    )

            print(f"Gemini:{response.text}")
            # self.update_message_signal.emit(f"Response: {markdown_to_html(response.text)}")
            self.update_message_signal.emit(f"Response: {response.text}")

        except Exception as e:
            print("🔥 Gemini 처리 중 에러 발생:", e)
            self.update_message_signal.emit(f"🔥 Gemini 처리 중 에러 발생: {e}")
            self.handle_query(f"🔥 Gemini 처리 중 에러 발생: {e}")


# PyQt 관련 UI 클래스 (pyQT_bot.py)
class WorkerThread(QThread):
    output_signal = pyqtSignal(str)
    send_query_signal = pyqtSignal(str)

    def __init__(self, client, server_params):
        super().__init__()
        self.client = client
        self.server_params = server_params
        self.query_queue = asyncio.Queue()
        self.chat = ChatCore(client)

        # 슬롯 연결
        self.send_query_signal.connect(self.enqueue_query)
        self.chat.update_message_signal.connect(self.output_signal)
        
    def stop(self):
        # 이 메서드를 호출하면 스레드가 종료되도록 처리
        self.terminate()  # 종료 신호 보내기

    @pyqtSlot(str)
    def enqueue_query(self, query):
        asyncio.run_coroutine_threadsafe(self.query_queue.put(query), self.loop)

    def run(self):
        # PyQt run은 async 못 씀. 대신 asyncio 이벤트 루프 따로 돌림
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.async_run())

    async def async_run(self):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                self.chat.session = session

                while True:
                    query = await self.query_queue.get()
                    await self.chat.handle_query(query)



class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.Load_push.clicked.connect(self.connect_and_load_databases)     # Load_push 버튼 클릭 연결
        self.ui.Conn_push.clicked.connect(self.toggle_connection)              # Conn_push 버튼 클릭 연결
        self.ui.Send_push.clicked.connect(self.send_query)                     # Send_push 버튼 클릭 연결



    #### 1. Load_Push 버튼 클릭 ####
    def connect_and_load_databases(self):
        # 현재 입력된 데이터를 토대로 정보 사용
        self.host = self.ui.HOST_edit.text().strip()
        self.port = self.ui.PORT_edit.text().strip()
        self.user = self.ui.USER_edit.text().strip()
        self.pw = self.ui.PASS_edit.text().strip()
        
        # 환경 정보를 불러옴
        load_dotenv(dotenv_path)
        set_key(dotenv_path, "HOST", self.host)
        set_key(dotenv_path, "PORT", self.port)
        set_key(dotenv_path, "USER", self.user)
        set_key(dotenv_path, "PASS", self.pw)

        try:
            port = int(self.port)
        except ValueError:
            QMessageBox.warning(self, "Invalid Port", "Port must be a number.")
            return

        # 정보를 이용해 접속 후 DB 조회
        try:
            conn = pymysql.connect(host=self.host, port=port, user=self.user, password=self.pw)
            cursor = conn.cursor()
            cursor.execute("SHOW DATABASES;")
            databases = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()

            self.ui.DB_combo.clear()
            self.ui.DB_combo.addItems(databases)

            QMessageBox.information(self, "Success", f"{len(databases)}개의 DB를 불러왔습니다.")

        except pymysql.err.OperationalError as e:
            QMessageBox.critical(self, "Login Failed", f"MySQL 로그인 실패:\n{str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"예기치 못한 오류 발생:\n{str(e)}")



    #### 2. Conn_push 버튼 클릭 ####
    def toggle_connection(self):
        # 이미 연결된 상태라면, 연결 끊기
        if self.ui.Conn_push.text() == "Connect":
            self.connect_to_selected_database()
        else:
            # 연결 된 상태라면, 연결 종료
            self.disconnect_database()

    #### 2-1. 연결 ####
    def connect_to_selected_database(self):
        # 환경 변수 설정
        client, server_params = self.build_server_params()
        if not client or not server_params:
            return
        self.worker = WorkerThread(client, server_params)
        self.worker.output_signal.connect(self.update_output_text)
        self.worker.start()

    ## 2-1-1. 환경 변수 설정 ##
    def build_server_params(self):
        
        if not check_node_and_npx():
            QMessageBox.critical(self, "환경 오류", "Node.js 또는 npx가 설치되어 있지 않습니다.\nhttps://nodejs.org 에서 설치해주세요.")
            return None, None
        
        # 환경 정보를 불러옴
        load_dotenv(dotenv_path)

        # 입력한 내용을 토대로
        database = self.ui.DB_combo.currentText()

        # 환경정보에서 Gemini api key를 불러옴.
        gemini_key = os.getenv("GEMINI_API_KEY")

        # 없으면 생성
        if not gemini_key:
            key, ok = QInputDialog.getText(self, "Gemini API Key 입력", "Gemini API Key가 없습니다.\n입력해주세요:")
            if ok and key:
                gemini_key = key.strip()
                set_key(dotenv_path, "GEMINI_API_KEY", gemini_key)
            else:
                QMessageBox.critical(self, "Key Missing", "Gemini API Key가 입력되지 않았습니다.")
                return None

            # ✅ 예외처리 추가!
        try:
            client = genai.Client(api_key=gemini_key)
        except Exception as e:
            QMessageBox.critical(self, "Gemini Init Error", f"Gemini Client 생성 실패:\n{e}")
            return None, None

        # 환경 정보를 이용해 MCP server params를 생성성
        env = {
            "MYSQL_HOST": self.host,
            "MYSQL_PORT": self.port,
            "MYSQL_USER": self.user,
            "MYSQL_PASS": self.pw,
            "MYSQL_DB": database,
            "ALLOW_INSERT_OPERATION": "true",
            "ALLOW_UPDATE_OPERATION": "true",
            "ALLOW_DELETE_OPERATION": "true",
            "DEBUG": "true"
        }

        self.ui.Output_text.append("🔥 MCP 환경 변수 준비 완료.")
        # self.Conn_push.setEnabled(False)
        
        # 연결 버튼 텍스트 변경
        self.ui.Conn_push.setText("Disconnect")

        # MCP서버 연결에 필요한 client, server params를 return
        return client, StdioServerParameters(
            command="npx",
            args=["-y", "@benborla29/mcp-server-mysql"],
            env=env
        )

    # 출력
    def update_output_text(self, message):
        # html = markdown_to_html(message)
        self.ui.Output_text.setHtml(message)

    ## 2-2. 연결 해제 ##
    def disconnect_database(self):
        # 스레드 종료 코드 (예: worker 종료)
        if hasattr(self, 'worker'):
            self.worker.stop()  # 스레드 종료 요청
            # self.worker.terminate()  # worker 스레드를 종료
            # self.worker.join()  # 스레드가 종료될 때까지 기다리기

        # 연결 끊기 후 처리 (필요에 따라)
        self.update_output_text("연결이 종료되었습니다.")
        # 버튼 텍스트 변경
        self.ui.Conn_push.setText("Connect")



    #### 3. Send_push 버튼 클릭 ####
    def send_query(self):
        user_query = self.ui.Input_edit.toPlainText().strip()
        if not user_query:
            QMessageBox.warning(self, "빈 쿼리", "쿼리를 입력해주세요.")
            return
        self.ui.Output_text.append(f"Query: {user_query}")
        if hasattr(self, 'worker'):
            self.worker.send_query_signal.emit(user_query)
        self.ui.Input_edit.setText("")  # 이게 핵심이다, 브로

    def run_query(self, query):
        client, server_params = self.build_server_params()
        if not server_params:
            return
        
        # `query`를 WorkerThread에 전달하도록 수정
        self.worker = WorkerThread(server_params, client, query)
        self.worker.output_signal.connect(self.update_output_text)
        self.worker.start()
    
    def update_output_text(self, message):
        # 결과 메시지를 Output_text에 출력
        self.ui.Output_text.append(message)

def check_node_and_npx():
    node_exists = shutil.which("node") is not None
    npx_exists = shutil.which("npx") is not None
    return node_exists and npx_exists

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
