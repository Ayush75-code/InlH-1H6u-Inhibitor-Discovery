# Internalin H Inhibitors for *Listeria monocytogenes* - In Silico Discovery

**Novel Anti-Virulence Therapy | Triterpenoid Inhibitors of InlH**

[![Published](https://img.shields.io/badge/Status-Published-green)](paper/published_paper.pdf)
[![MD Simulation](https://img.shields.io/badge/MD-125ns_GROMACS-blue)](simulations/)
[![Target](https://img.shields.io/badge/Target-Internalin_H-red)](https://www.rcsb.org/structure/1H6U)

## Abstract

*Listeria monocytogenes* is a lethal food-borne bacterium with high mortality rates (20–30%) and growing antimicrobial resistance. This study explores **anti-virulence therapy** by targeting **Internalin H (InlH)**, a key surface protein involved in immune evasion, as an alternative to conventional antibiotics.

### Key Finding
> **Hederagenin analogue (CID 137633443)** was identified as the most potent InlH inhibitor with:
> - Binding free energy (ΔGbind): **−17.09 kcal/mol**
> - Lowest HOMO-LUMO gap: **4.92 eV**
> - Superior dynamic stability (low RMSD, deep FEL basin)

## Target Protein

| Property | Detail |
|----------|--------|
| **Protein** | Internalin H (InlH) |
| **Organism** | *Listeria monocytogenes* |
| **PDB ID** | [1H6U](https://www.rcsb.org/structure/1H6U) |
| **Function** | Immune evasion virulence factor |
| **Therapeutic Strategy** | Anti-virulence (non-antibiotic) |

## Compounds Investigated

| Compound | PubChem CID | Role | ΔGbind (kcal/mol) |
|----------|-------------|------|-------------------|
| **Hederagenin analogue** | 137633443 | **Lead candidate** | **−17.09** |
| Lupeol analogue | 70626379 | Test compound | −9.33 |
| Oleanolic Acid analogue | 44575931 | Control | −10.88 |
| Maslinic Acid analogue | 163053220 | Test compound | −9.65 |

## Methodology

```
HTVS Virtual Screening → ADMET Profiling → Molecular Docking
                                              ↓
                              125 ns MD Simulation (GROMACS)
                                              ↓
                    RMSD, RMSF, Rg, SASA, H-bonds, PCA, FEL, DCCM
                                              ↓
                              MM/GBSA Binding Energy
                                              ↓
                              DFT (HOMO-LUMO, ESP)
```

| Step | Tool | Details |
|------|------|---------|
| Virtual Screening | AutoDock Vina | HTVS of compound library |
| ADMET | SwissADME, pkCSM | Pharmacokinetic profiling |
| MD Simulation | GROMACS 2021 | 125 ns, CHARMM36 FF |
| Binding Energy | gmx_MMPBSA | MM/GBSA decomposition |
| DFT Analysis | Gaussian | HOMO-LUMO, reactivity indices |

## Repository Structure

```
├── paper/                    # Published paper
├── notebooks/                # Colab/Jupyter notebooks
│   ├── Gromacs_Installation.ipynb
│   ├── GROMACS_hed.ipynb     # Hederagenin simulation
│   ├── GROMACS_lup.ipynb     # Lupeol simulation
│   ├── GROMACS_mas.ipynb     # Maslinic Acid simulation
│   ├── Control_run.ipynb     # Control simulation
│   └── GROMACS_runs_analysis.ipynb
├── analysis/                 # MD trajectory analysis
│   ├── rmsd/                # Stability analysis
│   ├── rmsf/                # Flexibility analysis
│   ├── pca_fel_dccm/        # Conformational dynamics
│   ├── mmpbsa/              # Binding energetics
│   └── dft/                 # Electronic properties
├── results/                  # Processed results
├── simulations/              # Raw MD data (~48 GB)
└── docs/                     # Supplementary data
```

## Data Availability

| Content | Size | Access |
|---------|------|--------|
| Analysis scripts & figures | ~600 MB | ✅ This repo |
| MD trajectories (.xtc) | ~48 GB | 📧 On request |

## Citation

If you use this data, please cite:

> **Targeting a key virulence factor in Listeria monocytogenes: An in silico discovery and pharmacokinetic profiling of novel internalin H inhibitors**  
> *In Silico* (2025)  
> DOI: [10.1016/j.insi.2025.100153](https://doi.org/10.1016/j.insi.2025.100153)

```bibtex
@article{inlh_inhibitors_2025,
  title={Targeting a key virulence factor in Listeria monocytogenes: 
         An in silico discovery and pharmacokinetic profiling of 
         novel internalin H inhibitors},
  journal={In Silico},
  year={2025},
  doi={10.1016/j.insi.2025.100153}
}
```

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

For questions, data requests, or collaborations:  
📧 **Email:** ayushd9275@gmail.com

---

**Keywords:** Internalin H, Listeria monocytogenes, anti-virulence therapy, molecular dynamics, triterpenoids, drug discovery, GROMACS, MM/GBSA, DFT
