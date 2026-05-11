import argparse
import json
import os
import sys
from typing import NoReturn

from zlapi import ZaloAPI, Message, ThreadType


def load_credential(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        error_exit(f"Credential file not found: {path}")
    except json.JSONDecodeError as e:
        error_exit(f"Invalid JSON in credential file: {e}")
    except Exception as e:  # pylint: disable=broad-exception-caught
        error_exit(f"Failed to load credential file: {e}")


def error_exit(message: str) -> NoReturn:
    json.dump({"success": False, "error": message}, sys.stderr, ensure_ascii=False)
    sys.stderr.write("\n")
    sys.exit(1)


def make_client(cred: dict) -> ZaloAPI:
    cookies = {"zpsid": cred["zpsid"], "zpw_sek": cred["zpw_sek"]}
    client = ZaloAPI(
        phone="",
        password="",
        imei=cred["imei"],
        session_cookies=cookies,
        auto_login=False,
    )
    client._state.set_cookies(cookies)  # pylint: disable=protected-access
    client._state.login(  # pylint: disable=protected-access
        phone="", password="", imei=cred["imei"]
    )
    client._imei = cred["imei"]  # pylint: disable=protected-access
    client.uid = client._state.user_id  # type: ignore[method-assign]  # pylint: disable=protected-access
    return client


def cmd_list_groups(client: ZaloAPI):
    try:
        all_groups = client.fetchAllGroups()
        grid_ver_map = dict(all_groups.gridVerMap or {})  # type: ignore[attr-defined]
        if not grid_ver_map:
            print("[]")
            return

        info = client.fetchGroupInfo(grid_ver_map)
        grid_info_map = dict(info.gridInfoMap or {})  # type: ignore[attr-defined]

        result = []
        for group_id, details in grid_info_map.items():
            if isinstance(details, dict):
                name = details.get("name", "")
            else:
                name = getattr(details, "name", "")
            result.append({"id": str(group_id), "name": name})

        print(json.dumps(result, ensure_ascii=False))
    except Exception as e:  # pylint: disable=broad-exception-caught
        error_exit(str(e))


def cmd_send_message(client: ZaloAPI, group_id: str, message_text: str):
    try:
        msg = Message(text=message_text)
        client.sendMessage(msg, group_id, ThreadType.GROUP)
        print(json.dumps({"success": True, "group_id": group_id}, ensure_ascii=False))
    except Exception as e:  # pylint: disable=broad-exception-caught
        error_exit(str(e))


def cmd_send_image(
    client: ZaloAPI, group_id: str, image_path: str, caption: str | None
):
    if not os.path.isfile(image_path):
        error_exit(f"Image file not found: {image_path}")
    try:
        msg = Message(text=caption) if caption else None
        client.sendLocalImage(image_path, group_id, ThreadType.GROUP, message=msg)
        print(json.dumps({"success": True, "group_id": group_id}, ensure_ascii=False))
    except Exception as e:  # pylint: disable=broad-exception-caught
        error_exit(str(e))


def main():
    parser = argparse.ArgumentParser(description="Send messages to Zalo groups")
    parser.add_argument(
        "--credential", required=True, help="Path to JSON credential file"
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list-groups", help="List all groups")

    send_p = sub.add_parser("send-message", help="Send a message to a group")
    send_p.add_argument("--group-id", required=True, help="Target group ID")
    send_p.add_argument("--message", required=True, help="Message text to send")

    img_p = sub.add_parser("send-image", help="Send a local image file to a group")
    img_p.add_argument("--group-id", required=True, help="Target group ID")
    img_p.add_argument(
        "--image", required=True, help="Path to the image file (PNG, JPG, ...)"
    )
    img_p.add_argument("--caption", default=None, help="Optional caption text")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    cred = load_credential(args.credential)
    for key in ("imei", "zpsid", "zpw_sek"):
        if key not in cred:
            error_exit(f"Missing required credential field: '{key}'")

    try:
        client = make_client(cred)
    except Exception as e:  # pylint: disable=broad-exception-caught
        error_exit(f"Failed to initialize Zalo client: {e}")

    if args.command == "list-groups":
        cmd_list_groups(client)
    elif args.command == "send-message":
        cmd_send_message(client, args.group_id, args.message)
    elif args.command == "send-image":
        cmd_send_image(client, args.group_id, args.image, args.caption)


if __name__ == "__main__":
    main()
