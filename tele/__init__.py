import requests
import os
import re
import logging
import warnings
import posixpath
from typing import Optional

logger = logging.getLogger(__name__)

BASE = "https://api.telegram.org/bot"


class Teleboy:
    def __init__(
        self,
        token: str,
        topic_id: Optional[str | int] = None,
        timeout: int = 10,
        chunk_size: int = 4096,
        base: Optional[None] = None,
    ) -> None:
        self.token: str = token
        self.topic_id: Optional[str | int] = topic_id
        self.timeout: int = timeout
        self.chunk_size: int = chunk_size
        if base is None:
            self.base_url: str = os.environ.get("TELEBOY_BASE", BASE)

    def _get(self, url: str, params: Optional[dict] = None) -> dict:
        p_url: str = posixpath.join(f"{self.base_url}{self.token}", url)
        req = requests.get(p_url, params=params, timeout=self.timeout)
        if req.status_code == 200:
            return req.json()
        logger.warning("%s  failed with %s", url, req.status_code)
        return {"error": req.status_code}

    def _get_updates(self) -> dict:
        url_req = "getUpdates"
        return self._get(url_req)

    def get_chats(self) -> dict:
        updates = self._get_updates()
        if "error" in updates or not updates:
            return {}

        if updates and not updates.get("ok", False):
            return {}

        out = {}
        for message in updates.get(
            "result", []
        ):  # pyright: ignore[reportGeneralTypeIssues]
            msg = message.get("message", {})
            chat = msg.get("chat", {})
            if not chat:
                continue
            chat_type = chat.get("type", "")
            if chat_type == "group":
                out[chat["id"]] = chat["title"]
            else:
                fname = chat.get("first_name", "")
                lname = chat.get("last_name", "")
                out[chat["id"]] = f"{fname} {lname}"
        return out

    def send_msg(
        self,
        chat_id: str,
        text: str,
        topic_id: Optional[str | int] = None,
        parse_mode: str = "MarkdownV2",
    ) -> None:
        if parse_mode == "MarkdownV2":
            text = re.sub(r"([_\[\]()~`>#+\-=|{}.!])", r"\\\1", text)
        if len(text) < self.chunk_size:
            rez = self._send_msg(
                chat_id, text, topic_id=topic_id, parse_mode=parse_mode
            )
            logger.info(rez)
            return
        out = [
            text[i: i + self.chunk_size] for i in range(0, len(text), self.chunk_size)
        ]
        for submsg in out:
            rez = self._send_msg(chat_id, submsg, topic_id, parse_mode)
            logger.info(rez)

    def _send_msg(
        self,
        chat_id: str,
        text: str,
        topic_id: Optional[str | int] = None,
        parse_mode: str = "MarkdownV2",
    ) -> dict:
        url_req: str = "sendMessage"
        params: dict = {"text": text, "chat_id": chat_id, "parse_mode": parse_mode}
        if topic_id:
            params["message_thread_id"] = topic_id
        return self._get(url_req, params=params)

    def send_msg_to_chats(self, text, chats):
        for chat_id in chats:
            self.send_msg(chat_id=chat_id, text=text)


def get_updates(token: str, timeout: int = 10) -> dict:
    warnings.warn("use new Teleboy Api via class", FutureWarning)
    teleboy = Teleboy(token=token, timeout=timeout)
    return teleboy._get_updates()


def send_msg(
    token: str,
    chat_id: str,
    text: str,
    timeout: int = 10,
    topic_id: Optional[str | int] = None,
    parse_mode: str = "MarkdownV2",
) -> None:
    warnings.warn("use new Teleboy Api via class", FutureWarning)
    teleboy = Teleboy(token=token, timeout=timeout)
    return teleboy.send_msg(
        chat_id=chat_id, text=text, topic_id=topic_id, parse_mode=parse_mode
    )


def send_msgs(token: str, chat_ids: list[str], text: str, timeout: int = 10) -> None:
    warnings.warn("use new Teleboy Api via class", FutureWarning)
    teleboy = Teleboy(token=token, timeout=timeout)
    return teleboy.send_msg_to_chats(chats=chat_ids, text=text)


def get_chats(token: str) -> dict:
    warnings.warn("use new Teleboy Api via class", FutureWarning)
    teleboy = Teleboy(token=token)
    return teleboy.get_chats()
