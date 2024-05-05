import requests
import os
import re
import logging
import warnings
import posixpath

logger = logging.getLogger(__name__)

BASE = "https://api.telegram.org/bot"
CHUNK_SIZE = 4096


class Teleboy:
    def __init__(self, token, topic_id=None, timeout=10, chunk_size=None, base=None):
        self.token = token
        self.topic_id = topic_id
        self.timeout = timeout
        if chunk_size is None:
            self.chunk_size = CHUNK_SIZE
        if base is None:
            self.base_url = os.environ.get("TELEBOY_BASE", BASE)

    def _get(self, url, params=None):
        p_url = posixpath.join(f"{self.base_url}{self.token}", url)
        req = requests.get(p_url, params=params, timeout=self.timeout)
        if req.status_code == 200:
            return req.json()
        logger.warning("%s  failed with %s", url, req.status_code)
        return {"error": req.status_code}

    def _get_updates(self):
        url_req = "getUpdates"
        return self._get(url_req)

    def get_chats(self):
        updates = self._get_updates()
        if "error" in updates or not updates:
            return {}

        if updates and not updates.get("ok", False):
            return {}

        out = {}
        for message in updates.get("result", []):  # pyright: ignore[reportGeneralTypeIssues]
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

    def send_msg(self, chat_id, text, topic_id=None, parse_mode="MarkdownV2"):
        if parse_mode == "MarkdownV2":
            text = re.sub(r"([_\[\]()~`>#+\-=|{}.!])", r"\\\1", text)
        if len(text) < self.chunk_size:
            rez = self._send_msg(chat_id, text, topic_id=topic_id, parse_mode=parse_mode)
            logger.info(rez)
            return
        out = [
            text[i: i + self.chunk_size] for i in range(0, len(text), self.chunk_size)
        ]
        for submsg in out:
            rez = self._send_msg(chat_id, submsg, topic_id, parse_mode)
            logger.info(rez)

    def _send_msg(self, chat_id, text, topic_id=None, parse_mode="MarkdownV2"):
        url_req = "sendMessage"
        params = {"text": text, "chat_id": chat_id, "parse_mode": parse_mode}
        if topic_id:
            params["message_thread_id"] = topic_id
        return self._get(url_req, params=params)

    def send_msg_to_chats(self, text, chats):
        for chat_id in chats:
            self.send_msg(chat_id=chat_id, text=text)


def get_updates(token, timeout=10):
    warnings.warn('use new Teleboy Api via class', FutureWarning)
    teleboy = Teleboy(token=token, timeout=timeout)
    return teleboy._get_updates()


def send_msg(token, chat_id, text, timeout=10, topic_id=None, parse_mode='MarkdownV2'):
    warnings.warn('use new Teleboy Api via class', FutureWarning)
    teleboy = Teleboy(token=token, timeout=timeout)
    teleboy.send_msg(chat_id=chat_id, text=text, topic_id=topic_id, parse_mode=parse_mode)


def send_msgs(token, chat_ids, text, timeout=10):
    warnings.warn('use new Teleboy Api via class', FutureWarning)
    teleboy = Teleboy(token=token, timeout=timeout)
    return teleboy.send_msg_to_chats(chats=chat_ids, text=text)


def get_chats(token, timeout=10):
    warnings.warn('use new Teleboy Api via class', FutureWarning)
    teleboy = Teleboy(token=token)
    return teleboy.get_chats()
