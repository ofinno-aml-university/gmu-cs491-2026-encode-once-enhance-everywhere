# Encode Once, Enhance Everywhere

**George Mason University CS491 capstone | Fall 2026 - Spring 2027 | Sponsored by Ofinno**

Build an offline video delivery pipeline that produces multiple output profiles from one stored package of standard video encodes and pretrained enhancement models. Measure when neural enhancement improves on ordinary bicubic upscaling, and what that improvement costs.

## Project status

Project setup is underway. This repository currently contains introductory documentation; application code, installation steps, and runnable examples will be added as the team develops the prototype. Features below describe the agreed project scope, not completed functionality.

## What we are building

| Component | Purpose |
| --- | --- |
| Packager | Encode compact base rungs and write a manifest containing measured enhancement options and costs. |
| Delivery compiler | Select a base rung and enhancement chain for each segment under a device and bandwidth budget. |
| Comparison interface | Show outputs side by side at matched delivered bitrate, with quality and performance measurements. |
| Evaluation harness | Reproduce benchmark results and figures with one command. |

Every quality comparison includes three anchors at matched delivered bitrate:

1. Direct encode at the output resolution.
2. Low-resolution base encode plus bicubic upscaling.
3. Low-resolution base encode plus neural enhancement.

The key result is the gain of anchor 3 over anchor 2, reported by content genre alongside compute cost. Report VMAF and VMAF-NEG together, with PSNR as a sanity check. Pin encoder settings and record measured bitrate, reference-machine details, and model versions.

## Delivery tiers

- **Tier 1: proof of concept.** Encode two base resolutions, apply a fixed allowlisted enhancement chain, generate at least two output profiles, and evaluate all three anchors at three or more rate points per clip. Produce reproducible rate-quality curves and BD-rate results against bicubic.
- **Tier 2: minimum viable product.** Add measured per-segment decisions, stable switching between enhancement chains, the comparison interface, and a reproducible report including packaging cost.
- **Tier 3: stretch work.** Select advanced capabilities with the sponsor, such as optimized inference, short-form output, or a quality-compute frontier study.

Fall emphasizes learning, baseline measurements, and validating approaches. Spring focuses on implementation, integration, and the final demonstration. The RFP remains the detailed technical acceptance specification; agree project checkpoints and provisional targets with the technical contacts.

## Course milestones

| Date | Milestone |
| --- | --- |
| October 2, 2026 | Proof of Concept Proposal: high-level design and project plan |
| November 20, 2026 | Proof of Concept Report; send to sponsor and copy faculty |
| December 4, 2026 | Interim Program Review (IPR) class presentation and Spring implementation proposal |
| April 30, 2027 | Final demonstration |

Students separately schedule a 30-60 minute sponsor review for the interim and final presentations. Course dates follow the Fall 2026 syllabus and Larry Bailey's September 8 clarification; follow subsequent instructor updates. Regular sponsor meetings are planned every two weeks for 30 minutes, with exact slots agreed by the team and both technical contacts.

## Getting started

1. Read the sponsor RFP and the current course syllabus.
2. Confirm the reference-machine specification, test clips, model allowlist, and cost-table format with the technical contacts.
3. Establish a Python-first toolchain using FFmpeg/x265, the reference VMAF implementation, and an inference runtime such as ONNX Runtime.
4. Reproduce the three-anchor comparison on a small test case before expanding the benchmark.
5. Add exact installation, execution, and reproduction commands to this README as code becomes available.

Processing is offline; Tier 1 and Tier 2 have no real-time requirement. Use pretrained allowlisted models only. Model training, fine-tuning, distillation, custom bitstreams, entropy coding, codec forks, and frame interpolation are outside the agreed scope.

## Working together

Use issues for scoped tasks and pull requests for teammate review. Document assumptions, experiment configurations, and negative results. Keep published work reproducible and use only materials whose licenses permit the intended use and redistribution.

**Technical contacts:** Jung-Kyung Lee and Thang Nguyen, Ofinno.  
**Sponsor contact:** Chia-Yang Tsai, Ofinno.

## License

The RFP requires the project deliverable to be released under the MIT License. A LICENSE file has not yet been added. Third-party code, models, and datasets retain their own licenses; document those separately.
