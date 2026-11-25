# Agreed ERD deviations

The implementation differs from the approved FYP1 ERD in these agreed ways:

- `ANNOTATION.label` accepts `MET`, `NOT_MET`, `PARTIAL`, `N/A`, and `NC`.
  `N/A` means the requirement does not apply to the service; `NC` means it
  applies, but the captured flow does not show that step. `FINDING.verdict`
  remains limited to `MET`, `NOT_MET`, and `PARTIAL`.
- `ANNOTATION` labels a `(flow, requirement)` pair, independently of any
  `FINDING`. Each annotator may provide one label for that pair.
- Each `FINDING` belongs to a `PIPELINE_RUN`, recording the model and whether
  screenshots were enabled. A run can have at most one finding per flow and
  requirement.
