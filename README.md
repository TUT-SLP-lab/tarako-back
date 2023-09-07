# Debug 方法

1. set open ai api key

.open_ai_api_key に api_key を追加

2. local 実行

```
sam build && sam local start-api --parameter-overrides PrNumber="37" OpenAiApiKey=$(cat .open_ai_api_key)
```
