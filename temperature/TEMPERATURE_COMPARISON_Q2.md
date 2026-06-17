# Temperature 对比分析 - 问题2: 上海活动建议

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

    B --> B1[发散性: 0.665]
    B --> B2[随机性: 0.967]

    C --> C1[发散性: 0.647]
    C --> C2[随机性: 0.973]

    D --> D1[发散性: 0.726]
    D --> D2[随机性: 0.965]

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

    A --> A1[发散性: 0.665]
    B --> B1[发散性: 0.647]
    C --> C1[发散性: 0.726]

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

    A --> A1[随机性: 0.967]
    B --> B1[随机性: 0.973]
    C --> C1[随机性: 0.965]

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
    "段落式" : 2
    "混合式" : 3
```

```mermaid
pie title Temperature 0.5 - 结构模式
    "列表式" : 1
    "段落式" : 3
    "混合式" : 1
```

```mermaid
pie title Temperature 1.0 - 结构模式
    "列表式" : 0
    "段落式" : 2
    "混合式" : 3
```

## 5. 表达风格特征对比

```mermaid
graph TB
    subgraph Temperature0.0
    A1[语气词: 3次]
    A2[具体例子: 4次]
    A3[数据引用: 5次]
    end

    subgraph Temperature0.5
    B1[语气词: 1次]
    B2[具体例子: 2次]
    B3[数据引用: 5次]
    end

    subgraph Temperature1.0
    C1[语气词: 1次]
    C2[具体例子: 2次]
    C3[数据引用: 5次]
    end

    style Temperature0.0 fill:#e1f5ff
    style Temperature0.5 fill:#fff4e1
    style Temperature1.0 fill:#ffe1f5
```

## 6. 回复长度统计对比

| Temperature | 最短 | 最长 | 平均 | 标准差 |
|:-----------|:----|:----|:----|:------|
| 0.0 | 164 | 514 | 319.8 | 131.2 |
| 0.5 | 149 | 363 | 240.8 | 81.2 |
| 1.0 | 151 | 441 | 319.2 | 136.8 |

## 7. 长度稳定性对比

```mermaid
graph LR
    A[Temperature 0.0]
    B[Temperature 0.5]
    C[Temperature 1.0]

    A --> A1[标准差: 131.2]
    B --> B1[标准差: 81.2]
    C --> C1[标准差: 136.8]

    A1 --> A2[不稳定]
    B1 --> B2[不稳定]
    C1 --> C2[不稳定]

    style A fill:#e1f5ff
    style B fill:#fff4e1
    style C fill:#ffe1f5
```

## 8. 语义内容关键词对比

```mermaid
graph TB
    subgraph Temperature0.0
    A0[关键词频率]
    多云: 1<br/>阴: 5<br/>雨: 4<br/>舒适: 2<br/>湿度: 5
    end

    subgraph Temperature0.5
    B0[关键词频率]
    阴: 5<br/>雨: 3<br/>舒适: 2<br/>湿度: 5<br/>温度: 2
    end

    subgraph Temperature1.0
    C0[关键词频率]
    多云: 1<br/>阴: 5<br/>雨: 3<br/>舒适: 2<br/>炎热: 1
    end

    style Temperature0.0 fill:#e1f5ff
    style Temperature0.5 fill:#fff4e1
    style Temperature1.0 fill:#ffe1f5
```

## 9. 综合对比雷达图数据

| 维度 | Temperature 0.0 | Temperature 0.5 | Temperature 1.0 |
|:-----|:----------------|:----------------|:----------------|
| 发散性 | 0.665 | 0.647 | 0.726 |
| 随机性 | 0.967 | 0.973 | 0.965 |
| 列表化倾向 | 0.0 | 0.2 | 0.0 |
| 长度稳定性 | -0.3 | 0.2 | -0.4 |
| 表达丰富度 | 0.7 | 0.3 | 0.3 |

---

**分析时间**: 自动生成  
**数据来源**: temperature:*_outputs.log
