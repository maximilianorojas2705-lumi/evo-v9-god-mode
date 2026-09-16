# Changelog

All notable changes to Vibe-Trading are documented in this file.
This project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Changed

- **The final-answer grounding gate no longer guesses what a number is from the
  words around it.** Only a number's SHAPE is inferred — a decimal point, a
  percent sign, a currency mark or a table cell makes it a measurement; dates
  (including year-less "09-14"), years, security codes, line-leading ordinals
  and code in a language-tagged fence are structure; a plain integer is checked
  only as a price of an instrument quoted in the thousands — so a sentence
  gets the same verdict in every language. A measurement that equals a price
  or volume this session's tools returned needs nothing more. Any other one is
  declared in a fenced `figures` block at the end of the answer, one line per
  figure — `value | role | note | ref` — and checked by role: `observed` must
  appear in the referenced call or tool (`ref` may name either), filtered to
  the figure's own symbol, with a currency-marked figure compared only against
  money-denominated values and a percent only against non-price ones;
  `derived` needs an evaluable formula whose added or subtracted operands are
  all observed, matching the figure at the precision and sign it was written
  with; `proposed` is a price inside its own symbol's observed range or a
  derivation; `cited` must name its source on the figure's own line, because
  the block is stripped before anyone reads the answer; `count` covers counts,
  weights, thresholds and probabilities, while a currency-marked figure, or one
  inside its instrument's price range that no derivation uses as a factor, is
  checked as observed when declared `count`. No role other than `observed` may sit in a
  price column. The block is stripped from the released answer and never
  streamed; the artifact keeps it. The price-word, level-word,
  derivation-phrase and metric-subject catalogues are deleted with it
  (65 compiled regexes → 12, all shape), and `src/agent/grounding.py` is now
  the `src/agent/grounding/` package.
