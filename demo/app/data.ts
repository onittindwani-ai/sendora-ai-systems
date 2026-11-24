// Fictional example data. Not real people or companies.
export interface Lead {
  id: string;
  name: string;
  company: string;
  email: string;
  score: number;
  stage: "new" | "contacted" | "replied" | "meeting" | "won";
  value: number;
}

const first = ["Ada", "Ravi", "Mei", "Tomas", "Lena", "Omar", "Priya", "Jonas", "Sara", "Kofi", "Noor", "Elif"];
const last = ["Hart", "Iyer", "Lindqvist", "Okoro", "Duarte", "Nakamura", "Costa", "Weber", "Haddad", "Moreau"];
const company = ["Northwind Test Co", "Bluebird Demo Ltd", "Harbor Example LLC", "Pine Street Sample", "Quill Fictional Inc"];
const stages: Lead["stage"][] = ["new", "contacted", "replied", "meeting", "won"];

export function makeLeads(n: number): Lead[] {
  return Array.from({ length: n }, (_, i) => {
    const f = first[i % first.length]!;
    const l = last[(i * 7) % last.length]!;
    return {
      id: `lead-${i}`,
      name: `${f} ${l}`,
      company: company[(i * 3) % company.length]!,
      email: `${f.toLowerCase()}.${l.toLowerCase()}${i}@example.test`,
      score: (i * 37) % 100,
      stage: stages[(i * 3 + (i >> 2)) % stages.length]!,
      value: 500 + ((i * 193) % 9500),
    };
  });
}

export const trend = [
  { d: "Mon", sent: 120, replies: 8 },
  { d: "Tue", sent: 164, replies: 14 },
  { d: "Wed", sent: 142, replies: 11 },
  { d: "Thu", sent: 188, replies: 19 },
  { d: "Fri", sent: 171, replies: 17 },
  { d: "Sat", sent: 60, replies: 4 },
  { d: "Sun", sent: 48, replies: 5 },
];
