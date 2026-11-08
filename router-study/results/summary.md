# Router study results

| Arm | Test acc | Test macro-F1 | Hard acc | Hard macro-F1 | Agent-action recall (test / hard) | p95 latency | Avg tokens in / out |
|---|---|---|---|---|---|---|---|
| tfidf-logreg | 83.8% | 83.6% | 75.0% | 74.5% | 80.0% / 70.0% | 2.21 ms | 0 / 0 |

## tfidf-logreg: errors

**test** (26 errors; top confusions: agent_action -> billing ×3, out_of_scope -> account ×3, out_of_scope -> agent_action ×3, calls -> data ×2, data -> out_of_scope ×1, data -> account ×1, data -> agent_action ×1, data -> billing ×1)

- `TE-data-06` '4G connected but pages time out': gold data, predicted out_of_scope
- `TE-data-08` 'where do I change APN on android': gold data, predicted account
- `TE-data-10` 'which add-on gives me the most GB for the price': gold data, predicted agent_action
- `TE-data-15` 'How many GB come with the starter plan?': gold data, predicted billing
- `TE-billing-13` 'how much does the Max plan cost per month': gold billing, predicted roaming
- `TE-sim-18` 'number transfer how many days': gold sim, predicted account
- `TE-sim-20` 'where is the ICCID printed': gold sim, predicted billing
- `TE-roaming-03` 'what do I need to do before an overseas trip': gold roaming, predicted sim
- `TE-roaming-05` 'do I pay for receiving calls overseas': gold roaming, predicted calls
- `TE-roaming-20` 'using my phone on a cruise ship': gold roaming, predicted data
- `TE-calls-06` 'what does it cost to call abroad': gold calls, predicted roaming
- `TE-calls-09` "data is fine but calls won't connect": gold calls, predicted data
- `TE-calls-12` 'does my plan include unlimited minutes': gold calls, predicted data
- `TE-calls-14` 'how do I withhold my number': gold calls, predicted sim
- `TE-account-20` "transfer the account to my son's name - how does it work": gold account, predicted agent_action
- `TE-agent_action-04` 'switch me to the Plus plan': gold agent_action, predicted billing
- `TE-agent_action-05` 'check why my bill is $30 higher this month': gold agent_action, predicted billing
- `TE-agent_action-07` 'there are calls on my bill I never made': gold agent_action, predicted billing
- `TE-agent_action-12` 'send a new SIM to my home': gold agent_action, predicted sim
- `TE-out_of_scope-04` 'how do I sort a list in JavaScript': gold out_of_scope, predicted account
- `TE-out_of_scope-09` 'recipe for biryani': gold out_of_scope, predicted agent_action
- `TE-out_of_scope-12` 'Tesla share price': gold out_of_scope, predicted billing
- `TE-out_of_scope-13` 'diet tips please': gold out_of_scope, predicted agent_action
- `TE-out_of_scope-14` 'can I sue my employer': gold out_of_scope, predicted account
- `TE-out_of_scope-16` 'how to change a flat tyre': gold out_of_scope, predicted account
- `TE-out_of_scope-19` 'write an email to my boss asking for leave': gold out_of_scope, predicted agent_action

**hard** (20 errors; top confusions: data -> out_of_scope ×3, data -> agent_action ×3, calls -> data ×2, agent_action -> sim ×2, data -> billing ×1, billing -> agent_action ×1, billing -> out_of_scope ×1, sim -> out_of_scope ×1)

- `HD-data-01` 'net not wrking since mrng pls help': gold data, predicted out_of_scope
- `HD-data-02` 'bought the 10gb thing yesterday but still feels like dial-up': gold data, predicted agent_action
- `HD-data-03` 'my hotspot thingy isnt sharing to my ipad': gold data, predicted agent_action
- `HD-data-04` 'is there a way to get more gigs without changing my whole plan?': gold data, predicted billing
- `HD-data-06` 'youtube is unwatchable': gold data, predicted out_of_scope
- `HD-data-08` 'how come my speeds tank every night around 9': gold data, predicted out_of_scope
- `HD-data-09` "the little 5G sign never shows up even though I'm in the city": gold data, predicted agent_action
- `HD-billing-03` "hi, I just want to understand what all the fees on my first bill are, it's confusing": gold billing, predicted agent_action
- `HD-billing-05` "what's this 'regulatory recovery' thing": gold billing, predicted out_of_scope
- `HD-sim-06` 'put wrong pin 3 times now it wants some PUK thing': gold sim, predicted out_of_scope
- `HD-roaming-01` 'flying to bkk tmrw what do i need to do with my phone': gold roaming, predicted sim
- `HD-roaming-04` "my brother got a huge bill abroad, how do i make sure that doesn't happen to me": gold roaming, predicted billing
- `HD-calls-04` 'phone never rings it just goes to vm': gold calls, predicted agent_action
- `HD-calls-08` 'my phone only says SOS': gold calls, predicted data
- `HD-calls-10` 'volte where in settings': gold calls, predicted data
- `HD-account-05` 'where do I find acct number': gold account, predicted sim
- `HD-agent_action-01` 'i want my money back for the roaming': gold agent_action, predicted roaming
- `HD-agent_action-02` "just cancel everything, I'm done with NovaCell": gold agent_action, predicted sim
- `HD-agent_action-09` 'my sim is blocked, unblock it': gold agent_action, predicted sim
- `HD-out_of_scope-09` 'my laptop screen is flickering': gold out_of_scope, predicted data
