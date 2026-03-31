# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2024-03-31

### Added
- **线程安全内置** - JLFDict 和 JLFList 现在默认线程安全
  - 使用 `threading.RLock` 保护所有操作
  - 支持批量操作优化（`with d:`/`with lst:`）
  - 性能开销仅 2-8%（平均）

- **完整测试覆盖**
  - 22 个 JLFDict 测试
  - 22 个 JLFList 测试
  - 索引恢复测试
  - 线程安全测试（并发读写）

- **详细文档**
  - [ARCHITECTURE.md](ARCHITECTURE.md) - 完整实现原理详解
  - [QUICK_START.md](QUICK_START.md) - 快速总结
  - [THREAD_SAFETY.md](THREAD_SAFETY.md) - 线程安全详解
  - [PERFORMANCE.md](PERFORMANCE.md) - 性能详细分析
  - [USABILITY.md](USABILITY.md) - 易用性分析
  - [COMPARISON.md](COMPARISON.md) - 与其他库对比
  - [INDEX_RECOVERY.md](INDEX_RECOVERY.md) - 索引恢复
  - [CHANGELOG_v0.2.0.md](CHANGELOG_v0.2.0.md) - 版本更新说明
  - [README_COMPARISON.md](README_COMPARISON.md) - 文档导航
  - [TEST_COVERAGE_ANALYSIS.md](TEST_COVERAGE_ANALYSIS.md) - 测试覆盖度分析

- **演示脚本**
  - [examples.py](examples.py) - 基础使用示例
  - [memory_demo.py](memory_demo.py) - 内存使用演示
  - [usability_demo.py](usability_demo.py) - 易用性对比演示
  - [test_index_recovery.py](test_index_recovery.py) - 索引恢复测试
  - [test_list_index_recovery.py](test_list_index_recovery.py) - 列表索引恢复测试
  - [test_thread_safety.py](test_thread_safety.py) - 线程安全测试

### Changed
- **线程安全模型** - 从可选包装器改为内置
  - 移除 `ThreadSafeJLFDict` 和 `ThreadSafeJLFDict` 类
  - JLFDict 和 JLFList 现在默认线程安全
  - 更新所有文档以反映新的线程安全模型

### Fixed
- **索引重建算法** - 修复了重建索引时可能的数据不一致问题
- **删除后的数据一致性** - 确保删除后读取正确
- **更新后的数据正确性** - 确保更新后读取最新值

### Improved
- **性能文档** - 详细的性能分析和对比
- **API 文档** - 扩展了线程安全说明
- **示例代码** - 添加更多使用示例

## [0.1.0] - 2024-03-25

### Added
- 🎉 **初始版本发布**
- ✅ JLFDict 完整类 dict 接口
- ✅ JLFList 完整类 list 接口
- ✅ 索引持久化快速启动
- ✅ Compact 操作清理删除记录
- ✅ 完整的测试覆盖
- ✅ README 中英文版本

### Features
- 🔑 JSONL 格式，人类可读
- 📦 追加写入，无需移动已有数据
- 🗜️ 软删除策略，保留删除历史
- 🔍 文件偏移量索引，O(1) 查找
- 💾 内存高效，只保存索引
- 🔄 数据可从 JSONL 文件完全重建
- 📊 支持特 JSON 数据值（None, bool, float, 嵌套结构等）

---

## 版本政策

**版本格式：** 主版本.次版本.修订版本（例如：1.2.3）

**语义化版本控制：**
- **主版本变更：** 重大功能变更，可能有不兼容的 API 变更
- **次版本变更：** 新增功能，向后兼容
- **修订版本变更：** Bug 修复或文档更新，向后兼容

---

## 发布时间表

| 版本 | 日期 | 状态 |
|------|------|------|
| 0.2.0 | 2024-03-31 | ✅ 当前版本 |
| 0.1.0 | 2024-03-25 | 📝 历史版本 |

---

**升级指南：** 查看项目文档中的版本特定变更说明。
