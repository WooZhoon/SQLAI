# SQLAI
MySQL Manager with Gemini api
![image](https://github.com/user-attachments/assets/8a28b063-b657-4161-a35e-503cf33f1b2f)

This is a MySQL Manager utilizing the Gemini API. The GUI was built using PyQt5, and it was developed with prompts written in Korean. 

~Although it's called a MySQL Manager, the problem is that it currently only supports queries. I'll fix this soon.~

[250511] Problem fixed. Let's be careful with uppercase and lowercase letters.

## 🔬References
- 🔗 [MySQL MCP Server](https://github.com/benborla/mcp-server-mysql)
- 🔗 [SQL AI Agent](https://github.com/bitswired/demos/tree/main/projects/introduction-to-mcp-with-sql-agent)
- 🔗 [SQL AI Agent (📼 Youtube Link)](https://www.youtube.com/watch?v=cxl3tPWLOQ8)
- 🔗 [Using MCP Server with Gemini API](https://ai.google.dev/gemini-api/docs/function-calling?hl=ko&authuser=1&example=chart#use_model_context_protocol_mcp)

I referred heavily to the references above. Thank you so much!

---

## 💾 Requirements
### ✅ Python Environment
- `python==3.12.3`

`pip` must be up-to-date:
```bash
python -m pip install --upgrade pip
```

### ✅ Python Dependencies
  All required packages are listed in `requirements.txt`. Install with:
  ```bash
  pip install -r requirements.txt
  ```
  Packages included:
  - `PyQt5==5.15.11` — GUI framework
  - `pymysql==1.1.1` — MySQL connector
  - `google-genai==1.12.1` — Gemini API
  - `python-dotenv==1.1.0` — Load .env configs

### 🔐 Gemini API key
  This app uses Gemini via Google's google-generativeai package.
  
  Get your API key from the link following: 🔗 https://aistudio.google.com/apikey

### ⚙️ Node.js Runtime (Required)
  The app relies on Node.js for running the MCP-Gemini bridge (for natural language to SQL translation).
  - Required: Node.js `v18` or higher
  - npx must be available
  Install from: 🔗 https://nodejs.org
  Verify installation:
  ```bash
  node -v   # should be >= v18
  npx -v    # should return a version
  ```

## 🪄 How to Use

Using this is dead simple. Just run `SQLAI.py` or `SQLAI.exe`, and you'll see a window like the one below:

![image](https://github.com/user-attachments/assets/d355e531-f888-4c24-8864-00350383cc4c)

Enter the `HOST`, `PORT`, `USER`, and `PASSWORD`, then click the **'LOAD DB'** button to fetch available databases.  
Select the DB you want to connect to, then hit the **Connect** button.

If this is your first time using the app, you'll need to enter your Gemini API key.  
The entered API key will be saved in an environment variable file and automatically loaded in the future.

![image](https://github.com/user-attachments/assets/108ddb6b-e713-4a53-bc5b-58b71e9312f5)

Once the connection is successful, you’ll see a **Ready** status like below:  
![image](https://github.com/user-attachments/assets/4cec9336-c928-424a-9347-7cbc1ff3b123)

You can now type a message in the input field below and click the **Send** button.  
The entered SQL query and the response will be displayed in the white block in the center.  
*Note: Messages are not saved anywhere.*

If you want to switch to a different DB, click **Disconnect**, select another DB, and click **Connect** again.

The conversation will reset when the connection is disconnected.

## License
The MCP server and many of the technologies used in this project are licensed under the MIT License. See the LICENSE file for details.
