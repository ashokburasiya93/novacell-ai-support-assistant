# Router study results

| Arm | Test acc | Test macro-F1 | Hard acc | Hard macro-F1 | Agent-action recall (test / hard) | p95 latency | Avg tokens in / out |
|---|---|---|---|---|---|---|---|
| llm-120b | 93.8% | 93.7% | 98.8% | 98.7% | 95.0% / 100.0% | 1760 ms | 593 / 27 |
| llm-20b | 88.8% | 89.0% | 85.0% | 85.8% | 100.0% / 100.0% | 1924 ms | 593 / 32 |
| finetuned-minilm | 95.6% | 95.6% | 88.8% | 88.7% | 95.0% / 90.0% | 6.9 ms | 0 / 0 |
| tfidf-logreg | 83.8% | 83.6% | 75.0% | 74.5% | 80.0% / 70.0% | 2.21 ms | 0 / 0 |

## llm-120b: errors

**test** (10 errors; top confusions: account -> agent_action ×5, roaming -> calls ×2, sim -> billing ×1, sim -> agent_action ×1, agent_action -> data ×1)

- `TE-sim-09` 'replacement SIM card price': gold sim, predicted billing
- `TE-sim-16` 'my SIM card is cracked': gold sim, predicted agent_action
- `TE-roaming-05` 'do I pay for receiving calls overseas': gold roaming, predicted calls
- `TE-roaming-15` 'does wifi calling cost anything abroad': gold roaming, predicted calls
- `TE-account-04` 'account locked after too many logins': gold account, predicted agent_action
- `TE-account-10` 'app shows a server error': gold account, predicted agent_action
- `TE-account-16` 'how do I close my online profile': gold account, predicted agent_action
- `TE-account-19` 'how to check my order status': gold account, predicted agent_action
- `TE-account-20` "transfer the account to my son's name - how does it work": gold account, predicted agent_action
- `TE-agent_action-10` 'how much data did I use last Tuesday on my line': gold agent_action, predicted data

**hard** (1 errors; top confusions: calls -> roaming ×1)

- `HD-calls-08` 'my phone only says SOS': gold calls, predicted roaming

## llm-20b: errors

**test** (18 errors; top confusions: account -> agent_action ×9, billing -> agent_action ×2, sim -> agent_action ×2, roaming -> calls ×1, roaming -> data ×1, calls -> agent_action ×1, calls -> roaming ×1, out_of_scope -> billing ×1)

- `TE-billing-04` 'how far back can I get old bills': gold billing, predicted agent_action
- `TE-billing-14` 'where do I find my invoice PDF': gold billing, predicted agent_action
- `TE-sim-08` 'moving eSIM to my new iPhone': gold sim, predicted agent_action
- `TE-sim-11` 'SIM PIN blocked after 3 tries': gold sim, predicted agent_action
- `TE-roaming-15` 'does wifi calling cost anything abroad': gold roaming, predicted calls
- `TE-roaming-18` 'can I use hotspot with the travel pass': gold roaming, predicted data
- `TE-calls-15` 'voicemail PIN forgotten': gold calls, predicted agent_action
- `TE-calls-20` 'is there an international calling bundle': gold calls, predicted roaming
- `TE-account-02` 'how to update the email on my account': gold account, predicted agent_action
- `TE-account-03` 'MyTelecom app crashes on launch': gold account, predicted agent_action
- `TE-account-04` 'account locked after too many logins': gold account, predicted agent_action
- `TE-account-06` "where's my account number": gold account, predicted agent_action
- `TE-account-10` 'app shows a server error': gold account, predicted agent_action
- `TE-account-12` "can I manage my partner's line from my login": gold account, predicted agent_action
- `TE-account-15` "the app won't show my usage": gold account, predicted agent_action
- `TE-account-19` 'how to check my order status': gold account, predicted agent_action
- `TE-account-20` "transfer the account to my son's name - how does it work": gold account, predicted agent_action
- `TE-out_of_scope-10` 'is T-Mobile cheaper than Verizon': gold out_of_scope, predicted billing

**hard** (12 errors; top confusions: account -> agent_action ×3, billing -> agent_action ×2, billing -> out_of_scope ×1, sim -> agent_action ×1, roaming -> data ×1, calls -> agent_action ×1, calls -> data ×1, account -> out_of_scope ×1)

- `HD-billing-01` 'y is my bill more than the plan price??': gold billing, predicted agent_action
- `HD-billing-05` "what's this 'regulatory recovery' thing": gold billing, predicted out_of_scope
- `HD-billing-06` 'bill pdf where': gold billing, predicted agent_action
- `HD-sim-03` 'lost my phone at the station, what do I do so nobody uses my number': gold sim, predicted agent_action
- `HD-roaming-09` 'can I use the hotspot while on the travel pass in Italy': gold roaming, predicted data
- `HD-calls-07` 'spam callers driving me mad': gold calls, predicted agent_action
- `HD-calls-08` 'my phone only says SOS': gold calls, predicted data
- `HD-account-03` 'need to change my email on file': gold account, predicted agent_action
- `HD-account-05` 'where do I find acct number': gold account, predicted agent_action
- `HD-account-09` 'change my address pls - how do I do it in the app': gold account, predicted agent_action
- `HD-account-10` 'is there a desktop version of the app or just mobile': gold account, predicted out_of_scope
- `HD-out_of_scope-07` 'who are you': gold out_of_scope, predicted invalid

## finetuned-minilm: errors

**test** (7 errors; top confusions: sim -> billing ×1, sim -> data ×1, calls -> roaming ×1, calls -> data ×1, calls -> account ×1, agent_action -> data ×1, out_of_scope -> agent_action ×1)

- `TE-sim-18` 'number transfer how many days': gold sim, predicted billing
- `TE-sim-20` 'where is the ICCID printed': gold sim, predicted data
- `TE-calls-06` 'what does it cost to call abroad': gold calls, predicted roaming
- `TE-calls-12` 'does my plan include unlimited minutes': gold calls, predicted data
- `TE-calls-14` 'how do I withhold my number': gold calls, predicted account
- `TE-agent_action-10` 'how much data did I use last Tuesday on my line': gold agent_action, predicted data
- `TE-out_of_scope-19` 'write an email to my boss asking for leave': gold out_of_scope, predicted agent_action

**hard** (9 errors; top confusions: data -> roaming ×2, calls -> data ×2, sim -> agent_action ×1, calls -> roaming ×1, account -> sim ×1, account -> agent_action ×1, agent_action -> sim ×1)

- `HD-data-05` "Hi, I'm working from a cafe and my laptop needs internet from my phone, is that allowed on my plan or do I need something extra?": gold data, predicted roaming
- `HD-data-09` "the little 5G sign never shows up even though I'm in the city": gold data, predicted roaming
- `HD-sim-06` 'put wrong pin 3 times now it wants some PUK thing': gold sim, predicted agent_action
- `HD-calls-04` 'phone never rings it just goes to vm': gold calls, predicted data
- `HD-calls-06` 'how much to ring my mum in Kerala': gold calls, predicted roaming
- `HD-calls-08` 'my phone only says SOS': gold calls, predicted data
- `HD-account-05` 'where do I find acct number': gold account, predicted sim
- `HD-account-08` 'locked out of my online account': gold account, predicted agent_action
- `HD-agent_action-09` 'my sim is blocked, unblock it': gold agent_action, predicted sim

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
