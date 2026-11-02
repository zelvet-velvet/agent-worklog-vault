"""Mermaid samples: every diagram type in Mermaid 11.13 (Obsidian 1.14) with its main features.
(title, short description of what it shows, code). Used for the Edge test page and the vault note."""

SAMPLES = [
('Flowchart', 'shapes, edge kinds, edge labels, subgraph, pass / fail classes', '''flowchart LR
    A[Rectangle] --> B(Rounded) --> C([Stadium])
    C -->|label| D{Decision}
    D -- yes --> E[(Database)]
    D -. dotted .-> F((Circle))
    D == thick ==> G>Flag]
    subgraph SG [Subgraph]
        H[/Parallelogram/] --- I{{Hexagon}}
    end
    E --> H
    G --> P[Passed]:::pass
    G --> X[Failed]:::fail
    classDef pass fill:none
    classDef fail fill:none'''),
('Flowchart 11.x features', 'expanded shapes (A@{ shape }), markdown labels, edge ends, animated edge, semantic classes', '''flowchart LR
    S@{ shape: sm-circ, label: "start" } --> D1@{ shape: doc, label: "Spec" }
    D1 --> P@{ shape: subproc, label: "Build" }
    P e1@==> T@{ shape: diam, label: "Tests?" }
    e1@{ animate: true }
    T -->|pass| OK["`**Release**
    _signed_`"]:::pass
    T -->|fail| BAD@{ shape: bang, label: "Broken" }
    BAD:::fail
    OK --o W[Wait]:::warn
    W --x M[Old step]:::muted
    OK <--> I@{ shape: cyl, label: "Store" }
    I:::info'''),
('Sequence', 'actor kinds, sync / async / reply messages, notes, loop / alt / opt / par / critical / rect, activation, autonumber', '''sequenceDiagram
    autonumber
    actor U as User
    participant A as App
    participant S as Server
    U->>A: Tap button
    activate A
    A->>+S: Request
    Note over A,S: TLS session
    loop Retry 3x
        S-->>A: Partial
    end
    alt OK
        S-->>-A: 200
    else Error
        S--xA: 500
    end
    opt Cache
        A-)A: Store
    end
    par Parallel
        A->>U: Show result
    and
        A->>S: Log
    end
    critical Must succeed
        A->>S: Commit
    end
    rect rgb(80, 80, 120)
        A->>U: Done
    end
    deactivate A'''),
('Class', 'classes, members, relations, cardinality, note', '''classDiagram
    class Animal {
        +String name
        +int age
        +makeSound() void
    }
    class Dog {
        +fetch() bool
    }
    class Owner
    Animal <|-- Dog : inherits
    Owner "1" --> "*" Dog : owns
    Dog *-- Tail
    Dog o-- Toy
    Dog ..> Food : eats
    note for Dog "Good boy"'''),
('State', 'start / end, composite state, choice, fork / join, note', '''stateDiagram-v2
    [*] --> Idle
    Idle --> Running : start
    state Running {
        [*] --> Loading
        Loading --> Ready
    }
    Running --> Check
    state Check <<choice>>
    Check --> Done : ok
    Check --> Failed : error
    state fork_state <<fork>>
    Done --> fork_state
    fork_state --> Save
    fork_state --> Notify
    state join_state <<join>>
    Save --> join_state
    Notify --> join_state
    join_state --> [*]
    note right of Failed : retry later
    Failed --> [*]'''),
('Entity relationship', 'entities, attributes with keys, relation cardinality', '''erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE_ITEM : contains
    PRODUCT ||--o{ LINE_ITEM : "ordered in"
    CUSTOMER {
        string id PK
        string name
        string email UK
    }
    ORDER {
        int id PK
        string customer_id FK
        date created
    }'''),
('User journey', 'sections, tasks, scores (faces), actors', '''journey
    title Release day
    section Build
        Write code: 5: Dev
        Review: 3: Dev, Lead
    section Ship
        Deploy: 2: Ops
        Celebrate: 5: Dev, Ops'''),
('Gantt', 'sections, done / active / critical tasks, milestone, today line', '''gantt
    title Plan
    dateFormat YYYY-MM-DD
    section Design
        Spec          :done, d1, 2026-10-01, 5d
        Review        :active, d2, after d1, 4d
    section Build
        Firmware      :crit, b1, after d2, 7d
        App           :b2, after d2, 6d
    section Release
        Ship          :milestone, m1, after b1, 0d'''),
('Pie', 'slices, legend, title, values', '''pie showData
    title Time spent
    "Coding" : 42
    "Review" : 18
    "Meetings" : 15
    "Testing" : 12
    "Docs" : 8
    "Other" : 5'''),
('Quadrant', 'axes, quadrant fills, points', '''quadrantChart
    title Effort vs value
    x-axis Low effort --> High effort
    y-axis Low value --> High value
    quadrant-1 Plan
    quadrant-2 Do now
    quadrant-3 Skip
    quadrant-4 Delegate
    Rollover script: [0.2, 0.8]
    Theme port: [0.7, 0.6]
    Light mode: [0.8, 0.3]
    Typo fix: [0.1, 0.2]'''),
('Requirement', 'requirements, element, relations', '''requirementDiagram
    requirement fast_boot {
        id: 1
        text: Boot under 2 s
        risk: medium
        verifymethod: test
    }
    functionalRequirement secure_store {
        id: 2
        text: Keys encrypted at rest
        risk: high
        verifymethod: inspection
    }
    element firmware {
        type: module
    }
    firmware - satisfies -> fast_boot
    firmware - satisfies -> secure_store
    secure_store - derives -> fast_boot'''),
('Git graph', 'branches (8 lane colours), merge, cherry-pick, tags, highlight / reverse commits', '''gitGraph
    commit id: "init"
    branch feature
    commit id: "f1"
    checkout main
    commit id: "m1" tag: "v1.0"
    branch fix
    commit id: "x1" type: HIGHLIGHT
    checkout main
    merge fix
    checkout feature
    commit id: "f2" type: REVERSE
    checkout main
    merge feature tag: "v1.1"
    branch docs
    commit id: "d1"
    branch b4
    commit id: "c4"
    branch b5
    commit id: "c5"
    branch b6
    commit id: "c6"
    branch b7
    commit id: "c7"
    checkout main
    cherry-pick id: "d1"'''),
('C4 context', 'person, system, external system, boundary, relations', '''C4Context
    title System context
    Person(user, "User", "Uses the app")
    System_Boundary(b, "Product") {
        System(app, "App", "Mobile app")
        SystemDb(db, "Database", "Stores data")
    }
    System_Ext(pay, "Payment", "External provider")
    Rel(user, app, "Uses")
    Rel(app, db, "Reads / writes")
    Rel(app, pay, "Charges", "HTTPS")'''),
('Mindmap', 'root and section colours by level', '''mindmap
    root((Project))
        Firmware
            Boot
            Crypto
        App
            UI
            Network
        Tools
            Scripts
        Docs
            Guide'''),
('Timeline', 'periods, events, section colours', '''timeline
    title Project history
    section 2026 Q3
        July : Kick-off
        August : Prototype : First test
    section 2026 Q4
        October : Release 1.0
        November : Template'''),
('Sankey', 'nodes and weighted flows', '''sankey-beta
Budget,Firmware,40
Budget,App,30
Budget,Tools,10
Firmware,Testing,15
App,Testing,10'''),
('XY chart', 'bar and line series, axes, title', '''xychart-beta
    title "Commits per week"
    x-axis [W40, W41, W42, W43, W44]
    y-axis "Commits" 0 --> 40
    bar [12, 25, 31, 18, 22]
    line [10, 20, 28, 22, 25]'''),
('Block', 'columns, blocks, shapes, arrows', '''block-beta
    columns 3
    a["Input"] space b["Process"]
    a --> b
    c(("Store")) d{"Check"} e["Output"]
    b --> e'''),
('Packet', 'bit fields of a frame', '''packet-beta
    0-7: "OP"
    8-23: "Length"
    24-31: "Flags"
    32-63: "Payload (variable)"'''),
('Kanban', 'columns and cards, ticket / assignee / priority', '''kanban
    todo[To do]
        t1[Write guide]
        t2[Port theme]@{ priority: 'High' }
    doing[In progress]
        t3[Mermaid colours]@{ assigned: 'agent' }
    done[Done]
        t4[Callouts]'''),
('Architecture', 'groups, services, edges', '''architecture-beta
    group cloud(cloud)[Cloud]
    service api(server)[API] in cloud
    service db(database)[DB] in cloud
    service disk(disk)[Storage] in cloud
    service web(internet)[Web]
    web:R --> L:api
    api:R -- L:db
    db:B -- T:disk'''),
('Radar', 'axes, two curves, legend', '''radar-beta
    title Skills
    axis a["Speed"], b["Safety"], c["Docs"], d["Tests"], e["UX"]
    curve now["Now"]{3, 4, 2, 3, 2}
    curve goal["Goal"]{4, 5, 4, 4, 4}
    max 5'''),
('Treemap', 'nested sections and leaf values', '''treemap-beta
"Project"
    "Firmware"
        "Crypto": 30
        "Boot": 10
    "App"
        "UI": 25
        "Network": 15
    "Docs": 8'''),
]
