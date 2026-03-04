# GitHub Actions 工作流

本目录包含所有 GitHub Actions 工作流配置文件。

## 📋 工作流列表

### 1. tests.yml - 自动测试工作流

**触发条件：**
- Push 到 `main` 或 `develop` 分支
- Pull Request 到 `main` 或 `develop` 分支

**功能：**
- 在多个 Python 版本（3.8, 3.9, 3.10, 3.11, 3.12）上运行测试
- 运行所有单元测试和集成测试
- 生成测试覆盖率报告
- 上传覆盖率到 Codecov

**步骤：**
1. Checkout 代码
2. 设置 Python 环境
3. 安装依赖
4. 安装包（`pip install -e .`）
5. 运行测试（`pytest`）
6. 上传覆盖率报告

---

### 2. install.yml - 安装测试工作流

**触发条件：**
- Push 到 `main` 或 `develop` 分支
- Pull Request 到 `main` 或 `develop` 分支

**功能：**
- 在多个 Python 版本上测试安装过程
- 验证 CLI 命令可用性
- 验证包结构完整性

**步骤：**
1. Checkout 代码
2. 设置 Python 环境
3. 安装依赖
4. 安装包（开发模式）
5. 验证安装成功
6. 测试 CLI 命令
7. 验证包结构

**测试的 CLI 命令：**
- `ai-pdf --version`
- `ai-pdf --help`
- `ai-pdf plugin list`
- `ai-pdf text --help`
- `ai-pdf to-markdown --help`
- `ai-pdf to-html --help`
- `ai-pdf to-json --help`

---

### 3. verify.yml - 安装后验证工作流

**触发条件：**
- Push 到 `main` 或 `develop` 分支
- Pull Request 到 `main`` 或 `develop` 分支
- 手动触发（`workflow_dispatch`）

**功能：**
- 验证 CLI 命令功能
- 验证插件系统
- 验证文本提取功能
- 验证格式转换功能
- 验证 Python API

**步骤：**
1. Checkout 代码
2. 设置 Python 3.11 环境
3. 安装依赖
4. 安装包
5. 验证 CLI 命令（version, help, plugin）
6. 验证插件系统（list, check）
7. 验证文本提取（创建样本 PDF，提取文本）
8. 验证格式转换（Markdown, JSON）
9. 验证 Python API（TextReaderPlugin, ToJsonPlugin）
10. 清理临时文件

---

### 4. release.yml - 发布工作流

**触发条件：**
- Push tag（`v*`）
- 手动触发（`workflow_dispatch`）

**功能：**
- 构建发布包
- 运行发布前测试
- 发布到 PyPI
- 创建 GitHub Release

**步骤：**
1. Checkout 代码
2. 设置 Python 3.11 环境
3. 安装依赖（build, twine, wheel）
4. 构建包（`python -m build`）
5. 检查版本号
6. 运行发布前测试
7. 发布到 PyPI（需要 `PYPI_API_TOKEN` secret）
8. 创建 GitHub Release（需要 `GITHUB_TOKEN`）

**需要的 Secrets：**
- `PYPI_API_TOKEN`: PyPI API token（用于上传包）
- `GITHUB_TOKEN`: GitHub token（自动提供）

---

## 🚀 使用说明

### 自动触发

大多数工作流会自动触发，无需手动操作：

**自动触发的工作流：**
- `tests.yml` - Push 或 PR 时自动运行
- `install.yml` - Push 或 PR 时自动运行
- `verify.yml` - Push 或 PR 时自动运行

**手动触发的工作流：**
- `release.yml` - Push tag 或手动触发

---

### 手动触发工作流

#### 1. 触发发布工作流

**通过 Tag 触发：**
```bash
# 创建并推送 tag
git tag v1.0.0
git push origin v1.0.0
```

**通过 GitHub UI 触发：**
1. 进入 GitHub Actions 页面
2. 选择 `release.yml` 工作流
3. 点击 "Run workflow"
4. 输入版本号（如 `v1.0.0`）
5. 点击 "Run workflow" 按钮

---

#### 2. 手动触发验证工作流

**通过 GitHub UI 触发：**
1. 进入 GitHub Actions 页面
2. 选择 `verify.yml` 工作流
3. 点击 "Run workflow"
4. 选择分支（如 `main`）
5. 点击 "Run workflow" 按钮

---

## 🔐 配置 Secrets

### PyPI API Token

**创建 PyPI API Token：**
1. 登录 [PyPI](https://pypi.org)
2. 进入 Account Settings
3. 创建 API Token
4. 复制 Token

**添加到 GitHub Secrets：**
1. 进入 GitHub 仓库设置
2. 选择 "Secrets and variables" → "Actions"
3. 点击 "New repository secret"
4. Name: `PYPI_API_TOKEN`
5. Value:（粘贴 PyPI API Token）
6. 点击 "Add secret"

---

## 📊 工作流状态

### 查看工作流状态

**通过 GitHub UI：**
1. 进入 GitHub 仓库
2. 点击 "Actions" 标签
3. 查看所有工作流运行状态

**通过 API：**
```bash
# 列出所有工作流运行
gh api repos/:owner/:repo/actions/runs