- **A rejected answer costs one correction round, not four, and is then
  released with its failing figures cut rather than refused.** The correction
  prompt lists every failing figure as written, with its declared role and what
  the evidence says (the observed range, the nearest observed values, or what
  its own formula evaluates to, in the figure's units), and names the three
  ways out: declare, rewrite to an observed value, or remove. If the second
  draft still fails, each failing figure is replaced by `（略※）` /
  `(omitted※)` at its own span, bare-integer restatements of a cut figure are
  swept too, a footnote says how many were omitted and why, and the whole
  document — footnote included — must pass the same gate before release. The
  canned fallback is left for an identity finding, a run that never observed a
  price, or a cut that still fails. Drafts that triggered bounded
  `search_symbol` / `get_market_data` recovery do not spend the correction
  budget. The run stays `degraded` with a reason naming the redaction, the
  release path's rechecks are not counted as rejected drafts, and the shipped
  document is recorded under `released` in `artifacts/grounding_evidence.json`.
- **A draft missing only a source or currency word gets a data note appended,
  not another model round.** The canonical symbol is deliberately not repaired
  this way: it is the figure's subject, and a note naming it under an answer
  about another instrument would footnote a misattribution.
- **The chat shows that the answer is being checked.** The agent loop emits
  `grounding_status` (`{stage: "revising", round, issues}` after a rejection,
  `{stage: "released_redacted", removed}` before a cut release), and the chat
  page shows "Checking the figures in this answer (round N)…" until answer text
  arrives, in all eight locales.

### Fixed

- **Plain integers in prose are not price claims.** A list number ("输出原则
  4"), a window length or a count was checked like a quoted price and could be
  cut from a released answer.
- **A drawdown against an observed high passes wherever the endpoints are
  written.** "较 5 月高点 1.053 元已回撤约 37%" was rejected when its endpoints sat
  on another line; a `derived` declaration does not depend on layout.
- **Price-denominated indicator values are evidence, by registration.**
  Moving averages, Bollinger bands and similar levels returned by
  `technical_indicators` are registered per tool as observed price evidence;
  RSI, MACD and other non-price leaves are not, and nothing is decided from a
  field name's words.
- **A year-less date is a date, and "24.6M" is 24.6 million.** Two real runs
  that followed the contract were still released redacted: "2026-09-11 /
  09-14" in a table cell shipped as "2026-09-11 /（略※）-（略※）", and
  "24.6M → 22.6M lots" as "(omitted※)M → (omitted※)M". A zero-padded MM-DD,
  or one opened by a full date in the same cell or line, is structure (an
  unpadded "| 11-12 |" is still checked, since it may be a price range). K / M
  / B / 千 / 万 / 亿 glued to a figure scale its comparison with the evidence,
  never its shape, and a cut removes the mark with the figure. Replayed on
  both runs' tool results, each second draft now passes as written.
- **Metadata counts are not metrics, and a tool's tail-risk result can ground
  a VaR** (#1420, #1426). `return_observations`, `n_returns`, `return_window`,
  `vol_lookback`, `max_drawdown_duration`, `aligned_days` and their `*_window` /
  `*_lookback` / `*_obs` / `n_*` / `*_count` / `*_days` / `*_duration` families
  no longer ground a percentage ("年化收益 81%" from 81 observations); `var`,
  `var_95`, `var_99`, `cvar`, `es` and `expected_shortfall` leaves are tail-risk
  evidence, so a correct VaR is no longer refused. A field's metric comes from
  the head of its name, so `sharpe_sample_size` and `drawdown_threshold` are
  no longer a Sharpe ratio or a drawdown.
- **A correction names the prints of the figure's own instrument** (#1433). The
  "nearest observed" values come from that symbol (and its table column or
  `ref`), not from every field of every symbol in the run.
- **A number is read the way the chat renders it** (#1418). Zero-width
  characters, a full-width or Arabic decimal point, a no-break space before
  "%", the U+2212 minus sign, a backslash escape ("0\\.888"), an HTML entity
  and an ISO code glued to the digits ("CNY0.888") no longer split a price into
  unchecked integers; a decimal comma ("0,666 CNY", "12,5 %") is a decimal
  while a valid grouping ("-1,250.00") stays grouped, and an answer that writes
  a marked decimal comma reads "2,237" and "−5,132%" beside it as decimals too. Fences follow CommonMark,
  and an unterminated code fence no longer exempts the rest of the answer.
- **A year is not a price shield.** "$2050", "1999 元" and a 2031 under a close
  column are checked; a price placed in a date or code column is checked; a
  compact date, a dotted date and a time are structure. 円 and 원 are currency
  marks, and "52pp" / "5200bp" are measurements.
- **A declaration cannot relocate or launder a figure.** A figure the sentence
  writes about one instrument cannot be declared another's close; a
  currency-marked result cannot be derived from an RSI or a volume; `count`,
  `derived` and `proposed` cannot sit in a price column.
- **A general answer with no tool evidence is cut, not refused.** A question
  about no instrument ("印花税怎么收") whose figures the gate cannot check is
  released with those figures omitted and a footnote, instead of a refusal
  about prices it never mentioned; a market answer that observed no price
  still falls back. A malformed figures block no longer forces the fallback
  either: the block is dropped and the draft is checked as written.
- **The tool-call-syntax fallback reaches the chat once.** When a model answered
  the forced-text iteration with tool-call markup in a run whose output is
  buffered, the replacement message was streamed by its own branch and again as
  the released answer, so the chat and the CLI showed it twice.
- **No unchecked number reaches the chat before the gate runs.** An unbuffered
  answer (no instrument asked about, no tool evidence yet) streamed its first
  draft live, numbers included, and a rejection then replaced it; the stream now
  stops at the first measurement-shaped number, and a rejected draft's shown
  prefix is cleared with `stream_reset`.
- **A trading plan in a bare code fence is checked.** Only a fence tagged with a
  language holds code; an untagged fence is read as prose.
- **An integer price of an instrument quoted in the thousands is checked**
  ("600519.SH 最新收盘 1520"), within half to twice its observed range; a
  window such as "200 日均线" stays unchecked.
- **A price declared `count` is checked.** A number inside its instrument's
  observed price range may be a `count` only when a declared derivation uses it
  as a factor.
- **A redaction footnote the model wrote itself is removed** before the real
  cuts, so a released answer never carries two contradictory footnotes or a
  marker for a cut that did not happen.
## [0.1.15] — 2026-09-09

Rolls up 551 commits / 162 merged pull requests since 0.1.14, from 35
contributors.

The theme of this cycle is data that says what it is. A price frame now
carries the adjustment caliber it was served under. A factor propagates the
gaps in its inputs instead of filling them. A loader that cannot serve a
market no longer claims it, and a source that fails to refresh is an error
rather than a smaller portfolio. Three of those were the same bug wearing
different clothes: a default that silently substitutes a plausible value for
a missing one, which is indistinguishable downstream from a real
observation. Three new markets, a fourteenth broker and fifteen Quant
Library additions land alongside.

### Added

- **UK equity market** (#1206, thanks @cgycorey) — LSE `.L` and `.IL`
  symbols end to end: market data, Yahoo-backed financial statements and
  indicators, trade-journal inference into `uk_equity`, and its own engine
  path. SDRT is modelled as what it actually is — a 0.5% duty on the
  **purchase** side only, not a symmetric round-trip cost. Charging both
  sides overstated the cost of every round trip by half, which is exactly
  the size of edge a mean-reversion strategy lives on.
- **Zerodha Kite Connect** (#1193, thanks @ashutoshsinghpr7) — a fourteenth
  broker connector for Indian equities. Kite exposes no runtime paper/live
  discriminator — no account-id format, host separation, demo flag or trade
  environment — so under the red line it is capped at paper plus read-only:
  `place_order` and `cancel_order` hard-refuse any non-paper config at the
  first line, and no `*-live-trade` profile exists to select. That now
  covers Longbridge, Dhan, Shoonya and Zerodha; Trading212 goes further and
  refuses all order placement including paper.
- **Read-only multi-broker portfolio** (#1072, thanks @goatyyc; onboarding
  contracts in #1250) — one aggregated snapshot across every enabled
  connection instance, reachable four ways: the Web `/portfolio` page, REST
  under `portfolio_routes.py`, the `portfolio_summary` agent tool, and
  `vibe-trading portfolio show | refresh | sources`. Three design points
  that are not incidental: a source that fails to refresh is an **error
  excluded from the totals** (status `error`, `last_success_at`,
  `complete=false`), never a carried-forward cache, so a partial snapshot
  cannot read as a smaller portfolio; every `remote_mcp` read passes
  `interactive_oauth=False`, so aggregation can never pop an auth prompt;
  and `analysis_context()` carries `risk_xray_args` so `portfolio_risk_xray`
  is *fed* rather than reimplemented. Eligibility is one rule —
  `is_portfolio_connection_profile` requires readonly **and** account.read
  **and** positio