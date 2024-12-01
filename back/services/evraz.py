import asyncio

import aiohttp
import requests
from loguru import logger

import config
from src.prompts import project_prompt, file_prompt, file_prompt_csharp, file_prompt_ts


class EvrazManager:
    def __init__(self):
        self.evraz_url = "http://84.201.152.196:8020/v1/completions"
        self.headers = {"Authorization": config.EVRAZ_API_KEY}

    def get_payload(self, content, system_prompt):
        return {
            "model": "mistral-nemo-instruct-2407",
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": content
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.3
        }

    def generate_answer(self, content, system_prompt):
        payload = self.get_payload(content, system_prompt)
        try:
            response = requests.post(self.evraz_url, json=payload, headers=self.headers)
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.exception(f"Ошибка {e} при запросе {content}")
            return "EVRAZ_API_ERROR"

    def generate_structure_answer(self, content):
        return self.generate_answer(content, project_prompt)

    def generate_file_answer(self, content):
        return self.generate_answer(content, file_prompt)

    def generate_files_answers(self, files_content):
        return asyncio.run(self.fetch_all(files_content))

    async def fetch_all(self, files_content):
        semaphore = asyncio.Semaphore(config.max_parallel)

        async def bound_fetch(session, content):
            async with semaphore:
                return await self.fetch_one(session, content)

        async with aiohttp.ClientSession() as session:
            tasks = [bound_fetch(session, content) for content in files_content]
            return await asyncio.gather(*tasks)

    async def fetch_one(self, session, content, try_count=3):
        payload = self.get_payload(content, file_prompt)
        try:
            async with session.post(self.evraz_url, json=payload, headers=self.headers) as response:
                response.raise_for_status()
                data = await response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.exception(f"Ошибка {e} при запросе {content}")
            if try_count == 0:
                return "EVRAZ_API_ERROR"
            return await self.fetch_one(session, content, try_count-1)

    def generate_file_answer_csharp(self, contents):
        return [self.generate_answer(content, file_prompt_csharp) for content in contents]

    def generate_file_answer_ts(self, contents):
        return [self.generate_answer(content, file_prompt_ts) for content in contents]