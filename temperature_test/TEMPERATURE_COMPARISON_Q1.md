# Temperature 对比分析 - 问题1: 南京天气感觉描述

## 1. 发散性与随机性对比

```mermaid
graph TD
    A[Temperature 参数影响]
    B[0.0]
    C[0.5]
    D[1.0]

    A --> B
    A --> C
    A --> D

    B --> B1[发散性: 0.328]
    B --> B2[随机性: 1.000]

    C --> C1[发散性: 0.468]
    C --> C2[随机性: 1.000]

    D --> D1[发散性: 0.525]
    D --> D2[随机性: 1.000]

    style B fill:#e1f5ff
    style C fill:#fff4e1
    style D fill:#ffe1f5
```

## 2. 发散性横向对比

```mermaid
graph LR
    A[Temperature 0.0]
    B[Temperature 0.5]
    C[Temperature 1.0]

    A --> A1[发散性: 0.328]
    B --> B1[发散性: 0.468]
    C --> C1[发散性: 0.525]

    A1 --> A2[低: 结构固定,表达一致]
    B1 --> B2[中: 有一定变化]
    C1 --> C2[高: 多样化表达]

    style A fill:#e1f5ff
    style B fill:#fff4e1
    style C fill:#ffe1f5
```

## 3. 随机性横向对比

```mermaid
graph LR
    A[Temperature 0.0]
    B[Temperature 0.5]
    C[Temperature 1.0]

    A --> A1[随机性: 1.000]
    B --> B1[随机性: 1.000]
    C --> C1[随机性: 1.000]

    A1 --> A2[词汇重复率高]
    B1 --> B2[词汇多样性中等]
    C1 --> C2[词汇丰富多样]

    style A fill:#e1f5ff
    style B fill:#fff4e1
    style C fill:#ffe1f5
```

## 4. 结构模式分布对比

```mermaid
pie title Temperature 0.0 - 结构模式
    "列表式" : 0
    "段落式" : 5
    "混合式" : 0
```

```mermaid
pie title Temperature 0.5 - 结构模式
    "列表式" : 0
    "段落式" : 5
    "混合式" : 0
```

```mermaid
pie title Temperature 1.0 - 结构模式
    "列表式" : 0
    "段落式" : 5
    "混合式" : 0
```

## 5. 表达风格特征对比

```mermaid
graph TB
    subgraph Temperature0.0
    A1[语气词: 0次]
    A2[具体例子: 0次]
    A3[数据引用: 5次]
    end

    subgraph Temperature0.5
    B1[语气词: 1次]
    B2[具体例子: 0次]
    B3[数据引用: 5次]
    end

    subgraph Temperature1.0
    C1[语气词: 1次]
    C2[具体例子: 0次]
    C3[数据引用: 5次]
    end

    style Temperature0.0 fill:#e1f5ff
    style Temperature0.5 fill:#fff4e1
    style Temperature1.0 fill:#ffe1f5
```

## 6. 回复长度统计对比

| Temperature | 最短 | 最长 | 平均 | 标准差 |
|:-----------|:----|:----|:----|:------|
| 0.0 | 118 | 160 | 147.4 | 15.9 |
| 0.5 | 136 | 200 | 160.4 | 23.2 |
| 1.0 | 146 | 198 | 177.4 | 17.7 |

## 7. 长度稳定性对比

```mermaid
graph LR
    A[Temperature 0.0]
    B[Temperature 0.5]
    C[Temperature 1.0]

    A --> A1[标准差: 15.9]
    B --> B1[标准差: 23.2]
    C --> C1[标准差: 17.7]

    A1 --> A2[中等稳定]
    B1 --> B2[不稳定]
    C1 --> C2[中等稳定]

    style A fill:#e1f5ff
    style B fill:#fff4e1
    style C fill:#ffe1f5
```

## 8. 语义内容关键词对比

```mermaid
graph TB
    subgraph Temperature0.0
    A0[关键词频率]
    多云: 5<br/>舒适: 5<br/>炎热: 2<br/>凉爽: 1<br/>湿度: 5
    end

    subgraph Temperature0.5
    B0[关键词频率]
    多云: 5<br/>舒适: 5<br/>炎热: 3<br/>凉爽: 3<br/>湿度: 5
    end

    subgraph Temperature1.0
    C0[关键词频率]
    多云: 5<br/>舒适: 5<br/>炎热: 3<br/>凉爽: 2<br/>湿度: 5
    end

    style Temperature0.0 fill:#e1f5ff
    style Temperature0.5 fill:#fff4e1
    style Temperature1.0 fill:#ffe1f5
```

## 9. 综合对比雷达图数据

| 维度 | Temperature 0.0 | Temperature 0.5 | Temperature 1.0 |
|:-----|:----------------|:----------------|:----------------|
| 发散性 | 0.328 | 0.468 | 0.525 |
| 随机性 | 1.000 | 1.000 | 1.000 |
| 列表化倾向 | 0.0 | 0.0 | 0.0 |
| 长度稳定性 | 0.8 | 0.8 | 0.8 |
| 表达丰富度 | 0.0 | 0.1 | 0.1 |

---

**分析时间**: 自动生成  
**数据来源**: temperature:*_outputs.log
