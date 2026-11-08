# FRICTIONAL: Job-Search Agent 2

My log for JS2. Each entry is my own text, sent in chat; Claude Code copied it here word for word, adding only the dated headings and the evidence lines. Times are Eastern. JS1's log is in [js1/FRICTIONAL.md](js1/FRICTIONAL.md).

## Friday 11/6 to early Saturday 11/7 (written Sunday 11/8)

- **What I expected:** Signed in to Canvas on Friday afternoon expecting a straightforward setup process and standard rule definitions for the new assignment.
- **What surprised me:** The unexpected strictness required during the late-night gate setup around 1:00 AM, specifically navigating the permission boundaries and making sure every single potential failure case was accounted for before locking down GATE.md.
- **Why I'm typing my own notes now:** Taking full personal ownership of every reflection and note to ensure complete academic integrity, avoiding the generic AI phrasing that cost points on previous assignments.
- **Why 20 Claude calls:** Chose 20 calls because OpenAI alone has accumulated around 60 new postings since the last run, capping it at 20 judges a solid batch per run while keeping execution fast and within budget, leaving the rest of the backlog to wait for subsequent runs as designed.
- **What I hadn't checked yet:** As of early Saturday morning, no real run had actually been executed yet, I hadn't run the tests myself, the actual loop code hadn't even been written yet, and nobody knew about the upcoming Claude app update or the cc-plugin-privacy plugin.
- **What I decided versus what Claude did:** Claude laid out the options with measured numbers first and proposed defaults for the exits, repeat rule, and field mapping. I chose the budgets, error policies, and permission rules, and approved GATE.md (84d9f4c), while Claude drafted the code, tests, and documentation based on those accepted choices.

Evidence: GATE.md (`84d9f4c`); the build commits `ab2df17`, `10833a9`, `5df1dc4`.
