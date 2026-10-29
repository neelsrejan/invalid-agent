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
            "text": "One shared constant keeps the promised validity and the two percent cap from drifting apart."
          },
          {
            "id": "b",
            "text": "The client importer blocks a bare number so the cap has to remain in a calculated custom field."
          },
          {
            "id": "c",
            "text": "Otherwise the interval helper drops its upper bound and the memo can print only a floor."
          },
          {
            "id": "d",
            "text": "The test runner refuses to compare two numeric literals so one of them has to be derived."
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
            "text": "The API token by itself enables the client even when the URL and the email stay blank."
          },
          {
            "id": "b",
            "text": "A base URL plus an email plus a token are all required or the client gate stays false."
          },
          {
            "id": "c",
            "text": "The openFDA key together with the account email opens the client and the token stays optional."
          },
          {
            "id": "d",
            "text": "Setting the project key to INV is the entire switch with or without an email address."
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
            "text": "The test runner is blocked from calling that view so a planted token cannot reach a log."
          },
          {
            "id": "b",
            "text": "It lowercases the model tag so the local runner cannot resolve llama3.1:8b at all."
          },
          {
            "id": "c",
            "text": "The generated view prints every stored field and also includes a planted API token."
          },
          {
            "id": "d",
            "text": "It hides the repository top so tests cannot locate the scenario folders on disk."
          }
        ],
        "salt": "7eeae6e7843514b8",
        "answerHash": "8342474d6b061f1d1d45d1e6e4354d360977e162e1e497f2749fc4267b0f55c9",
        "explain": "QSBwbGFudGVkIHNlY3JldCBpbiB0aGUgdG9rZW4gd291bGQgc2hvdyB1cCBpbiBsb2dzIGlmIHJlcHIgd2VyZSB0aGUgZGVmYXVsdC4gVGhlIG92ZXJyaWRlIHByaW50cyB0aGUgcmVkYWN0ZWQgdmlldyBvbmx5Lg=="
      },
      {
        "id": "s1q4",
        "prompt": "What is docs/jira/backlog.json, compared with the Jira sync added later?",
        "choices": [
          {
            "id": "a",
            "text": "It is the rehearsal record of SIM investigation issues written only after the client is built."
          },
          {
            "id": "b",
            "text": "It is the active customer-escalation board and a following push posts onto those same INV identifiers."
          },
          {
            "id": "c",
            "text": "It is the week-zero triage memo stored as structured data so an escalate flag can be imported."
          },
          {
            "id": "d",
            "text": "It is the three-sprint construction board and sprint 1 holds the issues INV-101 through INV-109."
          }
        ],
        "salt": "88a0929bc0363574",
        "answerHash": "3d585eac6126938425d1f0fbc4ed24ed98d2b8f4306b95e111ecc6d0022e4d83",
        "explain": "VGhpcyBKU09OIGlzIHRoZSB0aHJlZS1zcHJpbnQgYnVpbGQgYm9hcmQuIFNlc3Npb24gNSB3cml0ZXMgYSBkaWZmZXJlbnQgc2V0LCB0aGUgZmljdGlvbmFsIGludmVzdGlnYXRpb24sIGFuZCB0aG9zZSBrZXlzIGFyZSBTSU0tKiBzbyB0aGUgdHdvIGZpbGVzIGNhbm5vdCBiZSBjb25mdXNlZC4="
      },
      {
        "id": "s1q5",
        "prompt": "Why is dependencies an empty list in Session 1 pyproject.toml?",
        "choices": [
          {
            "id": "a",
            "text": "Nothing in this tag imports third-party libraries yet so the job skips those extra downloads."
          },
          {
            "id": "b",
            "text": "The build tool refuses a filled array while the version is still 0.1.0 so the job would fail closed."
          },
          {
            "id": "c",
            "text": "Python 3.11 blocks third-party imports which forces that array to stay vacant on purpose."
          },
          {
            "id": "d",
            "text": "The MIT license forbids third-party libraries and the installer blocks once that array is filled."
          }
        ],
        "salt": "7e3e843c6a8a3b5a",
        "answerHash": "49220412a55943e480e72fbd242c491da6b5a8b54ad5cb4db692dd50f0c5e65c",
        "explain": "TGF0ZXIgc2Vzc2lvbnMgYWRkIGEgbGlicmFyeSBvbmx5IHdoZW4gY29kZSBpbXBvcnRzIGl0LiBUaGUgbG9jYWwgbW9kZWwsIHdoZW4geW91IHdhbnQgb25lLCBpcyBNZXRhIExsYW1hIDMuMSA4QiB2aWEgT2xsYW1hLiBJdCBpcyBub3QgYSBkZXBlbmRlbmN5IGluIHRoaXMgdGFnLg=="
      },
      {
        "id": "s1q6",
        "prompt": "What does find_repo_root look for?",
        "choices": [
          {
            "id": "a",
            "text": "It stops at the first directory named out and treats that folder as proof of the project top."
          },
          {
            "id": "b",
            "text": "It accepts the project file sitting beside the scenarios directory or beside the package directory."
          },
          {
            "id": "c",
            "text": "It searches for an active model server on port 11434 and treats that process as the project top."
          },
          {
            "id": "d",
            "text": "It requires the TOPDIR variable and ignores the project file whenever that variable is missing."
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
            "text": "It resolves to the laptop model because rules means the local model should write the memo."
          },
          {
            "id": "b",
            "text": "It resolves to llamacpp because rules loads a GGUF even when the model path is vacant."
          },
          {
            "id": "c",
            "text": "It resolves to deterministic because rules and rules-only and mock are three names for that engine."
          },
          {
            "id": "d",
            "text": "It raises an error because rules is unrecognized and must not fall through to a silent template."
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
            "text": "Python 3.13 is the sole interpreter and the job injects a client token for the active client."
          },
          {
            "id": "b",
            "text": "The job downloads Llama 3.1 8B and then the dashboard before pytest is allowed to start."
          },
          {
            "id": "c",
            "text": "The hosted app platform replaces the hosted runners for this job and pytest never starts."
          },
          {
            "id": "d",
            "text": "Python 3.11 and 3.12 do an editable install with the dev extra and then pytest with no secrets."
          }
        ],
        "salt": "ac8759af61bd85bb",
        "answerHash": "4ee92197ae0279b570e90476871799309b91b97434467a8b5dd3ddd6f0da9458",
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
            "text": "Stacking two draws raises the complement or double-counts the pattern and replacing it leaves others untouched."
          },
          {
            "id": "b",
            "text": "The scenario document forbids a starting frequency so the only failing rows are the ones on that pattern."
          },
          {
            "id": "c",
            "text": "Two Bernoulli draws cannot share one numeric function so the extra toss has to be applied through SQL."
          },
          {
            "id": "d",
            "text": "Replacing the pattern lets the ranked chart count valid rows which a stacked probability would have dropped."
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
            "text": "It raises because a zero event count makes the denominator undefined and the memo cannot render."
          },
          {
            "id": "b",
            "text": "The analytic lower bound is zero and residue under 1e-12 snaps back to zero before the memo."
          },
          {
            "id": "c",
            "text": "It returns a negative lower bound and the caller clamps that bound back into the unit range before the memo may render."
          },
          {
            "id": "d",
            "text": "It returns the two percent promise as both ends since a sample with no failures is treated as the promise."
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
            "text": "The revision flips when the bad batch starts so the cutover marks the batch rather than the gauge."
          },
          {
            "id": "b",
            "text": "The batch id is copied into the gauge column which is what lines the two effects up."
          },
          {
            "id": "c",
            "text": "Place and gauge and batch and revision and operator are independent so a place is not tied to one gauge."
          },
          {
            "id": "d",
            "text": "Each collection place owns exactly one gauge so the two columns are aliases of one draw."
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
            "text": "Nelson tests 5 through 8 are the only ones used and the usual zone tests on a proportion plot are skipped."
          },
          {
            "id": "b",
            "text": "Only a single weekly point outside the two percent promise is checked and no zone tests run beyond that one comparison."
          },
          {
            "id": "c",
            "text": "A two-sample comparison on every gauge is recomputed from scratch at the end of each day."
          },
          {
            "id": "d",
            "text": "Zones are a point past 3 sigma then 2 of 3 past 2 sigma then 4 of 5 past 1 sigma then 8 on one side."
          }
        ],
        "salt": "f2ef2e7deccd4f1c",
        "answerHash": "e54f24960022ebe6fcbb99d0cea06fcd12f2195787b45bd744a2d65150325751",
        "explain": "VGhleSBydW4gb24gei1zY29yZXMgaW4gdGltZSBvcmRlci4gUnVsZSA0IG5lZWRzIGV2ZXJ5IHogaW4gYSB3aW5kb3cgb2YgOCBzdHJpY3RseSBvbiBvbmUgc2lkZSwgc28gYSBwb2ludCBvbiB0aGUgY2VudGVyIGxpbmUgYnJlYWtzIHRoZSBydW4u"
      },
      {
        "id": "s2q5",
        "prompt": "Where do the Mendeley hemolysis-index rows live in this repo?",
        "choices": [
          {
            "id": "a",
            "text": "They are absent and the seed module holds a lognormal stand-in plus the DOI and the source is only cited."
          },
          {
            "id": "b",
            "text": "They sit inside the week-zero memo as an appendix of raw values taken from that paper."
          },
          {
            "id": "c",
            "text": "The optional fetch module downloads those records on every build and caches them beside the scenario."
          },
          {
            "id": "d",
            "text": "They sit in the hil table copied verbatim from that paper so the builder can sample records instead of a lognormal stand-in."
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
            "text": "A call to the local model invents each record from the scenario title rather than from a seeded draw."
          },
          {
            "id": "b",
            "text": "A document plus a seed is the whole randomness source so one description reprints the field document."
          },
          {
            "id": "c",
            "text": "The interval formula itself is what that helper evaluates in place of a random generator."
          },
          {
            "id": "d",
            "text": "A fresh random sample is drawn on every execution so the printed frequency can be adjusted for the meeting."
          }
        ],
        "salt": "a6700a25f200619a",
        "answerHash": "74e834a50646443fa419f46be74b4d4b2e53b41ea6d630641529262c6e342e41",
        "explain": "Z2VuZXJhdGUgZG9lcyBuID0gaG9yaXpvbiB0aW1lcyBydW5zIHBlciBkYXksIHRoZW4gYmFzZWxpbmUsIHRoZW4gdGhlIGNhdXNlLiBzdW1tYXJpemUgb25seSBmb3JtYXRzIG1ldHJpY3MuIElmIGEgcHJpbnRlZCBudW1iZXIgaXMgd3JvbmcsIHRoZSBidWcgaXMgaW4gdGhlIGdlbmVyYXRvciBvciB0aGUgbWV0cmljcywgbm90IGluIGEgc2VudGVuY2Uu"
      },
      {
        "id": "s2q7",
        "prompt": "What does chi_square_by return when the table has a single level?",
        "choices": [
          {
            "id": "a",
            "text": "The interval of that lone stratum is handed back in place of the statistic."
          },
          {
            "id": "b",
            "text": "It raises ZeroDivisionError because a one-row grid has no complement to compare against."
          },
          {
            "id": "c",
            "text": "The result is probability 1 and statistic 0 because a calm scenario is not treated as an exception."
          },
          {
            "id": "d",
            "text": "The result is a probability of 0 and a huge statistic which forces the memo to escalate on any lone stratum."
          }
        ],
        "salt": "5f9fec985ab3e5d2",
        "answerHash": "5fae69c475991953914c82532e4f646c750eb3cb659abffc9190b69e67f99fac",
        "explain": "T25lIHN0cmF0dW0sIG9yIGEgY29sdW1uIG9mIGFsbCB6ZXJvcywgbWVhbnMgdGhlcmUgaXMgbm8gZXZpZGVuY2Ugb2YgYSBkaWZmZXJlbmNlLiBSZXR1cm5pbmcgcCA9IDEgbGV0cyB0aGUgcmFua2VyIG1vdmUgb24gaW5zdGVhZCBvZiBjcmFzaGluZyB0aGUgbWVtby4="
      },
      {
        "id": "s2q8",
        "prompt": "What does the Pareto exclude?",
        "choices": [
          {
            "id": "a",
            "text": "Any code whose share of failures is under 5 percent is dropped before the cumulative line is drawn."
          },
          {
            "id": "b",
            "text": "Records that belong to the injected batch are left out so the driver code cannot dominate the chart."
          },
          {
            "id": "c",
            "text": "The most common failure code is left out so the chart shows only the long tail of rare codes."
          },
          {
            "id": "d",
            "text": "Valid records are left out because an empty failure code must not count as a failure mode."
          }
        ],
        "salt": "b07fdadfa4b089fc",
        "answerHash": "4da747491769f41a07a1d67b29be30ab773fd2174ada3ca3408f2a51682d3f28",
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
            "text": "Metrics and the catalog and the memo are kept and a following step calls generate again from the same seed."
          },
          {
            "id": "b",
            "text": "It keeps the full grid on the graph state under a key and following steps read that key directly."
          },
          {
            "id": "c",
            "text": "It asks Llama 3.1 8B to remember the grid and a following step prompts the model for the same records."
          },
          {
            "id": "d",
            "text": "It writes the CSV into the issue description and a following step parses that description into records."
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
            "text": "A graph step may hand back only one string so several guesses cannot fit in the state at once."
          },
          {
            "id": "b",
            "text": "Other strata miss a gate such as 80 runs or lift 1.8 or 15 excess failures or probability under 0.01."
          },
          {
            "id": "c",
            "text": "Stakeholder remarks outvote every stratum except the batch which is why only L-4419 remains on the page."
          },
          {
            "id": "d",
            "text": "The memo has room for one guess sentence so extra strata are dropped while the text is formatted."
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
            "text": "The local model rewrites the line into the template before the guard ever scans the digits."
          },
          {
            "id": "b",
            "text": "Masking deletes 27.40 because that token looks like the batch id with the letters removed."
          },
          {
            "id": "c",
            "text": "It survives masking and is not within 0.03 of a walked fact so it lands in unknown and ok stays false."
          },
          {
            "id": "d",
            "text": "The guard accepts 27.40 because 27 sits close to the investigation lap number stored beside the facts."
          }
        ],
        "salt": "8aac7c13409ac90b",
        "answerHash": "ce38f801b7de07dcf99146fb52e33898ca248cbdaf8f8ae07df9045b5a163b45",
        "explain": "SWRlbnRpZmllcnMgc3VjaCBhcyBMLTQ0MTkgYXJlIHN0cmlwcGVkIG9ubHkgd2hlbiB0aGF0IGV4YWN0IHN0cmluZyBpcyBpbiB0aGUgZmFjdHMuIDI3LjQwIGlzIG5vdCBvbmUgb2YgdGhlbS4gMy42NyBpcyBhbGxvd2VkIGJlY2F1c2UgdGhlIHN0b3JlZCByYXRlIDAuMDM2NyBjb250cmlidXRlcyBpdHMgcGVyY2VudCBmb3JtLg=="
      },
      {
        "id": "s3q4",
        "prompt": "What happens if the Ollama backend is selected and the process cannot reach it?",
        "choices": [
          {
            "id": "a",
            "text": "The rejected draft is saved beside the memo with a warning banner and the bad number left intact."
          },
          {
            "id": "b",
            "text": "The memo document is left blank so a reviewer can see that the model call failed outright."
          },
          {
            "id": "c",
            "text": "The program exits and deletes the opening memo so a failed draft cannot be mistaken for the finished text."
          },
          {
            "id": "d",
            "text": "The narrator catches the exception and hands back the template without saving the failed draft."
          }
        ],
        "salt": "0fc9ec0466f832cb",
        "answerHash": "adc07f255476f50bb6f4968426be1f84a7b378c1d61ff202414196134e80d3ba",
        "explain": "VGhlIHRlbXBsYXRlIGlzIHJlbmRlcmVkIGZpcnN0LiBEZXRlcm1pbmlzdGljIG1vZGUgcmV0dXJucyBpdCBhZnRlciBhIGNoZWNrLiBBbnkgb3RoZXIgYmFja2VuZCB0aGF0IGVycm9ycywgcmV0dXJucyBlbXB0eSB0ZXh0LCBvciBmYWlscyB0aGUgZ3VhcmQgaXMgcmVwbGFjZWQuIEEgYnJva2VuIHRlbXBsYXRlIGlzIGEgYnVnIGFuZCByYWlzZXMu"
      },
      {
        "id": "s3q5",
        "prompt": "Why does rank_hypotheses ignore stakeholder injections?",
        "choices": [
          {
            "id": "a",
            "text": "A driver has to come from the grid because a QA line does not get a vote on the ordering."
          },
          {
            "id": "b",
            "text": "The framework refuses string fields so a remark cannot enter the ordering function at all."
          },
          {
            "id": "c",
            "text": "The scenario description has no such array yet so the ordering step has nothing to read."
          },
          {
            "id": "d",
            "text": "Those remarks are appended as extra field records before the statistic so a QA line can outrank a stratum."
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
            "text": "It switches the model name to llama3.2:1b and still writes the opening memo afterward."
          },
          {
            "id": "b",
            "text": "It stops on purpose so this snapshot cannot pretend the weekly loop already exists."
          },
          {
            "id": "c",
            "text": "It runs the full multi-lap loop and writes a schedule and a diagram and a deck in one pass."
          },
          {
            "id": "d",
            "text": "It skips the opening step and writes only the diagram using remarks as the guess."
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
            "text": "The job downloads model weights through httpx during pytest so the adapter has to be that library."
          },
          {
            "id": "b",
            "text": "The graph requires an httpx call inside every step including the path that never leaves the laptop."
          },
          {
            "id": "c",
            "text": "One httpx call is easier to mock and that call is skipped when the engine is deterministic."
          },
          {
            "id": "d",
            "text": "httpx is the sole client that can speak to a Llama 3.1 server so any other adapter is skipped."
          }
        ],
        "salt": "87adf0c5fd9f6348",
        "answerHash": "dc7b1f05638e5ffebd6fd3851e6eb7eab46e0bc8ef6aad6f36ec9c273c3a5c8d",
        "explain": "bGFuZ2NoYWluLWNvcmUgb25seSBzdXBwbGllcyB0aGUgcm9sZSBhbmQgY29udGVudCBwYWlycy4gbGxhbWEtY3BwLXB5dGhvbiBpcyBub3QgYSBkZXBlbmRlbmN5LiBJdCBpcyBpbXBvcnRlZCBvbmx5IGlmIHRoYXQgYmFja2VuZCBpcyBzZWxlY3RlZCwgYW5kIGEgbWlzc2luZyBpbnN0YWxsIGZhbGxzIGJhY2sgdG8gdGhlIHRlbXBsYXRlLg=="
      },
      {
        "id": "s3q8",
        "prompt": "Why are lot ids removed from the narrative instead of added to the numeric allow-list?",
        "choices": [
          {
            "id": "a",
            "text": "A schema model cannot hold strings and a batch id has to be coerced to a float before storage."
          },
          {
            "id": "b",
            "text": "The interval formula blocks integers and 4419 would otherwise break the computed bound."
          },
          {
            "id": "c",
            "text": "The scanner finishes faster on a one-page memo by skipping identifier-shaped tokens on the way through."
          },
          {
            "id": "d",
            "text": "Removing the identifier keeps 4419 from being reused as a permitted frequency in the paragraph."
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
            "text": "An empty bone scored at zero says that category was considered on the diagram reviewers expect."
          },
          {
            "id": "b",
            "text": "That category is hard-coded to position 1 so a quality diagram always leads with the gauge."
          },
          {
            "id": "c",
            "text": "The schema blocks a diagram object that has fewer than six filled bones whether or not they are empty."
          },
          {
            "id": "d",
            "text": "A remark that names a gauge forces the bone to carry a score even when no gauge column exists."
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
            "text": "Any item whose answer is under 200 characters is refused and that happens only after the markdown document already exists."
          },
          {
            "id": "b",
            "text": "An empty citation array or an unknown id is refused inside the builder before any markdown exists."
          },
          {
            "id": "c",
            "text": "A diagram whose top score is zero is refused and the check is skipped entirely on a laptop."
          },
          {
            "id": "d",
            "text": "A citation of the overall frequency metric is banned from an item even when the catalog already contains it."
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
            "text": "Yes but only when that remark is attached to the gauge bone rather than to material."
          },
          {
            "id": "b",
            "text": "Yes because every scenario entry is visible from the opening lap including the batch remark."
          },
          {
            "id": "c",
            "text": "No because entries are kept only through the case lap and that QA remark belongs to lap 1."
          },
          {
            "id": "d",
            "text": "No because QA remarks are dropped from the catalog permanently whatever lap the case has reached."
          }
        ],
        "salt": "d02672bcc70a5833",
        "answerHash": "5b0c70ce0f3df9b829e998367e2294c9cac99c6ec7f3f61ab7fb60c6b7335d94",
        "explain": "QXQgd2VlayAxIHRoZSBub3RlIGJlY29tZXMgY2l0YWJsZSwgd2l0aCBhbiBpZCBsaWtlIGluamVjdGlvbjoxOnFhLiBjYXRhbG9nLnVwZGF0ZShpbmplY3Rpb25zKSBpcyB3aGF0IG1ha2VzIHRoYXQgaWQgbGVnYWwuIEJlZm9yZSB0aGF0IGxpbmUsIHZhbGlkYXRlX3doeXMgd291bGQgcmVqZWN0IGl0Lg=="
      },
      {
        "id": "s4q4",
        "prompt": "What is the effectiveness metric in D6, and why does the record not claim the rate already recovered?",
        "choices": [
          {
            "id": "a",
            "text": "A customer-satisfaction score the model invents is the number that gets quoted and recovery is stated in that section."
          },
          {
            "id": "b",
            "text": "A fresh chi-square the language model computes replaces the proportion plot as the success test."
          },
          {
            "id": "c",
            "text": "The batch is treated as cured because the last section is closed and a healed frequency is quoted."
          },
          {
            "id": "d",
            "text": "The target is a return to the promise with no zone-1 point because follow-up runs do not exist yet."
          }
        ],
        "salt": "449c20a72f81b969",
        "answerHash": "a8048f939d0e7be00ac755b9cb35f475a9446c6b65e0f35834c70be5818667f2",
        "explain": "RDcgYW5kIEQ4IGFyZSB3cml0dGVuIGFuZCBtYXJrZWQgcHJlbGltaW5hcnkuIFRoZSBDQVBBIHNheXMgc28sIHNvIGEgcmVhZGVyIGRvZXMgbm90IHRoaW5rIHRoZSBpbnZlc3RpZ2F0aW9uIGlzIGFscmVhZHkgY2xvc2VkLiBUaGUgd29yZCBydWxlLTEga2VlcHMgdGhhdCBkaWdpdCBnbHVlZCB0byBhIGh5cGhlbiBmb3IgdGhlIGZpZGVsaXR5IHNjYW5uZXIu"
      },
      {
        "id": "s4q5",
        "prompt": "Where do DMAIC labels sit relative to the eight Ds?",
        "choices": [
          {
            "id": "a",
            "text": "Define maps to the opening pair and measure to the metrics and analyze to the contrast and the diagram."
          },
          {
            "id": "b",
            "text": "Each of the 8 sections is its own full cycle so the memo contains 8 separate full cycles from end to end."
          },
          {
            "id": "c",
            "text": "Those names appear only as a slide title in the final deck and are absent from this memo."
          },
          {
            "id": "d",
            "text": "Those names replace the three middle sections and the other headings are removed from the document."
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
            "text": "The gauge category comes first because an empty bone sorts ahead of every scored branch on the diagram."
          },
          {
            "id": "b",
            "text": "Material and the bad reagent batch come first and the fifth answer names L-4419 in the catalog line."
          },
          {
            "id": "c",
            "text": "Method and a software driver come first and the fifth answer is required to name version 2.4.0 as the stop."
          },
          {
            "id": "d",
            "text": "The unclear-driver label comes first and the fifth answer invents L-4419 without a scored bone."
          }
        ],
        "salt": "3f3a9a31af48a4e2",
        "answerHash": "3efecb62ef3827334e73e908055bcb332d55c9b0ef959a7ad0ac48bb59da01d3",
        "explain": "VGhlIHNvcnQgaXMgYnkgZGVzY2VuZGluZyBzY29yZS4gVGhlIGxvdCBpcyB0aGUgb25seSBub24temVybyBzY29yZS4gSGVtb2x5c2lzIGlzIGFsc28gTWF0ZXJpYWwgYW5kIHN0YXlzIGF0IDAgdW5kZXIgaXQuIG5vX3NpbmdsZV9jYXVzZSBpcyBub3QgYSBib25lLg=="
      },
      {
        "id": "s4q7",
        "prompt": "What does step 3 of the 5 Whys have to cite?",
        "choices": [
          {
            "id": "a",
            "text": "Whatever line the model prefers is accepted and a missing catalog id is only a warning."
          },
          {
            "id": "b",
            "text": "The client API token has to be quoted in that answer before any stratum contrast is allowed."
          },
          {
            "id": "c",
            "text": "A different column is required so the chain can show why the next stratum is not the driver."
          },
          {
            "id": "d",
            "text": "The same catalog line the previous answer already used is pasted again so the chain looks longer."
          }
        ],
        "salt": "6eb0462f25d2fd76",
        "answerHash": "22b149c105d650695e10d76a27982f33abae6d06ab7b623f672be60d2ec068cf",
        "explain": "U3RlcCAxIGlzIG92ZXJhbGwgdmVyc3VzIHNwZWMuIFN0ZXAgMiBpcyB0aGUgd2lubmluZyBzdHJhdHVtLiBTdGVwIDMgaXMgdGhlIGNvbnRyYXN0LiBTdGVwIDQgY2l0ZXMgYW4gaW5qZWN0aW9uIHRoYXQgbmFtZXMgdGhlIGxldmVsLCBvciB0aGUgc3RyYXR1bSdzIG4gc2VudGVuY2Ugd2hlbiBubyBpbmplY3Rpb24gaGFzIGFycml2ZWQu"
      },
      {
        "id": "s4q8",
        "prompt": "Which new package does Session 4 add?",
        "choices": [
          {
            "id": "a",
            "text": "A tiny local model is added and the job downloads it before the diagram check is allowed to execute."
          },
          {
            "id": "b",
            "text": "A diagram drawing library is added so the six bones can be rendered as an image beside the markdown."
          },
          {
            "id": "c",
            "text": "An export helper is added so the record can be saved as a PDF from the chart figure."
          },
          {
            "id": "d",
            "text": "No new library is added and the prior fidelity guard is reused on the three markdown documents."
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
            "text": "The export helper needs an extra browser library while the plotting path runs without that download."
          },
          {
            "id": "b",
            "text": "The client blocks an attachment unless the extra browser library produced it so the plotting chart cannot be attached."
          },
          {
            "id": "c",
            "text": "Picture files are banned from the tree which is why that export helper is never called on the schedule."
          },
          {
            "id": "d",
            "text": "The chart library has no timeline trace so a schedule chart has to be drawn by hand in another tool."
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
            "text": "Stamps are compared as month-day-year text which is why an ISO value would sort into the wrong place."
          },
          {
            "id": "b",
            "text": "A task opening must follow the predecessor closing and year-month-day stamps sort in calendar order."
          },
          {
            "id": "c",
            "text": "Predecessor links are comments inside the task record and the check that would inspect them is never called."
          },
          {
            "id": "d",
            "text": "A task may open the day before its predecessor closes which is how overlap gets onto the chart."
          }
        ],
        "salt": "1fd73dfa8ef8435f",
        "answerHash": "4ed06174e77e96c78411832c61ec424e0173955f532ed94059795685dee75a3a",
        "explain": "VGhlIGVuZCBpcyBleGNsdXNpdmU6IHN0YXJ0IHBsdXMgZGF5cy4gVGhlIHRlc3Qgd2Fsa3MgVDgsIHdoaWNoIHN0YXJ0cyB3aGVuIFQ2IGVuZHMsIGluc3RlYWQgb2YgdHJ1c3RpbmcgYSBjb21tZW50LiBBIGhhbmQtZWRpdGVkIGVhcmx5IHN0YXJ0IHJhaXNlcy4="
      },
      {
        "id": "s5q3",
        "prompt": "What changes between week 0 and week 2 on the Gantt and the risk register?",
        "choices": [
          {
            "id": "a",
            "text": "The disagreement hazard is removed on the second lap because release testing has already passed in the field."
          },
          {
            "id": "b",
            "text": "The bars stay identical across those laps and only the memo title text is different."
          },
          {
            "id": "c",
            "text": "The second lap adds the lab-director task and the first hazard moves down while another hazard moves up."
          },
          {
            "id": "d",
            "text": "Every baseline task is deleted on the second lap and replaced by the lab-director set alone."
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
            "text": "The epic identifier is copied from the scenario id and that id is the text SIM."
          },
          {
            "id": "b",
            "text": "A SIM prefix means the active site accepted the issue and then returned that identifier to the client."
          },
          {
            "id": "c",
            "text": "The hosted client blocks every project prefix except SIM so INV cannot be used in a rehearsal."
          },
          {
            "id": "d",
            "text": "The construction board uses INV identifiers and SIM makes a rehearsal document obviously different."
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
            "text": "The client catches the failure and stores the exception class and saves the file without the token."
          },
          {
            "id": "b",
            "text": "The client retries the post forever and the document is saved only after a success comes back."
          },
          {
            "id": "c",
            "text": "The API token is placed into the error text so the reader can see which credential failed."
          },
          {
            "id": "d",
            "text": "The program deletes the schedule document because a failed push means the schedule is no longer valid."
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
            "text": "A deletion is sent against every SIM identifier so the repeat pass clears the board before rebuilding it."
          },
          {
            "id": "b",
            "text": "The repeat pass makes no further posts because a known task id is edited in place after the first pass."
          },
          {
            "id": "c",
            "text": "Eleven additional posts are made one per task on every pass including the repeat pass."
          },
          {
            "id": "d",
            "text": "One post is sent whose body is the entire schedule instead of an epic plus separate stories."
          }
        ],
        "salt": "54f918147ac804c9",
        "answerHash": "cfee1bc1c7df628ea3622a0ad61f075f8f7b4148616b6642578134eefa48ee47",
        "explain": "VGhlIGZpcnN0IGNhbGwgaXMgMTEgcG9zdHM6IGVwaWMgcGx1cyAxMCB0YXNrcyBhdCB3ZWVrIDAuIFRoZSBieV90YXNrIG1hcCBza2lwcyBjcmVhdG9yIHdoZW4gdGhlIGlkIGV4aXN0cyBhbmQgc3RpbGwgcmVmcmVzaGVzIHN1bW1hcnksIHN0YXR1cywgYW5kIG93bmVyLiBEZXNjcmlwdGlvbnMgdXNlIEppcmEncyBkb2N1bWVudCBmb3JtYXQgYmVjYXVzZSBBUEkgdjMgcmVqZWN0cyBhIHBsYWluIHN0cmluZy4="
      },
      {
        "id": "s5q7",
        "prompt": "Why does plan run after triage and not after the fishbone?",
        "choices": [
          {
            "id": "a",
            "text": "A client project must already exist before any failure frequency is calculated from the grid."
          },
          {
            "id": "b",
            "text": "The bar dates are an input to the guess ordering so the scheduler has to finish before any stratum is scored."
          },
          {
            "id": "c",
            "text": "The scheduler reads the top guess only and the diagram step neither reads nor writes that schedule."
          },
          {
            "id": "d",
            "text": "The graph sorts step names alphabetically which places the scheduler behind the diagram step."
          }
        ],
        "salt": "ba424e0ed43edd12",
        "answerHash": "6e6f34aa83f9512b2669dd6203a5f73105785d08c63cf8b646986df54ebb059b",
        "explain": "VGhlIG9yZGVyIGlzIHRyaWFnZSwgcGxhbiwgcmNhLCBFTkQuIHJ1bl9jYXNlIGNyZWF0ZXMgdGhlIG91dHB1dCBkaXJlY3RvcnkgYmVmb3JlIGludm9rZSwgYmVjYXVzZSB0aGUgcGxhbiBub2RlIHdyaXRlcyBmaWxlcyBkdXJpbmcgdGhlIG5vZGUgdXNpbmcgc3RhdGUgb3V0X2Rpci4="
      },
      {
        "id": "s5q8",
        "prompt": "Who owns containment when the top cause is a lot, an instrument, or no single cause?",
        "choices": [
          {
            "id": "a",
            "text": "Every task including the first response is owned by the language model rather than by a named function."
          },
          {
            "id": "b",
            "text": "The customer holds the first response for a batch and for a gauge and for a case with no clear driver."
          },
          {
            "id": "c",
            "text": "The client assigns a random holder whenever the issue identifier starts with SIM."
          },
          {
            "id": "d",
            "text": "Quality holds a batch and manufacturing a gauge and development the code while an unclear driver stays."
          }
        ],
        "salt": "2f3a78be0caab485",
        "answerHash": "9e5df0b1b477f87ed045f5a7229bbb3cb088471ef3fde8177be9c5c44859ece6",
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
            "text": "The field document is fixed by the seed so the pass re-enters at the scheduler."
          },
          {
            "id": "b",
            "text": "The graph allows only one step in a program so the opening step cannot be entered a second time."
          },
          {
            "id": "c",
            "text": "The customer remark overwrites the metrics so another opening pass would have nothing left to read."
          },
          {
            "id": "d",
            "text": "The opening step is deleted from the graph once the scheduler exists which is why later passes skip it."
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
            "text": "Healthy is reserved for a successful model call and the second lap does not invoke a model at all."
          },
          {
            "id": "b",
            "text": "Frequency stays over the promise and containment waits so the second lap stays urgent and nothing is cured."
          },
          {
            "id": "c",
            "text": "The second lap turns healthy because release testing passed and the document is then marked cured."
          },
          {
            "id": "d",
            "text": "A retrieval index is what the color names and urgent means that index missed the batch remark."
          }
        ],
        "salt": "0e31370362844a87",
        "answerHash": "cca9c88d3e74a00c0008f6cfa6cf8e9bb4c2d8cdaf4b808e3b0e2f370f294e78",
        "explain": "SW4gdGhpcyBwcm9qZWN0IFJBRyBpcyB0aGUgUmVkIC8gQW1iZXIgLyBHcmVlbiBzdGF0dXMgY29sb3IsIG5vdCByZXRyaWV2YWwtYXVnbWVudGVkIGdlbmVyYXRpb24uIHJhZ19jb2xvciByZXR1cm5zIEdyZWVuIG9ubHkgd2hlbiB0aGUgcmF0ZSBkb2VzIG5vdCBleGNlZWQgdGhlIHNwZWMu"
      },
      {
        "id": "s6q3",
        "prompt": "What does the decision log record at week 2?",
        "choices": [
          {
            "id": "a",
            "text": "Close the final section and ship the executive deck at the end of the second lap."
          },
          {
            "id": "b",
            "text": "Delete the first task because its simulation lap has already passed and the row is stale."
          },
          {
            "id": "c",
            "text": "Keep the field ordering after a reported release pass and add the lab-director remark to the schedule."
          },
          {
            "id": "d",
            "text": "Switch the leading driver to software because the release remark passed and the grid should follow it."
          }
        ],
        "salt": "267f892434654159",
        "answerHash": "0fa87c1669e4aba17c2a1a87b5435d9c80f75e52b2857482d984d7a97cf9fc17",
        "explain": "V2VlayAxJ3Mgcm93IHNheXMgdGhlIFFBIG5vdGUgaXMgYSBjaXRhdGlvbiBhbmQgZG9lcyBub3QgZ2V0IGl0cyBvd24gc2NvcmUuIFdlZWsgMyBzYXlzIGRvIG5vdCBzd2l0Y2ggdGhlIGNhdXNlIG9udG8gdGhlIHNoaXBwaW5nIG5vdGUuIE9uZSByb3cgcGVyIHdlZWsgaXMgdGhlIGRpZmYgYSBQTSB3b3VsZCBzaG93Lg=="
      },
      {
        "id": "s6q4",
        "prompt": "How can the customer note mention a rate without the template doing arithmetic?",
        "choices": [
          {
            "id": "a",
            "text": "The small local model types the percent on the hosted screen and the wording pastes that text unchanged."
          },
          {
            "id": "b",
            "text": "The percent is copied from the complaint line which is why no calculation runs inside the wording."
          },
          {
            "id": "c",
            "text": "The wording multiplies failures by 100 and divides by the row count inside the formatted text itself."
          },
          {
            "id": "d",
            "text": "The facts builder rounds frequency onto a percent field and the wording inserts that field for the guard."
          }
        ],
        "salt": "666a134f18becf06",
        "answerHash": "77f770c99ea7da6748d2c74a843b5fea3c134e51cc005f19508aefcee7c7e70b",
        "explain": "VGhlIHRocmVlIGF1ZGllbmNlIHRlbXBsYXRlcyBzaGFyZSBfc3RhdHVzX2hlYWRlciwgc28gdGhlIHJhdGUgbGluZSBjYW5ub3QgZHJpZnQuIENvc3QgaXMgaW52YWxpZHMgdGltZXMgdGhlIHVuaXQgcHJpY2UsIGFuZCBib3RoIGZhY3RvcnMgc2l0IG9uIHRoZSBmYWN0cyBiZWZvcmUgYW55IHNlbnRlbmNlIGlzIHJlbmRlcmVkLg=="
      },
      {
        "id": "s6q5",
        "prompt": "Where do you look to diff week 0 and week 2 without re-running anything?",
        "choices": [
          {
            "id": "a",
            "text": "Compare the opening folder with the second because each is as of that lap and the top copy is newest."
          },
          {
            "id": "b",
            "text": "Compare the earlier tag with the following tag which is the opening versus second-lap schedule a reviewer would quote."
          },
          {
            "id": "c",
            "text": "Use only the final client document which keeps a copy of every lap schedule inside one document."
          },
          {
            "id": "d",
            "text": "Use the screen cache which stores each lap schedule under the audience selector key."
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
            "text": "It must include the client API token so the recipient can comment on the SIM issue directly."
          },
          {
            "id": "b",
            "text": "It must not state a confirmed driver and internal text gets the guess while leadership gets the cost."
          },
          {
            "id": "c",
            "text": "It must quote a different failure frequency from the one printed on the leadership version."
          },
          {
            "id": "d",
            "text": "It must name the batch and quote the chi-square probability and paste the five answers before the holding line."
          }
        ],
        "salt": "18033037414f7c25",
        "answerHash": "af819f5cc804b8589cb70ac6db844bb7553369e850de513f086e6482a88dc0c4",
        "explain": "SW50ZXJuYWwgcGFzdGVzIGluamVjdGlvbiB0ZXh0IHZlcmJhdGltIHNvIHRoZSBndWFyZCBjYW4gbWFzayBpdC4gVGhlIGN1c3RvbWVyIGFjdGlvbiBpcyBhIGhvbGRpbmcgc2VudGVuY2UuIFRoYXQgc3BsaXQgaXMgdGhlIHN0YWtlaG9sZGVyIHNraWxsIHRoZSBzZXNzaW9uIGlzIHByYWN0aWNpbmcu"
      },
      {
        "id": "s6q7",
        "prompt": "At the end of a week-3 run, which tasks are Done?",
        "choices": [
          {
            "id": "a",
            "text": "Finished is applied only by an active client transition and a rehearsal document leaves every task open."
          },
          {
            "id": "b",
            "text": "Every task stays in progress until the final deck is written including the earliest task on the schedule."
          },
          {
            "id": "c",
            "text": "Integer comparison marks the lap-0 task finished and the lap-2 task finished while the lap-4 task stays open."
          },
          {
            "id": "d",
            "text": "The lap-2 task does not exist yet at the end of lap 3 so only the earliest task can be finished."
          }
        ],
        "salt": "ebe74b486508e880",
        "answerHash": "58a6a85c026b4afe63fa699b9d8fb3a4f35df8373a47e5a89458128688ae94c2",
        "explain": "VGhlIGRyeS1ydW4gdXBzZXJ0IGZyb20gU2Vzc2lvbiA1IHJlZnJlc2hlcyBzdGF0dXMgaW4gcGxhY2UuIFRoZSBmaWxlIGF0IHRoZSBlbmQgb2Ygd2VlayAzIHNob3dzIHRoZSB0YXNrcyB3aG9zZSB3ZWVrIGhhcyBwYXNzZWQgYXMgRG9uZS4gTm8gdG9rZW4gaXMgcmVxdWlyZWQu"
      },
      {
        "id": "s6q8",
        "prompt": "What does route_after_status return when the week that just finished is still below the target?",
        "choices": [
          {
            "id": "a",
            "text": "The result is stop on every pass so the lap counter does not move at all."
          },
          {
            "id": "b",
            "text": "The result is the opening step and the field document is redrawn from a new seed."
          },
          {
            "id": "c",
            "text": "The result is the final wrap-up as soon as the first lap ends and the deck is written early."
          },
          {
            "id": "d",
            "text": "The result is advance which adds one to the lap and then edges back to the scheduler."
          }
        ],
        "salt": "2bd81e211dd86782",
        "answerHash": "94f1ed30d38144dd09c60ffbdc3dd5015070456a2c90fe754149e63130500f7e",
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
            "text": "The cloud app has no local runner and ships no weights so deterministic wording answers with no download."
          },
          {
            "id": "b",
            "text": "The chart library cannot draw a proportion plot while a model is loaded so the deterministic path is what keeps the chart alive."
          },
          {
            "id": "c",
            "text": "The screen raises unless the engine is the local runner and the deterministic flag is how that engine gets chosen."
          },
          {
            "id": "d",
            "text": "The job host serves the screen and forbids the language runtime so the screen has to stay on deterministic wording."
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
            "text": "There is no model name and with the toggle cleared the screen picks a model tag at random."
          },
          {
            "id": "b",
            "text": "LLM_MODEL wins when set and otherwise a local run asks for llama3.2:1b while commands stay on llama3.1:8b."
          },
          {
            "id": "c",
            "text": "The model name OLLAMA_MODEL overrides the other name and an absent value on the cloud screen downloads llama3.1:8b."
          },
          {
            "id": "d",
            "text": "The cloud screen always downloads Llama 3.1 8B and the toggle cannot change that model tag."
          }
        ],
        "salt": "7acc16b44f33dcb2",
        "answerHash": "3f5a1e63c8b1ebc9350c134499bf5aa48ecfa79b075437e62da50d768fa3baf2",
        "explain": "SE9TVEVEX0xMTV9NT0RFTCBpcyB0aGUgc21hbGwgdGFnLCBMbGFtYSAzLjIgMUIuIEl0IGlzIHdoYXQgdGhlIHRvZ2dsZSBhc2tzIGZvciBsb2NhbGx5LiBDb21tdW5pdHkgQ2xvdWQgc3RheXMgb24gdGhlIHJ1bGVzLW9ubHkgZGVmYXVsdCBiZWNhdXNlIENsb3VkIGNhbm5vdCBydW4gT2xsYW1hLiBHZW1tYSAzIGFuZCBQaGktNCBhcmUgb3RoZXIgdGFncyB5b3UgY2FuIHNldCB5b3Vyc2VsZi4="
      },
      {
        "id": "s7q3",
        "prompt": "Why does the before/after chart say the after series is not observed follow-up?",
        "choices": [
          {
            "id": "a",
            "text": "The later bars are a screenshot the recipient sent and then pasted on as watched results."
          },
          {
            "id": "b",
            "text": "The later bars are next-month complaints collected once the batch was quarantined in the field."
          },
          {
            "id": "c",
            "text": "Failures on the leading stratum of the same synthetic document are cleared and no new field data are collected."
          },
          {
            "id": "d",
            "text": "The plotting library simulates a cured program and rewrites the scenario document with the new frequency."
          }
        ],
        "salt": "e0bdbe9e62bf59fc",
        "answerHash": "3d2ddfb135232243b22aa53128ffb54b2c6cb670dd53086d67bccba5f87131dd",
        "explain": "VGhlIGZ1bmN0aW9uIGNvcGllcyB0aGUgZnJhbWUgYW5kIHJldHVybnMgYmVmb3JlL2FmdGVyIHJhdGVzLiBJdCBkb2VzIG5vdCByZXdyaXRlIHRoZSBzY2VuYXJpbyBmaWxlLiBiYWRfbG90IHN0YXlzIG92ZXIgc3BlYyBpbiB0aGUgb2JzZXJ2ZWQgc2VyaWVzLiBUaGUgY2FwdGlvbiByZXBlYXRzIHRoZSBwcm9qZWN0aW9uIGxhYmVsLg=="
      },
      {
        "id": "s7q4",
        "prompt": "What is cached, and what is not recomputed when you only change the audience radio?",
        "choices": [
          {
            "id": "a",
            "text": "Every selector click rebuilds the whole graph and ignores the stored result from the previous execution."
          },
          {
            "id": "b",
            "text": "The storage key is only the selector name so a new lap still serves the previous execution from memory."
          },
          {
            "id": "c",
            "text": "Nothing is stored because the framework forbids that decorator on a cloud app of this kind."
          },
          {
            "id": "d",
            "text": "The cache key covers scenario and lap and engine and model while the selector only rereads stored text."
          }
        ],
        "salt": "b22b1bb5615bd234",
        "answerHash": "cf41ba2dda45ccdccf9cb3b94ae68fb1b802346ae09b1422dedc2e95659c55e6",
        "explain": "X3J1biByZXN0b3JlcyB0aGUgZW52aXJvbm1lbnQgaW4gYSBmaW5hbGx5IGJsb2NrIHNvIGEgY2FjaGVkIGNhbGwgY2Fubm90IHBpbiBhIG1vZGVsIGZvciB0aGUgbmV4dCBDTEkgY29tbWFuZCBpbiB0aGUgc2FtZSBwcm9jZXNzLiBTd2l0Y2hpbmcgdGFicyBkb2VzIG5vdCBjYWxsIHJ1bl9jYXNlIGFnYWluLg=="
      },
      {
        "id": "s7q5",
        "prompt": "What does Neel still have to do before a public Streamlit URL exists?",
        "choices": [
          {
            "id": "a",
            "text": "Sign in on the cloud host with the code host and pick the app entry because the tree cannot do it."
          },
          {
            "id": "b",
            "text": "Nothing further is required because this snapshot already published the address and the tree contains that link."
          },
          {
            "id": "c",
            "text": "Commit a client API token so the cloud host can start a local model runner for the screen."
          },
          {
            "id": "d",
            "text": "Buy a charting license which is the gate the cloud host checks before the first deploy is allowed."
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
            "text": "The figure is a static picture embedded by an export helper and the alarm hue is only the chart border."
          },
          {
            "id": "b",
            "text": "Navy 0B3A5B and teal 1F7A8C draw the line and B23A48 marks zone-1 points with no purple gradient."
          },
          {
            "id": "c",
            "text": "A random palette gives one hue per functional owner and there is no fixed alarm hue for the zone-1 points."
          },
          {
            "id": "d",
            "text": "The alarm hue marks the projected bars and navy marks a model token sitting in the screen state."
          }
        ],
        "salt": "ba7dce9e8a01664a",
        "answerHash": "b9ac2aac7c1794c011f6c1b12a389c09892a49a2ad4a4ad45f067aca481d4afe",
        "explain": "Y2hhcnRzLnB5IHJlYWRzIHRoZSBwLWNoYXJ0IGRpY3QgYW5kIHRoZSBQYXJldG8gZGljdCB0aGUgZ3JhcGggYWxyZWFkeSBjb21wdXRlZC4gVGhlIHN0YXRpYyBQTkcgcGF0aCBmb3Igc2xpZGVzIHN0YXlzIG9uIG1hdHBsb3RsaWIgYmVjYXVzZSBQbG90bHkncyBleHBvcnQgbmVlZHMgS2FsZWlkbywgd2hpY2ggaXMgbm90IHNoaXBwZWQu"
      },
      {
        "id": "s7q7",
        "prompt": "What does requirements.txt deliberately leave out?",
        "choices": [
          {
            "id": "a",
            "text": "The chart library is omitted because the cloud screen draws every chart with matplotlib alone."
          },
          {
            "id": "b",
            "text": "The app framework itself is omitted so the cloud host is expected to serve the screen with another toolkit."
          },
          {
            "id": "c",
            "text": "A weight file stays out while data and graph and chart libraries and the app framework stay installed."
          },
          {
            "id": "d",
            "text": "The test runner is omitted and the cloud host needs it in the install array before the app will boot."
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
            "text": "Flipping the selector changes the failure frequency shown on the metric tile."
          },
          {
            "id": "b",
            "text": "An active browser click is required and the job performs that click against the cloud host on every pull request."
          },
          {
            "id": "c",
            "text": "The screen downloads llama3.1:8b during the render check and fails closed if that weight is missing."
          },
          {
            "id": "d",
            "text": "The screen shows the clinical-use banner and a metric and dropping the bad batch lowers the projection."
          }
        ],
        "salt": "b93a90e8549423f0",
        "answerHash": "6f0c2ea554e7cda4bc7c60790e9bec877af462506d9dd5f7106bd7a3dfa980b3",
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
            "text": "The table hit 22 of 22 for top choice and top three while notes hit 3 of 22 with no driver named."
          },
          {
            "id": "b",
            "text": "Both approaches were perfect on all 22 documents so an opening remark is as accurate as the table."
          },
          {
            "id": "c",
            "text": "The memo stores no counts and the perfect cell is typed into the opening readme by hand."
          },
          {
            "id": "d",
            "text": "The table ordering hit 3 of 22 and the note ordering hit 22 of 22 on the same documents."
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
            "text": "The table ordering is mistaken on that scenario and the note ordering is the number a reader should quote."
          },
          {
            "id": "b",
            "text": "The batch bump stays under the lift gate so withholding is right and notes still name the reagent batch."
          },
          {
            "id": "c",
            "text": "That scenario is one of the four held-out documents so it is excluded from the result entirely."
          },
          {
            "id": "d",
            "text": "An unclear label means generation failed so that scenario produced no grid that could be judged."
          }
        ],
        "salt": "70854749f7f893fc",
        "answerHash": "3342878f3212eedda588a9d41181ebae22cfb6ce41c08b136cda52216910c565",
        "explain": "VGhlIG92ZXJhbGwgcmF0ZSBjYW4gc3RpbGwgYmUgb3ZlciB0aGUgMiUgc3BlYyB3aGlsZSBubyBzdHJhdHVtIGNsZWFycyBsaWZ0IDEuOC4gV2l0aGhvbGRpbmcgaXMgdGhlIGRlc2lnbmVkIGNhbGwuIFRoYXQgaXMgdGhlIG9wcG9zaXRlIG9mIGZvcmNpbmcgYSBjYXVzZSB0byBtYWtlIHRoZSBzbGlkZSB0aWR5Lg=="
      },
      {
        "id": "s8q3",
        "prompt": "What extra call showed up on the drift scenarios, and did it change top-1?",
        "choices": [
          {
            "id": "a",
            "text": "The leading name flipped to the reagent batch on all four shifting documents and the gauge fell to second place."
          },
          {
            "id": "b",
            "text": "Those shifting documents were removed from the judged set once a second stratum appeared."
          },
          {
            "id": "c",
            "text": "A reagent-batch stratum also cleared the bar and the leading name stayed the drifting gauge on purpose."
          },
          {
            "id": "d",
            "text": "Only the note ordering saw the gauge and the table ordering stayed on the reagent batch."
          }
        ],
        "salt": "c8e7a637fa35ef3c",
        "answerHash": "771e59623494fc099e03e32125beebf8d690b6be533374abd78713532cf72da5",
        "explain": "QSByw6lzdW3DqSBidWxsZXQgdGhhdCBrZWVwcyAyMi8yMiBhbmQgZHJvcHMgdGhlIHNlY29uZCBzdHJhdHVtIGlzIG1pc2xlYWRpbmcuIFRoZSBmYWlsdXJlIG5vdGUgdHJhdmVscyB3aXRoIHRoZSBjZWxsLg=="
      },
      {
        "id": "s8q4",
        "prompt": "Why does the report not claim a Llama 3.1 8B versus Llama 3.2 1B accuracy?",
        "choices": [
          {
            "id": "a",
            "text": "An older llama pair is still the number a resume is supposed to quote in place of this table."
          },
          {
            "id": "b",
            "text": "The cloud host ran both llama tags across the full set and the two figures came out tied."
          },
          {
            "id": "c",
            "text": "The smaller llama tag won the comparison and that number is confidential so it stays out of the memo."
          },
          {
            "id": "d",
            "text": "No llama tag was installed and the table compares two ordering policies on the deterministic engine."
          }
        ],
        "salt": "7890e6fb3080a6c5",
        "answerHash": "d2795dfd4546725b252dc76b6c091f4d20032dbf10eb937598ce7397916b04c2",
        "explain": "VGhlIHBsYW4ncyBtb2RlbCBwYWlyIGlzIG5vdyB0aG9zZSB0d28gTGxhbWEgdGFncy4gQSBtb2RlbCBkcmFmdCB3b3VsZCBzdGlsbCBoYXZlIHRvIHBhc3MgdGhlIG51bWVyaWMtZmlkZWxpdHkgY2hlY2sgYmVmb3JlIGl0IHdhcyBzaG93bi4gRG8gbm90IHF1b3RlIHRoZSB0YWJsZSBhcyBhIG1vZGVsLWFjY3VyYWN5IG51bWJlci4="
      },
      {
        "id": "s8q5",
        "prompt": "Why is the red-herring key written \"true\" with quotes in the YAML?",
        "choices": [
          {
            "id": "a",
            "text": "The parser treats an unquoted true as a boolean and the builder looks up that string in the map."
          },
          {
            "id": "b",
            "text": "The marks around true force the batch id to be parsed as a float which is what the builder expects."
          },
          {
            "id": "c",
            "text": "The document is a braced data format that requires marks around every name including true."
          },
          {
            "id": "d",
            "text": "The marks around true tell the note ordering to skip the document so it cannot take the decoy."
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
            "text": "The two percent promise stays out because it would let the ordering step decide escalate before it sees a stratum."
          },
          {
            "id": "b",
            "text": "The hidden expected label stays out of ordering because that block is the grade and not an input."
          },
          {
            "id": "c",
            "text": "The description seed stays out because it would let the ordering step rebuild the grid another way."
          },
          {
            "id": "d",
            "text": "The column array stays out because it would tell the ordering step which strata it is allowed to grade."
          }
        ],
        "salt": "08157241d4804410",
        "answerHash": "1ef0bb6c3b5bbaf5c97b23ca44efab6c3b1de9e07388d777a173a462573bb44d",
        "explain": "a2V5d29yZF9jYXVzZSBvbmx5IHNjYW5zIHdlZWstMCBpbmplY3Rpb24gdGV4dCwgYW5kIHNvZnR3YXJlIGlzIGJlZm9yZSBsb3Qgc28gYSBzZW50ZW5jZSB0aGF0IHNheXMgYm90aCBzdGlsbCBoYXMgb25lIGNhbGwuIEl0IG5ldmVyIG9wZW5zIHRoZSB0YWJsZS4="
      },
      {
        "id": "s8q7",
        "prompt": "Why did version 2.4.0 need to be copied into the fidelity facts as a string?",
        "choices": [
          {
            "id": "a",
            "text": "That token is the failure frequency on a software scenario so it belongs in the fact bag as a percent."
          },
          {
            "id": "b",
            "text": "The note ordering treats 2.4 as its grade unless that token is listed in the fact bag."
          },
          {
            "id": "c",
            "text": "An identifier is stripped only when its exact text is in the fact bag so 2.4.0 must be placed there."
          },
          {
            "id": "d",
            "text": "The schema holds release text only after it is coerced to a float which is why 2.4.0 is placed in the bag."
          }
        ],
        "salt": "57bcc0bac62c18fd",
        "answerHash": "d7e4802e1fcbc3f169d37bed8a7ad6d0a30f5072a8f45ad5b14bf018ccb908f6",
        "explain": "VGhlIHRlcm1pbmFsIFdoeSBmb3IgYSBzb2Z0d2FyZSBoaXQgc2F5cyAyLjQuMC4gUHV0dGluZyB0aGF0IHRva2VuIGluIHRoZSBmYWN0cyBsZXRzIHRoZSBzZW50ZW5jZSBuYW1lIHRoZSB2ZXJzaW9uIHdpdGhvdXQgZmFpbGluZyB0aGUgZ3VhcmQuIFRoZSB0ZXN0IGluIHRlc3RfcmNhIGxvY2tzIGl0Lg=="
      },
      {
        "id": "s8q8",
        "prompt": "What does CI run from this session's script?",
        "choices": [
          {
            "id": "a",
            "text": "Nothing from the evaluation entry is executed and the memo is edited by hand before the job."
          },
          {
            "id": "b",
            "text": "All 22 documents are sent to an active llama server and the job fails if that server is down."
          },
          {
            "id": "c",
            "text": "A refit of the lift gate on the held-out split happens before the smoke limit is applied."
          },
          {
            "id": "d",
            "text": "The entry runs at limit 5 with a smoke flag and fails when top choice or fidelity is missed."
          }
        ],
        "salt": "15c51f71a75472dc",
        "answerHash": "ef94a8d4fb7f9baf50d6f730bfa8d96211f50e023b12303d79b29135dbda4608",
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
            "text": "The lap note is not the ending and the wrap-up confirms the last sections and builds the slides."
          },
          {
            "id": "b",
            "text": "The fourth lap deletes the schedule and starts the opening step again from a cleared guess list."
          },
          {
            "id": "c",
            "text": "A program outside the graph produces the slides and skips the fidelity check on purpose."
          },
          {
            "id": "d",
            "text": "The lap memo cannot represent numbers above 3 so the fourth lap has to leave the graph entirely."
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
            "text": "The forecast is a second scenario document the recipient signed so the watched label is a fair description."
          },
          {
            "id": "b",
            "text": "The field document is not rewritten and clearing the leading stratum is only a counterfactual case."
          },
          {
            "id": "c",
            "text": "The slide tool requires the watched-results phrase on the impact frame or the file will not save."
          },
          {
            "id": "d",
            "text": "Calling those bars watched results is fair because the scenario document already contains the cured records."
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
            "text": "It is the amount pasted from the complaint mail and the wording does not recompute that amount."
          },
          {
            "id": "b",
            "text": "It is a round number the model picks for an executive reader and it ignores both the row count and the unit price."
          },
          {
            "id": "c",
            "text": "It is failure count times unit price and on the bad batch that product is 529 times 85 with no typed total."
          },
          {
            "id": "d",
            "text": "It is the client points for the investigation epic multiplied by 1000 and then placed on the frame."
          }
        ],
        "salt": "068eee5576b06244",
        "answerHash": "ff774e35190a709c58109776df1bed64e329973282847c596791918aa8524ab9",
        "explain": "YnVpbGRfY2xvc2VvdXRfZmFjdHMgY29tcHV0ZXMgdGhlIHByb2R1Y3QgYW5kIGRyb3BzIHRoZSBmcmFtZSBiZWZvcmUgdGhlIHJlY29yZCBpcyBzdG9yZWQuIHB5dGhvbi1wcHR4IHdyaXRlcyB0aGUgc2xpZGUgZnJvbSB0aG9zZSBmYWN0cywgc28gYSBzbGlkZSBjYW5ub3QgaW52ZW50IGEgY29zdC4gbWF0cGxvdGxpYiB3aXRoIHRoZSBBZ2cgYmFja2VuZCBkcmF3cyB0aGUgY2hhcnQgUE5HLiBLYWxlaWRvIGlzIG5vdCBzaGlwcGVkLg=="
      },
      {
        "id": "s9q4",
        "prompt": "Which eval numbers are safe on a résumé, and which sentence has to sit next to them?",
        "choices": [
          {
            "id": "a",
            "text": "Quote any cell you like because the slides are a simulation and the disclaimer covers a comparison that was never run."
          },
          {
            "id": "b",
            "text": "Quote a perfect field accuracy because the table top choice was 22 of 22 and treat that cell as a clinical result."
          },
          {
            "id": "c",
            "text": "Quote the note ordering at 3 of 22 by itself and present that ratio as the accuracy of the whole ordering step."
          },
          {
            "id": "d",
            "text": "Quote the table result at 22 of 22 beside the notes at 3 of 22 and the shift documents and do not call it clinical."
          }
        ],
        "salt": "21ae2bfc46653180",
        "answerHash": "a99aac7db2ef159b63915867f50912009860ed78e4882fc201ea01dc1d6a3f30",
        "explain": "UkVTVU1FX0JVTExFVFMubWQgcHV0cyB0aGUga2V5d29yZCBtaXNzIGFuZCB0aGUgZHJpZnQgc2Vjb25kIHN0cmF0dW0gaW4gdGhlIHNhbWUgYnJlYXRoIGFzIDIyLzIyLiBRdW90aW5nIHRoZSBmaXJzdCBudW1iZXIgYWxvbmUgd291bGQgbWlzbGVhZC4gVGhlIGRpc2NsYWltZXIgc3RheXM6IHN5bnRoZXRpYywgbm90IGNsaW5pY2FsLCBub3QgYSBkZXZpY2Uu"
      },
      {
        "id": "s9q5",
        "prompt": "How many slides does write_deck create, and what does a no_single_cause call recommend?",
        "choices": [
          {
            "id": "a",
            "text": "Seven blank frames are produced and an unclear driver means the recommendation is not to contain a stratum."
          },
          {
            "id": "b",
            "text": "Twelve frames are produced with one for each client epic on the construction board plus the investigation tasks."
          },
          {
            "id": "c",
            "text": "One frame is produced and the model fills the title and the price and the recommendation into that lone frame."
          },
          {
            "id": "d",
            "text": "Seven frames are produced and an unclear driver still says to quarantine the first batch named on the document."
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
            "text": "Both name settings are required and the cloud app refuses to boot if either one is absent."
          },
          {
            "id": "b",
            "text": "The name defaults to llama3.1:8b on the desktop runner and the cloud app stays deterministic."
          },
          {
            "id": "c",
            "text": "The cloud app downloads the larger tag on every load and executes that tag while building the slides."
          },
          {
            "id": "d",
            "text": "The small tag on the cloud app produces the slides which is why the on-laptop name goes unused."
          }
        ],
        "salt": "ae5cb36718eed753",
        "answerHash": "22dffa53b1f33978df950b51825853aa9bc298e6e88566913e8b8c33433d7843",
        "explain": "VGhlIFJFQURNRSBtb2RlbCB0YWJsZSBzYXlzIHRoZSBzYW1lIHRoaW5nLiBHZW1tYSAzIGFuZCBQaGktNCBhcmUgb3RoZXIgZG9jdW1lbnRlZCB0YWdzLiBDbG9zZS1vdXQgaXRzZWxmIGlzIGEgdGVtcGxhdGUgcGx1cyB0aGUgZmlkZWxpdHkgZ3VhcmQuIE5vIG5ldyBtb2RlbCBsaWJyYXJ5Lg=="
      },
      {
        "id": "s9q7",
        "prompt": "What does the week-4 leadership injection on bad_lot ask for, and which ticket is the deck?",
        "choices": [
          {
            "id": "a",
            "text": "It requests an active chat thread and this snapshot ships that thread as the wrap-up instead of slides."
          },
          {
            "id": "b",
            "text": "It requests issue INV-101 and the original brief is rewritten into slides without opening a new issue."
          },
          {
            "id": "c",
            "text": "It wants the recommendation and the effectiveness check and those slides are issue INV-303 on epic INV-6."
          },
          {
            "id": "d",
            "text": "It requests a fine-tune of the table ordering on the full set and that tune is the fourth-lap deliverable."
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
            "text": "The installed model reads the complaint and names the driver and the slides then quote cured rows as watched results."
          },
          {
            "id": "b",
            "text": "A client token is required before the lap can finish and the note-only number is quoted once shift cases drop out."
          },
          {
            "id": "c",
            "text": "This is a medical device with a cleared claim of 22 of 22 and the cloud model writes it once a client token arrives."
          },
          {
            "id": "d",
            "text": "Strata over a fixed bar are kept and a wrong remark loses and the chart is a projection and the table hit 22 with notes at 3."
          }
        ],
        "salt": "94aec47c194e385b",
        "answerHash": "159302c3666f54f13df13d3d1e00a2ecacd20505b1cbc3a3698e385050940760",
        "explain": "VGhlIHBpdGNoIGtlZXBzIHRoZSBkaXNjbGFpbWVyLCB0aGUgZXZpZGVuY2UgYmFyLCB0aGUgaGVycmluZyByZXN1bHQsIGFuZCB0aGUgc2Vjb25kIHN0cmF0dW0uIEl0IGRvZXMgbm90IHR1cm4gdGhlIHNjb3JlY2FyZCBpbnRvIGEgY2xpbmljYWwgY2xhaW0uIFlvdSBjYW4gcnVuIHRoZSBkZXRlcm1pbmlzdGljIHBhdGggd2l0aCBubyBBUEkga2V5Lg=="
      }
    ]
  }
};
