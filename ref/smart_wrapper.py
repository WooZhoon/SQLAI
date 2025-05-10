# smart_wrapper.py
class SmartQueryWrapper:
    def __init__(self, client, session_mgr):
        self.client = client
        self.session = session_mgr

    async def ask(self, prompt, tools, model="gemini-2.0-flash"):
        self.session.append_history({"user": prompt})

        response = self.client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.3, tools=tools),
        )

        text = response.text.strip()

        # 1차 결과가 너무 빈약하면 재시도
        if not text or len(text) < 10 or "찾을 수 없습니다" in text:
            retry_prompt = self.suggest_retry(prompt)
            print(f"\n⚠️ 재시도 with: {retry_prompt}")
            response = self.client.models.generate_content(
                model=model,
                contents=retry_prompt,
                config=types.GenerateContentConfig(temperature=0.3, tools=tools),
            )

        return response

    def suggest_retry(self, prompt):
        # 아주 간단한 retry 전략
        if "Bentz" in prompt:
            return prompt.replace("Bentz", "벤츠")
        if "bmw" in prompt.lower():
            return prompt.replace("bmw", "비엠더블유")
        # 필요시 더 추가 가능
        return prompt
