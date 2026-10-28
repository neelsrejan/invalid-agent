window.QUIZZES = {
  "1": {
    "passMark": 0.8,
    "questions": [
      {
        "id": "s1q1",
        "prompt": "Why is the invalid-rate spec computed from 0.98 instead of typed as its own literal?",
        "choices": [
          {
            "id": "a",
            "text": "So the promised validity and the 2% invalid cap cannot drift apart."
          },
          {
            "id": "b",
            "text": "Because Jira refuses a field that is not a formula."
          },
          {
            "id": "c",
            "text": "Because pytest cannot compare two numeric literals."
          },
          {
            "id": "d",
            "text": "So the Wilson interval can skip the upper bound."
          }
        ],
        "salt": "1648a87e8b2a3dee",
        "answerHash": "f801faab7f187e2a9bcd4f066ba3eae7f7433b50a3f161a8f266c8f88db6f412",
        "explain": "U1BFQ19JTlZBTElEX1JBVEUgPSByb3VuZCgxIC0gUFJPTUlTRURfVkFMSURJVFksIDIpLiBOaW5ldHktZWlnaHQgcGVyY2VudCB2YWxpZCBtZWFucyBhdCBtb3N0IDIlIGludmFsaWQuIE9uZSBjb25zdGFudCBvd25zIHRoZSBwcm9taXNlLg=="
      },
      {
        "id": "s1q2",
        "prompt": "Which environment variables turn Jira on?",
        "choices": [
          {
            "id": "a",
            "text": "Only JIRA_API_TOKEN."
          },
          {
            "id": "b",
            "text": "A base URL, an email, and a token. Any missing piece leaves jira_enabled false."
          },
          {
            "id": "c",
            "text": "JIRA_PROJECT_KEY by itself."
          },
          {
            "id": "d",
            "text": "OPENFDA_API_KEY plus the email."
          }
        ],
        "salt": "397bee6cce6b881a",
        "answerHash": "3978a0788df4f9f2b461f8b38fc9ee6b0d0ccc9f4680c83b3fd7afb94fe8b64e",
        "explain": "VGhlIGdhdGUgaXMgYWxsIHRocmVlOiBKSVJBX0JBU0VfVVJMIG9yIEpJUkFfVVJMLCBKSVJBX0VNQUlMLCBhbmQgSklSQV9BUElfVE9LRU4gb3IgSklSQV9UT0tFTi4gVGhlIGxvbmdlciBuYW1lcyB3aW4gd2hlbiBib3RoIGFsaWFzZXMgYXJlIHNldC4="
      },
      {
        "id": "s1q3",
        "prompt": "What is wrong with the default frozen-dataclass repr?",
        "choices": [
          {
            "id": "a",
            "text": "It hides the repo root, so tests cannot find scenarios."
          },
          {
            "id": "b",
            "text": "It prints every field, including jira_api_token."
          },
          {
            "id": "c",
            "text": "It lowercases the model name and breaks Ollama."
          },
          {
            "id": "d",
            "text": "It cannot be called from pytest."
          }
        ],
        "salt": "7eeae6e7843514b8",
        "answerHash": "ebe8997eac473b6aaee9acf3b850d95c80afdeab293768388ce70020ad906787",
        "explain": "QSBwbGFudGVkIHNlY3JldCBpbiB0aGUgdG9rZW4gd291bGQgc2hvdyB1cCBpbiBsb2dzIGlmIHJlcHIgd2VyZSB0aGUgZGVmYXVsdC4gVGhlIG92ZXJyaWRlIHByaW50cyB0aGUgcmVkYWN0ZWQgdmlldyBvbmx5Lg=="
      },
      {
        "id": "s1q4",
        "prompt": "What is docs/jira/backlog.json, compared with the Jira sync added later?",
        "choices": [
          {
            "id": "a",
            "text": "The live customer-escalation board."
          },
          {
            "id": "b",
            "text": "The dry-run file of SIM-* investigation issues."
          },
          {
            "id": "c",
            "text": "The build backlog for constructing the agent. Sprint 1 is INV-101 through INV-109."
          },
          {
            "id": "d",
            "text": "The Week-0 triage memo."
          }
        ],
        "salt": "88a0929bc0363574",
        "answerHash": "8c4a7144acc24e8daf1e574b8f3adea4058656349ff0b5cdca5c29dff563151a",
        "explain": "VGhpcyBKU09OIGlzIHRoZSB0aHJlZS1zcHJpbnQgYnVpbGQgYm9hcmQuIFNlc3Npb24gNSB3cml0ZXMgYSBkaWZmZXJlbnQgc2V0LCB0aGUgZmljdGlvbmFsIGludmVzdGlnYXRpb24sIGFuZCB0aG9zZSBrZXlzIGFyZSBTSU0tKiBzbyB0aGUgdHdvIGZpbGVzIGNhbm5vdCBiZSBjb25mdXNlZC4="
      },
      {
        "id": "s1q5",
        "prompt": "Why is dependencies an empty list in Session 1 pyproject.toml?",
        "choices": [
          {
            "id": "a",
            "text": "Python 3.11 forbids third-party libraries."
          },
          {
            "id": "b",
            "text": "Nothing in this tag imports them yet, so CI should not download pandas, LangGraph, or a model client."
          },
          {
            "id": "c",
            "text": "The MIT license bans dependencies."
          },
          {
            "id": "d",
            "text": "setuptools cannot install a non-empty list."
          }
        ],
        "salt": "7e3e843c6a8a3b5a",
        "answerHash": "623c6041c0c8053961924005089651afda5fd3d7d771d3804ca1af28c2aca4f6",
        "explain": "TGF0ZXIgc2Vzc2lvbnMgYWRkIGEgbGlicmFyeSBvbmx5IHdoZW4gY29kZSBpbXBvcnRzIGl0LiBUaGUgbG9jYWwgbW9kZWwsIHdoZW4geW91IHdhbnQgb25lLCBpcyBNZXRhIExsYW1hIDMuMSA4QiB2aWEgT2xsYW1hLiBJdCBpcyBub3QgYSBkZXBlbmRlbmN5IGluIHRoaXMgdGFnLg=="
      },
      {
        "id": "s1q6",
        "prompt": "What does find_repo_root look for?",
        "choices": [
          {
            "id": "a",
            "text": "The first folder named out/."
          },
          {
            "id": "b",
            "text": "pyproject.toml sitting next to scenarios/ or src/invalid_agent/."
          },
          {
            "id": "c",
            "text": "An environment variable REPO_ROOT, which is required."
          },
          {
            "id": "d",
            "text": "A running Ollama process."
          }
        ],
        "salt": "e4d4cab896481ed3",
        "answerHash": "5f61387bbdd731e3d408cde426de7e5d195bdbae75c2f28be480567777c19d26",
        "explain": "V2Fsa2luZyBwYXJlbnRzIHVudGlsIHRoYXQgcGFpciBhcHBlYXJzIGtlZXBzIHNjZW5hcmlvIHBhdGhzIGNvcnJlY3Qgd2hlbiBTdHJlYW1saXQncyB3b3JraW5nIGRpcmVjdG9yeSBpcyB0aGUgcmVwbyBhbmQgd2hlbiB0aGUgcGFja2FnZSBpcyBhbiBlZGl0YWJsZSBpbnN0YWxsLg=="
      },
      {
        "id": "s1q7",
        "prompt": "LLM_BACKEND=rules-only becomes which backend?",
        "choices": [
          {
            "id": "a",
            "text": "ollama"
          },
          {
            "id": "b",
            "text": "llamacpp"
          },
          {
            "id": "c",
            "text": "deterministic"
          },
          {
            "id": "d",
            "text": "A hard error, because the name is unknown."
          }
        ],
        "salt": "8f5da9c3eef3b844",
        "answerHash": "e85fedb4dc2a86fe8d6c3753c8ddd133d6d5c3e7a7150e2aee2dbbe68527221c",
        "explain": "cnVsZXMsIHJ1bGVzLW9ubHksIGFuZCBtb2NrIGFyZSBzeW5vbnltcyBmb3IgZGV0ZXJtaW5pc3RpYy4gQW4gdW5rbm93biBuYW1lIGFsc28gZmFsbHMgYmFjayB0byBkZXRlcm1pbmlzdGljLCB3aGljaCBpcyB3aHkgYSBzbG9wcHkgdGVzdCBjYW4gcGFzcyBmb3IgdGhlIHdyb25nIHJlYXNvbi4="
      },
      {
        "id": "s1q8",
        "prompt": "What does the Session 1 GitHub Actions workflow run?",
        "choices": [
          {
            "id": "a",
            "text": "Python 3.11 and 3.12, editable install with the dev extra, then pytest. No secrets."
          },
          {
            "id": "b",
            "text": "Python 3.13 only, with a Jira token in the environment."
          },
          {
            "id": "c",
            "text": "A download of Llama 3.1 8B, then the dashboard."
          },
          {
            "id": "d",
            "text": "Streamlit Community Cloud."
          }
        ],
        "salt": "ac8759af61bd85bb",
        "answerHash": "3f79526b63ab5d9cd6244a80196ede80d90f05578af2672a85ac972ff9dd5c0a",
        "explain": "VGhlIHBsYW4gbmFtZXMgMy4xMS4gMy4xMiBpcyBhbHNvIGdhdGVkIGJlY2F1c2UgdGhhdCBpcyBhIGxhcHRvcCBpbnRlcnByZXRlciB5b3UgbWF5IGhhdmUuIFRoZSB3b3JrZmxvdyBuZXZlciBuZWVkcyBhIHRva2VuLg=="
      }
    ]
  },
  "2": {
    "passMark": 0.8,
    "questions": [
      {
        "id": "s2q1",
        "prompt": "Why does the generator redraw the cause mask instead of adding a second coin-flip on top of the baseline?",
        "choices": [
          {
            "id": "a",
            "text": "Stacking two draws would raise the complement too, or double-count the mask. Replacing the mask leaves everyone else at baseline."
          },
          {
            "id": "b",
            "text": "numpy cannot draw two Bernoulli variables in one function."
          },
          {
            "id": "c",
            "text": "The YAML forbids a baseline rate."
          },
          {
            "id": "d",
            "text": "So the Pareto chart can include valid rows."
          }
        ],
        "salt": "5b5e70da3b1520de",
        "answerHash": "cf5fc030b594f0c552203596098f90f33e1c4bdf784646569b182ca2c41cd50b",
        "explain": "VGhlIGNoaS1zcXVhcmUgdGVzdCBuZWVkcyBhIGNvbnRyYXN0OiB0aGUgY2F1c2Ugc3RyYXR1bSB2ZXJzdXMgcm93cyB0aGF0IHN0YXllZCBhdCB0aGUgYmFzZWxpbmUgcmF0ZS4gQWRkaW5nIHByb2JhYmlsaXRpZXMgd291bGQgc21lYXIgdGhhdCBjb250cmFzdC4="
      },
      {
        "id": "s2q2",
        "prompt": "What does the Wilson interval do for 0 invalids out of 100, and why?",
        "choices": [
          {
            "id": "a",
            "text": "It returns a negative lower bound and the caller clamps it."
          },
          {
            "id": "b",
            "text": "The analytic lower bound is 0. Floating point leaves a tiny residue, so anything under 1e-12 snaps back to 0."
          },
          {
            "id": "c",
            "text": "It raises, because a zero count is undefined."
          },
          {
            "id": "d",
            "text": "It returns the spec, 2%, as both ends."
          }
        ],
        "salt": "91c2c89da5b68c4d",
        "answerHash": "0645ba74a5e518587bce1a63de86081b6b7d241c69cda1749ea0b1f7f744546f",
        "explain": "VGhlIGZvcm11bGEncyBsb3dlciBib3VuZCBpcyAwIHdoZW4gayBpcyAwLiBUaGUgc25hcCBzdG9wcyBhIHJlc2lkdWUgYXJvdW5kIDFlLTE4IGZyb20gbG9va2luZyBsaWtlIGEgcmVhbCByYXRlIGluIHRoZSBtZW1vLg=="
      },
      {
        "id": "s2q3",
        "prompt": "A lot and an instrument both look high. Which design choice makes those two claims separable?",
        "choices": [
          {
            "id": "a",
            "text": "Site, instrument, lot, software, and operator are drawn independently. A collection site is not tied to one instrument."
          },
          {
            "id": "b",
            "text": "Each site owns exactly one instrument, so the columns are aliases."
          },
          {
            "id": "c",
            "text": "The lot id is copied into the instrument column."
          },
          {
            "id": "d",
            "text": "Software version changes on the same day the lot starts, on purpose."
          }
        ],
        "salt": "aa25122e5ee177ef",
        "answerHash": "d9b6b9011d07a2be7d62c09db7054d1490194ea4424356f113627790e934a48e",
        "explain": "VGhlIG1vZHVsZSBkb2NzdHJpbmcgc3RhdGVzIHRoZSByZWZlcmVuY2UtbGFiIGFzc3VtcHRpb24uIGJhZF9sb3QgYWxzbyBydW5zIGJvdGggc29mdHdhcmUgdmVyc2lvbnMgZm9yIHRoZSB3aG9sZSBob3Jpem9uIHNvIGEgdmVyc2lvbiBjdXRvdmVyIGlzIG5vdCBtaXN0YWtlbiBmb3IgdGhlIGxvdC4="
      },
      {
        "id": "s2q4",
        "prompt": "Which four Western Electric rules does this p-chart implement?",
        "choices": [
          {
            "id": "a",
            "text": "One point beyond 3 sigma; two of three beyond 2 sigma on one side; four of five beyond 1 sigma on one side; eight in a row on one side of the center."
          },
          {
            "id": "b",
            "text": "Only a single point outside the spec of 2%."
          },
          {
            "id": "c",
            "text": "A t-test on every instrument, every day."
          },
          {
            "id": "d",
            "text": "Nelson rules 5 through 8 only."
          }
        ],
        "salt": "f2ef2e7deccd4f1c",
        "answerHash": "be7a28a039a4a179475c410e3b11a12d0b3616f92be626d1eb3d33542ce738ed",
        "explain": "VGhleSBydW4gb24gei1zY29yZXMgaW4gdGltZSBvcmRlci4gUnVsZSA0IG5lZWRzIGV2ZXJ5IHogaW4gYSB3aW5kb3cgb2YgOCBzdHJpY3RseSBvbiBvbmUgc2lkZSwgc28gYSBwb2ludCBvbiB0aGUgY2VudGVyIGxpbmUgYnJlYWtzIHRoZSBydW4u"
      },
      {
        "id": "s2q5",
        "prompt": "Where do the Mendeley hemolysis-index rows live in this repo?",
        "choices": [
          {
            "id": "a",
            "text": "They do not. seeds.py holds a lognormal stand-in and the DOI. The file is cited, not redistributed."
          },
          {
            "id": "b",
            "text": "In scenarios/hil.csv, copied from the paper."
          },
          {
            "id": "c",
            "text": "openfda.py downloads them on every generate."
          },
          {
            "id": "d",
            "text": "Inside the Week-0 memo as an appendix."
          }
        ],
        "salt": "c56fcf3b3ee766c0",
        "answerHash": "b9058b86ee7ad29a1abfc66fd01c7cfc2c3f5f1346a44ebb54b7da1f4e0b0452",
        "explain": "SEVNT0xZU0lTX0JBU0VMSU5FIGFuZCBIRU1PTFlTSVNfU0VWRVJFIGFyZSBub3QgYSBmaXQgdG8gdGhhdCBmaWxlLiBEQVRBX0xJQ0VOU0VTLm1kIHNheXMgdGhlIHNhbWUgdGhpbmcuIG9wZW5mZGEucHkgY2FuIG9wdGlvbmFsbHkgYXNrIGZvciBhIGNvdW50IGFuZCBzd2FsbG93cyBuZXR3b3JrIGVycm9ycy4gZ2VuZXJhdGUgZG9lcyBub3QgY2FsbCBpdC4="
      },
      {
        "id": "s2q6",
        "prompt": "What does numpy's default_rng buy the PM?",
        "choices": [
          {
            "id": "a",
            "text": "A scenario file plus a seed is the whole source of randomness, so the same YAML reprints the same field file."
          },
          {
            "id": "b",
            "text": "A new random sample on every run, so the rate can be whatever the meeting needs."
          },
          {
            "id": "c",
            "text": "A call out to Ollama to invent rows."
          },
          {
            "id": "d",
            "text": "The Wilson formula."
          }
        ],
        "salt": "a6700a25f200619a",
        "answerHash": "bdf93606450dcc333be92b7dce5e66667683d2eaae3478578e758578ea587b7a",
        "explain": "Z2VuZXJhdGUgZG9lcyBuID0gaG9yaXpvbiB0aW1lcyBydW5zIHBlciBkYXksIHRoZW4gYmFzZWxpbmUsIHRoZW4gdGhlIGNhdXNlLiBzdW1tYXJpemUgb25seSBmb3JtYXRzIG1ldHJpY3MuIElmIGEgcHJpbnRlZCBudW1iZXIgaXMgd3JvbmcsIHRoZSBidWcgaXMgaW4gdGhlIGdlbmVyYXRvciBvciB0aGUgbWV0cmljcywgbm90IGluIGEgc2VudGVuY2Uu"
      },
      {
        "id": "s2q7",
        "prompt": "What does chi_square_by return when the table has a single level?",
        "choices": [
          {
            "id": "a",
            "text": "It raises ZeroDivisionError."
          },
          {
            "id": "b",
            "text": "p_value 1 and chi2 0. A quiet scenario is not an exception."
          },
          {
            "id": "c",
            "text": "p_value 0, which forces an escalation."
          },
          {
            "id": "d",
            "text": "The Wilson interval of the one level."
          }
        ],
        "salt": "5f9fec985ab3e5d2",
        "answerHash": "c2ad457d42d4c9b6085b928f11984d4bd8d80546404f959c982a563ad28c9d16",
        "explain": "T25lIHN0cmF0dW0sIG9yIGEgY29sdW1uIG9mIGFsbCB6ZXJvcywgbWVhbnMgdGhlcmUgaXMgbm8gZXZpZGVuY2Ugb2YgYSBkaWZmZXJlbmNlLiBSZXR1cm5pbmcgcCA9IDEgbGV0cyB0aGUgcmFua2VyIG1vdmUgb24gaW5zdGVhZCBvZiBjcmFzaGluZyB0aGUgbWVtby4="
      },
      {
        "id": "s2q8",
        "prompt": "What does the Pareto exclude?",
        "choices": [
          {
            "id": "a",
            "text": "Valid rows. An empty invalid code must not count as a failure mode."
          },
          {
            "id": "b",
            "text": "The most common code, so the chart shows only the tail."
          },
          {
            "id": "c",
            "text": "Any code whose share is under 5%."
          },
          {
            "id": "d",
            "text": "Rows from the injected lot."
          }
        ],
        "salt": "b07fdadfa4b089fc",
        "answerHash": "0faf403c51fb4e1f0b2f665937e81b65b4bddfb9b4a16dde871d44e90c06f75f",
        "explain": "cGFyZXRvIGtlZXBzIHJvd3Mgd2hlcmUgaW52YWxpZCBpcyB0cnVlLCBvcmRlcnMgY29kZXMgYnkgY291bnQsIGFuZCBjbG9zZXMgY3VtdWxhdGl2ZV9zaGFyZSBhdCAxLiBUaGF0IGNoYXJ0IGlzIHRoZSBQTSdzICd3aGljaCBmYWlsdXJlIG1vZGUnIHBpY3R1cmUsIGFuZCBpdCBpcyBjb21wdXRlZCwgbm90IG5hcnJhdGVkLg=="
      }
    ]
  },
  "3": {
    "passMark": 0.8,
    "questions": [
      {
        "id": "s3q1",
        "prompt": "What does the triage node store instead of the 14,400-row frame, and how does a later node get the rows back?",
        "choices": [
          {
            "id": "a",
            "text": "It stores metrics, hypotheses, the evidence catalog, the memo, and the fidelity record. A later node calls generate(scenario) again. The seed makes that the same frame."
          },
          {
            "id": "b",
            "text": "It stores the dataframe on the LangGraph state under the key rows."
          },
          {
            "id": "c",
            "text": "It writes the CSV into the Jira description."
          },
          {
            "id": "d",
            "text": "It asks Llama 3.1 8B to remember the table."
          }
        ],
        "salt": "704adf6e93902395",
        "answerHash": "3ab7e168e8a7ea27dd6cd4805a426ab0f56ccfcc8c41017b34b430174434d5a5",
        "explain": "VGhlIHN0YXRlIGhvbGRzIHRoZSBzY2VuYXJpbyBkaWN0IGFuZCBlbXB0eSBsaXN0cyBmb3IgbGF0ZXIgYXJ0aWZhY3RzLiBJdCBkb2VzIG5vdCBob2xkIGEgZGF0YWZyYW1lLiBTYW1lIHNlZWQsIHNhbWUgMTQsNDAwIHJvd3Mu"
      },
      {
        "id": "s3q2",
        "prompt": "Why does the bad-lot memo list one hypothesis rather than six?",
        "choices": [
          {
            "id": "a",
            "text": "The template has room for one sentence."
          },
          {
            "id": "b",
            "text": "Other strata miss at least one gate: 80 runs, lift 1.8, 15 excess invalids, and chi-square p < 0.01."
          },
          {
            "id": "c",
            "text": "Injections outvote every stratum except the lot."
          },
          {
            "id": "d",
            "text": "LangGraph nodes may return only one string."
          }
        ],
        "salt": "1708eb66038a7db0",
        "answerHash": "171bf9799569f00e3780d76096163e381f2b5ea084bea28daed7dd5ce9b9f218",
        "explain": "QSBsZXZlbCB0aGF0IGZhaWxzIGEgZ2F0ZSBpcyBkcm9wcGVkLCBub3QgZ2l2ZW4gYSBzbWFsbCBzY29yZS4gTC00NDE5IGNsZWFycyB0aGUgYmFyLiBJbnN0cnVtZW50cyBhcm91bmQgNCUgZG8gbm90LiBUd28gY2xvc2Ugd2lubmVycyB3b3VsZCBiZWNvbWUgbm9fc2luZ2xlX2NhdXNlIGluc3RlYWQgb2YgYSBjb2luIGZsaXAu"
      },
      {
        "id": "s3q3",
        "prompt": "Where does the planted sentence 'the invalid rate is 27.40%' die?",
        "choices": [
          {
            "id": "a",
            "text": "Masking removes it because 27.40 looks like a lot id."
          },
          {
            "id": "b",
            "text": "It survives masking, it is not within 0.03 of a walked fact, it lands in unknown, and ok is false."
          },
          {
            "id": "c",
            "text": "The guard accepts it because 27 is close to the week number."
          },
          {
            "id": "d",
            "text": "Ollama rewrites it before the guard runs."
          }
        ],
        "salt": "8aac7c13409ac90b",
        "answerHash": "f258bc4de148bd992370871b5167ec0572afeb66281a81d3a4e50ff7619d0c56",
        "explain": "SWRlbnRpZmllcnMgc3VjaCBhcyBMLTQ0MTkgYXJlIHN0cmlwcGVkIG9ubHkgd2hlbiB0aGF0IGV4YWN0IHN0cmluZyBpcyBpbiB0aGUgZmFjdHMuIDI3LjQwIGlzIG5vdCBvbmUgb2YgdGhlbS4gMy42NyBpcyBhbGxvd2VkIGJlY2F1c2UgdGhlIHN0b3JlZCByYXRlIDAuMDM2NyBjb250cmlidXRlcyBpdHMgcGVyY2VudCBmb3JtLg=="
      },
      {
        "id": "s3q4",
        "prompt": "What happens if the Ollama backend is selected and the process cannot reach it?",
        "choices": [
          {
            "id": "a",
            "text": "narrate catches the exception, sets rewritten true, and returns the template. The failed draft is not saved."
          },
          {
            "id": "b",
            "text": "The memo is left blank so the reviewer notices."
          },
          {
            "id": "c",
            "text": "The process exits and deletes week0_triage.md."
          },
          {
            "id": "d",
            "text": "The draft is saved with a warning banner and the bad number intact."
          }
        ],
        "salt": "0fc9ec0466f832cb",
        "answerHash": "ef61b9aedfd79b8a71526afd70299c7298cf0dca3bf674b51d2f989211a18dad",
        "explain": "VGhlIHRlbXBsYXRlIGlzIHJlbmRlcmVkIGZpcnN0LiBEZXRlcm1pbmlzdGljIG1vZGUgcmV0dXJucyBpdCBhZnRlciBhIGNoZWNrLiBBbnkgb3RoZXIgYmFja2VuZCB0aGF0IGVycm9ycywgcmV0dXJucyBlbXB0eSB0ZXh0LCBvciBmYWlscyB0aGUgZ3VhcmQgaXMgcmVwbGFjZWQuIEEgYnJva2VuIHRlbXBsYXRlIGlzIGEgYnVnIGFuZCByYWlzZXMu"
      },
      {
        "id": "s3q5",
        "prompt": "Why does rank_hypotheses ignore stakeholder injections?",
        "choices": [
          {
            "id": "a",
            "text": "A cause has to come from the table. A QA sentence does not get a vote."
          },
          {
            "id": "b",
            "text": "Injections are applied as extra rows before the chi-square test."
          },
          {
            "id": "c",
            "text": "The YAML schema has no injections field yet."
          },
          {
            "id": "d",
            "text": "LangChain refuses to read strings."
          }
        ],
        "salt": "749f56b8d4991b45",
        "answerHash": "e55be4afc1042e8c30f68855e83db7ecd70899c8e147615a000513cc12c58e64",
        "explain": "SW5qZWN0aW9ucyBhcmUgdGV4dC4gU2Vzc2lvbiA2IHNob3dzIHRoZW0gdG8gdGhlIHN0YXR1cyB3cml0ZXIuIFRoZXkgZG8gbm90IG91dHJhbmsgdGhlIGZpZWxkIGZpbGUuIGV2aWRlbmNlX2NhdGFsb2cgaXMgd2hhdCBsYXRlciBjaXRhdGlvbnMgYXJlIGFsbG93ZWQgdG8gdXNlLg=="
      },
      {
        "id": "s3q6",
        "prompt": "What does this tag do with --week other than 0?",
        "choices": [
          {
            "id": "a",
            "text": "It runs the full four-week loop."
          },
          {
            "id": "b",
            "text": "It exits on purpose, so the tag cannot pretend the weekly loop already exists."
          },
          {
            "id": "c",
            "text": "It skips triage and writes only the fishbone."
          },
          {
            "id": "d",
            "text": "It switches the model to Llama 3.2 1B."
          }
        ],
        "salt": "dd757ad561f4552a",
        "answerHash": "476d9e5092d9c1cf8b444918d5bb9edffc5ea76ca41e236a82841873ea4126b2",
        "explain": "YnVpbGRfZ3JhcGggaGFzIG9uZSBub2RlLCB0cmlhZ2UsIGVkZ2VkIHRvIEVORC4gVGhlIHdlZWtseSBsb29wIGlzIGEgbGF0ZXIgc2Vzc2lvbi4gSG9zdGVkIFN0cmVhbWxpdCwgd2hlbiBpdCBhcnJpdmVzLCBzdGF5cyBydWxlcy1vbmx5LiBUaGlzIHRhZydzIGRlbW8gaXMgdGhlIGRldGVybWluaXN0aWMgbWVtby4="
      },
      {
        "id": "s3q7",
        "prompt": "Why httpx, and not LangChain's Ollama integration?",
        "choices": [
          {
            "id": "a",
            "text": "One httpx call is easier to mock, and it is not called when the backend is deterministic."
          },
          {
            "id": "b",
            "text": "httpx is the only library that can speak to Llama 3.1."
          },
          {
            "id": "c",
            "text": "LangGraph requires httpx for every node, even rules-only."
          },
          {
            "id": "d",
            "text": "CI downloads the model through httpx."
          }
        ],
        "salt": "87adf0c5fd9f6348",
        "answerHash": "8350c3e6d73eb9ba29273f27ab601a4214c399bf2c1685c51e7a06a5bcd4523d",
        "explain": "bGFuZ2NoYWluLWNvcmUgb25seSBzdXBwbGllcyB0aGUgcm9sZSBhbmQgY29udGVudCBwYWlycy4gbGxhbWEtY3BwLXB5dGhvbiBpcyBub3QgYSBkZXBlbmRlbmN5LiBJdCBpcyBpbXBvcnRlZCBvbmx5IGlmIHRoYXQgYmFja2VuZCBpcyBzZWxlY3RlZCwgYW5kIGEgbWlzc2luZyBpbnN0YWxsIGZhbGxzIGJhY2sgdG8gdGhlIHRlbXBsYXRlLg=="
      },
      {
        "id": "s3q8",
        "prompt": "Why are lot ids removed from the narrative instead of added to the numeric allow-list?",
        "choices": [
          {
            "id": "a",
            "text": "So 4419 cannot be reused as a permitted rate."
          },
          {
            "id": "b",
            "text": "So the guard runs faster on short memos."
          },
          {
            "id": "c",
            "text": "Because Pydantic cannot store strings."
          },
          {
            "id": "d",
            "text": "Because the Wilson formula rejects integers."
          }
        ],
        "salt": "cb34da6250585deb",
        "answerHash": "2aee6dda2075fd35f2cda103443760a7db576e7dc3fcb99b1a3f5e5f8783a162",
        "explain": "TWFza2luZyBMLTQ0MTkgcmVtb3ZlcyB0aGUgaWRlbnRpZmllci4gSXQgZG9lcyBub3QgYXV0aG9yaXplIHRoZSBudW1iZXIgNDQxOSBhbnl3aGVyZSBlbHNlIGluIHRoZSBwYXJhZ3JhcGguIFRoZSBzYW1lIGlkZWEgbGF0ZXIgY292ZXJzIGEgc29mdHdhcmUgdmVyc2lvbiBzdWNoIGFzIDIuNC4wLg=="
      }
    ]
  },
  "4": {
    "passMark": 0.8,
    "questions": [
      {
        "id": "s4q1",
        "prompt": "Why is Measurement on the fishbone if the ranker has no measurement cause?",
        "choices": [
          {
            "id": "a",
            "text": "The 6M set is the diagram a quality reviewer expects. An empty bone with score zero says the category was considered."
          },
          {
            "id": "b",
            "text": "Measurement is always rank 1."
          },
          {
            "id": "c",
            "text": "The YAML injection names a gauge, so the bone is required to be non-empty."
          },
          {
            "id": "d",
            "text": "Pydantic rejects a fishbone with fewer than six filled bones."
          }
        ],
        "salt": "b3bfe52c32388dbf",
        "answerHash": "8f0383343c59fa6296f77321617fcb7daa970ffa175ce4a9dbe890c7bbb4e097",
        "explain": "RHJvcHBpbmcgdGhlIGJvbmUgd291bGQgbG9vayBsaWtlIHRoZSBjYXRlZ29yeSB3YXMgbmV2ZXIgY29uc2lkZXJlZC4gTWF0ZXJpYWwgYXBwZWFycyB0d2ljZSwgbG90IGFuZCBoZW1vbHlzaXMsIGJlY2F1c2UgYm90aCBhcmUgbWF0ZXJpYWwgYW5kIHRoZXkgYXJlIGRpZmZlcmVudCBhY3Rpb25zLg=="
      },
      {
        "id": "s4q2",
        "prompt": "What does validate_whys reject, and when does it run?",
        "choices": [
          {
            "id": "a",
            "text": "An empty citation list, or an id that is not in the catalog. It runs inside build_whys, before markdown exists."
          },
          {
            "id": "b",
            "text": "Any Why shorter than 200 characters, after the file is written."
          },
          {
            "id": "c",
            "text": "A fishbone whose rank-1 score is zero. It runs in CI only."
          },
          {
            "id": "d",
            "text": "A citation of metric:overall:rate, which is reserved for the memo."
          }
        ],
        "salt": "93be1754b6c9245e",
        "answerHash": "54f914b78359419e81dd044a5e9617770bffbe76fb4006430647517bc44d9908",
        "explain": "QSBXaHkgd2l0aCBubyBjaXRhdGlvbiBpcyBhbiBlcnJvciwgbm90IGEgd2FybmluZy4gVGhlIHRlc3QgcGxhbnRzIGNpdGF0aW9ucyBbXSBhbmQgZXhwZWN0cyAnd2h5IDEgaGFzIG5vIGNpdGF0aW9uJy4gQSBicm9rZW4gY2hhaW4gbmV2ZXIgYmVjb21lcyBhIGZpbGUu"
      },
      {
        "id": "s4q3",
        "prompt": "On bad_lot at week 0, can the 5 Whys cite the QA note about lot L-4419?",
        "choices": [
          {
            "id": "a",
            "text": "Yes. Every injection in the YAML is visible from week 0."
          },
          {
            "id": "b",
            "text": "No. index_injections keeps only injections whose week is less than or equal to the case week. That note is week 1."
          },
          {
            "id": "c",
            "text": "Yes, but only on the Measurement bone."
          },
          {
            "id": "d",
            "text": "No, because QA notes are excluded from the catalog forever."
          }
        ],
        "salt": "d02672bcc70a5833",
        "answerHash": "d14577d97e2af93ae1b608cbe03eb758055fa90ebed1fb3740042b01f09fb0bd",
        "explain": "QXQgd2VlayAxIHRoZSBub3RlIGJlY29tZXMgY2l0YWJsZSwgd2l0aCBhbiBpZCBsaWtlIGluamVjdGlvbjoxOnFhLiBjYXRhbG9nLnVwZGF0ZShpbmplY3Rpb25zKSBpcyB3aGF0IG1ha2VzIHRoYXQgaWQgbGVnYWwuIEJlZm9yZSB0aGF0IGxpbmUsIHZhbGlkYXRlX3doeXMgd291bGQgcmVqZWN0IGl0Lg=="
      },
      {
        "id": "s4q4",
        "prompt": "What is the effectiveness metric in D6, and why does the record not claim the rate already recovered?",
        "choices": [
          {
            "id": "a",
            "text": "Return to the spec and no rule-1 point on the weekly p-chart. Follow-up runs do not exist, so a before/after figure would be a projection."
          },
          {
            "id": "b",
            "text": "Customer satisfaction from a survey the model invents."
          },
          {
            "id": "c",
            "text": "The lot is already cured because D8 is closed."
          },
          {
            "id": "d",
            "text": "A new chi-square the language model computes."
          }
        ],
        "salt": "449c20a72f81b969",
        "answerHash": "cd1e52c7877ece623781795ad67ac833d507d4af1945f1d65bec2ad96406ee97",
        "explain": "RDcgYW5kIEQ4IGFyZSB3cml0dGVuIGFuZCBtYXJrZWQgcHJlbGltaW5hcnkuIFRoZSBDQVBBIHNheXMgc28sIHNvIGEgcmVhZGVyIGRvZXMgbm90IHRoaW5rIHRoZSBpbnZlc3RpZ2F0aW9uIGlzIGFscmVhZHkgY2xvc2VkLiBUaGUgd29yZCBydWxlLTEga2VlcHMgdGhhdCBkaWdpdCBnbHVlZCB0byBhIGh5cGhlbiBmb3IgdGhlIGZpZGVsaXR5IHNjYW5uZXIu"
      },
      {
        "id": "s4q5",
        "prompt": "Where do DMAIC labels sit relative to the eight Ds?",
        "choices": [
          {
            "id": "a",
            "text": "Define is D1–D2, Measure is the metrics, Analyze is D4 plus the fishbone and 5 Whys, Improve is D3 and D5, Control is D6 and D7. D8 is closure, not a DMAIC phase."
          },
          {
            "id": "b",
            "text": "Each D is its own DMAIC cycle, so there are eight cycles."
          },
          {
            "id": "c",
            "text": "DMAIC replaces D4 through D6 and the other Ds are dropped."
          },
          {
            "id": "d",
            "text": "DMAIC is only a slide title in Session 9. It is not in this tag."
          }
        ],
        "salt": "6ea08b9512df6622",
        "answerHash": "7cf8c3f505e0deaea7cfcc04dcad393b201f2288b286d2433fcefef03a7a7724",
        "explain": "QSBxdWFsaXR5IGhpcmluZyBtYW5hZ2VyIGxvb2tzIGZvciB0aGF0IG1hcHBpbmcuIFRoZSBsYWJlbHMgbGl2ZSBpbiB0aGUgQ0FQQSBmaWxlLCBub3QgYXMgYSBjbGFpbSB0aGF0IGFuIGFnZW50IHN3YXJtIGRpZCB0aGUgYW5hbHlzaXMu"
      },
      {
        "id": "s4q6",
        "prompt": "On bad_lot, what is rank 1, and what must step 5 say?",
        "choices": [
          {
            "id": "a",
            "text": "Material / bad_reagent_lot. Step 5 starts with a lot-level stop and includes the catalog sentence that names L-4419."
          },
          {
            "id": "b",
            "text": "Method / software. Step 5 names version 2.4.0."
          },
          {
            "id": "c",
            "text": "no_single_cause. Step 5 invents a lot so the bad-lot test passes."
          },
          {
            "id": "d",
            "text": "Measurement, because the empty bone sorts first."
          }
        ],
        "salt": "3f3a9a31af48a4e2",
        "answerHash": "91f05f406ce7a0bd62fa564425b730820e0a130329b38ffbb9f7a91788b3c042",
        "explain": "VGhlIHNvcnQgaXMgYnkgZGVzY2VuZGluZyBzY29yZS4gVGhlIGxvdCBpcyB0aGUgb25seSBub24temVybyBzY29yZS4gSGVtb2x5c2lzIGlzIGFsc28gTWF0ZXJpYWwgYW5kIHN0YXlzIGF0IDAgdW5kZXIgaXQuIG5vX3NpbmdsZV9jYXVzZSBpcyBub3QgYSBib25lLg=="
      },
      {
        "id": "s4q7",
        "prompt": "What does step 3 of the 5 Whys have to cite?",
        "choices": [
          {
            "id": "a",
            "text": "A different column, so the chain says why the next stratum is not the cause."
          },
          {
            "id": "b",
            "text": "The same sentence as step 2, copied twice."
          },
          {
            "id": "c",
            "text": "The Jira token."
          },
          {
            "id": "d",
            "text": "Whatever the model prefers, with no catalog id."
          }
        ],
        "salt": "6eb0462f25d2fd76",
        "answerHash": "507272bc49104c1a19c72df300014453ef02bace404565bb15dc23d8e3ed46e4",
        "explain": "U3RlcCAxIGlzIG92ZXJhbGwgdmVyc3VzIHNwZWMuIFN0ZXAgMiBpcyB0aGUgd2lubmluZyBzdHJhdHVtLiBTdGVwIDMgaXMgdGhlIGNvbnRyYXN0LiBTdGVwIDQgY2l0ZXMgYW4gaW5qZWN0aW9uIHRoYXQgbmFtZXMgdGhlIGxldmVsLCBvciB0aGUgc3RyYXR1bSdzIG4gc2VudGVuY2Ugd2hlbiBubyBpbmplY3Rpb24gaGFzIGFycml2ZWQu"
      },
      {
        "id": "s4q8",
        "prompt": "Which new package does Session 4 add?",
        "choices": [
          {
            "id": "a",
            "text": "None. Pydantic checks the branch and the Why. The Session 3 fidelity guard is reused on the three markdown files."
          },
          {
            "id": "b",
            "text": "A fishbone drawing library."
          },
          {
            "id": "c",
            "text": "kaleido, for the CAPA PDF."
          },
          {
            "id": "d",
            "text": "Llama 3.2 1B, downloaded in CI."
          }
        ],
        "salt": "305d08e0d687d061",
        "answerHash": "d7e398798648a0ad8056155d65e3661bb82e9bcb0a85e11f4827efcb2a008cb5",
        "explain": "VGhlIGdyYXBoIGlzIHRyaWFnZSB0aGVuIHJjYSB0aGVuIEVORC4gcnVuX2Nhc2Ugd3JpdGVzIHRoZSBtZW1vIHBsdXMgZmlzaGJvbmUubWQsIGZpdmVfd2h5cy5tZCwgYW5kIGNhcGE4ZC5tZC4gV2Vla3MgYWJvdmUgMCBvbmx5IGNoYW5nZSB3aGljaCBpbmplY3Rpb25zIFJDQSBjYW4gY2l0ZS4gVGhlIHBsYW4gaXMgU2Vzc2lvbiA1Lg=="
      }
    ]
  },
  "5": {
    "passMark": 0.8,
    "questions": [
      {
        "id": "s5q1",
        "prompt": "Why is the Gantt PNG not fig.write_image?",
        "choices": [
          {
            "id": "a",
            "text": "write_image needs kaleido and a browser. The matplotlib path runs in CI and on a laptop without that download."
          },
          {
            "id": "b",
            "text": "Plotly cannot draw a timeline."
          },
          {
            "id": "c",
            "text": "PNG files are disallowed in the repo."
          },
          {
            "id": "d",
            "text": "Jira rejects images that did not come from kaleido."
          }
        ],
        "salt": "5605f72faeb11c80",
        "answerHash": "db6794d12da490793bad62fcffaea9b3cc69d9f90faecd21423488d3f9b4802f",
        "explain": "VGhlIEhUTUwgaXMgcHgudGltZWxpbmUgc28gYSByZXZpZXdlciBjYW4gaG92ZXIgb3duZXJzLiBpbmNsdWRlX3Bsb3RseWpzIGNkbiBrZWVwcyB0aGF0IGZpbGUgc21hbGxlci4gVGhlIFBORyBkcmF3cyBvbmUgYmFyaCBwZXIgdGFzaywgcmV2ZXJzZWQgc28gVDEgaXMgb24gdG9wLCBhbmQgYSBtaW5pbXVtIHdpZHRoIHNvIGEgc2hvcnQgdGFzayBkb2VzIG5vdCB2YW5pc2gu"
      },
      {
        "id": "s5q2",
        "prompt": "What is the dependency rule, and why is a string comparison of the dates safe?",
        "choices": [
          {
            "id": "a",
            "text": "A task's start must be greater than or equal to the predecessor's end. The dates are YYYY-MM-DD, so dictionary order matches calendar order."
          },
          {
            "id": "b",
            "text": "A task may start the day before its predecessor ends, to create overlap."
          },
          {
            "id": "c",
            "text": "Dependencies are comments. The assert never runs."
          },
          {
            "id": "d",
            "text": "Dates are compared as US month/day strings."
          }
        ],
        "salt": "1fd73dfa8ef8435f",
        "answerHash": "277f637e2054108b4892f29c8c6d75a3ed3992c4446e4d8ca229ed311b481021",
        "explain": "VGhlIGVuZCBpcyBleGNsdXNpdmU6IHN0YXJ0IHBsdXMgZGF5cy4gVGhlIHRlc3Qgd2Fsa3MgVDgsIHdoaWNoIHN0YXJ0cyB3aGVuIFQ2IGVuZHMsIGluc3RlYWQgb2YgdHJ1c3RpbmcgYSBjb21tZW50LiBBIGhhbmQtZWRpdGVkIGVhcmx5IHN0YXJ0IHJhaXNlcy4="
      },
      {
        "id": "s5q3",
        "prompt": "What changes between week 0 and week 2 on the Gantt and the risk register?",
        "choices": [
          {
            "id": "a",
            "text": "Week 2 adds T11, the lab-director note. R1's trend goes from new to down and its likelihood drops. R4 appears with trend up."
          },
          {
            "id": "b",
            "text": "Every baseline task is deleted and replaced."
          },
          {
            "id": "c",
            "text": "The Gantt is unchanged. Only the memo title changes."
          },
          {
            "id": "d",
            "text": "R4 is deleted because release testing passed."
          }
        ],
        "salt": "0b6527d5129bd6de",
        "answerHash": "d201f4af8ce37745f36e1b9b4b954e2bfe8df4012b584d04ef0fd64b03acc9b6",
        "explain": "VDEyLCBsYW5lIHRlbXBlcmF0dXJlLCB3YWl0cyBmb3Igd2VlayAzLiBCYXNlbGluZSB0YXNrcyBzdGF5LCBiZWNhdXNlIGEgcmUtcGxhbiB0aGF0IHRocm93cyBhd2F5IHRoZSBmaXNoYm9uZSByZXZpZXcgaXMgbm90IGEgcmUtcGxhbi4gUjQgaXMgdGhlIGRpc2FncmVlbWVudCBiZXR3ZWVuIHJlbGVhc2UgdGVzdGluZyBhbmQgdGhlIGZpZWxkIHJhdGUu"
      },
      {
        "id": "s5q4",
        "prompt": "Why are dry-run keys SIM-*?",
        "choices": [
          {
            "id": "a",
            "text": "The build backlog uses INV-*. SIM-* makes a dry-run file obviously not that board."
          },
          {
            "id": "b",
            "text": "Jira Cloud Free only accepts the SIM project key."
          },
          {
            "id": "c",
            "text": "SIM means the live site accepted the issue."
          },
          {
            "id": "d",
            "text": "The epic key is copied from the scenario id, which is SIM."
          }
        ],
        "salt": "9da334efd4f63eaa",
        "answerHash": "28908618487f351e27eacdfc3d8437c7861d1ec8b71a71ccabfdd7010899f406",
        "explain": "V2l0aCBubyB0b2tlbiwgc3luYyB3cml0ZXMgamlyYV9pc3N1ZXMuanNvbiBhbmQgZG9lcyBub3Qgb3BlbiBhIHNvY2tldC4gVGhlIGZpbGUgY2FycmllcyBhIHNpbXVsYXRpb24gZGlzY2xhaW1lci4gbWFrZV9jbGllbnQgcmV0dXJucyBEcnlSdW5KaXJhIHVubGVzcyBhbGwgdGhyZWUgSmlyYSBzZXR0aW5ncyBhcmUgcHJlc2VudC4="
      },
      {
        "id": "s5q5",
        "prompt": "What happens if the live Jira call raises?",
        "choices": [
          {
            "id": "a",
            "text": "LiveJira.sync catches it, stores the exception class name, writes the JSON, and does not raise. The token is not put in the error or in repr."
          },
          {
            "id": "b",
            "text": "The token is written into the error string so the PM can debug it."
          },
          {
            "id": "c",
            "text": "The process deletes the plan."
          },
          {
            "id": "d",
            "text": "The client retries forever."
          }
        ],
        "salt": "00af55c5ea95f202",
        "answerHash": "2780d2e4534d212dfe491b4476aa7a1dfb9f992e0b8355a7db326e0c53beb1d9",
        "explain": "VGVzdHMgcGFzcyBhIGZha2UgdHJhbnNwb3J0IGFuZCBuZXZlciBjb25zdHJ1Y3QgdGhlIHJlYWwgaHR0cHggY2xpZW50IGZvciB0aGUgZHJ5LXJ1bi4gQSBwbGFudGVkIHRva2VuIG11c3QgYmUgYWJzZW50IGZyb20gcmVwci4="
      },
      {
        "id": "s5q6",
        "prompt": "What does the live test count on the second sync?",
        "choices": [
          {
            "id": "a",
            "text": "Zero new POSTs. The first sync posts the epic plus the tasks. _upsert updates a story in place when the task id is already in the file."
          },
          {
            "id": "b",
            "text": "Eleven more POSTs, one per task, every time."
          },
          {
            "id": "c",
            "text": "A DELETE of every SIM-* issue."
          },
          {
            "id": "d",
            "text": "One POST of the whole plan as a single issue."
          }
        ],
        "salt": "54f918147ac804c9",
        "answerHash": "ac013b7f3b40bc9501e6976819448e1fed66a8321f6533020b464aef051d708a",
        "explain": "VGhlIGZpcnN0IGNhbGwgaXMgMTEgcG9zdHM6IGVwaWMgcGx1cyAxMCB0YXNrcyBhdCB3ZWVrIDAuIFRoZSBieV90YXNrIG1hcCBza2lwcyBjcmVhdG9yIHdoZW4gdGhlIGlkIGV4aXN0cyBhbmQgc3RpbGwgcmVmcmVzaGVzIHN1bW1hcnksIHN0YXR1cywgYW5kIG93bmVyLiBEZXNjcmlwdGlvbnMgdXNlIEppcmEncyBkb2N1bWVudCBmb3JtYXQgYmVjYXVzZSBBUEkgdjMgcmVqZWN0cyBhIHBsYWluIHN0cmluZy4="
      },
      {
        "id": "s5q7",
        "prompt": "Why does plan run after triage and not after the fishbone?",
        "choices": [
          {
            "id": "a",
            "text": "The planner reads the top hypothesis. It does not read the fishbone. RCA does not read the plan."
          },
          {
            "id": "b",
            "text": "LangGraph sorts node names alphabetically."
          },
          {
            "id": "c",
            "text": "The Gantt is an input to the ranker."
          },
          {
            "id": "d",
            "text": "Jira must exist before any metric is computed."
          }
        ],
        "salt": "ba424e0ed43edd12",
        "answerHash": "cf1a38ca8c12969a9a661beca2b38a3f1b9e128402144006f7d329b5cbc60357",
        "explain": "VGhlIG9yZGVyIGlzIHRyaWFnZSwgcGxhbiwgcmNhLCBFTkQuIHJ1bl9jYXNlIGNyZWF0ZXMgdGhlIG91dHB1dCBkaXJlY3RvcnkgYmVmb3JlIGludm9rZSwgYmVjYXVzZSB0aGUgcGxhbiBub2RlIHdyaXRlcyBmaWxlcyBkdXJpbmcgdGhlIG5vZGUgdXNpbmcgc3RhdGUgb3V0X2Rpci4="
      },
      {
        "id": "s5q8",
        "prompt": "Who owns containment when the top cause is a lot, an instrument, or no single cause?",
        "choices": [
          {
            "id": "a",
            "text": "A lot is QA. An instrument or a temperature lane is Manufacturing. Software is R&D. No single cause stays with the PM, which means do not quarantine yet."
          },
          {
            "id": "b",
            "text": "Every task is owned by the model."
          },
          {
            "id": "c",
            "text": "The customer owns the corrective action."
          },
          {
            "id": "d",
            "text": "Jira assigns a random owner when the key starts with SIM."
          }
        ],
        "salt": "2f3a78be0caab485",
        "answerHash": "6b1bf62f3d19eab6d4013d26d9c4b1d9c5ff70b46a0a00492a3200cd02bb5129",
        "explain": "VGhlIG93bmVyIG1hcCBpcyB0aGUgc3RhZmZpbmcgc3Rvcnkgb24gdGhlIEdhbnR0LiBTY29yZSBvbiB0aGUgcmVnaXN0ZXIgaXMgbGlrZWxpaG9vZCB0aW1lcyBpbXBhY3QsIGFuZCBhIGxvb3AgY2hlY2tzIHRoZSBwcm9kdWN0IHNvIGEgZnV0dXJlIGVkaXQgY2Fubm90IHR5cGUgdGhlIHNjb3JlIGJ5IGhhbmQu"
      }
    ]
  },
  "6": {
    "passMark": 0.8,
    "questions": [
      {
        "id": "s6q1",
        "prompt": "Why does triage not run on every lap of the loop?",
        "choices": [
          {
            "id": "a",
            "text": "The field file is fixed by the scenario seed. Re-running triage would recompute the same metrics. The lap re-enters at plan."
          },
          {
            "id": "b",
            "text": "LangGraph allows only one node per process."
          },
          {
            "id": "c",
            "text": "Triage is deleted after Session 5."
          },
          {
            "id": "d",
            "text": "The customer note replaces the metrics."
          }
        ],
        "salt": "348cbf7de3078da9",
        "answerHash": "a944e5f9ab87f343f2f4c2daa39f391f2d93b5401a1ecaa92295ee9429d54e37",
        "explain": "VGhlIGNvbmRpdGlvbmFsIGVkZ2UgYWZ0ZXIgc3RhdHVzIGVpdGhlciBlbmRzIG9yIGFkdmFuY2VzIHRoZSB3ZWVrIGFuZCByZXR1cm5zIHRvIHBsYW4uIFRyaWFnZSBydW5zIG9uY2UuIFRoZSB3ZWVrIGNoYW5nZXMgd2hpY2ggaW5qZWN0aW9ucyBhbmQgdGFza3MgYXJlIGluIHNjb3BlLg=="
      },
      {
        "id": "s6q2",
        "prompt": "What makes week 2 Red on bad_lot, and why does the case never go Green?",
        "choices": [
          {
            "id": "a",
            "text": "The rate is still over spec, and containment is week 3, so week 2 is Red. The synthetic file is not rewritten, so it never goes Green. Amber means containment is underway, not that the rate recovered."
          },
          {
            "id": "b",
            "text": "Green is reserved for the language model."
          },
          {
            "id": "c",
            "text": "Week 2 is Green because release testing passed."
          },
          {
            "id": "d",
            "text": "RAG here means a retrieval index, and Red means the index missed."
          }
        ],
        "salt": "0e31370362844a87",
        "answerHash": "d1dc1105dadfba162b18c3e4d3bbe1dfd28c4b0feeb7c55ede8f8c4b50fb6703",
        "explain": "SW4gdGhpcyBwcm9qZWN0IFJBRyBpcyB0aGUgUmVkIC8gQW1iZXIgLyBHcmVlbiBzdGF0dXMgY29sb3IsIG5vdCByZXRyaWV2YWwtYXVnbWVudGVkIGdlbmVyYXRpb24uIHJhZ19jb2xvciByZXR1cm5zIEdyZWVuIG9ubHkgd2hlbiB0aGUgcmF0ZSBkb2VzIG5vdCBleGNlZWQgdGhlIHNwZWMu"
      },
      {
        "id": "s6q3",
        "prompt": "What does the decision log record at week 2?",
        "choices": [
          {
            "id": "a",
            "text": "Keep the field ranking after release testing was reported as a pass, and add the lab-director note to the plan."
          },
          {
            "id": "b",
            "text": "Switch the cause to software because the note said so."
          },
          {
            "id": "c",
            "text": "Close D8 and ship the deck."
          },
          {
            "id": "d",
            "text": "Delete T1 because its week has passed."
          }
        ],
        "salt": "267f892434654159",
        "answerHash": "fd49102ea2bfa6748e6b6dd1aee87a83c9571b0c4afb207b5b96521f79b6767b",
        "explain": "V2VlayAxJ3Mgcm93IHNheXMgdGhlIFFBIG5vdGUgaXMgYSBjaXRhdGlvbiBhbmQgZG9lcyBub3QgZ2V0IGl0cyBvd24gc2NvcmUuIFdlZWsgMyBzYXlzIGRvIG5vdCBzd2l0Y2ggdGhlIGNhdXNlIG9udG8gdGhlIHNoaXBwaW5nIG5vdGUuIE9uZSByb3cgcGVyIHdlZWsgaXMgdGhlIGRpZmYgYSBQTSB3b3VsZCBzaG93Lg=="
      },
      {
        "id": "s6q4",
        "prompt": "How can the customer note mention a rate without the template doing arithmetic?",
        "choices": [
          {
            "id": "a",
            "text": "build_status_facts rounds the computed rate onto rate_pct. The template interpolates that field. The guard then checks the sentence."
          },
          {
            "id": "b",
            "text": "The template multiplies k by 100 and divides by n in the f-string."
          },
          {
            "id": "c",
            "text": "Llama 3.2 1B types the percent on Streamlit Community Cloud."
          },
          {
            "id": "d",
            "text": "The rate is copied from the complaint sentence."
          }
        ],
        "salt": "666a134f18becf06",
        "answerHash": "dd69dc3da7c6d37a182f578912f59252c4550aacf0d5dcf2826bf49dce773e0f",
        "explain": "VGhlIHRocmVlIGF1ZGllbmNlIHRlbXBsYXRlcyBzaGFyZSBfc3RhdHVzX2hlYWRlciwgc28gdGhlIHJhdGUgbGluZSBjYW5ub3QgZHJpZnQuIENvc3QgaXMgaW52YWxpZHMgdGltZXMgdGhlIHVuaXQgcHJpY2UsIGFuZCBib3RoIGZhY3RvcnMgc2l0IG9uIHRoZSBmYWN0cyBiZWZvcmUgYW55IHNlbnRlbmNlIGlzIHJlbmRlcmVkLg=="
      },
      {
        "id": "s6q5",
        "prompt": "Where do you look to diff week 0 and week 2 without re-running anything?",
        "choices": [
          {
            "id": "a",
            "text": "out/week0/ and out/week2/. Compare plan.json and risk_register.md. The root copy is latest. The week folder is as of that week."
          },
          {
            "id": "b",
            "text": "Only the final jira_issues.json, which stores every week's plan."
          },
          {
            "id": "c",
            "text": "git diff between session-5 and session-6."
          },
          {
            "id": "d",
            "text": "The Streamlit cache."
          }
        ],
        "salt": "755749f7c0fae2b6",
        "answerHash": "74c9b14945fb4b8abc8121cbfe73f638210079858c815800061ec1ef87fc222b",
        "explain": "VGhvc2Ugd2VlayBmb2xkZXJzIHdlcmUgd3JpdHRlbiBieSBwbGFuX25vZGUgb24gdGhhdCBsYXAsIG5vdCByZWNvbnN0cnVjdGVkIGxhdGVyLiBXZWVrIDAncyByZWdpc3RlciBoYXMgbm8gUjQuIFdlZWsgMidzIGRvZXMu"
      },
      {
        "id": "s6q6",
        "prompt": "What must the customer note not do?",
        "choices": [
          {
            "id": "a",
            "text": "It must not state a confirmed cause. Internal gets the hypothesis. Leadership gets the cost and the ask."
          },
          {
            "id": "b",
            "text": "It must name the lot, the p-value, and the 5 Whys."
          },
          {
            "id": "c",
            "text": "It must be a different rate from the leadership note."
          },
          {
            "id": "d",
            "text": "It must include the Jira token so the customer can comment."
          }
        ],
        "salt": "18033037414f7c25",
        "answerHash": "758c68e6b7b8d180c9df62798f80f15aff7dccbce00a5747ef1fc8ea63ef1788",
        "explain": "SW50ZXJuYWwgcGFzdGVzIGluamVjdGlvbiB0ZXh0IHZlcmJhdGltIHNvIHRoZSBndWFyZCBjYW4gbWFzayBpdC4gVGhlIGN1c3RvbWVyIGFjdGlvbiBpcyBhIGhvbGRpbmcgc2VudGVuY2UuIFRoYXQgc3BsaXQgaXMgdGhlIHN0YWtlaG9sZGVyIHNraWxsIHRoZSBzZXNzaW9uIGlzIHByYWN0aWNpbmcu"
      },
      {
        "id": "s6q7",
        "prompt": "At the end of a week-3 run, which tasks are Done?",
        "choices": [
          {
            "id": "a",
            "text": "Status is a comparison of integers. T1 (sim week 0) is Done and T11 (sim week 2) is Done. T10 (sim week 4) is still To Do."
          },
          {
            "id": "b",
            "text": "Every task is In Progress until the deck is written."
          },
          {
            "id": "c",
            "text": "T11 does not exist yet at week 3."
          },
          {
            "id": "d",
            "text": "Done is set by a live Jira transition only."
          }
        ],
        "salt": "ebe74b486508e880",
        "answerHash": "74904605499c22db5fa5dd7903f1a5c7408e6a09f46d3f572448333a3376e629",
        "explain": "VGhlIGRyeS1ydW4gdXBzZXJ0IGZyb20gU2Vzc2lvbiA1IHJlZnJlc2hlcyBzdGF0dXMgaW4gcGxhY2UuIFRoZSBmaWxlIGF0IHRoZSBlbmQgb2Ygd2VlayAzIHNob3dzIHRoZSB0YXNrcyB3aG9zZSB3ZWVrIGhhcyBwYXNzZWQgYXMgRG9uZS4gTm8gdG9rZW4gaXMgcmVxdWlyZWQu"
      },
      {
        "id": "s6q8",
        "prompt": "What does route_after_status return when the week that just finished is still below the target?",
        "choices": [
          {
            "id": "a",
            "text": "advance, which adds one to the week and edges back to plan."
          },
          {
            "id": "b",
            "text": "end, always."
          },
          {
            "id": "c",
            "text": "closeout, even in week 1."
          },
          {
            "id": "d",
            "text": "triage, so the frame is regenerated with a new seed."
          }
        ],
        "salt": "2bd81e211dd86782",
        "answerHash": "24515f7887c2f1677bbc8ee29654e83f50aa5accb72c05b8a789d137d07ce3c1",
        "explain": "VGhlIHN0cmluZyBlbmQgbWFwcyB0byBMYW5nR3JhcGgncyBFTkQuIFRoZXJlIGlzIG5vIGNsb3Nlb3V0IG5vZGUgdW50aWwgU2Vzc2lvbiA5LiBUaGlzIHRhZydzIGxvb3AgaXMgcGxhbiwgUkNBLCBzdGF0dXMu"
      }
    ]
  },
  "7": {
    "passMark": 0.8,
    "questions": [
      {
        "id": "s7q1",
        "prompt": "Why is rules-only the default on the hosted page?",
        "choices": [
          {
            "id": "a",
            "text": "Streamlit Community Cloud has no Ollama, and this repo does not ship weights. The deterministic templates answer without a download."
          },
          {
            "id": "b",
            "text": "Plotly cannot draw a chart while a model is loaded."
          },
          {
            "id": "c",
            "text": "The page crashes unless LLM_BACKEND is ollama."
          },
          {
            "id": "d",
            "text": "GitHub Actions hosts the dashboard and forbids Python."
          }
        ],
        "salt": "573fe1424ad5e481",
        "answerHash": "5b1e7cdc1262c9c835810aed6c85ceb48167bf7220b8d28b2427d94f279fb8b1",
        "explain": "QSBtaXNzaW5nIG1vZGVsIGlzIGEgZmFsbGJhY2ssIG5vdCBhIGNyYXNoLiBuYXJyYXRlIHN0aWxsIHJlcGxhY2VzIGEgcmVqZWN0ZWQgZHJhZnQgd2l0aCB0aGUgdGVtcGxhdGUuIFRoZSBiYW5uZXIgaXMgdGhlIGZpcnN0IHRoaW5nIG9uIHRoZSBwYWdlLCBpbmNsdWRpbmcgdGhlIGNsaW5pY2FsLXVzZSBsaW5lLg=="
      },
      {
        "id": "s7q2",
        "prompt": "Which variable names the model, and what does the page request when rules-only is off and that variable is unset?",
        "choices": [
          {
            "id": "a",
            "text": "LLM_MODEL. An explicit value wins. With the toggle off and the variable unset, a local or self-hosted run asks Ollama for llama3.2:1b. The CLI default remains llama3.1:8b."
          },
          {
            "id": "b",
            "text": "OLLAMA_MODEL, which overrides LLM_MODEL."
          },
          {
            "id": "c",
            "text": "The page always downloads Llama 3.1 8B on Community Cloud."
          },
          {
            "id": "d",
            "text": "There is no model setting. The page picks at random."
          }
        ],
        "salt": "7acc16b44f33dcb2",
        "answerHash": "bbc30b9e32390883035d7e89dac10cc99fc82899c653688b71e9c939351abc39",
        "explain": "SE9TVEVEX0xMTV9NT0RFTCBpcyB0aGUgc21hbGwgdGFnLCBMbGFtYSAzLjIgMUIuIEl0IGlzIHdoYXQgdGhlIHRvZ2dsZSBhc2tzIGZvciBsb2NhbGx5LiBDb21tdW5pdHkgQ2xvdWQgc3RheXMgb24gdGhlIHJ1bGVzLW9ubHkgZGVmYXVsdCBiZWNhdXNlIENsb3VkIGNhbm5vdCBydW4gT2xsYW1hLiBHZW1tYSAzIGFuZCBQaGktNCBhcmUgb3RoZXIgdGFncyB5b3UgY2FuIHNldCB5b3Vyc2VsZi4="
      },
      {
        "id": "s7q3",
        "prompt": "Why does the before/after chart say the after series is not observed follow-up?",
        "choices": [
          {
            "id": "a",
            "text": "projection_summary clears invalids on the leading stratum of the same synthetic file. No new field data were collected."
          },
          {
            "id": "b",
            "text": "The after series is next month's real complaints."
          },
          {
            "id": "c",
            "text": "Matplotlib simulated a cured process and rewrote the YAML."
          },
          {
            "id": "d",
            "text": "The chart is a screenshot from the customer."
          }
        ],
        "salt": "e0bdbe9e62bf59fc",
        "answerHash": "48ea81bb4541f72bfd345dbbec07cd9d79d72ee750fdc14a0cc04d0fd9da26de",
        "explain": "VGhlIGZ1bmN0aW9uIGNvcGllcyB0aGUgZnJhbWUgYW5kIHJldHVybnMgYmVmb3JlL2FmdGVyIHJhdGVzLiBJdCBkb2VzIG5vdCByZXdyaXRlIHRoZSBzY2VuYXJpbyBmaWxlLiBiYWRfbG90IHN0YXlzIG92ZXIgc3BlYyBpbiB0aGUgb2JzZXJ2ZWQgc2VyaWVzLiBUaGUgY2FwdGlvbiByZXBlYXRzIHRoZSBwcm9qZWN0aW9uIGxhYmVsLg=="
      },
      {
        "id": "s7q4",
        "prompt": "What is cached, and what is not recomputed when you only change the audience radio?",
        "choices": [
          {
            "id": "a",
            "text": "_run is cached on scenario, week, backend, and model. The radio only picks a string already stored on status_updates."
          },
          {
            "id": "b",
            "text": "Every radio click reruns the four-week graph and ignores the cache."
          },
          {
            "id": "c",
            "text": "The cache key is the audience name only."
          },
          {
            "id": "d",
            "text": "Nothing is cached, because Streamlit forbids st.cache_data."
          }
        ],
        "salt": "b22b1bb5615bd234",
        "answerHash": "bea34eec54cb0ada383579881e22c4470ae2d675c2f2d11fc2a8b741663854e7",
        "explain": "X3J1biByZXN0b3JlcyB0aGUgZW52aXJvbm1lbnQgaW4gYSBmaW5hbGx5IGJsb2NrIHNvIGEgY2FjaGVkIGNhbGwgY2Fubm90IHBpbiBhIG1vZGVsIGZvciB0aGUgbmV4dCBDTEkgY29tbWFuZCBpbiB0aGUgc2FtZSBwcm9jZXNzLiBTd2l0Y2hpbmcgdGFicyBkb2VzIG5vdCBjYWxsIHJ1bl9jYXNlIGFnYWluLg=="
      },
      {
        "id": "s7q5",
        "prompt": "What does Neel still have to do before a public Streamlit URL exists?",
        "choices": [
          {
            "id": "a",
            "text": "Sign in to Streamlit Community Cloud with GitHub and select app/streamlit_app.py or the root streamlit_app.py. The repo cannot do that sign-in."
          },
          {
            "id": "b",
            "text": "Commit an API token so Cloud can start Ollama."
          },
          {
            "id": "c",
            "text": "Buy a Plotly license."
          },
          {
            "id": "d",
            "text": "Nothing. Session 7 already published the URL."
          }
        ],
        "salt": "d2a33e926656e5ca",
        "answerHash": "b63af5af590b8cbc97cad65087c5e92af48de25138e3cfdb618afd794e2dcb13",
        "explain": "VGhlIHJvb3QgZmlsZSB1c2VzIHJ1bnB5IHNvIGJvdGggZW50cnkgcG9pbnRzIHdvcmsuIFRpY2tldCBJTlYtMzAxIGlzIHRoZSBkYXNoYm9hcmQuIFRoZSBhY2FkZW15IGxlYXZlcyBzdHJlYW1saXRVcmwgYmxhbmsgdW50aWwgdGhhdCBVUkwgZXhpc3RzLg=="
      },
      {
        "id": "s7q6",
        "prompt": "Which colors mark the p-chart, and what is red for?",
        "choices": [
          {
            "id": "a",
            "text": "Navy #0B3A5B and teal #1F7A8C for the series, red #B23A48 for rule-1 marks. No purple gradient."
          },
          {
            "id": "b",
            "text": "A random palette per owner, same as a default Plotly theme."
          },
          {
            "id": "c",
            "text": "Red means the projection. Navy means a model token."
          },
          {
            "id": "d",
            "text": "The chart is a matplotlib PNG embedded by Kaleido."
          }
        ],
        "salt": "ba7dce9e8a01664a",
        "answerHash": "1f17f0463c445f6602870b79176f1257c4f4a77e1847f7b6847e94188207a286",
        "explain": "Y2hhcnRzLnB5IHJlYWRzIHRoZSBwLWNoYXJ0IGRpY3QgYW5kIHRoZSBQYXJldG8gZGljdCB0aGUgZ3JhcGggYWxyZWFkeSBjb21wdXRlZC4gVGhlIHN0YXRpYyBQTkcgcGF0aCBmb3Igc2xpZGVzIHN0YXlzIG9uIG1hdHBsb3RsaWIgYmVjYXVzZSBQbG90bHkncyBleHBvcnQgbmVlZHMgS2FsZWlkbywgd2hpY2ggaXMgbm90IHNoaXBwZWQu"
      },
      {
        "id": "s7q7",
        "prompt": "What does requirements.txt deliberately leave out?",
        "choices": [
          {
            "id": "a",
            "text": "A GGUF weight file. The install list is pandas, numpy, scipy, PyYAML, Pydantic, httpx, LangGraph, langchain-core, Plotly, matplotlib, python-pptx, and Streamlit."
          },
          {
            "id": "b",
            "text": "Streamlit itself, so Cloud uses a different framework."
          },
          {
            "id": "c",
            "text": "Plotly, because the page uses only matplotlib."
          },
          {
            "id": "d",
            "text": "pytest, which Cloud needs in order to serve the page."
          }
        ],
        "salt": "5d265b0f400a07e3",
        "answerHash": "dbd77c456940516671d8f9daecc5e24438f85b0eaecb5c9830989db72c222e8b",
        "explain": "VGhlIGNvbW1lbnQgYXQgdGhlIHRvcCBvZiB0aGUgZmlsZSBzYXlzIHRoZSBkZWZhdWx0IGJhY2tlbmQgaXMgZGV0ZXJtaW5pc3RpYy4gLnN0cmVhbWxpdC9jb25maWcudG9tbCBzZXRzIHRoZSBuYXZ5IHRoZW1lLCBoZWFkbGVzcyBtb2RlLCBhbmQgdHVybnMgdXNhZ2Ugc3RhdHMgb2ZmLg=="
      },
      {
        "id": "s7q8",
        "prompt": "What does the dashboard test require the page to show?",
        "choices": [
          {
            "id": "a",
            "text": "AppTest renders the banner without an exception, including the clinical-use line, and at least one metric. A second test checks that removing the bad lot lowers the projected rate."
          },
          {
            "id": "b",
            "text": "A live click in a browser, which CI performs on Community Cloud."
          },
          {
            "id": "c",
            "text": "That the page downloads llama3.1:8b."
          },
          {
            "id": "d",
            "text": "That the audience radio changes the invalid rate."
          }
        ],
        "salt": "b93a90e8549423f0",
        "answerHash": "2d14f0ff518002cec3365481ae37e5105024fd6865aa68f55803a09db6af6e4b",
        "explain": "cHl0ZXN0IHN0YXlzIG9mZmxpbmUuIFRoZSBudW1iZXJzIG9uIHRoZSB0aWxlcyBhcmUgdGhlIG1ldHJpY3Mgb2JqZWN0LCBub3QgYSBzZW50ZW5jZSB0aGUgbW9kZWwgd3JvdGUuIFRoZSBkZWx0YSBvbiB0aGUgcmF0ZSB0aWxlIGlzIGNvbG9yZWQgc28gJ2Fib3ZlIHNwZWMnIHJlYWRzIGFzIGJhZC4="
      }
    ]
  },
  "8": {
    "passMark": 0.8,
    "questions": [
      {
        "id": "s8q1",
        "prompt": "What did the evidence ranker score on the 22 scenarios, and what did the keyword ranker score?",
        "choices": [
          {
            "id": "a",
            "text": "Evidence top-1 and top-3 were 22/22. Keyword top-1 was 3/22. The three keyword hits are the flat files, whose week-0 note names no cause."
          },
          {
            "id": "b",
            "text": "Both rankers scored 22/22, so the note is as good as the table."
          },
          {
            "id": "c",
            "text": "Evidence was 3/22 and the keyword ranker was 22/22."
          },
          {
            "id": "d",
            "text": "The report has no counts. The 22/22 figure is typed into the README by hand."
          }
        ],
        "salt": "1f7a97edfa9bf876",
        "answerHash": "8495c5d9261ed99ce1b1b923348159cceeca047ec98bbea2f67c518db1c78f3c",
        "explain": "SG9sZG91dCB3YXMgNCBvZiAyMi4gR2F0ZXMgd2VyZSBub3QgcmVmaXQuIFJlYWQgdGhlIHdlYWstbG90IHJvdyBhbmQgdGhlIGRyaWZ0IGV4dHJhLXN0cmF0dW0gbGluZXMgYmVmb3JlIHF1b3RpbmcgdGhlIDIyLzIyIGNlbGwu"
      },
      {
        "id": "s8q2",
        "prompt": "Why is weak_lot a success when the evidence call is no_single_cause?",
        "choices": [
          {
            "id": "a",
            "text": "The lot bump was built to stay under the lift gate. The correct call is to withhold. The keyword ranker repeats the note and says bad_reagent_lot."
          },
          {
            "id": "b",
            "text": "no_single_cause means the file failed to generate."
          },
          {
            "id": "c",
            "text": "The evidence ranker is wrong and the keyword ranker is the one to quote."
          },
          {
            "id": "d",
            "text": "weak_lot is held out and therefore not scored."
          }
        ],
        "salt": "70854749f7f893fc",
        "answerHash": "5c618b7daeeebb8c3476d8ff80b3e70fa72f3c29d84bbce37b4b06b0edab4bc6",
        "explain": "VGhlIG92ZXJhbGwgcmF0ZSBjYW4gc3RpbGwgYmUgb3ZlciB0aGUgMiUgc3BlYyB3aGlsZSBubyBzdHJhdHVtIGNsZWFycyBsaWZ0IDEuOC4gV2l0aGhvbGRpbmcgaXMgdGhlIGRlc2lnbmVkIGNhbGwuIFRoYXQgaXMgdGhlIG9wcG9zaXRlIG9mIGZvcmNpbmcgYSBjYXVzZSB0byBtYWtlIHRoZSBzbGlkZSB0aWR5Lg=="
      },
      {
        "id": "s8q3",
        "prompt": "What extra call showed up on the drift scenarios, and did it change top-1?",
        "choices": [
          {
            "id": "a",
            "text": "A reagent-lot stratum also cleared the bar. Top-1 stayed drifting_instrument. The report lists that second stratum on purpose."
          },
          {
            "id": "b",
            "text": "Top-1 flipped to the lot on all four files."
          },
          {
            "id": "c",
            "text": "The drift files were deleted from the score."
          },
          {
            "id": "d",
            "text": "The keyword ranker was the only one that saw the instrument."
          }
        ],
        "salt": "c8e7a637fa35ef3c",
        "answerHash": "f5f19d1d32c43b9fbfd446c12e9b2bef76764e925ce91bd00d2ecd2c5d04d246",
        "explain": "QSByw6lzdW3DqSBidWxsZXQgdGhhdCBrZWVwcyAyMi8yMiBhbmQgZHJvcHMgdGhlIHNlY29uZCBzdHJhdHVtIGlzIG1pc2xlYWRpbmcuIFRoZSBmYWlsdXJlIG5vdGUgdHJhdmVscyB3aXRoIHRoZSBjZWxsLg=="
      },
      {
        "id": "s8q4",
        "prompt": "Why does the report not claim a Llama 3.1 8B versus Llama 3.2 1B accuracy?",
        "choices": [
          {
            "id": "a",
            "text": "Neither model was installed. The table compares two ranking policies on the deterministic backend."
          },
          {
            "id": "b",
            "text": "Llama 3.2 1B won, but the number is confidential."
          },
          {
            "id": "c",
            "text": "The 7B versus 1.5B figure from an older plan is still the one to quote."
          },
          {
            "id": "d",
            "text": "Community Cloud ran both models and they tied."
          }
        ],
        "salt": "7890e6fb3080a6c5",
        "answerHash": "c482cbda2bb03633ccf6915bc51d9f644f34e71b73fde46bba80b6ccb4c67c69",
        "explain": "VGhlIHBsYW4ncyBtb2RlbCBwYWlyIGlzIG5vdyB0aG9zZSB0d28gTGxhbWEgdGFncy4gQSBtb2RlbCBkcmFmdCB3b3VsZCBzdGlsbCBoYXZlIHRvIHBhc3MgdGhlIG51bWVyaWMtZmlkZWxpdHkgY2hlY2sgYmVmb3JlIGl0IHdhcyBzaG93bi4gRG8gbm90IHF1b3RlIHRoZSB0YWJsZSBhcyBhIG1vZGVsLWFjY3VyYWN5IG51bWJlci4="
      },
      {
        "id": "s8q5",
        "prompt": "Why is the red-herring key written \"true\" with quotes in the YAML?",
        "choices": [
          {
            "id": "a",
            "text": "PyYAML 1.1 treats an unquoted true as a boolean. The generator looks up the string key \"true\"."
          },
          {
            "id": "b",
            "text": "Quotes make the lot id a float."
          },
          {
            "id": "c",
            "text": "The quotes tell the keyword ranker to ignore the file."
          },
          {
            "id": "d",
            "text": "JSON requires quotes, and the scenario is JSON."
          }
        ],
        "salt": "04f27cf10dc8d444",
        "answerHash": "60935c30e43914aa7c994dcdd64da5b9cf58c48b799ace5066ac9272e0202d86",
        "explain": "aGVycmluZ19zb2Z0d2FyZSdzIHdlZWstMCBub3RlIHNheXMgc29mdHdhcmUuIHJvb3RfY2F1c2UudHJ1ZSBpcyB0aGUgbG90LiBUaGUgcmFua2VyIGRvZXMgbm90IHJlY2VpdmUgZXZhbC5leHBlY3RfY2F1c2UuIFRoZSBub3RlIGRvZXMgbm90IGdldCB0byBvdXR2b3RlIHRoZSB0YWJsZS4="
      },
      {
        "id": "s8q6",
        "prompt": "What does score_scenario refuse to pass into the ranker?",
        "choices": [
          {
            "id": "a",
            "text": "eval.expect_cause. That block is the label for the score, not an input."
          },
          {
            "id": "b",
            "text": "The scenario seed."
          },
          {
            "id": "c",
            "text": "The spec of 2%."
          },
          {
            "id": "d",
            "text": "The column list."
          }
        ],
        "salt": "08157241d4804410",
        "answerHash": "90a5d86fed7a76fdad0a3ecbe26ce3ba8e7ece07a58093e7acee7b0afdc91447",
        "explain": "a2V5d29yZF9jYXVzZSBvbmx5IHNjYW5zIHdlZWstMCBpbmplY3Rpb24gdGV4dCwgYW5kIHNvZnR3YXJlIGlzIGJlZm9yZSBsb3Qgc28gYSBzZW50ZW5jZSB0aGF0IHNheXMgYm90aCBzdGlsbCBoYXMgb25lIGNhbGwuIEl0IG5ldmVyIG9wZW5zIHRoZSB0YWJsZS4="
      },
      {
        "id": "s8q7",
        "prompt": "Why did version 2.4.0 need to be copied into the fidelity facts as a string?",
        "choices": [
          {
            "id": "a",
            "text": "The guard strips an identifier only when the exact string is in the facts. Otherwise 2.4.0 was scanned as the number 2.4. Lot ids were already safe behind a hyphen. The guard's thresholds did not change."
          },
          {
            "id": "b",
            "text": "2.4.0 is the invalid rate on software scenarios."
          },
          {
            "id": "c",
            "text": "Pydantic cannot store version strings unless they are floats."
          },
          {
            "id": "d",
            "text": "The keyword ranker uses 2.4 as a score."
          }
        ],
        "salt": "57bcc0bac62c18fd",
        "answerHash": "6792aec8040a3be9fa730c7f6a19ca9c1fd1e08051d52737ba9202c8329678f9",
        "explain": "VGhlIHRlcm1pbmFsIFdoeSBmb3IgYSBzb2Z0d2FyZSBoaXQgc2F5cyAyLjQuMC4gUHV0dGluZyB0aGF0IHRva2VuIGluIHRoZSBmYWN0cyBsZXRzIHRoZSBzZW50ZW5jZSBuYW1lIHRoZSB2ZXJzaW9uIHdpdGhvdXQgZmFpbGluZyB0aGUgZ3VhcmQuIFRoZSB0ZXN0IGluIHRlc3RfcmNhIGxvY2tzIGl0Lg=="
      },
      {
        "id": "s8q8",
        "prompt": "What does CI run from this session's script?",
        "choices": [
          {
            "id": "a",
            "text": "The same eval entry point with --limit 5 --smoke. It fails if evidence top-1, fidelity, citations, or escalation miss."
          },
          {
            "id": "b",
            "text": "All 22 scenarios against a live Llama 3.1 server."
          },
          {
            "id": "c",
            "text": "Nothing. The report is hand-edited and CI ignores it."
          },
          {
            "id": "d",
            "text": "A refit of the lift gate on the holdout."
          }
        ],
        "salt": "15c51f71a75472dc",
        "answerHash": "b852d8ef7564582425ed6db28d0ccce16bfd3e18581eb150e6d809a0e9c8cb3c",
        "explain": "VGhlIGZ1bGwgcmVwb3J0J3MgY291bnRzIGNvbWUgZnJvbSBhIHJ1biBvZiBldmFscy9ydW5fZXZhbC5weS4gU2Vzc2lvbiA5IGNvcGllcyB0aG9zZSBjb3VudHMgYW5kIGRvZXMgbm90IGludmVudCBhIG1vZGVsIGNvbXBhcmlzb24uIFdlZWstMCBncmFwaCBjaGVja3Mgb24gdGhlIHNhbWUgMjIgd2VyZSBmaWRlbGl0eSAyMi8yMiwgY2l0YXRpb25zIDIyLzIyLCBlc2NhbGF0aW9uIDIyLzIyLCBtZWFuIGxhdGVuY3kgYWJvdXQgMC41NSBzZWNvbmRzLg=="
      }
    ]
  },
  "9": {
    "passMark": 0.8,
    "questions": [
      {
        "id": "s9q1",
        "prompt": "Why does week 4 not simply end on the status node?",
        "choices": [
          {
            "id": "a",
            "text": "Status is the weekly note. Close-out confirms D7 and D8 and writes the deck. Routing week 4 to closeout keeps that work inside the graph, under the fidelity check."
          },
          {
            "id": "b",
            "text": "The status node cannot count to 4."
          },
          {
            "id": "c",
            "text": "Week 4 deletes the plan and starts triage over."
          },
          {
            "id": "d",
            "text": "A separate script writes the deck and skips the guard on purpose."
          }
        ],
        "salt": "890b0e2c9ce37da1",
        "answerHash": "31941e977a032b7d3d9dbdd34d9e0653114d09befb420925c1883f0abd9ee76f",
        "explain": "cm91dGVfYWZ0ZXJfc3RhdHVzIHNlbmRzIHdlZWsgNCB0byBjbG9zZW91dC4gV2Vla3MgMCB0aHJvdWdoIDMgc3RpbGwgZW5kIG9yIGFkdmFuY2UsIHNvIGVhcmxpZXIgdGVzdHMgZG8gbm90IGJ1aWxkIGEgZGVjay4gcHJlbGltaW5hcnlfY2xvc2UgYmVjb21lcyBmYWxzZSBvbmNlIEQ3IGFuZCBEOCBhcmUgY29uZmlybWVkLg=="
      },
      {
        "id": "s9q2",
        "prompt": "What would be false about the deck if the projected rate were labeled as follow-up?",
        "choices": [
          {
            "id": "a",
            "text": "The generator does not rewrite the field file. Clearing the leading stratum is a counterfactual. bad_lot stays over spec in the observed series."
          },
          {
            "id": "b",
            "text": "Follow-up is the right word because the YAML contains next quarter's rows."
          },
          {
            "id": "c",
            "text": "The projection is a second scenario file the customer signed."
          },
          {
            "id": "d",
            "text": "Labeling it follow-up is required by python-pptx."
          }
        ],
        "salt": "74109de835691552",
        "answerHash": "61fa960c884e989a8587fde43fcc919f8fdc29e6849e6bef514ff3ab794ece93",
        "explain": "VGhlIGVmZmVjdGl2ZW5lc3Mgc2VudGVuY2UgaW5jbHVkZXMgdGhlIGxhYmVsICdOb3Qgb2JzZXJ2ZWQgZm9sbG93LXVwLicgVGhlIHJvb3QtY2F1c2Ugc2xpZGUncyBjaGFydCBpcyB0aGUgb2JzZXJ2ZWQgd2Vla2x5IHJhdGUuIFRoZSBzZW50ZW5jZSB1bmRlciB0aGUgcmVjb21tZW5kYXRpb24gc2F5cyBub3QgdG8gdHJlYXQgdGhlIHByb2plY3RlZCByYXRlIGFzIG9ic2VydmVkIGZvbGxvdy11cC4="
      },
      {
        "id": "s9q3",
        "prompt": "Where does the dollar cost on the impact slide come from?",
        "choices": [
          {
            "id": "a",
            "text": "k times cost_per_invalid_usd from the scenario. For bad_lot that is 529 times 85. The template does not type the product."
          },
          {
            "id": "b",
            "text": "A round number the model chooses for an executive audience."
          },
          {
            "id": "c",
            "text": "The Jira story points, times 1000."
          },
          {
            "id": "d",
            "text": "The customer's email, pasted verbatim."
          }
        ],
        "salt": "068eee5576b06244",
        "answerHash": "46bf2ba327625780000b6cf232bf6356e7371bab836077f423c89963553e868a",
        "explain": "YnVpbGRfY2xvc2VvdXRfZmFjdHMgY29tcHV0ZXMgdGhlIHByb2R1Y3QgYW5kIGRyb3BzIHRoZSBmcmFtZSBiZWZvcmUgdGhlIHJlY29yZCBpcyBzdG9yZWQuIHB5dGhvbi1wcHR4IHdyaXRlcyB0aGUgc2xpZGUgZnJvbSB0aG9zZSBmYWN0cywgc28gYSBzbGlkZSBjYW5ub3QgaW52ZW50IGEgY29zdC4gbWF0cGxvdGxpYiB3aXRoIHRoZSBBZ2cgYmFja2VuZCBkcmF3cyB0aGUgY2hhcnQgUE5HLiBLYWxlaWRvIGlzIG5vdCBzaGlwcGVkLg=="
      },
      {
        "id": "s9q4",
        "prompt": "Which eval numbers are safe on a résumé, and which sentence has to sit next to them?",
        "choices": [
          {
            "id": "a",
            "text": "Safe: evidence top-1 22/22 on this constructed set, keyword top-1 3/22, fidelity 22/22, and the four drift files where a lot also cleared the bar. Not safe: calling 22/22 a clinical accuracy rate, or a Llama 3.1 versus Llama 3.2 comparison. Those models were not run."
          },
          {
            "id": "b",
            "text": "Safe: 'the model is 100% accurate in the field.'"
          },
          {
            "id": "c",
            "text": "Safe: the keyword ranker's 3/22, quoted alone as the system's accuracy."
          },
          {
            "id": "d",
            "text": "Safe: any number, because the deck is a simulation and the disclaimer covers a false comparison."
          }
        ],
        "salt": "21ae2bfc46653180",
        "answerHash": "689cd51ca5cd483721639fb36b7343d9e32e7e4edb926a126dcd6739b93bb08c",
        "explain": "UkVTVU1FX0JVTExFVFMubWQgcHV0cyB0aGUga2V5d29yZCBtaXNzIGFuZCB0aGUgZHJpZnQgc2Vjb25kIHN0cmF0dW0gaW4gdGhlIHNhbWUgYnJlYXRoIGFzIDIyLzIyLiBRdW90aW5nIHRoZSBmaXJzdCBudW1iZXIgYWxvbmUgd291bGQgbWlzbGVhZC4gVGhlIGRpc2NsYWltZXIgc3RheXM6IHN5bnRoZXRpYywgbm90IGNsaW5pY2FsLCBub3QgYSBkZXZpY2Uu"
      },
      {
        "id": "s9q5",
        "prompt": "How many slides does write_deck create, and what does a no_single_cause call recommend?",
        "choices": [
          {
            "id": "a",
            "text": "Seven blank-layout slides: title and disclaimer, summary, impact, root cause, options, recommendation, ask. No single cause recommends not containing a stratum."
          },
          {
            "id": "b",
            "text": "One slide, generated by the model."
          },
          {
            "id": "c",
            "text": "Twelve slides, one per Jira epic."
          },
          {
            "id": "d",
            "text": "Seven slides, and no_single_cause still says to quarantine the first lot."
          }
        ],
        "salt": "3720eeda6bc40cb3",
        "answerHash": "ca4e3b8746b2ab38072072b44baa78d4662337d18574cd9a9be847dd93fd01be",
        "explain": "QSBzaW5nbGUtY2F1c2UgY2FsbCByZWNvbW1lbmRzIGNvbnRhaW5pbmcgdGhhdCBzdHJhdHVtIGFuZCBub3QgZXhwYW5kaW5nIHRoZSBwdWxsLiBDb2xvcnMgYXJlIG5hdnkgYW5kIHRlYWwsIHdpdGggdGhlIGRpc2NsYWltZXIgaW4gd2hpdGUgb24gbmF2eSBvbiB0aGUgdGl0bGUgc2xpZGUuIFRoZSB0ZXN0IG9wZW5zIHRoZSBwcHR4IGFuZCBjaGVja3Mgc2V2ZW4gc2xpZGVzLCB0aGUgZGlzY2xhaW1lciwgdGhlIHByb2plY3Rpb24gbGFiZWwsIDMuNjclLCBhbmQgTC00NDE5Lg=="
      },
      {
        "id": "s9q6",
        "prompt": "What is the local model default, and what does hosted Streamlit run?",
        "choices": [
          {
            "id": "a",
            "text": "LLM_MODEL defaults to llama3.1:8b, Meta Llama 3.1 8B via Ollama. Hosted Streamlit runs rules-only. llama3.2:1b is the small tag for a local or self-hosted run."
          },
          {
            "id": "b",
            "text": "Hosted Streamlit downloads Llama 3.1 8B on every page load."
          },
          {
            "id": "c",
            "text": "There are two model settings, OLLAMA_MODEL and LLM_MODEL, and both are required."
          },
          {
            "id": "d",
            "text": "The deck is written by Llama 3.2 1B on Community Cloud."
          }
        ],
        "salt": "ae5cb36718eed753",
        "answerHash": "c8691c255c62b84115b276c627f4d1182a48629e2bed2385b9846399506ac0cf",
        "explain": "VGhlIFJFQURNRSBtb2RlbCB0YWJsZSBzYXlzIHRoZSBzYW1lIHRoaW5nLiBHZW1tYSAzIGFuZCBQaGktNCBhcmUgb3RoZXIgZG9jdW1lbnRlZCB0YWdzLiBDbG9zZS1vdXQgaXRzZWxmIGlzIGEgdGVtcGxhdGUgcGx1cyB0aGUgZmlkZWxpdHkgZ3VhcmQuIE5vIG5ldyBtb2RlbCBsaWJyYXJ5Lg=="
      },
      {
        "id": "s9q7",
        "prompt": "What does the week-4 leadership injection on bad_lot ask for, and which ticket is the deck?",
        "choices": [
          {
            "id": "a",
            "text": "The recommendation and the effectiveness check. The deck is that answer. Ticket INV-303, epic INV-6. No Jira token is required to generate it."
          },
          {
            "id": "b",
            "text": "A live Slack thread, which Session 9 ships."
          },
          {
            "id": "c",
            "text": "A fine-tune of the ranker on the 22 scenarios."
          },
          {
            "id": "d",
            "text": "Ticket INV-101, the PRD, rewritten as slides."
          }
        ],
        "salt": "21d89c3eb0d52b05",
        "answerHash": "43eede750ca825848dffe5494f8741c47a6330b85f9df0d22131844265abf325",
        "explain": "TGVhZGVyc2hpcCdzIGFzayBpcyB0aGUgY2xvc2Utb3V0LiBUaGUgYXNrIHNsaWRlIHNheXMgdG8gYXBwcm92ZSB0aGUgcmVjb21tZW5kYXRpb24gb3Igc2VuZCB0aGUgY2FzZSBiYWNrIGZvciB0aGUgd2lkZXIgcHVsbCwgYW5kIG5vdCB0byB0cmVhdCB0aGUgcHJvamVjdGlvbiBhcyBmb2xsb3ctdXAu"
      },
      {
        "id": "s9q8",
        "prompt": "Which sentence belongs in a two-minute pitch of the whole system?",
        "choices": [
          {
            "id": "a",
            "text": "A lab says a fictional panel missed a 98% validity promise. The ranker only keeps strata that clear a fixed bar. Notes that name the wrong cause do not outvote the table. The deck labels the before/after chart as a projection. On 22 synthetic scenarios the evidence ranker matched the designed call 22 times, a note-only ranker matched 3, and four drift cases also cleared a lot."
          },
          {
            "id": "b",
            "text": "The model reads the complaint and the investigation is done."
          },
          {
            "id": "c",
            "text": "This is a medical device with a cleared clinical claim of 22/22."
          },
          {
            "id": "d",
            "text": "Jira is required, and the demo does not run without a token."
          }
        ],
        "salt": "94aec47c194e385b",
        "answerHash": "ba858366cec7e8d4bf3b544a14d13c182cb544d773a1d1822db26747a3fdda27",
        "explain": "VGhlIHBpdGNoIGtlZXBzIHRoZSBkaXNjbGFpbWVyLCB0aGUgZXZpZGVuY2UgYmFyLCB0aGUgaGVycmluZyByZXN1bHQsIGFuZCB0aGUgc2Vjb25kIHN0cmF0dW0uIEl0IGRvZXMgbm90IHR1cm4gdGhlIHNjb3JlY2FyZCBpbnRvIGEgY2xpbmljYWwgY2xhaW0uIFlvdSBjYW4gcnVuIHRoZSBkZXRlcm1pbmlzdGljIHBhdGggd2l0aCBubyBBUEkga2V5Lg=="
      }
    ]
  }
};
