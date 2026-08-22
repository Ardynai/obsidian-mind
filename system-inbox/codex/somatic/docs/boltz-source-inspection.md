# Boltz Source Inspection

Phase 6A inspected the staged `jwohlwend/boltz` source read-only at
`C:\AI\external-sources\somatic\boltz`, commit
`b1ebfc46ecf57f5414e0d1a6f9027bbb122c53bc`. No dependencies were installed,
no package manager was run, no Boltz command was executed, no model weights,
datasets, or MSAs were downloaded, and no network or MSA server call was made.

## Source Status

- Source path: `C:\AI\external-sources\somatic\boltz`
- Inspected commit: `b1ebfc46ecf57f5414e0d1a6f9027bbb122c53bc`
- License: MIT via `LICENSE`
- Package: `boltz` version `2.2.1`
- Python range: `>=3.10,<3.13`
- Console script: `boltz = boltz.main:cli`
- Primary command: `boltz predict <INPUT_PATH> [OPTIONS]`

## Package Weight

Boltz is too heavy for Somatic's basic install. Its package metadata declares
dependencies including `torch`, `pytorch-lightning`, `rdkit`, `requests`,
`pandas`, `fairscale`, `wandb`, `biopython`, `scipy`, `numba`, `gemmi`,
`scikit-learn`, and chemistry/modeling helpers. Its optional `cuda` extra adds
cuEquivariance CUDA packages.

Somatic must not add `boltz` or these transitive packages to the basic install.
The current `biomodel` extra remains a planning lane, not a Boltz runtime lane.

## Prediction Command Shape

The inspected CLI shape is:

```text
boltz predict <INPUT_PATH> [OPTIONS]
```

Important options for future planning metadata:

- `--model` selects `boltz1` or `boltz2`; upstream defaults to `boltz2`.
- `--out_dir` selects the prediction output root.
- `--cache` selects the model/data cache; default is `~/.boltz` or `BOLTZ_CACHE`.
- `--accelerator` defaults to `gpu` and can be `gpu`, `cpu`, or `tpu`.
- `--devices`, `--recycling_steps`, `--sampling_steps`, and
  `--diffusion_samples` affect compute requirements.
- `--output_format` can be `mmcif` or `pdb`.
- `--use_msa_server` enables remote MSA generation and must remain disabled.
- `--msa_server_url` defaults to `https://api.colabfold.com` when MSA server
  mode is enabled.
- `--msa_server_username`, `--msa_server_password`, `--api_key_header`, and
  `--api_key_value` are credential surfaces for MSA server use.

## Input Formats

Boltz prediction accepts a single YAML or FASTA file, or a directory of YAML or
FASTA inputs. YAML is preferred; FASTA is documented as deprecated.

The YAML input schema supports:

- `sequences`: proteins, DNA, RNA, and ligands.
- Ligands: either SMILES or CCD code.
- Protein MSA references: `.a3m`, CSV with `sequence,key`, `empty`, or omitted
  only when MSA server generation is enabled.
- `constraints`: bonds, pockets, and contacts.
- `templates`: CIF or PDB structure templates.
- `properties`: affinity prediction for a single small-molecule binder.

Somatic should plan against YAML metadata first and treat FASTA as a legacy
input reference only.

## Output Formats

Boltz writes outputs under an output directory shaped like:

```text
out_dir/
  boltz_results_<input-stem>/
    predictions/
      <input-id>/
        <input-id>_model_<rank>.cif
        confidence_<input-id>_model_<rank>.json
        affinity_<input-id>.json
        pae_<input-id>_model_<rank>.npz
        pde_<input-id>_model_<rank>.npz
        plddt_<input-id>_model_<rank>.npz
    processed/
```

The confidence JSON contains aggregate structure-confidence fields such as
`confidence_score`, `ptm`, `iptm`, `complex_plddt`, chain scores, and pairwise
interface scores. Affinity output contains `affinity_pred_value` and
`affinity_probability_binary`, with optional ensemble-specific fields.

In Somatic Phase 6A these paths are only planned artifact references. No actual
prediction output is generated.

## Download And Network Behavior

The inspected source downloads model/data artifacts when cache files are absent.
For Boltz-2 that includes molecule data, the structure checkpoint, and the
affinity checkpoint. URLs include `model-gateway.boltz.bio` and Hugging Face.

MSA generation can call a remote MMseqs2/ColabFold server when
`--use_msa_server` is set. The code supports basic auth and API-key auth via
CLI options and environment variables.

Somatic must keep all of these disabled by default:

- checkpoint downloads
- molecule/CCD cache downloads
- remote MSA server calls
- credential handling for MSA servers
- training data downloads
- evaluation dataset downloads
- telemetry or W&B training behavior

## Compute And Resource Boundary

Boltz upstream recommends `boltz[cuda]` for GPU use. CPU/non-CUDA use is
possible but documented as significantly slower. The prediction command defaults
to GPU acceleration. Training and data processing require additional storage and
tools; training docs describe hundreds of GB of data and external tools such as
MMseqs2 and Redis for preprocessing.

Somatic Phase 6A does not perform resource probing beyond documenting the
future requirement. Any real mode must require explicit resource review before
GPU, TPU, large cache, model download, or long-running execution is allowed.

## Somatic Wrap Decision

Somatic should wrap only the planning boundary:

- desired objective and target refs
- input artifact refs and expected Boltz input format
- selected model family/version
- expected command shape
- cache, weights, MSA, and compute requirements
- expected output artifact refs
- provenance, assumptions, and limitations
- consent gates for any future model runtime, download, MSA server, or cloud use

Somatic must not enable by default:

- importing `boltz`
- calling `boltz predict`
- loading checkpoints
- downloading model/data/MSA assets
- calling MSA servers
- using GPU/TPU runtime
- running training, evaluation, or processing scripts
- making scientific, clinical, lab, or efficacy claims

The implemented scaffold is `somatic.providers.boltz`. It is fake-backed,
deterministic, and disabled by default.
