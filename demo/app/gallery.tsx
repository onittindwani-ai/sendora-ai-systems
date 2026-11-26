"use client";
import { AlertTriangle, Gauge as GaugeIcon, Kanban as KanbanIcon, Layers, Table2 } from "lucide-react";
import { useMemo, useState } from "react";
import {
  AppShell, AreaChart, Badge, Button, Card, CommandPalette, ConfirmDialog, ConnectionWizard, CopyButton, DataTable, DateRange, EmptyState, ErrorState,
  Field, FilterBar, Gauge, Kanban, OfflineBanner, SegmentedControl, Sheet, Skeleton, Sparkline, SplitView, Stat, TableSkeleton, TabsView, ThemeProvider, Toaster,
  formatCurrency, middleTruncate, notify, useTheme, type Column, type DateRangeValue, type PaletteItem,
} from "@sendora/ui-kit";
import { makeLeads, trend, type Lead } from "./data";

const wait = (ms: number): Promise<void> => new Promise((r) => setTimeout(r, ms));

type View = "overview" | "pipeline" | "leads" | "states";

function Inner() {
  const [view, setView] = useState<View>("overview");
  const [range, setRange] = useState<DateRangeValue>("7d");
  const [palette, setPalette] = useState(false);
  const [sheetLead, setSheetLead] = useState<Lead | null>(null);
  const [confirm, setConfirm] = useState(false);
  const [email, setEmail] = useState("");
  const [items, setItems] = useState(() => makeLeads(14).map((l) => ({ id: l.id, columnId: l.stage, lead: l })));
  const leads = useMemo(() => makeLeads(5000), []);
  const { setChoice } = useTheme();
  const [stateKind, setStateKind] = useState<"empty" | "error" | "loading">("empty");
  const [steps, setSteps] = useState<("todo" | "ok" | "error")[]>(["todo", "todo"]);

  const columns: Column<Lead>[] = [
    { key: "name", header: "Name", width: "1.4fr", sortValue: (r) => r.name },
    { key: "company", header: "Company", width: "1.4fr", sortValue: (r) => r.company },
    { key: "email", header: "Email", width: "1.8fr", render: (r) => <span title={r.email}>{middleTruncate(r.email, 30)}</span> },
    { key: "stage", header: "Stage", width: "110px", render: (r) => <Badge tone={r.stage === "won" ? "success" : r.stage === "replied" ? "accent" : "neutral"}>{r.stage}</Badge>, sortValue: (r) => r.stage },
    { key: "score", header: "Score", width: "80px", align: "right", sortValue: (r) => r.score },
    { key: "value", header: "Value", width: "100px", align: "right", render: (r) => formatCurrency(r.value), sortValue: (r) => r.value },
  ];

  const paletteItems: PaletteItem[] = [
    { id: "go-overview", label: "Go to overview", group: "Navigate", shortcut: ["G", "O"], onSelect: () => setView("overview") },
    { id: "go-pipeline", label: "Go to pipeline", group: "Navigate", shortcut: ["G", "P"], onSelect: () => setView("pipeline") },
    { id: "go-leads", label: "Go to leads", group: "Navigate", onSelect: () => setView("leads") },
    { id: "dark", label: "Switch to dark theme", group: "Actions", keywords: ["espresso", "night"], onSelect: () => setChoice("dark") },
    { id: "toast", label: "Show a toast", group: "Actions", onSelect: () => notify.success("Saved. This is a demo toast.") },
  ];

  return (
    <>
      <AppShell
        productName="UI Kit"
        activeId={view}
        onNavigate={(id) => setView(id as View)}
        onOpenPalette={() => setPalette(true)}
        breadcrumbs={["Demo", { overview: "Overview", pipeline: "Pipeline", leads: "Leads", states: "States and forms" }[view]]}
        nav={[
          { id: "overview", label: "Overview", icon: GaugeIcon },
          { id: "pipeline", label: "Pipeline", icon: KanbanIcon, count: items.length },
          { id: "leads", label: "Leads", icon: Table2, count: 5000 },
          { id: "states", label: "States and forms", icon: Layers },
        ]}
      >
        {view === "overview" && (
          <>
            <div className="sx-row" style={{ justifyContent: "space-between" }}>
              <div>
                <h1 className="sx-serif" style={{ fontSize: "var(--sx-text-h1)" }}>Good morning</h1>
                <p className="sx-muted sx-measure" style={{ margin: "8px 0 0" }}>Sample data only. This page proves the shared kit renders.</p>
              </div>
              <DateRange value={range} onChange={setRange} />
            </div>
            <div className="sx-grid sx-grid--stats">
              <Card><Stat label="Sent" value={range === "7d" ? 893 : 3720} delta={12} note="vs prior period" /></Card>
              <Card><Stat label="Replies" value={range === "7d" ? 78 : 331} delta={-4} note="vs prior period" /></Card>
              <Card><Stat label="Meetings" value={range === "7d" ? 12 : 51} delta={9} /></Card>
              <Card title="Speed to lead" lift>
                <div className="sx-row" style={{ gap: 21 }}>
                  <Gauge value={0.82} label="under 5 min" />
                  <Sparkline data={[3, 5, 4, 7, 6, 9, 8, 11]} label="Replies" />
                </div>
              </Card>
            </div>
            <Card title="Sent and replies">
              <AreaChart data={trend} xKey="d" series={[{ key: "sent", label: "Sent" }, { key: "replies", label: "Replies" }]} />
            </Card>
            <Card title="Deliverability warning">
              <div className="sx-row" style={{ justifyContent: "space-between" }}>
                <div className="sx-row"><AlertTriangle aria-hidden /><div><strong>Mailbox 2 is near its daily cap</strong><p className="sx-muted" style={{ margin: 0 }}>38 of 40 sends used. Sending resumes tomorrow.</p></div></div>
                <Badge tone="warning">Near limit</Badge>
              </div>
            </Card>
            <div className="sx-row">
              <Button variant="primary" onClick={() => wait(1800)}>Run a slow action</Button>
              <Button onClick={() => void notify.undo("Archived 3 leads", () => void notify.info("Restored"))}>Archive with undo</Button>
              <Button variant="danger" feedback={false} onClick={() => setConfirm(true)}>Delete all</Button>
              <Button disabled disabledReason="Connect an inbox first">Send</Button>
              <CopyButton value="hello@example.test" label="Copy email" />
            </div>
          </>
        )}

        {view === "pipeline" && (
          <>
            <h1 className="sx-serif" style={{ fontSize: "var(--sx-text-h1)" }}>Pipeline</h1>
            <Kanban
              label="Deal pipeline"
              columns={[{ id: "new", title: "New" }, { id: "contacted", title: "Contacted" }, { id: "replied", title: "Replied" }, { id: "meeting", title: "Meeting" }, { id: "won", title: "Won" }]}
              items={items}
              onMove={(id, to) => setItems((xs) => xs.map((x) => (x.id === id ? { ...x, columnId: to as Lead["stage"] } : x)))}
              onOpen={(i) => setSheetLead(i.lead)}
              cardLabel={(i) => `Lead ${i.lead.name}`}
              renderCard={(i) => (
                <div style={{ display: "grid", gap: 3 }}>
                  <strong>{i.lead.name}</strong>
                  <span className="sx-quiet" style={{ fontSize: 13 }}>{i.lead.company}</span>
                  <span className="sx-num" style={{ fontSize: 13 }}>{formatCurrency(i.lead.value)}</span>
                  <a href={`mailto:${i.lead.email}`} style={{ fontSize: 13, color: "var(--sx-accent)" }}>Email {i.lead.name.split(" ")[0]}</a>
                </div>
              )}
            />
          </>
        )}

        {view === "leads" && (
          <>
            <h1 className="sx-serif" style={{ fontSize: "var(--sx-text-h1)" }}>Leads</h1>
            <FilterBar>
              <Field label="Search" value="" onChange={() => {}} placeholder="Name or company" />
            </FilterBar>
            <DataTable
              label="Leads"
              rows={leads}
              rowKey={(r) => r.id}
              columns={columns}
              selectable
              onRowOpen={setSheetLead}
              rowActions={(r) => <Button size="sm" feedback={false} onClick={() => setSheetLead(r)}>Open</Button>}
              bulkActions={(sel, clear) => <Button variant="primary" onClick={async () => { await new Promise((r) => setTimeout(r, 500)); notify.undo(`Archived ${sel.length} leads`, () => {}); clear(); }}>Archive</Button>}
            />
          </>
        )}

        {view === "states" && (
          <>
            <h1 className="sx-serif" style={{ fontSize: "var(--sx-text-h1)" }}>States and forms</h1>
            <SegmentedControl label="State" value={stateKind} onChange={setStateKind} options={[{ value: "empty", label: "Empty" }, { value: "error", label: "Error" }, { value: "loading", label: "Loading" }]} />
            <Card>
              {stateKind === "empty" && <EmptyState title="No leads yet" body="Import a CSV or connect your CRM and your first leads will show up here." actionLabel="Import leads" onAction={() => wait(800)} />}
              {stateKind === "error" && <ErrorState title="Inbox not connected" whatHappened="The mailbox rejected the password, so replies cannot be read." howToFix="Create a new app password in your mail settings and paste it into the connection." onRetry={() => wait(800)} />}
              {stateKind === "loading" && <TableSkeleton rows={5} columns={4} />}
            </Card>
            <SplitView
              list={<Card title="Connect your tools"><ConnectionWizard onStatus={(id, s) => setSteps((st) => st.map((v, i) => ((i === 0 ? "mail" : "sms") === id ? s : v)))} steps={[
                { id: "mail", title: "Email", description: "Gmail or any inbox", status: steps[0]!, onTest: async () => { await new Promise((r) => setTimeout(r, 600)); } },
                { id: "sms", title: "Text messages", description: "Carrier registration needed first", status: steps[1]!, onTest: async () => { await new Promise((r) => setTimeout(r, 600)); throw new Error("not registered"); } },
              ]} /></Card>}
              detail={<Card title="Form"><TabsView items={[
                { value: "a", label: "Details", content: <Field label="Email" value={email} onChange={setEmail} maxLength={60} clearable hint="We never share this." validate={(v) => (/^\S+@\S+\.\S+$/.test(v) ? null : "Add an @ and a domain, like name@company.com")} /> },
                { value: "b", label: "Loading", content: <div style={{ display: "grid", gap: 8 }}><Skeleton height={21} width="60%" /><Skeleton height={13} /><Skeleton height={13} width="80%" /></div> },
              ]} /></Card>}
            />
          </>
        )}
      </AppShell>
      <CommandPalette items={paletteItems} open={palette} onOpenChange={setPalette} />
      <Sheet open={sheetLead !== null} onOpenChange={(o) => !o && setSheetLead(null)} title={sheetLead?.name ?? ""} description={sheetLead ? `${sheetLead.company}, ${sheetLead.email}` : undefined}>
        {sheetLead ? (
          <div style={{ display: "grid", gap: 13 }}>
            <div className="sx-row"><Badge tone="accent">{sheetLead.stage}</Badge><span className="sx-num">Score {sheetLead.score}</span></div>
            <Gauge value={sheetLead.score / 100} label="fit score" size={120} />
          </div>
        ) : null}
      </Sheet>
      <ConfirmDialog open={confirm} onOpenChange={setConfirm} title="Delete all leads?" description="This removes every lead in this demo. You can undo it for six seconds." confirmLabel="Delete all" destructive onConfirm={() => void notify.undo("Deleted all leads", () => {})} />
      <OfflineBanner />
      <Toaster />
    </>
  );
}

export function Gallery() {
  return (
    <ThemeProvider accent="clay">
      <Inner />
    </ThemeProvider>
  );
}
