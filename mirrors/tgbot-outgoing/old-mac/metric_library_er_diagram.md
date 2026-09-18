# 指标库 ER 图（按 v0.3 完整设计 · 2026-08-24）

> **源文档**：`omdb/tgbot/incoming/spec_v0.3_20260824.md`（指标库概念模型 v0.3 完整设计）  
> **底座**：又初 v0.2 metric-first 三层（实线）  
> **扩层**：v0.3 `entity_dict` / `event_ext` / `role_dict` + 字段增量 + `report_metric_binding`  
> **HTML 审阅版**：`docs/metric_library_er_diagram_20260824.html`

## Mermaid

```mermaid
erDiagram
    %% ========== 已有元数据（灰） ==========
    glossaryterm ||--o| event_ext : "1:1 extend"
    tabledefinition ||--o{ columndefinition : "contains"
    tabledefinition ||--o{ metric_implementation : "table_fqn"
    columndefinition ||--o{ metric_implementation : "column_name"

    %% ========== v0.3 实体 / 事件 / 角色 / 维度 ==========
    entity_dict ||--o{ event_ext : "owns"
    entity_dict ||--o{ dimension_standard : "owns"
    entity_dict ||--o{ metric_concept : "measures"
    glossaryterm ||--o{ metric_concept : "main_event"
    glossaryterm ||--o{ role_dict : "source_event"
    dimension_standard ||--o{ metric_implementation : "dim_uses JSON"
    role_dict ||--o{ metric_implementation : "dim_uses JSON"

    %% ========== v0.2 指标核心 ==========
    metric_concept ||--o{ metric_label : "1:N names"
    metric_concept ||--o{ metric_implementation : "1:N impls"
    metric_concept ||--o| metric_concept : "derived num or den"
    metric_impl_candidate }o--o| metric_implementation : "promote"
    metric_concept ||--o{ report_metric_binding : "cited_by"

    entity_dict {
        string entity_code PK
        string chinese
        string pk_col
        string entry_action_event FK
        string snapshot_table_fqn
        bool usable_as_dim
        enum status
    }

    event_ext {
        string event_code PK_FK
        string entity_code FK
        bool is_entry_action
        string raw_table_fqn
        json built_in_attrs
    }

    role_dict {
        string role_code PK
        string chinese
        string source_event_code FK
        text value_expr_template
        enum temporal_kind
        enum status
    }

    dimension_standard {
        string name PK
        string chinese
        string data_type
        string entity_code FK
        enum status
    }

    metric_concept {
        string concept_code PK
        text definition
        enum metric_kind
        string numerator_concept_code FK
        string denominator_concept_code FK
        string granularity
        string default_aggregation
        string req_ref
        enum lifecycle_status
        enum origin
        int version
        string entity_code FK
        string main_event_code FK
        json related_event_codes
    }

    metric_label {
        bigint id PK
        string concept_code FK
        enum label_kind
        string label_text
        bool is_primary
    }

    metric_implementation {
        bigint id PK
        string concept_code FK
        string table_fqn FK
        string column_name FK
        text formula
        string aggregation
        bool is_primary
        enum impl_status
        string session_code
        string lineage_ref
        json dim_uses
    }

    metric_impl_candidate {
        bigint id PK
        string table_fqn
        string column_name
        enum column_role
        text scan_formula
        string legacy_name
        enum candidate_status
        string lineage_ref
    }

    report_metric_binding {
        bigint id PK
        string report_id
        string concept_code FK
        text usage_note
        bool is_active
    }

    glossaryterm {
        string name PK
        string displayName
    }

    tabledefinition {
        bigint id PK
        string database
        string name
    }

    columndefinition {
        bigint id PK
        bigint table_id FK
        string name
    }
```

## 读图说明

| 区 | 表 | 来源 |
|----|-----|------|
| 指标核心 | `metric_concept` / `metric_label` / `metric_implementation` / `metric_impl_candidate` | v0.2 底座；concept 加 entity/main_event；impl 加 dim_uses |
| 元数据扩层 | `entity_dict` / `event_ext` / `role_dict` | v0.3 新建 |
| 维度 | `dimension_standard` | 已有；v0.3 加 `entity_code` |
| 流程闭环 | `report_metric_binding` | v0.3 新建；报表↔concept 引用计数 |
| 已有元数据 | `glossaryterm` / `tabledefinition` / `columndefinition` | 不侵入，仅 FK 挂接 |

## 关键关系（对照 spec §2 / §7 / §13）

1. **concept → entity / main_event**：published 硬门槛 G7-a；G7-b 校验 event_ext.entity == concept.entity  
2. **impl.dim_uses**：`[{dim, role_code}, ...]`，role 写死在 impl，不是查询参数  
3. **candidate → implementation**：扫表只进 staging，禁直建 concept  
4. **derived**：concept 自关联分子/分母；禁比率进 atomic  
5. **report_metric_binding**：引用归零且 proposed 超 30 天 → orphaned  

## 仓库 / 文档库

- Markdown：`docs/metric_library_er_diagram.md`
- HTML：`docs/metric_library_er_diagram_20260824.html`
- 源 spec：`omdb/tgbot/incoming/spec_v0.3_20260824.md`
