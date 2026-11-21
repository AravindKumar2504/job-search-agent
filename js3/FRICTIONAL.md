# FRICTIONAL.md: Job-Search Agent 3

My dated notes while building JS3. I type every entry myself; Claude Code only fixes spelling and adds the
evidence line under each entry. Entries keep the day they are about and say when they were written.

## Friday 2026-11-20 (written the same night, about 11:30 PM ET)

**Tried and expected.** I ran the agent at 6:39 AM and expected it to process the available job boards, check the postings and show me which jobs matched Jane's requirements. I expected an individual posting with missing information to be handled separately.

**Surprise.** I was surprised that one posting with a blank title caused the entire OpenAI board to be refused. I decided that only the posting with the missing title should be marked as "cannot tell" while the remaining postings should still be processed.

**My changes.** Across the four drafts, I changed the rules based on how they affected actual job postings. I made level restrictions hard again, decided to reject jobs outside the US, made years of experience required by default unless clearly optional, and added more specific rules for locations, start dates and technical keywords.

**Claude's part.** Claude helped review my rules against the saved postings, pointed out problems and suggested changes. After I asked Claude to stop asking me about every remaining decision and make the draft, it prepared Sections 2 to 7, which I can review and adjust.

**Still unsure.** I am still not completely sure whether the 60-point cutoff and the top 10 shortlist are the right choices. I want to see the actual results from the built filter and the audit before deciding whether the scoring and ranking need further changes.

*Evidence:* my run `runs/2026-11-20T113915Z` and the starting-point commit `34aa5d6`; FILTER.md v1.0 in
`66e26d9`, with my four drafts in `filter-drafts/`.
