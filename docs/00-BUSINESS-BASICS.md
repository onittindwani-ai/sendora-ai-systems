# Business basics: do this before any of the seven systems

Every system here sends email, texts or calls on behalf of a business. The tools are easy to set up. The business setup behind them is what makes them work, and what keeps your messages out of spam. This guide is the short path.

It is general information, not legal or tax advice. Rules differ by country and state. Each fact that comes from outside has a source and a date in `FACTS-AND-SOURCES.md`, marked VERIFIED or UNVERIFIED. Where a step names a tool we could not check, the guide says so.

Who this is for: an AI implementer setting up one copy of a system per client, or a business owner running one for their own company. If you do it for a client, the client's company (not yours) is the one that registers, because messages go out under their name.

## 1. The company and its tax number

1. Form the company with your state first. An LLC or corporation must exist before you ask for a tax number.
2. Get the EIN (employer identification number) from the IRS. For a US company it is free, and the IRS says you never have to pay a fee for one. You apply online, you need the responsible party's Social Security number or ITIN, only one EIN can be issued per responsible party per day, and the session ends after 15 minutes without activity, so have everything ready. The online form is for entities with a principal place of business in the US or its territories. Source: https://www.irs.gov/businesses/small-businesses-self-employed/apply-for-an-employer-identification-number-ein-online (VERIFIED 2026-11-22).
3. Keep one place with the exact legal company name, the address and the EIN. You will type them the same way many times. Small differences (Inc against Inc., a missing suite number) cause rejections later.

If the company is outside the US, the EIN path above does not apply. Texting in the US still needs a registered business identity, so ask your texting provider what they accept for non US companies. This guide does not cover it (UNVERIFIED).

## 2. The domain and its DNS

1. Buy the domain at a registrar. Namecheap is our example. Use a name that matches the company, because carriers and email providers compare it with your registration.
2. Decide where DNS lives. DNS is the list of records that says where the website and the email go. It is hosted by whoever answers for your nameservers, and that is not always the registrar.
3. Our default is Cloudflare for DNS only. Add the domain to a free Cloudflare account, then at Namecheap open the domain, set Nameservers to Custom DNS, paste the two nameservers Cloudflare gives you, and save. Return to Cloudflare and run the check until it shows Active. Records you made at Namecheap stop working after the switch, so recreate every record (website, email MX, SPF, DKIM, DMARC) in Cloudflare. Sources: https://www.namecheap.com/support/knowledgebase/article.aspx/9607/2210/how-to-set-up-dns-records-for-your-domain-in-a-cloudflare-account/ and https://developers.cloudflare.com/dns/zone-setups/full-setup/setup/ (VERIFIED from search summaries 2026-11-22). Changes can take from minutes to a day or more to spread.
4. Do not register the domain itself at Cloudflare if a mailbox provider you plan to use wants to manage the domain's records or its registration. Check that provider's domain connection guide first. We could not find InboxKit's or SendKit's own guide for this, so their exact requirements are UNVERIFIED.
5. Before you change anything, look up who currently answers DNS for the domain. Add records where the nameservers point, otherwise nothing happens.

## 3. The website

Carriers and email providers look at your website. It should say the company name exactly as registered, what the company does, a contact method, and a privacy policy. For texting it should also say how people sign up to get texts. Telnyx's own help says the most common fix for a low trust score is making the website, the company name and the EIN agree. Source: https://support.telnyx.com/en/articles/6325747-10dlc-messaging-throughput-trust-scores-campaign-use-cases-and-vetting (VERIFIED from a search summary 2026-11-22).

## 4. Mailboxes

Keep two kinds of email apart.

1. The main mailbox: your real company address on the main domain, used for people, invoices and replies. Use a normal provider (Google Workspace or Microsoft 365 are the usual ones). Never use this domain for cold outreach.
2. Outreach domains: separate domains that look like the brand (for example the company name with a small extra word) used only for cold outreach. If one gets blocked, the main domain is safe. Pipecairn and Ringlark are built around this split.

