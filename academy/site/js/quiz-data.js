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
            "text": "Jira's importer rejects a bare number, so the cap has to be stored as a calculated custom field."
          },
          {
            "id": "c",
            "text": "Otherwise the Wilson helper drops its upper bound and the memo can print only a floor."
          },
          {
            "id": "d",
            "text": "pytest refuses to compare two numeric literals, which is why one of them is computed."
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
            "text": "A base URL, an email, and a token. Any missing piece leaves jira_enabled false."
          },
          {
            "id": "b",
            "text": "JIRA_API_TOKEN by itself enables the client, even when the URL and the email are blank."
          },
          {
            "id": "c",
            "text": "OPENFDA_API_KEY together with JIRA_EMAIL opens Jira, and the token stays optional."
          },
          {
            "id": "d",
            "text": "JIRA_PROJECT_KEY set to INV is the entire switch, with or without an email address."
          }
        ],
        "salt": "397bee6cce6b881a",
        "answerHash": "a60293dbe4625543c1d8c2a45309f433180eaae1fad4dc7512cbafb6f2be90ed",
        "explain": "VGhlIGdhdGUgaXMgYWxsIHRocmVlOiBKSVJBX0JBU0VfVVJMIG9yIEpJUkFfVVJMLCBKSVJBX0VNQUlMLCBhbmQgSklSQV9BUElfVE9LRU4gb3IgSklSQV9UT0tFTi4gVGhlIGxvbmdlciBuYW1lcyB3aW4gd2hlbiBib3RoIGFsaWFzZXMgYXJlIHNldC4="
      },
      {
        "id": "s1q3",
        "prompt": "What is wrong with the default frozen-dataclass repr?",
        "choices": [
          {
            "id": "a",
            "text": "pytest is blocked from calling repr, so a planted token can never reach a log."
          },
          {
            "id": "b",
            "text": "It lowercases LLM_MODEL, so Ollama cannot resolve the llama3.1:8b tag."
          },
          {
            "id": "c",
            "text": "It hides the repo root, so tests cannot find scenarios."
          },
          {
            "id": "d",
            "text": "It prints every field, including jira_api_token."
          }
        ],
        "salt": "7eeae6e7843514b8",
        "answerHash": "24f90d6aeac9d207d7e52ede8ddf7100af4205c7d20290b22da50f3864178ea9",
        "explain": "QSBwbGFudGVkIHNlY3JldCBpbiB0aGUgdG9rZW4gd291bGQgc2hvdyB1cCBpbiBsb2dzIGlmIHJlcHIgd2VyZSB0aGUgZGVmYXVsdC4gVGhlIG92ZXJyaWRlIHByaW50cyB0aGUgcmVkYWN0ZWQgdmlldyBvbmx5Lg=="
      },
      {
        "id": "s1q4",
        "prompt": "What is docs/jira/backlog.json, compared with the Jira sync added later?",
        "choices": [
          {
            "id": "a",
            "text": "It is the dry-run file of SIM investigation issues, written only after make_client runs."
          },
          {
            "id": "b",
            "text": "It is the live customer-escalation board, and later sync posts onto those same INV keys."
          },
          {
            "id": "c",
            "text": "The build backlog for constructing the agent. Sprint 1 is INV-101 through INV-109."
          },
          {
            "id": "d",
            "text": "It is the Week-0 triage memo stored as JSON so an escalate flag can be imported."
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
            "text": "Python 3.11 rejects third-party imports, which forces the dependencies list to stay empty."
          },
          {
            "id": "b",
            "text": "setuptools refuses a non-empty dependencies list while the version is still 0.1.0, so CI would fail closed."
          },
          {
            "id": "c",
            "text": "Nothing in this tag imports them yet, so CI should not download pandas, LangGraph, or a model client."
          },
          {
            "id": "d",
            "text": "The MIT license forbids dependencies, and pip blocks install once that list is filled."
          }
        ],
        "salt": "7e3e843c6a8a3b5a",
        "answerHash": "224f2da90b5b4f7795c2c11b271d42ac6eaff98f48b2d844df61682a30c248c4",
        "explain": "TGF0ZXIgc2Vzc2lvbnMgYWRkIGEgbGlicmFyeSBvbmx5IHdoZW4gY29kZSBpbXBvcnRzIGl0LiBUaGUgbG9jYWwgbW9kZWwsIHdoZW4geW91IHdhbnQgb25lLCBpcyBNZXRhIExsYW1hIDMuMSA4QiB2aWEgT2xsYW1hLiBJdCBpcyBub3QgYSBkZXBlbmRlbmN5IGluIHRoaXMgdGFnLg=="
      },
      {
        "id": "s1q6",
        "prompt": "What does find_repo_root look for?",
        "choices": [
          {
            "id": "a",
            "text": "It stops at the first directory named out, treating that folder as proof of the repo root."
          },
          {
            "id": "b",
            "text": "It requires the REPO_ROOT variable and ignores pyproject.toml whenever that variable is missing."
          },
          {
            "id": "c",
            "text": "It looks for a live Ollama server on port 11434 and treats that process as the project root."
          },
          {
            "id": "d",
            "text": "pyproject.toml sitting next to scenarios/ or src/invalid_agent/."
          }
        ],
        "salt": "e4d4cab896481ed3",
        "answerHash": "d582bf283ecededfda6d6b338f2a792a94d5a3fbfbded698ee5bf3185eaea86a",
        "explain": "V2Fsa2luZyBwYXJlbnRzIHVudGlsIHRoYXQgcGFpciBhcHBlYXJzIGtlZXBzIHNjZW5hcmlvIHBhdGhzIGNvcnJlY3Qgd2hlbiBTdHJlYW1saXQncyB3b3JraW5nIGRpcmVjdG9yeSBpcyB0aGUgcmVwbyBhbmQgd2hlbiB0aGUgcGFja2FnZSBpcyBhbiBlZGl0YWJsZSBpbnN0YWxsLg=="
      },
      {
        "id": "s1q7",
        "prompt": "LLM_BACKEND=rules-only becomes which backend?",
        "choices": [
          {
            "id": "a",
            "text": "llamacpp, because a rules-only flag loads a GGUF even when the model path is empty."
          },
          {
            "id": "b",
            "text": "deterministic, because rules, rules-only, and mock are three names for that one backend."
          },
          {
            "id": "c",
            "text": "ollama, because a rules-only flag means the laptop model should write the memo."
          },
          {
            "id": "d",
            "text": "A raised error, because an unrecognized backend must not fall through to a silent template."
          }
        ],
        "salt": "8f5da9c3eef3b844",
        "answerHash": "58253e23aa0fa04c800c431a756c5e1461e2d712ec4498eb7752dfe2ef30efb8",
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
            "text": "Python 3.13 only, and the job injects a Jira token so the live client runs inside Actions."
          },
          {
            "id": "c",
            "text": "A download of Llama 3.1 8B, then the dashboard, before pytest is allowed to start."
          },
          {
            "id": "d",
            "text": "Streamlit Community Cloud, which replaces GitHub-hosted runners for this workflow."
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
            "text": "The YAML forbids a baseline rate, so the only legal invalids are the ones on the cause mask."
          },
          {
            "id": "c",
            "text": "numpy cannot draw two Bernoulli variables inside one function, so a second coin-flip is illegal and the mask would have to be applied in SQL instead."
          },
          {
            "id": "d",
            "text": "Redrawing lets the Pareto count valid rows, which a stacked probability would have dropped."
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
            "text": "It raises, because a zero event count makes the Wilson denominator undefined."
          },
          {
            "id": "b",
            "text": "It returns a negative lower bound, and the caller clamps that bound back into the unit interval before the memo is allowed to render."
          },
          {
            "id": "c",
            "text": "The analytic lower bound is 0. Floating point leaves a tiny residue, so anything under 1e-12 snaps back to 0."
          },
          {
            "id": "d",
            "text": "It returns the 2% spec as both ends, since a sample with no invalids is treated as the promise."
          }
        ],
        "salt": "91c2c89da5b68c4d",
        "answerHash": "0a37a3a1c835784d479f5f02cd02cd63d4d7b94fa47c24109f84019c90699ea2",
        "explain": "VGhlIGZvcm11bGEncyBsb3dlciBib3VuZCBpcyAwIHdoZW4gayBpcyAwLiBUaGUgc25hcCBzdG9wcyBhIHJlc2lkdWUgYXJvdW5kIDFlLTE4IGZyb20gbG9va2luZyBsaWtlIGEgcmVhbCByYXRlIGluIHRoZSBtZW1vLg=="
      },
      {
        "id": "s2q3",
        "prompt": "A lot and an instrument both look high. Which design choice makes those two claims separable?",
        "choices": [
          {
            "id": "a",
            "text": "Software version flips on the same day the bad lot starts, so the version cutover marks the lot rather than an independent instrument draw."
          },
          {
            "id": "b",
            "text": "The lot id is copied into the instrument column, which is what makes the two effects line up."
          },
          {
            "id": "c",
            "text": "Site, instrument, lot, software, and operator are drawn independently. A collection site is not tied to one instrument."
          },
          {
            "id": "d",
            "text": "Each collection site owns exactly one instrument, so the two columns are aliases of one draw."
          }
        ],
        "salt": "aa25122e5ee177ef",
        "answerHash": "4ae9c48e172e800cc45b05272fb1fb8cfb0477f7db5b12a39dec4ca50f84d9c3",
        "explain": "VGhlIG1vZHVsZSBkb2NzdHJpbmcgc3RhdGVzIHRoZSByZWZlcmVuY2UtbGFiIGFzc3VtcHRpb24uIGJhZF9sb3QgYWxzbyBydW5zIGJvdGggc29mdHdhcmUgdmVyc2lvbnMgZm9yIHRoZSB3aG9sZSBob3Jpem9uIHNvIGEgdmVyc2lvbiBjdXRvdmVyIGlzIG5vdCBtaXN0YWtlbiBmb3IgdGhlIGxvdC4="
      },
      {
        "id": "s2q4",
        "prompt": "Which four Western Electric rules does this p-chart implement?",
        "choices": [
          {
            "id": "a",
            "text": "Nelson rules 5 through 8 only, skipping the four zone rules a p-chart usually quotes."
          },
          {
            "id": "b",
            "text": "One point beyond 3 sigma; two of three beyond 2 sigma on one side; four of five beyond 1 sigma on one side; eight in a row on one side of the center."
          },
          {
            "id": "c",
            "text": "A two-sample t-test on every instrument, recomputed from scratch at the end of each day."
          },
          {
            "id": "d",
            "text": "Only a single weekly point outside the 2% spec, with no zone rules beyond that one comparison."
          }
        ],
        "salt": "f2ef2e7deccd4f1c",
        "answerHash": "92c724bf6a3b8e70afe6218c562244ab17dd27a62489cfdda08311f44938c13f",
        "explain": "VGhleSBydW4gb24gei1zY29yZXMgaW4gdGltZSBvcmRlci4gUnVsZSA0IG5lZWRzIGV2ZXJ5IHogaW4gYSB3aW5kb3cgb2YgOCBzdHJpY3RseSBvbiBvbmUgc2lkZSwgc28gYSBwb2ludCBvbiB0aGUgY2VudGVyIGxpbmUgYnJlYWtzIHRoZSBydW4u"
      },
      {
        "id": "s2q5",
        "prompt": "Where do the Mendeley hemolysis-index rows live in this repo?",
        "choices": [
          {
            "id": "a",
            "text": "openfda.py downloads the Mendeley rows on every generate and caches them beside the scenario."
          },
          {
            "id": "b",
            "text": "Inside the Week-0 memo as an appendix of raw hemolysis indexes taken from that paper."
          },
          {
            "id": "c",
            "text": "In scenarios/hil.csv, copied verbatim from the Mendeley paper so the generator can sample rows instead of a lognormal stand-in."
          },
          {
            "id": "d",
            "text": "They do not. seeds.py holds a lognormal stand-in and the DOI. The file is cited, not redistributed."
          }
        ],
        "salt": "c56fcf3b3ee766c0",
        "answerHash": "795c498059515727575a14638a4735bad94ad87d030eb721fa3d0d1f88312b3c",
        "explain": "SEVNT0xZU0lTX0JBU0VMSU5FIGFuZCBIRU1PTFlTSVNfU0VWRVJFIGFyZSBub3QgYSBmaXQgdG8gdGhhdCBmaWxlLiBEQVRBX0xJQ0VOU0VTLm1kIHNheXMgdGhlIHNhbWUgdGhpbmcuIG9wZW5mZGEucHkgY2FuIG9wdGlvbmFsbHkgYXNrIGZvciBhIGNvdW50IGFuZCBzd2FsbG93cyBuZXR3b3JrIGVycm9ycy4gZ2VuZXJhdGUgZG9lcyBub3QgY2FsbCBpdC4="
      },
      {
        "id": "s2q6",
        "prompt": "What does numpy's default_rng buy the PM?",
        "choices": [
          {
            "id": "a",
            "text": "A call to Ollama that invents each row from the scenario title instead of a seeded draw, using the complaint text as the prompt."
          },
          {
            "id": "b",
            "text": "A fresh random sample on every run, so the printed rate can be adjusted for the meeting."
          },
          {
            "id": "c",
            "text": "The Wilson formula itself, which default_rng evaluates in place of a random generator."
          },
          {
            "id": "d",
            "text": "A scenario file plus a seed is the whole source of randomness, so the same YAML reprints the same field file."
          }
        ],
        "salt": "a6700a25f200619a",
        "answerHash": "8314649112ea834367f55544dc2620bb5f23e5a03830e5d9df7cfbfe0944682a",
        "explain": "Z2VuZXJhdGUgZG9lcyBuID0gaG9yaXpvbiB0aW1lcyBydW5zIHBlciBkYXksIHRoZW4gYmFzZWxpbmUsIHRoZW4gdGhlIGNhdXNlLiBzdW1tYXJpemUgb25seSBmb3JtYXRzIG1ldHJpY3MuIElmIGEgcHJpbnRlZCBudW1iZXIgaXMgd3JvbmcsIHRoZSBidWcgaXMgaW4gdGhlIGdlbmVyYXRvciBvciB0aGUgbWV0cmljcywgbm90IGluIGEgc2VudGVuY2Uu"
      },
      {
        "id": "s2q7",
        "prompt": "What does chi_square_by return when the table has a single level?",
        "choices": [
          {
            "id": "a",
            "text": "p_value 0 and a huge chi-square, which forces the memo to escalate on any lone stratum."
          },
          {
            "id": "b",
            "text": "It raises ZeroDivisionError, because a one-row table has no complement to compare."
          },
          {
            "id": "c",
            "text": "The Wilson interval of that single level, returned in place of a chi-square result."
          },
          {
            "id": "d",
            "text": "p_value 1 and chi2 0. A quiet scenario is not an exception."
          }
        ],
        "salt": "5f9fec985ab3e5d2",
        "answerHash": "f1457ffc02ecb09f7e2432b24e3ce610928d0e8f50eef1eb2b1af5bb3133710e",
        "explain": "T25lIHN0cmF0dW0sIG9yIGEgY29sdW1uIG9mIGFsbCB6ZXJvcywgbWVhbnMgdGhlcmUgaXMgbm8gZXZpZGVuY2Ugb2YgYSBkaWZmZXJlbmNlLiBSZXR1cm5pbmcgcCA9IDEgbGV0cyB0aGUgcmFua2VyIG1vdmUgb24gaW5zdGVhZCBvZiBjcmFzaGluZyB0aGUgbWVtby4="
      },
      {
        "id": "s2q8",
        "prompt": "What does the Pareto exclude?",
        "choices": [
          {
            "id": "a",
            "text": "The most common invalid code, so the chart shows only the long tail of rare codes."
          },
          {
            "id": "b",
            "text": "Any code whose share of invalids is under 5%, which is dropped before the cumulative line."
          },
          {
            "id": "c",
            "text": "Valid rows. An empty invalid code must not count as a failure mode."
          },
          {
            "id": "d",
            "text": "Rows that belong to the injected lot, so the cause code cannot dominate the chart."
          }
        ],
        "salt": "b07fdadfa4b089fc",
        "answerHash": "44039c2dd35dd00a6f5b57285f881a19a63ad4031258cce1336054447e2c864e",
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
            "text": "It asks Llama 3.1 8B to remember the table, and a later node prompts the model for the same rows."
          },
          {
            "id": "b",
            "text": "It stores metrics, hypotheses, the evidence catalog, the memo, and the fidelity record. A later node calls generate(scenario) again. The seed makes that the same frame."
          },
          {
            "id": "c",
            "text": "It writes the CSV into the Jira issue description, and a later node parses that description back into rows."
          },
          {
            "id": "d",
            "text": "It stores the 14,400-row dataframe on the LangGraph state under the key rows, and later nodes read that key."
          }
        ],
        "salt": "704adf6e93902395",
        "answerHash": "e3cbeb3de3dec7f0f3e12c954f8421dc1e80e8381d8ef1306e6d1335c9a7dc85",
        "explain": "VGhlIHN0YXRlIGhvbGRzIHRoZSBzY2VuYXJpbyBkaWN0IGFuZCBlbXB0eSBsaXN0cyBmb3IgbGF0ZXIgYXJ0aWZhY3RzLiBJdCBkb2VzIG5vdCBob2xkIGEgZGF0YWZyYW1lLiBTYW1lIHNlZWQsIHNhbWUgMTQsNDAwIHJvd3Mu"
      },
      {
        "id": "s3q2",
        "prompt": "Why does the bad-lot memo list one hypothesis rather than six?",
        "choices": [
          {
            "id": "a",
            "text": "A LangGraph node may return only one string, so six hypotheses cannot fit in the state."
          },
          {
            "id": "b",
            "text": "Other strata miss at least one gate: 80 runs, lift 1.8, 15 excess invalids, and chi-square p < 0.01."
          },
          {
            "id": "c",
            "text": "Stakeholder injections outvote every stratum except the lot, which is why only L-4419 remains."
          },
          {
            "id": "d",
            "text": "The memo template has room for one hypothesis sentence, so extra strata are dropped while formatting."
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
            "text": "Ollama rewrites the sentence into the template before the guard ever scans the digits."
          },
          {
            "id": "b",
            "text": "Masking deletes 27.40 because that token looks like the lot id L-4419 with the letters removed."
          },
          {
            "id": "c",
            "text": "The guard accepts 27.40 because 27 sits close to the investigation week number stored in facts and week numbers are treated as percents."
          },
          {
            "id": "d",
            "text": "It survives masking, it is not within 0.03 of a walked fact, it lands in unknown, and ok is false."
          }
        ],
        "salt": "8aac7c13409ac90b",
        "answerHash": "4f0ee5ce9cd6bb3c990aa111bc4270759baeba098fa594da160c4567f7ce9c0a",
        "explain": "SWRlbnRpZmllcnMgc3VjaCBhcyBMLTQ0MTkgYXJlIHN0cmlwcGVkIG9ubHkgd2hlbiB0aGF0IGV4YWN0IHN0cmluZyBpcyBpbiB0aGUgZmFjdHMuIDI3LjQwIGlzIG5vdCBvbmUgb2YgdGhlbS4gMy42NyBpcyBhbGxvd2VkIGJlY2F1c2UgdGhlIHN0b3JlZCByYXRlIDAuMDM2NyBjb250cmlidXRlcyBpdHMgcGVyY2VudCBmb3JtLg=="
      },
      {
        "id": "s3q4",
        "prompt": "What happens if the Ollama backend is selected and the process cannot reach it?",
        "choices": [
          {
            "id": "a",
            "text": "The process exits and deletes week0_triage.md so a failed draft cannot be mistaken for the memo."
          },
          {
            "id": "b",
            "text": "narrate catches the exception, sets rewritten true, and returns the template. The failed draft is not saved."
          },
          {
            "id": "c",
            "text": "The memo file is left blank so a reviewer can see that the model call failed."
          },
          {
            "id": "d",
            "text": "The rejected draft is saved beside the memo with a warning banner and the bad number left intact for the reviewer to compare."
          }
        ],
        "salt": "0fc9ec0466f832cb",
        "answerHash": "70e8719092eedf44a10d4146885a76c8636353201f80deb122f35f26a31e2cf8",
        "explain": "VGhlIHRlbXBsYXRlIGlzIHJlbmRlcmVkIGZpcnN0LiBEZXRlcm1pbmlzdGljIG1vZGUgcmV0dXJucyBpdCBhZnRlciBhIGNoZWNrLiBBbnkgb3RoZXIgYmFja2VuZCB0aGF0IGVycm9ycywgcmV0dXJucyBlbXB0eSB0ZXh0LCBvciBmYWlscyB0aGUgZ3VhcmQgaXMgcmVwbGFjZWQuIEEgYnJva2VuIHRlbXBsYXRlIGlzIGEgYnVnIGFuZCByYWlzZXMu"
      },
      {
        "id": "s3q5",
        "prompt": "Why does rank_hypotheses ignore stakeholder injections?",
        "choices": [
          {
            "id": "a",
            "text": "The scenario YAML has no injections list yet, so the ranker has nothing to read."
          },
          {
            "id": "b",
            "text": "LangChain refuses string fields, so an injection cannot enter the ranking function."
          },
          {
            "id": "c",
            "text": "Injections are appended as extra field rows before chi-square, so a QA note can outrank a stratum."
          },
          {
            "id": "d",
            "text": "A cause has to come from the table. A QA sentence does not get a vote."
          }
        ],
        "salt": "749f56b8d4991b45",
        "answerHash": "cff23214a407b1bdc0053b31184689e7a7f82b2719617c4bc233564f13a6da00",
        "explain": "SW5qZWN0aW9ucyBhcmUgdGV4dC4gU2Vzc2lvbiA2IHNob3dzIHRoZW0gdG8gdGhlIHN0YXR1cyB3cml0ZXIuIFRoZXkgZG8gbm90IG91dHJhbmsgdGhlIGZpZWxkIGZpbGUuIGV2aWRlbmNlX2NhdGFsb2cgaXMgd2hhdCBsYXRlciBjaXRhdGlvbnMgYXJlIGFsbG93ZWQgdG8gdXNlLg=="
      },
      {
        "id": "s3q6",
        "prompt": "What does this tag do with --week other than 0?",
        "choices": [
          {
            "id": "a",
            "text": "It switches LLM_MODEL to llama3.2:1b and still writes the week-0 memo."
          },
          {
            "id": "b",
            "text": "It exits on purpose, so the tag cannot pretend the weekly loop already exists."
          },
          {
            "id": "c",
            "text": "It runs the full four-week loop and writes a plan, a fishbone, and a deck."
          },
          {
            "id": "d",
            "text": "It skips triage and writes only the fishbone, using injections as the hypothesis."
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
            "text": "LangGraph requires an httpx call inside every node, including the rules-only path that never leaves the laptop."
          },
          {
            "id": "b",
            "text": "httpx is the only client that can speak to a Llama 3.1 server, which is why the LangChain adapter is skipped."
          },
          {
            "id": "c",
            "text": "CI downloads the model weights through httpx during pytest, so the adapter has to be that library."
          },
          {
            "id": "d",
            "text": "One httpx call is easier to mock, and it is not called when the backend is deterministic."
          }
        ],
        "salt": "87adf0c5fd9f6348",
        "answerHash": "ebb07a54e5535fbc794799ce3ed7df206cb6f4072f73862ae48c2d7fbca1a4d3",
        "explain": "bGFuZ2NoYWluLWNvcmUgb25seSBzdXBwbGllcyB0aGUgcm9sZSBhbmQgY29udGVudCBwYWlycy4gbGxhbWEtY3BwLXB5dGhvbiBpcyBub3QgYSBkZXBlbmRlbmN5LiBJdCBpcyBpbXBvcnRlZCBvbmx5IGlmIHRoYXQgYmFja2VuZCBpcyBzZWxlY3RlZCwgYW5kIGEgbWlzc2luZyBpbnN0YWxsIGZhbGxzIGJhY2sgdG8gdGhlIHRlbXBsYXRlLg=="
      },
      {
        "id": "s3q8",
        "prompt": "Why are lot ids removed from the narrative instead of added to the numeric allow-list?",
        "choices": [
          {
            "id": "a",
            "text": "Because a Pydantic model cannot store strings, and a lot id has to be coerced to a float."
          },
          {
            "id": "b",
            "text": "Because the Wilson formula rejects integers, and 4419 would otherwise break the interval."
          },
          {
            "id": "c",
            "text": "So the scanner finishes faster on a one-page memo by skipping identifier-shaped tokens."
          },
          {
            "id": "d",
            "text": "So 4419 cannot be reused as a permitted rate."
          }
        ],
        "salt": "cb34da6250585deb",
        "answerHash": "86bcd6fcc431eca8164b7568d62fc16ec626444f751bab6d73b1719bb46b8c6f",
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
            "text": "Measurement is hard-coded to rank 1 so a quality diagram always leads with the gauge."
          },
          {
            "id": "b",
            "text": "The 6M set is the diagram a quality reviewer expects. An empty bone with score zero says the category was considered."
          },
          {
            "id": "c",
            "text": "Pydantic rejects a fishbone object that has fewer than six filled bones, empty or not."
          },
          {
            "id": "d",
            "text": "The scenario YAML names a gauge in an injection, which forces that bone to carry a score even when no measurement column exists."
          }
        ],
        "salt": "b3bfe52c32388dbf",
        "answerHash": "84388fad44f59f846b8d423cf5eea5f7b0678d9be857999a271571fc9ed35df0",
        "explain": "RHJvcHBpbmcgdGhlIGJvbmUgd291bGQgbG9vayBsaWtlIHRoZSBjYXRlZ29yeSB3YXMgbmV2ZXIgY29uc2lkZXJlZC4gTWF0ZXJpYWwgYXBwZWFycyB0d2ljZSwgbG90IGFuZCBoZW1vbHlzaXMsIGJlY2F1c2UgYm90aCBhcmUgbWF0ZXJpYWwgYW5kIHRoZXkgYXJlIGRpZmZlcmVudCBhY3Rpb25zLg=="
      },
      {
        "id": "s4q2",
        "prompt": "What does validate_whys reject, and when does it run?",
        "choices": [
          {
            "id": "a",
            "text": "Any Why whose answer is under 200 characters, and only after the markdown file already exists."
          },
          {
            "id": "b",
            "text": "An empty citation list, or an id that is not in the catalog. It runs inside build_whys, before markdown exists."
          },
          {
            "id": "c",
            "text": "A fishbone whose top score is zero. The check runs in CI and is skipped on a laptop."
          },
          {
            "id": "d",
            "text": "A citation of metric:overall:rate, which is reserved for the triage memo and banned from a Why even when the catalog contains it."
          }
        ],
        "salt": "93be1754b6c9245e",
        "answerHash": "f85e115777c0f9f6fd61a4792ff4b6f564db8ec996ee49c2091e5cb317af528c",
        "explain": "QSBXaHkgd2l0aCBubyBjaXRhdGlvbiBpcyBhbiBlcnJvciwgbm90IGEgd2FybmluZy4gVGhlIHRlc3QgcGxhbnRzIGNpdGF0aW9ucyBbXSBhbmQgZXhwZWN0cyAnd2h5IDEgaGFzIG5vIGNpdGF0aW9uJy4gQSBicm9rZW4gY2hhaW4gbmV2ZXIgYmVjb21lcyBhIGZpbGUu"
      },
      {
        "id": "s4q3",
        "prompt": "On bad_lot at week 0, can the 5 Whys cite the QA note about lot L-4419?",
        "choices": [
          {
            "id": "a",
            "text": "No. index_injections keeps only injections whose week is less than or equal to the case week. That note is week 1."
          },
          {
            "id": "b",
            "text": "Yes. Every injection in the scenario file is visible from week 0, including the QA lot note about L-4419 entering distribution."
          },
          {
            "id": "c",
            "text": "No. QA notes are dropped from the catalog permanently, whatever week the case has reached."
          },
          {
            "id": "d",
            "text": "Yes, but only when that note is attached to the Measurement bone rather than Material."
          }
        ],
        "salt": "d02672bcc70a5833",
        "answerHash": "aff6a50f2efcde5df4086ea12e1f0ffab5a503b88c51aa7dec09f848f6eb8b9b",
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
            "text": "A fresh chi-square the language model computes, replacing the p-chart as the effectiveness test."
          },
          {
            "id": "c",
            "text": "The lot is already cured, because D8 is closed and the record can quote a recovered rate."
          },
          {
            "id": "d",
            "text": "A customer-satisfaction score the model invents, which is why recovery is already claimed in D6."
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
            "text": "Each of the eight D fields is its own DMAIC cycle, so the record contains eight full cycles."
          },
          {
            "id": "b",
            "text": "Define is D1–D2, Measure is the metrics, Analyze is D4 plus the fishbone and 5 Whys, Improve is D3 and D5, Control is D6 and D7. D8 is closure, not a DMAIC phase."
          },
          {
            "id": "c",
            "text": "DMAIC appears only as a slide title in the week-4 deck and is absent from this tag's CAPA."
          },
          {
            "id": "d",
            "text": "DMAIC replaces D4, D5, and D6, and the other D headings are removed from the file."
          }
        ],
        "salt": "6ea08b9512df6622",
        "answerHash": "14810c540e5b4813fdd288e2db55e8b9c9de45514c1e58ac6b1f4c7368649a07",
        "explain": "QSBxdWFsaXR5IGhpcmluZyBtYW5hZ2VyIGxvb2tzIGZvciB0aGF0IG1hcHBpbmcuIFRoZSBsYWJlbHMgbGl2ZSBpbiB0aGUgQ0FQQSBmaWxlLCBub3QgYXMgYSBjbGFpbSB0aGF0IGFuIGFnZW50IHN3YXJtIGRpZCB0aGUgYW5hbHlzaXMu"
      },
      {
        "id": "s4q6",
        "prompt": "On bad_lot, what is rank 1, and what must step 5 say?",
        "choices": [
          {
            "id": "a",
            "text": "no_single_cause. Step 5 invents lot L-4419 so the bad-lot assertion in the test can pass without a scored Material bone."
          },
          {
            "id": "b",
            "text": "Measurement, because an empty bone sorts ahead of every scored branch."
          },
          {
            "id": "c",
            "text": "Material / bad_reagent_lot. Step 5 starts with a lot-level stop and includes the catalog sentence that names L-4419."
          },
          {
            "id": "d",
            "text": "Method and a software cause. Step 5 is required to name version 2.4.0 as the stop."
          }
        ],
        "salt": "3f3a9a31af48a4e2",
        "answerHash": "923244144e1f6075599675c2eb59ada4920c36f78f4a911282530eb551304699",
        "explain": "VGhlIHNvcnQgaXMgYnkgZGVzY2VuZGluZyBzY29yZS4gVGhlIGxvdCBpcyB0aGUgb25seSBub24temVybyBzY29yZS4gSGVtb2x5c2lzIGlzIGFsc28gTWF0ZXJpYWwgYW5kIHN0YXlzIGF0IDAgdW5kZXIgaXQuIG5vX3NpbmdsZV9jYXVzZSBpcyBub3QgYSBib25lLg=="
      },
      {
        "id": "s4q7",
        "prompt": "What does step 3 of the 5 Whys have to cite?",
        "choices": [
          {
            "id": "a",
            "text": "Whatever sentence the model prefers, and a missing catalog id is only a warning."
          },
          {
            "id": "b",
            "text": "The Jira API token, which step 3 has to quote before any stratum contrast is allowed."
          },
          {
            "id": "c",
            "text": "The same catalog sentence step 2 already used, pasted a second time so the chain looks longer."
          },
          {
            "id": "d",
            "text": "A different column, so the chain says why the next stratum is not the cause."
          }
        ],
        "salt": "6eb0462f25d2fd76",
        "answerHash": "7d2c57813753b1d09da52505e536f390b6e3d5cde3c932b520b170594423cdc4",
        "explain": "U3RlcCAxIGlzIG92ZXJhbGwgdmVyc3VzIHNwZWMuIFN0ZXAgMiBpcyB0aGUgd2lubmluZyBzdHJhdHVtLiBTdGVwIDMgaXMgdGhlIGNvbnRyYXN0LiBTdGVwIDQgY2l0ZXMgYW4gaW5qZWN0aW9uIHRoYXQgbmFtZXMgdGhlIGxldmVsLCBvciB0aGUgc3RyYXR1bSdzIG4gc2VudGVuY2Ugd2hlbiBubyBpbmplY3Rpb24gaGFzIGFycml2ZWQu"
      },
      {
        "id": "s4q8",
        "prompt": "Which new package does Session 4 add?",
        "choices": [
          {
            "id": "a",
            "text": "Llama 3.2 1B, which CI downloads before the fishbone test is allowed to run."
          },
          {
            "id": "b",
            "text": "A fishbone drawing library that renders the six bones as an image beside the markdown and is imported by rca.py for the PNG."
          },
          {
            "id": "c",
            "text": "kaleido, so the CAPA record can be exported to PDF from the Plotly figure."
          },
          {
            "id": "d",
            "text": "None. Pydantic checks the branch and the Why. The Session 3 fidelity guard is reused on the three markdown files."
          }
        ],
        "salt": "305d08e0d687d061",
        "answerHash": "31c34248597c9155a4b535a7e2b9f7d65732c73047df5033219f4304c449cf5c",
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
            "text": "Plotly has no timeline trace, so a Gantt PNG has to be drawn by hand in another tool."
          },
          {
            "id": "b",
            "text": "Jira rejects an image unless kaleido produced it, so the matplotlib PNG cannot be attached to the epic or the stories."
          },
          {
            "id": "c",
            "text": "PNG files are banned from the repo, which is why write_image is never called."
          },
          {
            "id": "d",
            "text": "write_image needs kaleido and a browser. The matplotlib path runs in CI and on a laptop without that download."
          }
        ],
        "salt": "5605f72faeb11c80",
        "answerHash": "4b1a575018eeaa887735045cbc93b060cdde9930fa33dd23e17b30a97cd5fb92",
        "explain": "VGhlIEhUTUwgaXMgcHgudGltZWxpbmUgc28gYSByZXZpZXdlciBjYW4gaG92ZXIgb3duZXJzLiBpbmNsdWRlX3Bsb3RseWpzIGNkbiBrZWVwcyB0aGF0IGZpbGUgc21hbGxlci4gVGhlIFBORyBkcmF3cyBvbmUgYmFyaCBwZXIgdGFzaywgcmV2ZXJzZWQgc28gVDEgaXMgb24gdG9wLCBhbmQgYSBtaW5pbXVtIHdpZHRoIHNvIGEgc2hvcnQgdGFzayBkb2VzIG5vdCB2YW5pc2gu"
      },
      {
        "id": "s5q2",
        "prompt": "What is the dependency rule, and why is a string comparison of the dates safe?",
        "choices": [
          {
            "id": "a",
            "text": "Dependencies are comments in the task dict. The assert that would check them is never called."
          },
          {
            "id": "b",
            "text": "Dates are compared as US month/day/year strings, which is why an ISO value would sort wrong."
          },
          {
            "id": "c",
            "text": "A task may start the day before its predecessor ends, which is how overlap gets onto the chart."
          },
          {
            "id": "d",
            "text": "A task's start must be greater than or equal to the predecessor's end. The dates are YYYY-MM-DD, so dictionary order matches calendar order."
          }
        ],
        "salt": "1fd73dfa8ef8435f",
        "answerHash": "8b1959844fa8ca53afec906fb269b96e844c4e52764f631c9619c10c61b598c1",
        "explain": "VGhlIGVuZCBpcyBleGNsdXNpdmU6IHN0YXJ0IHBsdXMgZGF5cy4gVGhlIHRlc3Qgd2Fsa3MgVDgsIHdoaWNoIHN0YXJ0cyB3aGVuIFQ2IGVuZHMsIGluc3RlYWQgb2YgdHJ1c3RpbmcgYSBjb21tZW50LiBBIGhhbmQtZWRpdGVkIGVhcmx5IHN0YXJ0IHJhaXNlcy4="
      },
      {
        "id": "s5q3",
        "prompt": "What changes between week 0 and week 2 on the Gantt and the risk register?",
        "choices": [
          {
            "id": "a",
            "text": "R4 is removed at week 2 because release testing passed and the disagreement is over."
          },
          {
            "id": "b",
            "text": "The Gantt bars stay identical. Only the memo title string changes between those weeks."
          },
          {
            "id": "c",
            "text": "Week 2 adds T11, the lab-director note. R1's trend goes from new to down and its likelihood drops. R4 appears with trend up."
          },
          {
            "id": "d",
            "text": "Every baseline task is deleted at week 2 and replaced by the lab-director set."
          }
        ],
        "salt": "0b6527d5129bd6de",
        "answerHash": "f53caa0efa1232676c9601ab66fa0f4498652630861b0f66d5c022009d794a9e",
        "explain": "VDEyLCBsYW5lIHRlbXBlcmF0dXJlLCB3YWl0cyBmb3Igd2VlayAzLiBCYXNlbGluZSB0YXNrcyBzdGF5LCBiZWNhdXNlIGEgcmUtcGxhbiB0aGF0IHRocm93cyBhd2F5IHRoZSBmaXNoYm9uZSByZXZpZXcgaXMgbm90IGEgcmUtcGxhbi4gUjQgaXMgdGhlIGRpc2FncmVlbWVudCBiZXR3ZWVuIHJlbGVhc2UgdGVzdGluZyBhbmQgdGhlIGZpZWxkIHJhdGUu"
      },
      {
        "id": "s5q4",
        "prompt": "Why are dry-run keys SIM-*?",
        "choices": [
          {
            "id": "a",
            "text": "The epic key is copied from the scenario id, and that id is the string SIM."
          },
          {
            "id": "b",
            "text": "A SIM prefix means the live site accepted the issue and returned that key."
          },
          {
            "id": "c",
            "text": "Jira Cloud Free rejects every project key except SIM, so INV cannot be used in a dry-run."
          },
          {
            "id": "d",
            "text": "The build backlog uses INV-*. SIM-* makes a dry-run file obviously not that board."
          }
        ],
        "salt": "9da334efd4f63eaa",
        "answerHash": "f29af06093fed25d74e4d9873b85e05cc06ffdf1aada964c09ce2e9b18c41cc0",
        "explain": "V2l0aCBubyB0b2tlbiwgc3luYyB3cml0ZXMgamlyYV9pc3N1ZXMuanNvbiBhbmQgZG9lcyBub3Qgb3BlbiBhIHNvY2tldC4gVGhlIGZpbGUgY2FycmllcyBhIHNpbXVsYXRpb24gZGlzY2xhaW1lci4gbWFrZV9jbGllbnQgcmV0dXJucyBEcnlSdW5KaXJhIHVubGVzcyBhbGwgdGhyZWUgSmlyYSBzZXR0aW5ncyBhcmUgcHJlc2VudC4="
      },
      {
        "id": "s5q5",
        "prompt": "What happens if the live Jira call raises?",
        "choices": [
          {
            "id": "a",
            "text": "The API token is interpolated into the error string so the PM can see which credential failed."
          },
          {
            "id": "b",
            "text": "The client retries the POST forever, and the JSON file is written only after a success."
          },
          {
            "id": "c",
            "text": "LiveJira.sync catches it, stores the exception class name, writes the JSON, and does not raise. The token is not put in the error or in repr."
          },
          {
            "id": "d",
            "text": "The process deletes plan.json, because a failed sync means the schedule is no longer valid."
          }
        ],
        "salt": "00af55c5ea95f202",
        "answerHash": "c29e05a8c70557c1dfebe6256126a3df4d87411a283195423ef717c9c68df66a",
        "explain": "VGVzdHMgcGFzcyBhIGZha2UgdHJhbnNwb3J0IGFuZCBuZXZlciBjb25zdHJ1Y3QgdGhlIHJlYWwgaHR0cHggY2xpZW50IGZvciB0aGUgZHJ5LXJ1bi4gQSBwbGFudGVkIHRva2VuIG11c3QgYmUgYWJzZW50IGZyb20gcmVwci4="
      },
      {
        "id": "s5q6",
        "prompt": "What does the live test count on the second sync?",
        "choices": [
          {
            "id": "a",
            "text": "Eleven additional POSTs, one per task, on every sync including the second call."
          },
          {
            "id": "b",
            "text": "One POST whose body is the entire plan, instead of an epic plus separate stories."
          },
          {
            "id": "c",
            "text": "Zero new POSTs. The first sync posts the epic plus the tasks. _upsert updates a story in place when the task id is already in the file."
          },
          {
            "id": "d",
            "text": "A DELETE against every SIM key, so the second sync clears the board before rewriting it."
          }
        ],
        "salt": "54f918147ac804c9",
        "answerHash": "050cd9cde67e55a9d021b70f00397ba704c2b0936b24d0c263a214a48d48f0e7",
        "explain": "VGhlIGZpcnN0IGNhbGwgaXMgMTEgcG9zdHM6IGVwaWMgcGx1cyAxMCB0YXNrcyBhdCB3ZWVrIDAuIFRoZSBieV90YXNrIG1hcCBza2lwcyBjcmVhdG9yIHdoZW4gdGhlIGlkIGV4aXN0cyBhbmQgc3RpbGwgcmVmcmVzaGVzIHN1bW1hcnksIHN0YXR1cywgYW5kIG93bmVyLiBEZXNjcmlwdGlvbnMgdXNlIEppcmEncyBkb2N1bWVudCBmb3JtYXQgYmVjYXVzZSBBUEkgdjMgcmVqZWN0cyBhIHBsYWluIHN0cmluZy4="
      },
      {
        "id": "s5q7",
        "prompt": "Why does plan run after triage and not after the fishbone?",
        "choices": [
          {
            "id": "a",
            "text": "A Jira project must already exist before any invalid rate is computed."
          },
          {
            "id": "b",
            "text": "The Gantt dates are an input to the hypothesis ranker, so plan has to finish before any stratum is scored."
          },
          {
            "id": "c",
            "text": "LangGraph sorts node names alphabetically, which places plan after rca."
          },
          {
            "id": "d",
            "text": "The planner reads the top hypothesis. It does not read the fishbone. RCA does not read the plan."
          }
        ],
        "salt": "ba424e0ed43edd12",
        "answerHash": "881684784949af00ca043568a993f623672502fa3df3b76357a903d7214b7457",
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
            "text": "Every task, including containment, is owned by the language model rather than a function."
          },
          {
            "id": "c",
            "text": "Jira assigns a random owner whenever the issue key starts with SIM."
          },
          {
            "id": "d",
            "text": "The customer owns containment for a lot, an instrument, and a case with no single cause."
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
            "text": "Triage is deleted from the graph after Session 5, which is why later laps skip it."
          },
          {
            "id": "b",
            "text": "The field file is fixed by the scenario seed. Re-running triage would recompute the same metrics. The lap re-enters at plan."
          },
          {
            "id": "c",
            "text": "The customer note overwrites the metrics, so a second triage would have nothing to read."
          },
          {
            "id": "d",
            "text": "LangGraph allows only one node in a process, so triage cannot be entered again."
          }
        ],
        "salt": "348cbf7de3078da9",
        "answerHash": "c77f7c19539bd14c26926691b968b55b05c7ecf3c9f29df4f5eb94c330a8b7d3",
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
            "text": "Week 2 turns Green because release testing passed, and the file is then cured."
          },
          {
            "id": "c",
            "text": "Green is reserved for a successful model call, and week 2 never invokes one."
          },
          {
            "id": "d",
            "text": "RAG names a retrieval index here, and Red means that index missed the lot note."
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
            "text": "Switch the leading cause to software, because the release note said the lot had passed and the table should follow the note."
          },
          {
            "id": "b",
            "text": "Delete task T1, because its simulation week has already passed."
          },
          {
            "id": "c",
            "text": "Close D8 and ship the executive deck at the end of week 2."
          },
          {
            "id": "d",
            "text": "Keep the field ranking after release testing was reported as a pass, and add the lab-director note to the plan."
          }
        ],
        "salt": "267f892434654159",
        "answerHash": "164a160423ed5dd1f54c64d2718b754079e892c9c422a9d03cca4cc54791f679",
        "explain": "V2VlayAxJ3Mgcm93IHNheXMgdGhlIFFBIG5vdGUgaXMgYSBjaXRhdGlvbiBhbmQgZG9lcyBub3QgZ2V0IGl0cyBvd24gc2NvcmUuIFdlZWsgMyBzYXlzIGRvIG5vdCBzd2l0Y2ggdGhlIGNhdXNlIG9udG8gdGhlIHNoaXBwaW5nIG5vdGUuIE9uZSByb3cgcGVyIHdlZWsgaXMgdGhlIGRpZmYgYSBQTSB3b3VsZCBzaG93Lg=="
      },
      {
        "id": "s6q4",
        "prompt": "How can the customer note mention a rate without the template doing arithmetic?",
        "choices": [
          {
            "id": "a",
            "text": "The template multiplies invalids by 100 and divides by the row count inside the f-string."
          },
          {
            "id": "b",
            "text": "Llama 3.2 1B types the percent on Streamlit Community Cloud, and the template pastes that string."
          },
          {
            "id": "c",
            "text": "build_status_facts rounds the computed rate onto rate_pct. The template interpolates that field. The guard then checks the sentence."
          },
          {
            "id": "d",
            "text": "The percent is copied from the customer's complaint sentence, which is why no arithmetic runs."
          }
        ],
        "salt": "666a134f18becf06",
        "answerHash": "5d84f488296324711eacfc0792850f440f47c4d3cbf3ffcbd6287bcd75957f8c",
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
            "text": "A git diff between the session-5 tag and the session-6 tag, which is the week-0 versus week-2 plan a reviewer would quote in the decision log."
          },
          {
            "id": "c",
            "text": "Only the final jira_issues.json, which keeps a copy of every week's plan inside one file."
          },
          {
            "id": "d",
            "text": "The Streamlit cache, which stores each week's plan.json under the audience radio key."
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
            "text": "It must include the Jira API token so the customer can comment on the SIM issue."
          },
          {
            "id": "b",
            "text": "It must quote a different invalid rate from the one printed on the leadership note."
          },
          {
            "id": "c",
            "text": "It must name the lot, quote the chi-square p-value, and paste the 5 Whys for the customer before the holding sentence."
          },
          {
            "id": "d",
            "text": "It must not state a confirmed cause. Internal gets the hypothesis. Leadership gets the cost and the ask."
          }
        ],
        "salt": "18033037414f7c25",
        "answerHash": "bbce7a8746ef1eff294c6102eba14eac639f8bcd008cbc426d89a29872fe94f8",
        "explain": "SW50ZXJuYWwgcGFzdGVzIGluamVjdGlvbiB0ZXh0IHZlcmJhdGltIHNvIHRoZSBndWFyZCBjYW4gbWFzayBpdC4gVGhlIGN1c3RvbWVyIGFjdGlvbiBpcyBhIGhvbGRpbmcgc2VudGVuY2UuIFRoYXQgc3BsaXQgaXMgdGhlIHN0YWtlaG9sZGVyIHNraWxsIHRoZSBzZXNzaW9uIGlzIHByYWN0aWNpbmcu"
      },
      {
        "id": "s6q7",
        "prompt": "At the end of a week-3 run, which tasks are Done?",
        "choices": [
          {
            "id": "a",
            "text": "Done is applied only by a live Jira transition, and a dry-run file leaves every task in To Do regardless of sim week or owner."
          },
          {
            "id": "b",
            "text": "Status is a comparison of integers. T1 (sim week 0) is Done and T11 (sim week 2) is Done. T10 (sim week 4) is still To Do."
          },
          {
            "id": "c",
            "text": "Every task stays In Progress until the week-4 deck is written, including T1."
          },
          {
            "id": "d",
            "text": "T11 does not exist yet at the end of week 3, so only T1 can be Done."
          }
        ],
        "salt": "ebe74b486508e880",
        "answerHash": "843127940da5aa2f882dfec40a939fb195329eaac5a776429459e997ee24e305",
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
            "text": "It returns triage, and the field file is redrawn from a new seed."
          },
          {
            "id": "c",
            "text": "It returns end on every lap, so the week counter never moves."
          },
          {
            "id": "d",
            "text": "It returns closeout as soon as week 1 finishes, and the deck is written early."
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
            "text": "The page raises unless LLM_BACKEND is ollama, and rules-only is how that backend is selected."
          },
          {
            "id": "b",
            "text": "Streamlit Community Cloud has no Ollama, and this repo does not ship weights. The deterministic templates answer without a download."
          },
          {
            "id": "c",
            "text": "Plotly cannot draw a p-chart while a model is loaded, so rules-only keeps the chart alive."
          },
          {
            "id": "d",
            "text": "GitHub Actions hosts the dashboard and forbids Python, so the page has to stay rules-only."
          }
        ],
        "salt": "573fe1424ad5e481",
        "answerHash": "40d9834fe471f82944d4c7f164bf68bb93e4cb1c448a4c5c0dff4201003c5d0f",
        "explain": "QSBtaXNzaW5nIG1vZGVsIGlzIGEgZmFsbGJhY2ssIG5vdCBhIGNyYXNoLiBuYXJyYXRlIHN0aWxsIHJlcGxhY2VzIGEgcmVqZWN0ZWQgZHJhZnQgd2l0aCB0aGUgdGVtcGxhdGUuIFRoZSBiYW5uZXIgaXMgdGhlIGZpcnN0IHRoaW5nIG9uIHRoZSBwYWdlLCBpbmNsdWRpbmcgdGhlIGNsaW5pY2FsLXVzZSBsaW5lLg=="
      },
      {
        "id": "s7q2",
        "prompt": "Which variable names the model, and what does the page request when rules-only is off and that variable is unset?",
        "choices": [
          {
            "id": "a",
            "text": "There is no model variable. With the toggle off the page picks a tag at random."
          },
          {
            "id": "b",
            "text": "The hosted page always downloads Llama 3.1 8B, and the toggle cannot change that tag."
          },
          {
            "id": "c",
            "text": "LLM_MODEL. An explicit value wins. With the toggle off and the variable unset, a local or self-hosted run asks Ollama for llama3.2:1b. The CLI default remains llama3.1:8b."
          },
          {
            "id": "d",
            "text": "OLLAMA_MODEL overrides LLM_MODEL, and an unset value on the hosted page downloads llama3.1:8b."
          }
        ],
        "salt": "7acc16b44f33dcb2",
        "answerHash": "7cbce749ebbcd80f5f6f9634afe3d16bb570614de7bd8a86e4654ef1d27052e4",
        "explain": "SE9TVEVEX0xMTV9NT0RFTCBpcyB0aGUgc21hbGwgdGFnLCBMbGFtYSAzLjIgMUIuIEl0IGlzIHdoYXQgdGhlIHRvZ2dsZSBhc2tzIGZvciBsb2NhbGx5LiBDb21tdW5pdHkgQ2xvdWQgc3RheXMgb24gdGhlIHJ1bGVzLW9ubHkgZGVmYXVsdCBiZWNhdXNlIENsb3VkIGNhbm5vdCBydW4gT2xsYW1hLiBHZW1tYSAzIGFuZCBQaGktNCBhcmUgb3RoZXIgdGFncyB5b3UgY2FuIHNldCB5b3Vyc2VsZi4="
      },
      {
        "id": "s7q3",
        "prompt": "Why does the before/after chart say the after series is not observed follow-up?",
        "choices": [
          {
            "id": "a",
            "text": "Matplotlib simulates a cured process and rewrites the scenario YAML with the new rate."
          },
          {
            "id": "b",
            "text": "projection_summary clears invalids on the leading stratum of the same synthetic file. No new field data were collected."
          },
          {
            "id": "c",
            "text": "The after series is a screenshot the customer sent, pasted onto the chart as observed follow-up after the quarantine was approved."
          },
          {
            "id": "d",
            "text": "The after series is next month's real complaints, collected after the lot was quarantined."
          }
        ],
        "salt": "e0bdbe9e62bf59fc",
        "answerHash": "a644faf7f75ee331c3c454deaca3109c42e9203e0d675681dda4396ad7b55b68",
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
            "text": "Every audience click reruns the four-week graph and ignores st.cache_data."
          },
          {
            "id": "c",
            "text": "Nothing is cached, because Streamlit forbids st.cache_data on a Community Cloud app."
          },
          {
            "id": "d",
            "text": "The cache key is only the audience name, so a new week still serves the previous run from memory without calling run_case."
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
            "text": "Nothing. Session 7 already published the public URL, and the repo contains that link."
          },
          {
            "id": "b",
            "text": "Buy a Plotly license, which is the gate Community Cloud checks before the first deploy."
          },
          {
            "id": "c",
            "text": "Sign in to Streamlit Community Cloud with GitHub and select app/streamlit_app.py or the root streamlit_app.py. The repo cannot do that sign-in."
          },
          {
            "id": "d",
            "text": "Commit a Jira API token so Community Cloud can start Ollama for the hosted page."
          }
        ],
        "salt": "d2a33e926656e5ca",
        "answerHash": "72877c2368c17be6be06fb73109e262ad0713cb89b6e2bcf2ef261d967e92ce9",
        "explain": "VGhlIHJvb3QgZmlsZSB1c2VzIHJ1bnB5IHNvIGJvdGggZW50cnkgcG9pbnRzIHdvcmsuIFRpY2tldCBJTlYtMzAxIGlzIHRoZSBkYXNoYm9hcmQuIFRoZSBhY2FkZW15IGxlYXZlcyBzdHJlYW1saXRVcmwgYmxhbmsgdW50aWwgdGhhdCBVUkwgZXhpc3RzLg=="
      },
      {
        "id": "s7q6",
        "prompt": "Which colors mark the p-chart, and what is red for?",
        "choices": [
          {
            "id": "a",
            "text": "The figure is a matplotlib PNG embedded by Kaleido, and red is the PNG border."
          },
          {
            "id": "b",
            "text": "A random Plotly palette, one color per functional owner, with no fixed red for rule-1 marks on the p-chart."
          },
          {
            "id": "c",
            "text": "Navy #0B3A5B and teal #1F7A8C for the series, red #B23A48 for rule-1 marks. No purple gradient."
          },
          {
            "id": "d",
            "text": "Red marks the projected series. Navy marks a model token sitting in the page state."
          }
        ],
        "salt": "ba7dce9e8a01664a",
        "answerHash": "fe3b3ac5af54dd30c327be4870bf89d643cfe84dfadf1ce14baadeb9fcdb06f4",
        "explain": "Y2hhcnRzLnB5IHJlYWRzIHRoZSBwLWNoYXJ0IGRpY3QgYW5kIHRoZSBQYXJldG8gZGljdCB0aGUgZ3JhcGggYWxyZWFkeSBjb21wdXRlZC4gVGhlIHN0YXRpYyBQTkcgcGF0aCBmb3Igc2xpZGVzIHN0YXlzIG9uIG1hdHBsb3RsaWIgYmVjYXVzZSBQbG90bHkncyBleHBvcnQgbmVlZHMgS2FsZWlkbywgd2hpY2ggaXMgbm90IHNoaXBwZWQu"
      },
      {
        "id": "s7q7",
        "prompt": "What does requirements.txt deliberately leave out?",
        "choices": [
          {
            "id": "a",
            "text": "Plotly, because the hosted page draws every chart with matplotlib instead."
          },
          {
            "id": "b",
            "text": "Streamlit itself, so Community Cloud is expected to serve the page with another framework."
          },
          {
            "id": "c",
            "text": "A GGUF weight file. The install list is pandas, numpy, scipy, PyYAML, Pydantic, httpx, LangGraph, langchain-core, Plotly, matplotlib, python-pptx, and Streamlit."
          },
          {
            "id": "d",
            "text": "pytest, which Community Cloud needs in the install list before it will boot the app."
          }
        ],
        "salt": "5d265b0f400a07e3",
        "answerHash": "19058a6d12b638bbe40cecb92dd0f14214ee732a3912da9fa7553fd2b5202785",
        "explain": "VGhlIGNvbW1lbnQgYXQgdGhlIHRvcCBvZiB0aGUgZmlsZSBzYXlzIHRoZSBkZWZhdWx0IGJhY2tlbmQgaXMgZGV0ZXJtaW5pc3RpYy4gLnN0cmVhbWxpdC9jb25maWcudG9tbCBzZXRzIHRoZSBuYXZ5IHRoZW1lLCBoZWFkbGVzcyBtb2RlLCBhbmQgdHVybnMgdXNhZ2Ugc3RhdHMgb2ZmLg=="
      },
      {
        "id": "s7q8",
        "prompt": "What does the dashboard test require the page to show?",
        "choices": [
          {
            "id": "a",
            "text": "That flipping the audience radio changes the invalid rate shown on the tile."
          },
          {
            "id": "b",
            "text": "AppTest renders the banner without an exception, including the clinical-use line, and at least one metric. A second test checks that removing the bad lot lowers the projected rate."
          },
          {
            "id": "c",
            "text": "A live browser click, which CI performs against Community Cloud on every pull request."
          },
          {
            "id": "d",
            "text": "That the page downloads llama3.1:8b during AppTest and fails if the weight is missing."
          }
        ],
        "salt": "b93a90e8549423f0",
        "answerHash": "7c666f51c5be8ad1ce43e6cab204a5ea17ca96f6922a4d0ea41158da7c1cb6c3",
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
            "text": "The report stores no counts. The 22 of 22 cell is typed into the README by hand."
          },
          {
            "id": "b",
            "text": "Evidence top-1 and top-3 were 22/22. Keyword top-1 was 3/22. The three keyword hits are the flat files, whose week-0 note names no cause."
          },
          {
            "id": "c",
            "text": "Evidence top-1 was 3 of 22 and the keyword ranker was 22 of 22 on the same files."
          },
          {
            "id": "d",
            "text": "Both rankers scored 22 of 22, so a week-0 note is as accurate as the evidence table."
          }
        ],
        "salt": "1f7a97edfa9bf876",
        "answerHash": "788058c41f24f5c32934b692359c1e391786338787e72bfc94753c172e43e193",
        "explain": "SG9sZG91dCB3YXMgNCBvZiAyMi4gR2F0ZXMgd2VyZSBub3QgcmVmaXQuIFJlYWQgdGhlIHdlYWstbG90IHJvdyBhbmQgdGhlIGRyaWZ0IGV4dHJhLXN0cmF0dW0gbGluZXMgYmVmb3JlIHF1b3RpbmcgdGhlIDIyLzIyIGNlbGwu"
      },
      {
        "id": "s8q2",
        "prompt": "Why is weak_lot a success when the evidence call is no_single_cause?",
        "choices": [
          {
            "id": "a",
            "text": "The evidence ranker is wrong on weak_lot, and the keyword ranker is the number to quote."
          },
          {
            "id": "b",
            "text": "no_single_cause means generate failed, so weak_lot never produced a frame to score."
          },
          {
            "id": "c",
            "text": "weak_lot is one of the four holdout files, so it is excluded from the score entirely."
          },
          {
            "id": "d",
            "text": "The lot bump was built to stay under the lift gate. The correct call is to withhold. The keyword ranker repeats the note and says bad_reagent_lot."
          }
        ],
        "salt": "70854749f7f893fc",
        "answerHash": "4c23cb9c38f79232a9ac52a87752b6264826382926fba76f20ead698f75c9108",
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
            "text": "The drift files were removed from the scored set once a second stratum appeared."
          },
          {
            "id": "c",
            "text": "Top-1 flipped to the reagent lot on all four drift files, and the instrument fell to second."
          },
          {
            "id": "d",
            "text": "Only the keyword ranker saw the instrument. The evidence ranker stayed on the lot."
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
            "text": "Llama 3.2 1B won the comparison, but that accuracy figure is confidential and stays out of the report."
          },
          {
            "id": "b",
            "text": "Community Cloud ran both models on the 22 files, and the two accuracies came out tied."
          },
          {
            "id": "c",
            "text": "Neither model was installed. The table compares two ranking policies on the deterministic backend."
          },
          {
            "id": "d",
            "text": "The older 7B versus 1.5B comparison is still the number a resume is supposed to quote."
          }
        ],
        "salt": "7890e6fb3080a6c5",
        "answerHash": "2c73be13b0937b9b4bcff2e0587d7d1c1e6715156a8fb4f00e4685f721c0ff87",
        "explain": "VGhlIHBsYW4ncyBtb2RlbCBwYWlyIGlzIG5vdyB0aG9zZSB0d28gTGxhbWEgdGFncy4gQSBtb2RlbCBkcmFmdCB3b3VsZCBzdGlsbCBoYXZlIHRvIHBhc3MgdGhlIG51bWVyaWMtZmlkZWxpdHkgY2hlY2sgYmVmb3JlIGl0IHdhcyBzaG93bi4gRG8gbm90IHF1b3RlIHRoZSB0YWJsZSBhcyBhIG1vZGVsLWFjY3VyYWN5IG51bWJlci4="
      },
      {
        "id": "s8q5",
        "prompt": "Why is the red-herring key written \"true\" with quotes in the YAML?",
        "choices": [
          {
            "id": "a",
            "text": "The quotes force the lot id to be parsed as a float, which is what the generator expects for L-4419."
          },
          {
            "id": "b",
            "text": "PyYAML 1.1 treats an unquoted true as a boolean. The generator looks up the string key \"true\"."
          },
          {
            "id": "c",
            "text": "The scenario is JSON, and JSON requires quotes around every key including true."
          },
          {
            "id": "d",
            "text": "The quotes mark the file so the keyword ranker skips it and cannot take the herring."
          }
        ],
        "salt": "04f27cf10dc8d444",
        "answerHash": "ac3ef2c69009698ef7c50aba43161f620b04f24cefc448ff6743bb00ccfa0891",
        "explain": "aGVycmluZ19zb2Z0d2FyZSdzIHdlZWstMCBub3RlIHNheXMgc29mdHdhcmUuIHJvb3RfY2F1c2UudHJ1ZSBpcyB0aGUgbG90LiBUaGUgcmFua2VyIGRvZXMgbm90IHJlY2VpdmUgZXZhbC5leHBlY3RfY2F1c2UuIFRoZSBub3RlIGRvZXMgbm90IGdldCB0byBvdXR2b3RlIHRoZSB0YWJsZS4="
      },
      {
        "id": "s8q6",
        "prompt": "What does score_scenario refuse to pass into the ranker?",
        "choices": [
          {
            "id": "a",
            "text": "The 2% spec, which would let the ranker decide escalate before it sees a stratum."
          },
          {
            "id": "b",
            "text": "The scenario seed, which would let the ranker rebuild the frame a second way."
          },
          {
            "id": "c",
            "text": "eval.expect_cause. That block is the label for the score, not an input."
          },
          {
            "id": "d",
            "text": "The column list, which would tell the ranker which strata it is allowed to score."
          }
        ],
        "salt": "08157241d4804410",
        "answerHash": "9004fcbe6ca2cb2ed29b0c5b391836ace383d9b30d42a1fdb6855f007768e264",
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
            "text": "The keyword ranker treats 2.4 as its score unless that token is listed in the facts."
          },
          {
            "id": "c",
            "text": "2.4.0 is the invalid rate on a software scenario, so it belongs in the facts as a percent."
          },
          {
            "id": "d",
            "text": "Pydantic stores version strings only after they are coerced to floats, which is why 2.4.0 is copied."
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
            "text": "Nothing from the eval script. The report is edited by hand and CI does not read it."
          },
          {
            "id": "b",
            "text": "The same eval entry point with --limit 5 --smoke. It fails if evidence top-1, fidelity, citations, or escalation miss."
          },
          {
            "id": "c",
            "text": "A refit of the lift gate on the holdout split, which CI runs before the smoke limit."
          },
          {
            "id": "d",
            "text": "All 22 scenarios against a live Llama 3.1 server, and CI fails if that server is down or the tag is missing from the laptop."
          }
        ],
        "salt": "15c51f71a75472dc",
        "answerHash": "8154b0c1834e1785ba3fe41742fe31ae30631af1c88f2c9cefa052cdb7dc2d77",
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
            "text": "The status node cannot represent week numbers above 3, so week 4 has to leave the graph."
          },
          {
            "id": "b",
            "text": "Week 4 deletes the plan and starts triage again from an empty hypothesis list."
          },
          {
            "id": "c",
            "text": "A script outside the graph writes the deck and deliberately skips the fidelity check."
          },
          {
            "id": "d",
            "text": "Status is the weekly note. Close-out confirms D7 and D8 and writes the deck. Routing week 4 to closeout keeps that work inside the graph, under the fidelity check."
          }
        ],
        "salt": "890b0e2c9ce37da1",
        "answerHash": "54f71c5a37f4c1739ad93db45be0ac09690850817e2726dd22e4eb0d3190199d",
        "explain": "cm91dGVfYWZ0ZXJfc3RhdHVzIHNlbmRzIHdlZWsgNCB0byBjbG9zZW91dC4gV2Vla3MgMCB0aHJvdWdoIDMgc3RpbGwgZW5kIG9yIGFkdmFuY2UsIHNvIGVhcmxpZXIgdGVzdHMgZG8gbm90IGJ1aWxkIGEgZGVjay4gcHJlbGltaW5hcnlfY2xvc2UgYmVjb21lcyBmYWxzZSBvbmNlIEQ3IGFuZCBEOCBhcmUgY29uZmlybWVkLg=="
      },
      {
        "id": "s9q2",
        "prompt": "What would be false about the deck if the projected rate were labeled as follow-up?",
        "choices": [
          {
            "id": "a",
            "text": "The projection is a second scenario file the customer signed, so calling it follow-up is fair."
          },
          {
            "id": "b",
            "text": "The generator does not rewrite the field file. Clearing the leading stratum is a counterfactual. bad_lot stays over spec in the observed series."
          },
          {
            "id": "c",
            "text": "python-pptx requires the word follow-up on the impact slide or the deck will not save."
          },
          {
            "id": "d",
            "text": "Follow-up would be accurate, because the scenario YAML already contains next quarter's cured rows."
          }
        ],
        "salt": "74109de835691552",
        "answerHash": "4cec79727ccdfcb3a5a4493eda09abc013052a391b12e53ea0275cbc50cc9c77",
        "explain": "VGhlIGVmZmVjdGl2ZW5lc3Mgc2VudGVuY2UgaW5jbHVkZXMgdGhlIGxhYmVsICdOb3Qgb2JzZXJ2ZWQgZm9sbG93LXVwLicgVGhlIHJvb3QtY2F1c2Ugc2xpZGUncyBjaGFydCBpcyB0aGUgb2JzZXJ2ZWQgd2Vla2x5IHJhdGUuIFRoZSBzZW50ZW5jZSB1bmRlciB0aGUgcmVjb21tZW5kYXRpb24gc2F5cyBub3QgdG8gdHJlYXQgdGhlIHByb2plY3RlZCByYXRlIGFzIG9ic2VydmVkIGZvbGxvdy11cC4="
      },
      {
        "id": "s9q3",
        "prompt": "Where does the dollar cost on the impact slide come from?",
        "choices": [
          {
            "id": "a",
            "text": "The dollar amount pasted from the customer's email, which the template does not recompute."
          },
          {
            "id": "b",
            "text": "k times cost_per_invalid_usd from the scenario. For bad_lot that is 529 times 85. The template does not type the product."
          },
          {
            "id": "c",
            "text": "A round dollar figure the model picks for an executive audience, independent of the row count and the unit price in the YAML."
          },
          {
            "id": "d",
            "text": "Jira story points for the investigation epic, multiplied by 1000."
          }
        ],
        "salt": "068eee5576b06244",
        "answerHash": "823600df6953b8efc9fc9456acd24dd8b0ffc5b16661b412103cb4564ce77968",
        "explain": "YnVpbGRfY2xvc2VvdXRfZmFjdHMgY29tcHV0ZXMgdGhlIHByb2R1Y3QgYW5kIGRyb3BzIHRoZSBmcmFtZSBiZWZvcmUgdGhlIHJlY29yZCBpcyBzdG9yZWQuIHB5dGhvbi1wcHR4IHdyaXRlcyB0aGUgc2xpZGUgZnJvbSB0aG9zZSBmYWN0cywgc28gYSBzbGlkZSBjYW5ub3QgaW52ZW50IGEgY29zdC4gbWF0cGxvdGxpYiB3aXRoIHRoZSBBZ2cgYmFja2VuZCBkcmF3cyB0aGUgY2hhcnQgUE5HLiBLYWxlaWRvIGlzIG5vdCBzaGlwcGVkLg=="
      },
      {
        "id": "s9q4",
        "prompt": "Which eval numbers are safe on a résumé, and which sentence has to sit next to them?",
        "choices": [
          {
            "id": "a",
            "text": "Safe to quote any cell, because the deck is a simulation and the disclaimer covers a false comparison."
          },
          {
            "id": "b",
            "text": "Safe: evidence top-1 22/22 on this constructed set, keyword top-1 3/22, fidelity 22/22, and the four drift files where a lot also cleared the bar. Not safe: calling 22/22 a clinical accuracy rate, or a Llama 3.1 versus Llama 3.2 comparison. Those models were not run."
          },
          {
            "id": "c",
            "text": "Safe to quote the keyword ranker's 3 of 22 by itself as the system's accuracy."
          },
          {
            "id": "d",
            "text": "Safe to quote: the model is 100% accurate in the field, because evidence top-1 was 22 of 22."
          }
        ],
        "salt": "21ae2bfc46653180",
        "answerHash": "de4fd5d0622345f320f76f62f3a894e84d275f6b4501098da88b46060afd2638",
        "explain": "UkVTVU1FX0JVTExFVFMubWQgcHV0cyB0aGUga2V5d29yZCBtaXNzIGFuZCB0aGUgZHJpZnQgc2Vjb25kIHN0cmF0dW0gaW4gdGhlIHNhbWUgYnJlYXRoIGFzIDIyLzIyLiBRdW90aW5nIHRoZSBmaXJzdCBudW1iZXIgYWxvbmUgd291bGQgbWlzbGVhZC4gVGhlIGRpc2NsYWltZXIgc3RheXM6IHN5bnRoZXRpYywgbm90IGNsaW5pY2FsLCBub3QgYSBkZXZpY2Uu"
      },
      {
        "id": "s9q5",
        "prompt": "How many slides does write_deck create, and what does a no_single_cause call recommend?",
        "choices": [
          {
            "id": "a",
            "text": "Twelve slides, one for each Jira epic in the build backlog plus the five investigation tasks."
          },
          {
            "id": "b",
            "text": "One slide, and the model writes the title, the cost, and the recommendation into that single frame."
          },
          {
            "id": "c",
            "text": "Seven blank-layout slides: title and disclaimer, summary, impact, root cause, options, recommendation, ask. No single cause recommends not containing a stratum."
          },
          {
            "id": "d",
            "text": "Seven slides, and a no_single_cause call still recommends quarantining the first lot on the file."
          }
        ],
        "salt": "3720eeda6bc40cb3",
        "answerHash": "b6d8dfcc250ff6bedadaa2f20a46534cf72c6a12edf7f7a797a903ad58b26bb7",
        "explain": "QSBzaW5nbGUtY2F1c2UgY2FsbCByZWNvbW1lbmRzIGNvbnRhaW5pbmcgdGhhdCBzdHJhdHVtIGFuZCBub3QgZXhwYW5kaW5nIHRoZSBwdWxsLiBDb2xvcnMgYXJlIG5hdnkgYW5kIHRlYWwsIHdpdGggdGhlIGRpc2NsYWltZXIgaW4gd2hpdGUgb24gbmF2eSBvbiB0aGUgdGl0bGUgc2xpZGUuIFRoZSB0ZXN0IG9wZW5zIHRoZSBwcHR4IGFuZCBjaGVja3Mgc2V2ZW4gc2xpZGVzLCB0aGUgZGlzY2xhaW1lciwgdGhlIHByb2plY3Rpb24gbGFiZWwsIDMuNjclLCBhbmQgTC00NDE5Lg=="
      },
      {
        "id": "s9q6",
        "prompt": "What is the local model default, and what does hosted Streamlit run?",
        "choices": [
          {
            "id": "a",
            "text": "Hosted Streamlit downloads Llama 3.1 8B on every page load and runs that tag for the deck."
          },
          {
            "id": "b",
            "text": "Llama 3.2 1B on Community Cloud writes the deck, which is why the local default is unused."
          },
          {
            "id": "c",
            "text": "LLM_MODEL defaults to llama3.1:8b, Meta Llama 3.1 8B via Ollama. Hosted Streamlit runs rules-only. llama3.2:1b is the small tag for a local or self-hosted run."
          },
          {
            "id": "d",
            "text": "OLLAMA_MODEL and LLM_MODEL are both required, and the hosted page refuses to boot if either is unset."
          }
        ],
        "salt": "ae5cb36718eed753",
        "answerHash": "cbcd45591378fc55ec3102dae6291dd21a016aed63a6031d088224251da1014e",
        "explain": "VGhlIFJFQURNRSBtb2RlbCB0YWJsZSBzYXlzIHRoZSBzYW1lIHRoaW5nLiBHZW1tYSAzIGFuZCBQaGktNCBhcmUgb3RoZXIgZG9jdW1lbnRlZCB0YWdzLiBDbG9zZS1vdXQgaXRzZWxmIGlzIGEgdGVtcGxhdGUgcGx1cyB0aGUgZmlkZWxpdHkgZ3VhcmQuIE5vIG5ldyBtb2RlbCBsaWJyYXJ5Lg=="
      },
      {
        "id": "s9q7",
        "prompt": "What does the week-4 leadership injection on bad_lot ask for, and which ticket is the deck?",
        "choices": [
          {
            "id": "a",
            "text": "A live Slack thread for leadership, which Session 9 ships as the close-out instead of a deck."
          },
          {
            "id": "b",
            "text": "Ticket INV-101, the original PRD, rewritten into slides without a new issue."
          },
          {
            "id": "c",
            "text": "The recommendation and the effectiveness check. The deck is that answer. Ticket INV-303, epic INV-6. No Jira token is required to generate it."
          },
          {
            "id": "d",
            "text": "A fine-tune of the evidence ranker on the 22 scenarios, filed as the week-4 deliverable."
          }
        ],
        "salt": "21d89c3eb0d52b05",
        "answerHash": "8e90ba850a8f18c14075cda0cb3069c4d5791632ef800c4c9bb4246fb3bd3e59",
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
            "text": "Jira is required, and the week-4 demo does not run unless a token is present."
          },
          {
            "id": "c",
            "text": "The model reads the complaint, names the cause, and the investigation is finished."
          },
          {
            "id": "d",
            "text": "This is a medical device with a cleared clinical claim of 22 correct calls out of 22."
          }
        ],
        "salt": "94aec47c194e385b",
        "answerHash": "ba858366cec7e8d4bf3b544a14d13c182cb544d773a1d1822db26747a3fdda27",
        "explain": "VGhlIHBpdGNoIGtlZXBzIHRoZSBkaXNjbGFpbWVyLCB0aGUgZXZpZGVuY2UgYmFyLCB0aGUgaGVycmluZyByZXN1bHQsIGFuZCB0aGUgc2Vjb25kIHN0cmF0dW0uIEl0IGRvZXMgbm90IHR1cm4gdGhlIHNjb3JlY2FyZCBpbnRvIGEgY2xpbmljYWwgY2xhaW0uIFlvdSBjYW4gcnVuIHRoZSBkZXRlcm1pbmlzdGljIHBhdGggd2l0aCBubyBBUEkga2V5Lg=="
      }
    ]
  }
};
