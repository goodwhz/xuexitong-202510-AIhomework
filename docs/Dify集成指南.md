# Dify AI助手集成指南

## 概述

本文档说明如何在论文搜索引擎项目中集成Dify AI助手，提供智能问答功能。

## 集成内容

### 1. 前端集成

在 `frontend/index.html` 文件中添加了Dify配置：

```html
<!-- Dify AI助手配置 -->
<script>
    window.difyChatbotConfig = {
        token: 'lyRLrElEpJPKlfCV',
        baseUrl: 'https://dify.aipfuture.com',
        inputs: {
            // 可以在这里定义来自开始节点的输入
        },
        systemVariables: {
            // user_id: '您可以在这里定义用户ID',
            // conversation_id: '您可以在这里定义对话ID，必须是有效的UUID',
        },
        userVariables: {
            // avatar_url: '您可以在这里定义用户头像URL',
            // name: '您可以在这里定义用户名',
        }
    }
</script>
<script
    src="https://dify.aipfuture.com/embed.min.js"
    id="lyRLrElEpJPKlfCV"
    defer>
</script>
```

### 2. 样式优化

在 `frontend/static/css/style.css` 中添加了Dify样式优化：

- 按钮圆角效果和阴影
- 悬停动画效果
- 移动端响应式适配
- 深色模式支持
- 打印模式隐藏

## 配置说明

### Dify配置参数

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| token | string | Dify应用令牌 | lyRLrElEpJPKlfCV |
| baseUrl | string | Dify服务地址 | https://dify.aipfuture.com |
| inputs | object | 输入变量配置 | {} |
| systemVariables | object | 系统变量配置 | {} |
| userVariables | object | 用户变量配置 | {} |

### 可配置项说明

#### inputs（输入变量）
用于定义从开始节点传递的变量，例如：
```javascript
inputs: {
    user_name: "访客",
    user_role: "学生"
}
```

#### systemVariables（系统变量）
用于定义系统级别的变量：
```javascript
systemVariables: {
    user_id: 'user_123456',
    conversation_id: 'uuid-string-here'
}
```

#### userVariables（用户变量）
用于定义用户相关的变量：
```javascript
userVariables: {
    avatar_url: 'https://example.com/avatar.jpg',
    name: '张三'
}
```

## 使用说明

### 1. 基本使用

Dify AI助手将在页面右下角显示一个浮动按钮，点击即可打开聊天窗口。

### 2. 自定义配置

如需修改Dify配置，请编辑 `frontend/index.html` 文件中的 `window.difyChatbotConfig` 对象。

### 3. 样式定制

如需修改Dify样式，请编辑 `frontend/static/css/style.css` 文件中的相关CSS规则。

## 部署注意事项

### 1. 网络要求

确保部署环境能够访问 `https://dify.aipfuture.com` 域名。

### 2. 安全配置

- 建议在生产环境中配置合适的CSP策略
- 确保Dify令牌的安全性
- 考虑用户隐私保护

### 3. 性能优化

- Dify脚本已添加 `defer` 属性，不会阻塞页面加载
- 样式已优化，确保良好的用户体验

## 故障排除

### 常见问题

1. **Dify按钮不显示**
   - 检查网络连接
   - 验证Dify服务是否可用
   - 检查浏览器控制台错误信息

2. **样式异常**
   - 检查CSS文件是否正确加载
   - 验证CSS选择器优先级

3. **功能异常**
   - 检查Dify配置参数是否正确
   - 验证token是否有效

### 调试方法

1. 打开浏览器开发者工具
2. 检查Console面板的错误信息
3. 检查Network面板的请求状态
4. 验证Dify配置参数

## 版本信息

- 集成时间：2025年1月
- Dify版本：最新稳定版
- 兼容性：支持现代浏览器（Chrome、Firefox、Safari、Edge）

## 联系方式

如有问题，请联系技术支持团队。