# 查看特定工作流运行
gh run view <run-id>
```

---

## 🐛 调试工作流

### 查看工作流日志

**通过 GitHub UI：**
1. 进入 GitHub Actions 页面
2. 点击失败的运行
3. 点击失败的作业
4. 查看详细日志

### 常见问题

**问题 1：依赖安装失败**
```
解决方案：检查 requirements.txt 是否完整
```

**问题 2：测试失败**
```
解决方案：查看测试日志，修复失败的测试
```

**问题 3：PyPI 上传失败**
```
解决方案：检查 PYPI_API_TOKEN 是否正确配置
```

**问题 4：版本号冲突**
```
解决方案：确保 setup.py 中的版本号与 tag 一致
```

---

## 📈 工作流优化建议

### 性能优化

1. **使用缓存**
   - Python 包缓存（已启用）
   - 依赖缓存（已启用）

2. **并行运行**
   - 多个 Python 版本并行测试（已启用）

3. **增量运行**
   - 只运行变更的文件测试（可添加）

### 安全优化

1. **限制权限**
   - 工作流只访问必要的资源

2. **定期更新**
   - 定期更新 GitHub Actions 版本

3. **代码审查**
   - 工作流更改需要代码审查

---

## 📝 工作流最佳实践

### 1. 保持工作流简单

**推荐：**
- ✅ 每个工作流只做一件事
- ✅ 清晰的步骤命名
- ✅ 详细的错误处理

**不推荐：**
- ❌ 一个工作流做太多事情
- ❌ 复杂的条件逻辑
- ❌ 难以理解的步骤

---

### 2. 使用矩阵策略

**优势：**
- ✅ 并行运行多个版本
- ✅ 节省时间
- ✅ 全面测试

**示例：**
```yaml
strategy:
  matrix:
    python-version: ['3.8', '3.9', '3.10', '3.11', '3.12']
```

---

### 3. 缓存依赖

**优势：**
- ✅ 加速工作流
- ✅ 节省网络带宽
- ✅ 减少依赖下载时间

**示例：**
```yaml
- uses: actions/setup-python@v5
  with:
    python-version: ${{ matrix.python-version }}
    cache: 'pip'
```

---

### 4. 上传构建产物

**优势：**
- ✅ 便于调试
- ✅ 保存测试结果
- ✅ 可以下载检查

**示例：**
```yaml
- uses: actions/upload-artifact@v4
  with:
    name: coverage-report
    path: htmlcov/
```

---

## 🎉 总结

GitHub Actions 工作流提供了完整的 CI/CD 流程：

- ✅ **自动测试** - 多版本测试，覆盖率报告
- ✅ **安装验证** - 确保安装过程正确
- ✅ **功能验证** - 验证所有功能正常
- ✅ **自动发布** - 自动发布到 PyPI

这些工作流确保代码质量、安装正确性和功能完整性。

---

**Created:** 2026-03-04
**Version:** 1.0.0
**Status:** ✅ Active
