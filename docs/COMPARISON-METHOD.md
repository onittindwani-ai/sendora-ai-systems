# How paid tools and open source alternatives are compared

Every system repo has a `TOOLS-AND-ALTERNATIVES.md`. This is how the scores in it are made, so you can redo them for your own client.

## The six criteria and their weights

| Criterion | Weight | What it asks |
| --- | --- | --- |
| Fit | 35 | Does it do what this system needs, with the features this system calls |
| Setup effort | 15 | How long and how hard for a non technical client, from nothing to working |
| Reliability and upkeep | 15 | Does it keep working, and what does keeping it working cost in time |
| Cost | 15 | What it costs in plain terms at the size of a small business |
| Data control and privacy | 10 | Who holds the data, can you export it, can you host it yourself |
| Integration depth | 10 | How much of the tool our adapter really uses, and how well it was tested |

Each criterion is scored 0 to 100 with one written evidence line (a link or the thing we ran). The tool score is the weighted sum.

## Closeness

Closeness is the open source tool's fit score divided by the paid tool's fit score, as a percentage. It answers one question: does the free one do the same job.

## Rules

1. Scores are judgement from sources and our own adapter work. They are not benchmarks, and the document says so at the top.
2. Every score has a date. A score is redone when the evidence changes (a new release, a price change, a failed test).
3. Prices are written in plain terms ("free up to a small team", "paid per seat") with the vendor price page link and the date checked. We do not copy price tables, because they change.
4. A tool we never ran is scored from its documentation only, and the row says "not run".
5. Each comparison ends with a plain recommendation by user type: a beginner, an implementer running it for clients, and a cost sensitive owner. It also says when open source is the right call and when it is not.
6. A paid tool with no close open source replacement says so. We do not invent a match.

## First pass (before the build, judgement only, to be redone with evidence)

| Category | Paid | Open source | Paid score | Open source score | Closeness |
| --- | --- | --- | --- | --- | --- |
| CRM | HubSpot | Twenty | 81 | 77 | about 82 percent |
| Help desk | Intercom | Chatwoot | 76 | 79 | about 76 percent |
| Accounting | QuickBooks Online | Akaunting | 77 | 67 | about 61 percent |

These first numbers came from reading, not from running anything. They are replaced by evidence backed scores as each system is built.
