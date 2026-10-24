# GitHub upload packaging verification

This is a repository packaging operation, not another answering-system revision.

- Final portable application: **2.0-portable**.
- Original executable: **26,878,965 bytes**.
- Upload executable: **23,925,189 bytes** (22.82 MiB).
- Every one of the **198** archive-entry contents is byte-identical after recompression.
- All **195** readable source/assets match the original payload.
- Launcher modules remain deflated for executable ZIP import; payload assets use Python's
  standard-library ZIP/LZMA decompression. No new third-party dependencies or model are introduced.
- The recompressed executable was run with third-party site packages disabled: **118 tests
  passed** and all 30 PDF hashes matched. See `packaging_test_log.txt`.
- Verification environment: Linux / Python 3.13.5. The exact recompressed archive
  has not been run natively on macOS or Windows in this packaging check.
- Browser behavior and answer contents are not newly improved or claimed accurate by recompression.
- The original repaired ZIP and historical experiment outputs remain unchanged.
- The original complete 12-commit Git bundle is preserved; its actual authors and dates remain.
- No genuine human ratings saved only on the user's laptop have been imported here.
- No synthetic test ratings are shipped as participant or research observations.

Trello evidence is a documented privacy-minimised derivative; the original export remains untouched.
The raw export, invite URL, card email addresses and account profile metadata are not uploaded.

The app remains a local research prototype and the written report is still a separate deliverable.
Github browser upload limits were checked against official documentation:
https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository

## Additional repository checks

The root `run.py` launcher was executed in an isolated workspace with site packages disabled.
The actual HTTP API returned the repaired REPLUG/FiD comparison, the PDF endpoint returned
the exact original FiD bytes, and record export contained no invented human or pilot ratings.
A pattern-based credential scan covered working text and 37 historical text blobs with no
matching access tokens, private keys, Trello invitation links or card email addresses found.
This pattern scan is not a guarantee against every possible secret.
