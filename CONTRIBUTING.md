# 贡献指南

感谢你对推箱子游戏项目的关注！我们欢迎所有形式的贡献，包括但不限于：

- 报告问题
- 提交功能建议
- 提交代码改进
- 改进文档
- 添加新关卡

## 如何贡献

### 报告问题
1. 使用 GitHub Issues 提交问题
2. 使用清晰的标题描述问题
3. 提供详细的问题描述，包括：
   - 问题的具体表现
   - 复现步骤
   - 期望的行为
   - 系统环境信息

### 提交代码
1. Fork 项目仓库
2. 创建你的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交你的改动 (`git commit -m '添加一些很棒的功能'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建一个 Pull Request

### 代码规范
- 遵循 PEP 8 Python 代码风格指南
- 添加适当的注释
- 确保代码通过所有测试
- 为新功能添加测试用例

### 提交关卡
1. 使用关卡编辑器创建关卡
2. 确保关卡是可完成的
3. 将关卡文件放在 `levels` 目录下
4. 在 Pull Request 中说明关卡难度和特点

## 开发环境设置
1. 克隆仓库
```bash
git clone https://github.com/yourusername/sokoban.git
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

## 提交信息规范
提交信息应该清晰地描述改动的内容，建议使用以下格式：

- feat: 添加新功能
- fix: 修复问题
- docs: 更新文档
- style: 代码格式调整
- refactor: 代码重构
- test: 添加测试
- chore: 其他改动

例如：
```
feat: 添加关卡编辑器撤销功能
```

## 版本发布流程
1. 更新版本号
2. 更新 CHANGELOG.md
3. 创建发布标签
4. 编写发布说明

## 行为准则
- 保持友善和专业
- 尊重所有贡献者
- 接受建设性的批评
- 专注于项目改进

## 获取帮助
- 查看项目 Wiki
- 在 Issues 中提问
- 通过邮件联系维护者

再次感谢你的贡献！
