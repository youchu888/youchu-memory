---
name: starrocks primary key partition rules
description: In StarRocks primary key tables, partition columns must be included in the primary key list, and leading table column order should match primary key order.
type: feedback
---
For StarRocks Primary Key table design in this project, if a table is partitioned by a field such as `dt`, that partition field must be included in the primary key list; and the leading physical column order in the DDL should match the primary key column order.

**Why:** The user explicitly corrected the recharge time-slot design and wants these two StarRocks DDL rules remembered for future table design reviews.

**How to apply:** When drafting or reviewing StarRocks PK-table DDL, first ensure partition columns are present in the PK definition, then align the top column order with the PK order before finalizing docs or SQL.