Mailbox tools that create many mailboxes (InboxKit is one we plan to document) and sending tools (SendKit is one) are third party products. We did not find their current documentation during this check, so how they ask you to connect domains, how many mailboxes you may create and what they cost are UNVERIFIED. Read their pages before you pay. Each outreach mailbox needs SPF, DKIM and DMARC records on its domain, set up in Cloudflare. A new mailbox should send a few messages a day and rise slowly. The systems enforce a daily cap per mailbox for this reason.

## 5. Texting in the US: carrier registration with Telnyx

US text messages from a normal 10 digit number need registration, called 10DLC. The order, from Telnyx's current docs, is brand, then vetting, then campaign. Sources: https://developers.telnyx.com/docs/messaging/10dlc/quickstart/index and https://developers.telnyx.com/docs/messaging/10dlc/brand-registration (VERIFIED from search summaries 2026-11-22).

1. Brand. Register the business identity with The Campaign Registry through Telnyx. You give the legal company name, the EIN, the address and the website. Use the exact values from section 1. A sole proprietor without an EIN follows a separate and more limited path.
2. Vetting. A third party check, typically 1 to 7 business days, that returns a trust score from 0 to 100. The score sets how many messages per second you can send on the big carriers. It is optional, but a campaign submitted before vetting finishes fails, so wait for it. If the score is low, fix the website, company name and EIN mismatch and ask for a new vetting.
3. Campaign. Register what you will send: the use case, how people opt in, and three to five sample messages. Opt out words (STOP) and a clear opt in are required in practice, and the systems here send a STOP line in every text.
4. Buy a number, link it to the campaign, and only then send.

Costs and how long a vetting result stays valid: UNVERIFIED. Sources disagree (one lists a one time brand fee and a per submission vetting fee, another says the score never changes while the troubleshooting docs say it can expire). Read the portal before you pay.

Each client registers their own brand. You cannot send a client's texts under your own registration.

## 6. Order of work and rough waiting times

| Step | Why it comes here | Wait |
| --- | --- | --- |
| Form the company | Needed for the EIN | days, set by the state |
| EIN | Needed for texting and many accounts | same session, if details are right |
| Domain and DNS | Needed for website and email | minutes to a day |
| Website | Needed for vetting | your build time |
| Main mailbox | Needed to run the business | same day |
| Outreach domains and mailboxes | Needed for cold email | add a warm up period before volume (rule of thumb, UNVERIFIED) |
| Telnyx brand, vetting, campaign, number | Needed for texting | vetting 1 to 7 business days per Telnyx |

## 7. What the systems check for you

Each system's `docs/02-BUSINESS-BASICS-CHECK.md` links here and lists the items that system needs (table in section 8). The `tools/doctor.py` of each system checks what it can check without calling your vendors (variables present, formats right, mode is draft). It never reads your secrets for any other purpose and never prints them.

## 8. Which basics each system needs

| System | Company and EIN | Domain and DNS | Website | Mailboxes | Texting registration | Also needs |
| --- | --- | --- | --- | --- | --- | --- |
| Pipecairn | yes | yes | yes | yes, separate outreach domains | if you text | an address and a stop line in every message |
| Ringlark | yes | yes | yes | for follow ups | yes, and a registered caller ID | consent records, the agent says it is an AI |
| Booklantern | yes | if it emails customers | no | a billing address | no | your accounting tool and a bank export |
| Deskfern | yes | yes | yes, with a privacy notice | a support address | no | refund rules written down, help pages that are true |
| Lorefern | yes | no | no | no | no | agreement to record meetings, a visibility plan |
| Penlark | yes | for tracked links | yes | no | no | permission to use the writing, two people who approve |
| Slatehire | yes, as an employer | for the careers address | yes | a careers address | no | local hiring and data rules, a retention rule, a privacy notice |

A "yes" means the system works poorly or not at all without it. "If you..." means only when you use that feature. This table is our reading of each system's own check list, not legal advice.
