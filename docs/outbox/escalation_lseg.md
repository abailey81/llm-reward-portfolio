# OUTBOX — LSEG/Datastream entitlement escalation
**Recipient guidance:** send to UCL Library Data Services (library data-support address) and CC the
IFT programme administrator; if the library redirects, forward to the LSEG/Refinitiv account contact
they name. Evidence backing every claim: `docs/evidence/entitlement_report.md` (+ `entitlement_probes.json`),
generated live by `make data-probe`. Body finalized verbatim from that report, with the account
identifier added. Nothing has been sent on your behalf.

---

**To:** UCL Library Data Services
**Cc:** IFT Programme Administration
**Subject:** Datastream/DSWS service enablement for MSc dissertation (supervisor: Dr R. Okhrati)

Dear Library Data Services,

For my IFTE0008 dissertation I require Datastream constituent lists (`LS&PCOMP` + monthly
`LS&PCOMPmmyy`, 2005–2016) and the `RI` total-return datatype for delisted/exited S&P 500 members.

My existing LSEG credentials AUTHENTICATE against the Datastream Web Service, but the account —
username **ZLDU178** — is "not entitled to ClientApi service". Could that service flag (DSWS/ClientApi)
be enabled on my existing account, or access granted via the Datastream Excel add-in?

Separately, my LSEG platform token carries no API scopes — if RDP data scopes (datagrid /
historical-pricing) can be attached to the account (I have regenerated an app key with the EDP API
permission), that would also unblock the build.

Could you also confirm whether UCL provides WRDS/CRSP access (`MSP500LIST`)?

Timeline is tight (data build starts mid-June). Thank you,

Tamer Atesyakar (MSc B&DF, IFT)
