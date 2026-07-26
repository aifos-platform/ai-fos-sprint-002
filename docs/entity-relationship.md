# Entity Relationship Overview

```text
ORG_ORGANISATION
├── ORG_LEGAL_ENTITY
├── ORG_DEPARTMENT
│   └── ORG_COST_CENTRE
├── OPS_PROGRAMME
│   └── OPS_PROJECT
├── GRT_DONOR
│   └── GRT_GRANT
├── FIN_ACCOUNT
├── FIN_BUDGET
│   └── FIN_BUDGET_LINE
├── ING_IMPORT_JOB
│   └── ING_COLUMN_MAPPING
├── AI_INSIGHT
├── AI_RISK
│   └── AI_RECOMMENDATION
└── FIN_JOURNAL
    └── FIN_TRANSACTION
```

`FIN_TRANSACTION` can reference:

- Account
- Department
- Cost centre
- Programme
- Project
- Grant
- Donor
- Journal
