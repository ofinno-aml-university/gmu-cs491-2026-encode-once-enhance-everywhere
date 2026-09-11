# Encode Once, Enhance Everywhere

**George Mason University CS491 | Fall 2026 - Spring 2027 | Sponsored by Ofinno**

Build an offline video delivery pipeline that combines a compact encoded base with pretrained neural enhancement. Measure **how much neural enhancement improves quality over bicubic upscaling, on which content, and at what compute cost**.

[Read the project one-pager (PDF)](project-2-one-pager-public-v1.0.pdf)

**Status:** Project setup. Implementation, installation commands and results will be added as the team develops the pipeline. Values illustrated in the one-pager are examples, not measured project results. The accepted sponsor RFP defines the detailed requirements.

## What we are building

| Component | Purpose |
| --- | --- |
| Packager | Encode compact base representations, measure segments and produce a manifest. |
| Compiler | Select a base and enhancement chain for each segment within a device compute budget. |
| Comparison interface | Show the selected outputs and their quality/cost tradeoffs. |
| Evaluation harness | Reproduce the three anchors, metrics and comparison report. |

The expected stack is Python, FFmpeg/x265, VMAF and pretrained inference models, with ONNX Runtime where appropriate. Record the exact model, tool and configuration versions used.

## Evaluation approach

Compare these three anchors at matched delivered bits:

1. Direct encoding at the target resolution.
2. A lower-resolution base followed by bicubic upscaling.
3. A lower-resolution base followed by neural enhancement.

The key comparison is **neural versus bicubic**, not only neural versus direct encoding. Report VMAF and VMAF-NEG alongside PSNR, inference cost and the test-machine configuration. Pin encoding settings, use at least three rate points per clip, and produce rate-quality curves and BD-rate comparisons against the bicubic anchor. Report results by content genre.

## Scope and success criteria

- **Tier 1: End-to-end PoC.** Base encoding and a fixed allowlisted enhancement chain, at least two output profiles, all three anchors and reproducible first curves.
- **Tier 2: MVP.** Measured per-segment cost tables drive content-adaptive selection, with stable switching, a comparison interface and reproducible reports. Report packaging cost separately.
- **Tier 3: Extensions.** Explore optimized or real-time inference, short-form output, per-genre frontiers or streaming packaging after the MVP works.

Fall focuses on learning, baseline validation, the PoC and Spring plan. Spring develops and integrates the MVP. Tier 1/2 operate offline with pretrained models; training, fine-tuning, frame interpolation and custom codec development are outside this scope.

## Getting started

1. Review the RFP and course syllabus with the team.
2. Confirm the reference machine, licensed clips and pretrained-model allowlist with the project contacts.
3. Reproduce a small direct-encode and bicubic baseline before adding neural enhancement.
4. Record dependencies, encoder settings, model licenses and measurement commands.
5. Add installation instructions and a small repeatable evaluation when code is available.

## Course milestones

| Date | Checkpoint |
| --- | --- |
| October 2, 2026 | Project proposal |
| November 20, 2026 | Proof of concept |
| December 4, 2026 | Interim Program Review (IPR) and Spring implementation plan |
| April 30, 2027 | Final demonstration |

IPR means **Interim Program Review**, the course progress review. These dates follow the Fall 2026 syllabus and instructor clarification; later course announcements take precedence. The team separately schedules its sponsor review. Plan a 30-minute sponsor meeting every two weeks, with the recurring slot agreed in the project Teams group chat.

## Collaboration and contact

Use the **project Teams group chat** for coordination and sponsor questions. Keep technical tasks, decisions and reproducible bug reports in GitHub Issues; submit changes through pull requests with a short description and validation evidence. Agree on the review workflow with the project contacts.

Ofinno project contacts: **Jung-Kyung and Thang**. Student team: **6 students**.

Sponsor contact: **Chia-Yang Tsai (Ofinno)**. Student contact details and Teams invitation links are not published here.

## License

Original project code is released under the [MIT License](LICENSE). Contributors retain copyright in their contributions. MIT permits commercial reuse, including use in a startup, subject to its notice requirements.

Third-party code, model weights, datasets and media remain subject to their own licenses. Record their sources and license terms before adding them. The Ofinno name and logo in the sponsor one-pager identify the sponsor; the MIT software license grants no trademark rights or endorsement.
