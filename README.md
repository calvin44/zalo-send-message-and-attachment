# send_zalo

A CLI tool for sending messages and images to Zalo groups.

## Requirements

- `credentials.json` file with your Zalo session credentials (see below)

---

## Credential File

Copy `credentials.example.json` to `credentials.json` and fill in your values:

```
cp credentials.example.json credentials.json
```

```json
{
  "imei": "your_imei_value",
  "zpsid": "your_zpsid_cookie",
  "zpw_sek": "your_zpw_sek_cookie"
}
```

> **Never commit `credentials.json`** — it contains live session tokens. It is listed in `.gitignore`.

---

## Commands

### List Groups

Fetch all groups you are a member of.

```
send_zalo.exe --credential "C:\Users\calvi\Documents\zalo-send-message\credentials.json" list-groups
```

**Output:**
```json
[{ "id": "6724803157250097854", "name": "UDC POC" }]
```

---

### Send Message

Send a text message to a group.

```
send_zalo.exe --credential "C:\Users\calvi\Documents\zalo-send-message\credentials.json" send-message --group-id 6724803157250097854 --message "Hello"
```

**Output:**
```json
{ "success": true, "group_id": "6724803157250097854" }
```

---

### Send Image

Send a local image file to a group, with an optional caption.

```
send_zalo.exe --credential "C:\Users\calvi\Documents\zalo-send-message\credentials.json" send-image --group-id 6724803157250097854 --image "C:\Users\calvi\OneDrive\Pictures\capture_260119_110444.png"
```

With caption:

```
send_zalo.exe --credential "C:\Users\calvi\Documents\zalo-send-message\credentials.json" send-image --group-id 6724803157250097854 --image "C:\Users\calvi\OneDrive\Pictures\capture_260119_110444.png" --caption "Test send image attachment"
```

**Output:**
```json
{ "success": true, "group_id": "6724803157250097854" }
```

---

## Parameters

| Parameter | Required | Description |
|---|---|---|
| `--credential` | Yes | Path to the JSON credential file |
| `--group-id` | Yes (send commands) | Target group ID |
| `--message` | Yes (send-message) | Text message to send |
| `--image` | Yes (send-image) | Full path to the image file (PNG, JPG, etc.) |
| `--caption` | No (send-image) | Optional caption text to send with the image |

---

## Error Handling

All errors are printed as JSON to stderr:

```json
{ "success": false, "error": "error message here" }
```

---

## Building from Source

```
pip install "git+https://github.com/Its-VrxxDev/zlapi.git"
pip install pyinstaller
pyinstaller --onefile --name send_zalo send_zalo.py
```

The executable will be output to `dist\send_zalo.exe`.
