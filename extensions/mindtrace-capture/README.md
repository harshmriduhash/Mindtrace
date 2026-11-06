# Mindtrace Capture (Chrome MV3)

Save the current tab title/URL and selected text into your Mindtrace Learn graph.

## Install (unpacked)

1. Start the Mindtrace API (`http://localhost:8000` or your deployed API).
2. Chrome → **Extensions** → **Developer mode** → **Load unpacked** → select this folder.
3. In the web app → **Settings** → **Generate extension token**.
4. Open the extension **options** page → paste token + API base (`http://localhost:8000/api/v1`).

## Capture flow

Popup → `POST /api/v1/extension/capture` with `Authorization: Bearer <token>` → source appears in **Learn** for concept review.
