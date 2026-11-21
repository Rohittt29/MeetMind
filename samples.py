SAMPLES = {
    "Team Standup": "Alice: Hi guys, let's do the standup. My update: I finished the frontend login. Today I'll work on the API integration but I'm blocked on the auth token from Bob. Bob: Yeah, sorry about that, I'll send you the token by noon today. I'm finishing the database schema. Charlie: I'm working on the design system. Do we want to use React or Vue? Alice: I thought we agreed on React? Charlie: We didn't finalize it. Let's decide tomorrow. Bob: Ok.",
    "Client Call": "Client (Sarah): We reviewed the alpha build. We like the dashboard but we need the export to PDF feature before we can launch. Can we get that by Friday? PM (Mark): Export to PDF is tricky. Dev (John): I can probably do a basic PDF export by Friday, but it won't have the custom charts yet. Sarah: That's fine for now, we just need the data tables. Mark: Great, John will handle the basic PDF export by Friday. Also, Sarah, did your team approve the new pricing tier? Sarah: Not yet, our legal team is still reviewing it.",
    "Strategy Meeting": "CEO (David): We need to increase Q3 revenue. Marketing, what's the plan? CMO (Lisa): We're launching the summer campaign. We need $50k budget. CFO (Tom): We only have $30k allocated for marketing. David: We need to figure this out. Can we reallocate from HR? HR (Anna): We have $20k we haven't used, but we need it for hiring. David: Let's hold off on hiring for two weeks. Tom, move the $20k to marketing by tomorrow. Tom: Understood. Lisa, send me the campaign brief by EOD. Lisa: Will do."
}

# Authored preview for the client-call sample. Live analyses always use Gemini.
def client_preview():
    from analysis import Action, Drafts, Email, Notes, Quality

    return (
        Notes(summary="The client accepted a first PDF export containing data tables. Custom charts are outside the first release. Pricing approval is still with legal.",
              action_items=[Action(task="Deliver the basic PDF export with data tables.", owner="John", deadline="Friday", priority="Unspecified")],
              conflicts=["When will legal finish reviewing the new pricing tier?"]),
        Drafts(emails=[Email(owner="John", subject="PDF export for Friday",
                             body="Hi John,\n\nPlease deliver the basic PDF export with data tables by Friday. Sarah confirmed the first version can ship without custom charts.\n\nThanks!")]),
        Quality(clarity=8, decisiveness=8, accountability=7, overall=7.7,
                verdict="The export has a clear owner and deadline. The pricing review still needs a follow-up date."),
    )
