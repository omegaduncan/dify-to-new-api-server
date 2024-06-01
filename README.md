# Dify OpenAI 中转服务

本项目提供一个 Flask server，用于将 OpenAI 格式的请求转换为 Dify 格式，并将 Dify 的响应转换回 OpenAI 格式。这使得您可以使用 Dify 作为 OpenAI API 的代理，并在 new-api 等工具中使用 Dify 应用。

## 环境变量

在启动 Flask server 之前，您需要设置以下环境变量：

- `DIFY_URL=https://api.dify.ai/v1/chat-messages`：Dify API 的地址。
- `DIFY_KEY=你的 dify 金钥`：您的 Dify 金钥。

## Docker 部署

1.  **构建 Docker 镜像：**

    ```bash
    docker build --build-arg DIFY_URL=https://api.dify.ai/v1/chat-messages --build-arg DIFY_KEY=your-dify-secret-key -t dify-openai-transformer .
    ```

    **请将 `your-dify-secret-key` 替换为您的实际 Dify 金钥。**

2.  **运行 Docker 容器：**

    ```bash
    docker run -p 3000:3000 --env-file .env dify-openai-transformer
    ```

    这将启动 Flask server 并监听端口 3000。

## New-api 配置

1. 在 new-api 中添加一个新的 OpenAI 渠道。
2. 将渠道地址设置为 Flask server 的地址，例如 `http://127.0.0.1:3000/v1/chat/completions`。
3. 将金钥字段留空。
4. 模型字段可以设置为任意值，因为中转服务会使用环境变量中设置的 Dify 应用。

**示例配置:**

```json
{
    "type": "openai",
    "api_url": "http://127.0.0.1:3000/v1/chat/completions",
    "api_key": ""
}
```

## 代码说明

### server.py

-   **`transform_openai_to_dify`  函数：**
    -   接收 OpenAI 格式的请求数据。
    -   提取用户消息。
    -   将请求数据转换为 Dify 格式，包括添加  `query`  参数。
-   **`transform_dify_to_openai`  函数：**
    -   接收 Dify 格式的响应数据。
    -   将响应数据转换为 OpenAI 格式。
-   **`/v1/chat/completions`  路由：**
    -   接收 OpenAI 格式的请求。
    -   调用  `transform_openai_to_dify`  函数转换请求数据。
    -   将转换后的请求发送到 Dify API。
    -   调用  `transform_dify_to_openai`  函数转换 Dify API 的响应。
    -   将转换后的响应返回给客户端。

### Dockerfile

-   使用 Python 3.9 作为基础镜像。
-   将当前目录复制到容器的 `/app` 目录。
-   安装 Flask 和 requests 库。
-   将端口 3000 暴露给外部。
-   设置环境变量。
-   运行 `server.py` 启动 Flask server。

### .env 文件

-   存储 Dify API 地址和金钥。

## 测试

1.  确保 Docker 容器正在运行并监听端口 3000。
2.  使用 Postman 或其他 HTTP 客户端向中转服务发送请求，确认中转服务正常工作。
3.  在 new-api 中配置中转服务，并尝试发送请求。

## 问题排查

如果遇到问题，请检查以下内容：

-   确保环境变量设置正确。
-   检查 Flask server 的日志以获取更多信息。
-   确认 new-api 配置正确。

## 更新日志

-   **2024-06-02:** 修复了请求中缺少 `query` 参数的问题。
