# 本地化证据关键词

## 基本信息

- 提交 ID：63
- 项目：MedTour AI Planner
- 首发市场：新加坡
- 第二阶段市场：印度尼西亚
- 评审 Commit：`1757bc58ed9b452aa8756035ea5cc8a1925f6d0b`
- 仓库：https://github.com/ZhiHaoSun/ChinaHospitals
- Demo：https://traechinahospital1355.vercel.app/

## 市场定位

- 新加坡
- 英语用户
- 中文用户
- 中等收入人群
- 高净值人群
- 计划性医疗
- 非急诊医疗
- 中国跨境医疗
- 自费用户
- 商业保险用户

## 新加坡市场依据

- 公立专科等待时间
- 私立医疗费用
- 医院费
- 外科医生费
- 麻醉师费
- 住院查房费
- SGD 费用基准
- 费用透明度
- 医疗总价比较

## 新加坡公开来源

- MOH 专科等待时间：https://www.moh.gov.sg/newsroom/wait-time-for-primary-c/
- MOH 医院账单与费用基准：https://www.moh.gov.sg/managing-expenses/bills-and-fee-benchmarks/hospital-bills-and-fee-benchmarks/
- ICA 中新 30 天免签：https://www.ica.gov.sg/news-and-publications/newsroom/media-release/mutual-30-day-visa-exemption-arrangement-between-singapore-and-the-people-s-republic-of-china

## 中国就医本地化

- 国际患者流程
- 医院国际部
- 外国患者服务
- 多语言支持
- 预约系统
- 保险直付
- 医疗旅游试点
- 上海国际医疗服务
- 入境准备
- 支付准备

## 中国公开来源

- 中国支付指南：https://english.www.gov.cn/news/202404/11/content_WS6617c858c6d0868f4e8e5f4d.html
- 外国人在华生活指南：https://english.www.gov.cn/2025special/bizexpatsinchina2025
- 上海国际医疗服务能力：https://english.shanghai.gov.cn/en-Latest-WhatsNew/20260303/56484619104544d8a49847ab9a4c389b.html
- 上海公立医院国际医疗旅游试点：https://english.shanghai.gov.cn/en-Latest-WhatsNew/20240923/85f2a95e516c42ce95643d1c9a39f59a.html
- 国际患者门诊流程：https://en.nhc.gov.cn/2025-12/12/c_86536.htm

## 产品适配

- 新加坡默认出发地
- SGD/RMB 切换
- 新加坡费用基准
- 保险公司输入
- 预授权提示
- 直付假设
- 理赔文件清单
- 医院国际部路径
- 外国患者服务路径
- 入境确认
- Alipay 国际用户设置
- 备用支付方式
- 外宾酒店检查
- 英语
- 简体中文
- Bahasa Indonesia

## 产品适配证据

- 多语言与默认设置：https://github.com/ZhiHaoSun/ChinaHospitals/blob/1757bc58ed9b452aa8756035ea5cc8a1925f6d0b/app.js#L5
- 地区与保险输入：https://github.com/ZhiHaoSun/ChinaHospitals/blob/1757bc58ed9b452aa8756035ea5cc8a1925f6d0b/app.js#L3818
- 新加坡费用基准：https://github.com/ZhiHaoSun/ChinaHospitals/blob/1757bc58ed9b452aa8756035ea5cc8a1925f6d0b/medtour_ai/services/singapore_benchmarks.py#L8
- SGD 总费用：https://github.com/ZhiHaoSun/ChinaHospitals/blob/1757bc58ed9b452aa8756035ea5cc8a1925f6d0b/medtour_ai/agents/tools.py#L774
- 入境与支付准备：https://github.com/ZhiHaoSun/ChinaHospitals/blob/1757bc58ed9b452aa8756035ea5cc8a1925f6d0b/medtour_ai/agents/tools.py#L1129
- 保险预授权与理赔：https://github.com/ZhiHaoSun/ChinaHospitals/blob/1757bc58ed9b452aa8756035ea5cc8a1925f6d0b/medtour_ai/agents/tools.py#L1188

## 用户习惯关键词

- SGD 总预算
- 有限年假
- 书面费用
- 医院路径
- 保险文件
- 预约确认
- 复查安排
- 返程安排

## 用户顾虑关键词

- 医院接收资格
- 医生可信度
- 医疗服务可信度
- 保险覆盖
- 预授权
- 直付
- 跨境支付
- 术后复诊
- 并发症处理
- 隐私合规

## 印度尼西亚状态

- 第二阶段市场
- 专科可及性
- 医疗人力分布
- IDR：未支持
- 本地保险：未支持
- 当地费用基准：未支持
- 用户测试：未完成

## 印度尼西亚来源

- WHO Indonesia：https://www.who.int/indonesia/news/detail/03-03-2026-indonesia-strengthens-health-workforce-planning-through-labour-market-analysis

## 非正式调研

- 华人微信群
- 新加坡华裔用户
- 同事
- 同学
- 邻居
- 赴华看病兴趣
- 公立预约等待
- 私立价格顾虑
- 私立质量顾虑

## 正式测试状态

- 当地用户测试：未完成
- 测试人数：0
- 访谈脚本：未提供
- 可用性录屏：未提供
- 问卷结果：未提供
- 任务完成率：未提供
- 付费意愿：未验证
- 医院报价：未验证
- 保险确认：未验证
- 预约转化：未验证

## 下一步验证

- 新加坡用户：8-12 名
- 需求填写任务
- 四城市比较任务
- 费用理解任务
- 风险理解任务
- 准备清单任务
- 信任评分
- 费用理解度
- 任务完成率
- 转化率

## Web 验证附录

- 文件：`evidence/localization/web-search-validation.md`
- 已支持：市场背景、SGD 成本、入境准备、支付准备、国际患者路径
- 未支持：产品信任、赴华意愿、付费意愿、真实报价、保险批准、预约转化
